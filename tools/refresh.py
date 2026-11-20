#!/usr/bin/env python3
"""Refresh the catalog from GeoNode, one version per change.

For each collection in ``tools/sources.json``:

1. Probe GeoNode: the dataset's ``last_updated``, and the WFS
   ``resultType=hits`` count.
2. Skip it unless it is due. A collection is due when ``last_updated`` moved
   past the current version (or the last check that changed nothing), or the
   count changed, and at least ``min_days`` have passed since the current
   version. ``min_days`` comes from the dataset's declared
   ``maintenance_frequency``.
3. Extract, repair and sort (``tools/extract.py``). When the rows hash the
   same as the current version, only the metadata is refreshed from GeoNode.
4. Check the style against the new rows (``tools/check_styles.py``).
5. Download the outgoing current file from the public URL to
   ``catalog/<coll>/versions/<version>.parquet``, and check it against the
   checksum the Collection records.
6. Write the new ``<leaf>.parquet`` and ``<leaf>.pmtiles``, and record the
   new version in ``collection.json`` (``tools/build_collection.py``).

Then the imagery and the virtual collections get their own refresh
(``tools/imagery/refresh.py``, ``tools/virtual/refresh.py``) when those
modules exist, and the run compares GeoNode's dataset list with
``sources.json``. A new or removed dataset is reported, never added: each
layer gets a data review before it is mirrored.

The measured doc facts of every changed collection are re-measured, the docs
regenerate, and the group and root catalogs are relinked.

A collection that fails at any step is rolled back: its folder returns to
its state before the run. The others go on. Nothing here uploads. The
workflow runs the gates, then ``tools/publish.py``.

    python3 tools/refresh.py --dry-run          # what is due, and why
    python3 tools/refresh.py                    # refresh what is due
    python3 tools/refresh.py --only limites/cpa --force
    python3 tools/refresh.py --restamp limites/cpa   # after a style edit
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import traceback
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_collection  # noqa: E402
import check_styles  # noqa: E402
import check_sync  # noqa: E402
import extract as extractor  # noqa: E402
import geonode  # noqa: E402
import snapshot  # noqa: E402
import stac_versions as stac  # noqa: E402
from tiles import tile_columns  # noqa: E402
from publish import ROOT, load_config  # noqa: E402
from styles import place_style  # noqa: E402

STATE = ROOT / "state" / "checks.json"
GENERATE = HERE / "generate"
FAILED = ("style", "error")


def parse(stamp: str) -> datetime:
    return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc)


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def decide(collection: str, entry: dict, probe: geonode.SourceState,
           current: dict | None, state: dict,
           now: datetime) -> tuple[bool, str]:
    """Whether a collection is due, and a sentence saying why.

    ``current`` is the current version asset of the Collection, or None.
    """
    if current is None:
        return True, "no version yet"
    seen = state.get(collection, {})
    known = max(filter(None, [current.get("pergamino:source_updated"),
                              seen.get("source_updated")]), default=None)
    count = seen.get("count", current.get("table:row_count"))
    edited = known is None or probe.last_updated > known
    recount = probe.count != count
    if not edited and not recount:
        return False, f"source unchanged since {known}"
    why = (f"source updated {probe.last_updated}" if edited else
           f"row count {count} -> {probe.count}")
    last = parse(current["created"])
    due = last + timedelta(days=entry["min_days"])
    if now < due:
        return False, (f"{why}, but the current version is "
                       f"{last:%Y-%m-%d}; next due {due:%Y-%m-%d}")
    return True, why


def download(url: str, out: Path) -> None:
    """Fetch a public object. data.source.coop answers 403 to urllib's
    default User-Agent, so the request names this tool."""
    out.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url, headers={"User-Agent": geonode.USER_AGENT})
    with urllib.request.urlopen(request, timeout=600) as response, \
            out.open("wb") as handle:
        shutil.copyfileobj(response, handle)


class StyleError(Exception):
    def __init__(self, problems: list[str]):
        super().__init__("\n".join(problems))
        self.problems = problems


class Context:
    def __init__(self, config: dict, sources: dict, now: datetime):
        self.public_base = config["public_base"].rstrip("/")
        self.catalog = ROOT / config["publish_dir"]
        self.sources = sources
        self.now = now
        self.stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    def url(self, collection: str, href: str) -> str:
        return stac.public_url(self.public_base, collection, href)


def assert_in_sync(ctx: Context, collection: str) -> None:
    """Refuse to run when the bucket holds a version git does not.

    That happens when a run published and then failed to commit. A refresh
    from the older checkout would archive the wrong file under the wrong
    label, and the bucket and git would disagree about history.
    """
    remote = check_sync.ahead_of(ctx.catalog, ctx.public_base, collection)
    if remote is not None:
        raise RuntimeError(
            f"{collection}: the bucket is at version {remote}, which this "
            "checkout does not have. Commit the published catalog/ state "
            "before refreshing again.")


def archive_current(ctx: Context, collection: str, asset: dict) -> Path:
    """Write the outgoing current file to ``versions/<version>.parquet``.

    The bytes come from the public URL and must match the checksum the
    Collection records, so the archive is exactly what readers had.
    """
    label = asset["version"]
    out = ctx.catalog / collection / "versions" / f"{label}.parquet"
    if not out.exists():
        download(ctx.url(collection, asset["href"]), out)
    if stac.multihash(out) != asset["file:checksum"]:
        out.unlink()
        raise RuntimeError(
            f"{collection}: the published {asset['href']} does not match "
            f"the checksum of version {label}; the file changed outside the "
            "refresh")
    return out


def rebuild(ctx: Context, collection: str, record: dict) -> bool:
    """Rebuild collection.json with no new version. True when it changed.

    ``updated`` moves only when something else in the document moved.
    """
    entry = ctx.sources["collections"][collection]
    path = ctx.catalog / collection / "collection.json"
    before = json.loads(path.read_text())
    after = build_collection.build(ctx.catalog, collection, entry, record,
                                   updated=before["updated"])
    if after == before:
        return False
    build_collection.build(ctx.catalog, collection, entry, record,
                           updated=ctx.stamp)
    return True


def refresh_one(ctx: Context, collection: str, probe: geonode.SourceState,
                state: dict) -> str:
    entry = ctx.sources["collections"][collection]
    leaf = stac.leaf(collection)
    folder = ctx.catalog / collection
    assert_in_sync(ctx, collection)
    current = stac.current(ctx.catalog, collection)
    record = snapshot.refresh([collection])[entry["alternate"]]

    with tempfile.TemporaryDirectory(prefix=f"refresh-{leaf}-") as tmp:
        result = extractor.extract(collection, Path(tmp), ctx.sources)
        if current and result.content_hash == current.get(
                "pergamino:content_hash"):
            state[collection] = {"source_updated": probe.last_updated,
                                 "count": probe.count, "checked": ctx.stamp}
            changed = rebuild(ctx, collection, record)
            return (f"rows unchanged since version {current['version']}; "
                    f"metadata {'updated' if changed else 'unchanged'}")

        previous = ctx.url(collection, current["href"]) if current else None
        folder.mkdir(parents=True, exist_ok=True)
        if not (folder / "styles" / "default.json").exists():
            place_style(folder, result.style, leaf)
        problems = check_styles.check(collection, str(result.parquet),
                                      previous, ctx.catalog)
        if problems:
            raise StyleError(problems)

        if current:
            archive_current(ctx, collection, current)
        label = stac.next_version(ctx.catalog, collection, ctx.stamp[:10])
        shutil.copyfile(result.parquet, folder / f"{leaf}.parquet")
        if result.legend:
            (folder / "legends").mkdir(exist_ok=True)
            shutil.copyfile(result.legend, folder / "legends" / "source.png")

    extractor.make_pmtiles(folder / f"{leaf}.parquet",
                           folder / f"{leaf}.pmtiles", leaf,
                           tile_columns(collection))
    build_collection.build(
        ctx.catalog, collection, entry, record, updated=ctx.stamp,
        new_version={
            "version": label,
            "created": ctx.stamp,
            "pergamino:source_updated": probe.last_updated,
            "pergamino:content_hash": result.content_hash,
            "pergamino:repaired_geometries": result.repaired,
            "pergamino:null_geometries": result.null_geometries,
        })
    state.pop(collection, None)
    return f"version {label}: {result.rows} rows"


def guarded(ctx: Context, collection: str, probe, state: dict) -> dict:
    """refresh_one, with the collection rolled back if it raises."""
    folder = ctx.catalog / collection
    with tempfile.TemporaryDirectory() as tmp:
        saved = Path(tmp) / "saved"
        if folder.exists():
            shutil.copytree(folder, saved)
        try:
            detail = refresh_one(ctx, collection, probe, state)
            return {"status": "ok", "detail": detail}
        except Exception as exc:  # noqa: BLE001 - report, roll back, go on
            if folder.exists():
                shutil.rmtree(folder)
            if saved.exists():
                shutil.copytree(saved, folder)
            kind = "style" if isinstance(exc, StyleError) else "error"
            detail = str(exc) if kind == "style" else traceback.format_exc()
            return {"status": kind, "detail": detail}


def source_changes(sources: dict) -> list[str]:
    """GeoNode datasets added or removed since sources.json was written."""
    from generate.grouping import EXCLUDED, LAYER_TO_GROUP

    served = geonode.wfs_typenames()
    records = {geonode.name_of(r): r for r in geonode.datasets()}
    known = {e["alternate"] for e in sources["collections"].values()}
    notes = []
    for name, record in sorted(records.items()):
        if geonode.eligible(record, served) is not None:
            continue
        if record["alternate"] in known:
            continue
        if name in LAYER_TO_GROUP:
            notes.append(f"{name}: grouped, but not in sources.json; run "
                         "python3 tools/geonode.py sources")
        elif name not in EXCLUDED:
            notes.append(f"{name}: a new GeoNode dataset with no group. It "
                         "needs a data review before it is mirrored.")
    alternates = {r["alternate"] for r in records.values()}
    for collection, entry in sorted(sources["collections"].items()):
        if entry["alternate"] not in alternates:
            notes.append(f"{collection}: {entry['alternate']} is gone from "
                         "GeoNode")
    return notes


def hook(name: str):
    """``tools/<name>/refresh.py`` as a module, or None when absent."""
    path = HERE / name / "refresh.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"{name}_refresh", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def regenerate(ctx: Context, changed: list[str],
               restamped: list[str] | None = None) -> None:
    """Re-measure the changed collections, then rebuild docs and catalogs.

    The docs feed back into the Collection: its documentation asset carries
    the README's size and checksum. Every changed or restamped collection is
    rebuilt after the docs are written.
    """
    python = sys.executable
    catalog = str(ctx.catalog)
    if changed:
        subprocess.run([python, str(GENERATE / "measure.py"), catalog,
                        *changed], check=True)
    subprocess.run([python, str(GENERATE / "build_docs.py"), catalog],
                   check=True)
    records = snapshot.load()
    for collection in changed + (restamped or []):
        alternate = ctx.sources["collections"][collection]["alternate"]
        rebuild(ctx, collection, records[alternate])
    subprocess.run([python, str(GENERATE / "build_catalogs.py"), catalog],
                   check=True)


def restamp(ctx: Context, names: list[str]) -> int:
    """Rebuild collection.json for ``names`` after a hand edit to a style,
    a legend or a thumbnail, with no new version."""
    records = snapshot.load()
    for name in names:
        alternate = ctx.sources["collections"][name]["alternate"]
        changed = rebuild(ctx, name, records[alternate])
        print(f"{name}: {'restamped' if changed else 'unchanged'}")
    regenerate(ctx, [], names)
    return 0


def select(sources: dict, only: str | None) -> list[str]:
    names = sorted(sources["collections"])
    if not only:
        return names
    picked = [n.strip() for n in only.split(",") if n.strip()]
    unknown = set(picked) - set(names)
    if unknown:
        sys.exit(f"unknown collection(s): {', '.join(sorted(unknown))}")
    return picked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", help="comma-separated collection ids")
    parser.add_argument("--force", action="store_true",
                        help="ignore min_days and the source signals")
    parser.add_argument("--dry-run", action="store_true",
                        help="print what is due and stop")
    parser.add_argument("--report", type=Path,
                        help="write the outcome per collection as JSON")
    parser.add_argument("--changed", type=Path,
                        help="write the ids of collections with a new "
                        "version, one per line")
    parser.add_argument("--restamp", metavar="IDS",
                        help="rebuild collection.json for these ids and stop")
    args = parser.parse_args()

    config = load_config()
    sources = geonode.load_sources()
    ctx = Context(config, sources, datetime.now(timezone.utc))
    if args.restamp:
        return restamp(ctx, select(sources, args.restamp))
    names = select(sources, args.only)

    state = load_state()
    report: dict[str, dict] = {}
    for name in names:
        try:
            probe = geonode.probe(sources["collections"][name])
        except Exception as exc:  # noqa: BLE001 - one dataset, not the run
            report[name] = {"status": "error",
                            "detail": f"probe failed: {exc}"}
            print(f"FAIL {name:55} probe failed: {exc}", flush=True)
            continue
        due, why = decide(name, sources["collections"][name], probe,
                          stac.current(ctx.catalog, name), state, ctx.now)
        if args.force:
            due, why = True, f"forced; {why}"
        print(f"{'DUE ' if due else 'skip'} {name:55} {why}", flush=True)
        if not due or args.dry_run:
            report[name] = {"status": "due" if due else "skipped",
                            "detail": why}
            continue
        report[name] = guarded(ctx, name, probe, state)
        print(f"     {name:55} {report[name]['status']}: "
              f"{report[name]['detail'].splitlines()[0]}", flush=True)

    if not args.only:
        for name in ("imagery", "virtual"):
            module = hook(name)
            if module is None:
                continue
            try:
                outcome = module.refresh(ctx.catalog, ctx.now, args.dry_run)
            except Exception:  # noqa: BLE001 - report and go on
                outcome = {f"{name}/*": {"status": "error",
                                         "detail": traceback.format_exc()}}
            report.update(outcome)
        try:
            notes = source_changes(sources)
        except Exception as exc:  # noqa: BLE001 - a notice, not a failure
            notes = [f"could not compare the GeoNode dataset list: {exc}"]
        for note in notes:
            print(f"note {note}", flush=True)
        if notes:
            report["geonode/datasets"] = {"status": "notice",
                                          "detail": "\n".join(notes)}

    versioned = [n for n, r in report.items()
                 if r["status"] == "ok" and r["detail"].startswith("version ")
                 and n in sources["collections"]]
    if not args.dry_run:
        save_state(state)
        if any(r["status"] == "ok" for r in report.values()):
            regenerate(ctx, versioned)
    if args.changed:
        args.changed.write_text("".join(f"{n}\n" for n in versioned))
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    failed = [n for n, r in report.items() if r["status"] in FAILED]
    for name in failed:
        print(f"\n--- {name} ({report[name]['status']})\n"
              f"{report[name]['detail']}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
