#!/usr/bin/env python3
"""Weekly check of the virtual collections (sources.json, ``collection``).

    python3 tools/virtual/refresh.py --dry-run     # report only
    python3 tools/virtual/refresh.py               # rebuild what moved

The weekly job calls ``refresh(catalog, now, dry_run)``. It returns one entry
per collection id::

    {"catastro/edificios_overture": {"status": "ok", "detail": "..."}}

Statuses:

- ``ok``: upstream answers and nothing moved, or (not dry run) it moved and
  the collection was rebuilt;
- ``due``: dry run only, a rebuild is needed (new Overture release, a part
  href that no longer answers, a GloFAS COG that moved);
- ``skipped``: the collection is configured but not built yet;
- ``error``: upstream could not be resolved, or a rebuild failed.

Overture is re-resolved through overture-portolan first and Overture's own
STAC second (see overture.resolve); the path used is stored per collection in
``pergamino:virtual.resolved_via``. GloFAS COGs are re-resolved through the
jrc-glofas items and probed with HEAD.

Outside a dry run every checked collection gets ``updated`` set to ``now``:
core.md (Source Provenance) asks a sync to stamp everything it checks, changed
or not. The group catalogs take the newest collection's stamp when
tools/generate/build_catalogs.py relinks them.

The decision logic is in pure functions (``decide_overture``,
``decide_glofas``) so tests/test_virtual_refresh.py covers it offline.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# tools/, for the package imports below. A bare ``import common`` would share
# one sys.modules entry with tools/imagery/common.py; see tools/refresh.py hook.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from virtual import common as C  # noqa: E402
from virtual import docs  # noqa: E402
from virtual import glofas as G  # noqa: E402
from virtual import overture as O  # noqa: E402

Result = dict[str, dict[str, str]]


# --- pure decisions ------------------------------------------------------


def stored_overture(collection: dict, hrefs: list[str]) -> dict:
    """What a built Overture collection currently points at."""
    virt = collection.get("pergamino:virtual", {})
    return {
        "release": virt.get("overture_release"),
        "resolved_via": virt.get("resolved_via"),
        "hrefs": sorted(hrefs),
    }


def decide_overture(stored: dict, resolved: dict | None,
                    error: str | None, live: dict[str, int],
                    dry_run: bool) -> tuple[str, str, bool]:
    """(status, detail, rebuild) for one Overture collection.

    ``live`` maps each stored href to its HTTP status. A rebuild is needed
    when the resolved release or part list differs from what is stored, or
    when a stored href no longer answers 200.
    """
    if resolved is None:
        return "error", f"cannot resolve upstream: {error}", False
    new_hrefs = sorted(p["href"] for p in resolved["parts"])
    dead = sorted(h for h, code in live.items() if code != 200)
    via = f"via {resolved['resolved_via']}"
    older = (stored["release"] or "") > resolved["release"]
    if older and not dead:
        # The mirror can lag behind a release this collection already
        # follows. Never step back while the stored hrefs still answer.
        return ("ok", f"{stored['release']} kept; {via} offers older "
                f"{resolved['release']}", False)
    reasons = []
    if resolved["release"] != stored["release"]:
        reasons.append(f"release {stored['release']} -> "
                       f"{resolved['release']}")
    elif new_hrefs != stored["hrefs"]:
        reasons.append("part list changed")
    if dead:
        reasons.append(f"{len(dead)} stored href(s) do not answer 200")
    if not reasons:
        return "ok", f"{stored['release']} unchanged, {via}", False
    detail = "; ".join(reasons) + f"; {via}"
    if dry_run:
        return "due", detail, False
    return "ok", "rebuilt: " + detail, True


def decide_glofas(stored_href: str, resolved_href: str | None,
                  error: str | None, code: int,
                  dry_run: bool) -> tuple[str, str, bool]:
    """(status, detail, rebuild) for one GloFAS collection."""
    if resolved_href is None:
        return "error", f"cannot resolve upstream item: {error}", False
    if resolved_href != stored_href:
        detail = f"COG moved: {stored_href} -> {resolved_href}"
        return ("due", detail, False) if dry_run else \
            ("ok", "rebuilt: " + detail, True)
    if code != 200:
        return "error", f"COG answers {code or 'nothing'}", False
    return "ok", "COG answers 200", False


# --- io ----------------------------------------------------------------------


def use_catalog(catalog: Path) -> None:
    """Point the builders at another catalog directory (tests, staging)."""
    C.CATALOG = catalog


def _load(path: Path) -> dict | None:
    return json.loads(path.read_text()) if path.exists() else None


def _stamp(path: Path, now: datetime) -> None:
    doc = _load(path)
    if doc is not None:
        C.write_json(path, C.keep_updated(path, doc, now, force=True))


def refresh_overture(now: datetime, dry_run: bool, partido) -> Result:
    out: Result = {}
    for layer in O.OVERTURE["layers"]:
        cid = layer["collection"]
        folder = C.folder(cid)
        coll = _load(folder / "collection.json")
        if coll is None:
            out[cid] = {"status": "skipped",
                        "detail": "not built; run tools/virtual/build.py"}
            continue
        stored = stored_overture(coll, O.stored_parts(coll, folder))
        resolved, error = None, None
        try:
            resolved = O.resolve(layer, partido.bbox)
        except Exception as exc:  # noqa: BLE001 - reported as error
            error = str(exc)
        live = {h: C.probe(h) for h in stored["hrefs"]}
        status, detail, rebuild = decide_overture(stored, resolved, error,
                                                  live, dry_run)
        rebuilt = False
        if rebuild:
            try:
                O.write_collection(layer, resolved, partido, docs, now,
                                   force_updated=True)
                rebuilt = True
            except Exception as exc:  # noqa: BLE001 - reported as error
                status, detail = "error", f"rebuild failed: {exc}"
        elif not dry_run and status == "ok":
            _stamp(folder / "collection.json", now)
        # The .ddb is gitignored: a fresh checkout has none, so write it
        # whenever it is missing, not only after a rebuild.
        ddb = folder / O.ddb_name(cid)
        if (not dry_run and resolved is not None and status == "ok"
                and (rebuilt or not ddb.exists())):
            detail += "; " + O.write_recipe(layer, resolved, partido)
        out[cid] = {"status": status, "detail": detail}
    return out


def refresh_glofas(now: datetime, dry_run: bool, partido) -> Result:
    out: Result = {}
    rebuild_any = False
    for layer in G.GLOFAS["layers"]:
        cid = layer["collection"]
        path = C.folder(cid) / "collection.json"
        coll = _load(path)
        if coll is None:
            out[cid] = {"status": "skipped",
                        "detail": "not built; run tools/virtual/build.py"}
            continue
        stored = coll["assets"]["data"]["href"]
        resolved, error = None, None
        try:
            resolved = G.resolve_cog(layer)[1]
        except Exception as exc:  # noqa: BLE001 - reported as error
            error = str(exc)
        code = C.probe(resolved or stored)
        status, detail, rebuild = decide_glofas(stored, resolved, error,
                                                code, dry_run)
        rebuild_any |= rebuild
        if not dry_run and status == "ok" and not rebuild:
            _stamp(path, now)
        out[cid] = {"status": status, "detail": detail}
    if rebuild_any:
        try:
            G.build(partido, docs, now)
            for cid, entry in out.items():
                if entry["status"] == "ok":
                    _stamp(C.CATALOG / cid / "collection.json", now)
        except Exception as exc:  # noqa: BLE001 - reported as error
            for cid, entry in out.items():
                if entry["detail"].startswith("rebuilt"):
                    out[cid] = {"status": "error",
                                "detail": f"rebuild failed: {exc}"}
    return out


def refresh(catalog: Path, now: datetime, dry_run: bool) -> Result:
    """Check every virtual collection; rebuild what moved unless dry_run."""
    use_catalog(catalog)
    partido = C.load_partido()
    result: Result = {}
    result.update(refresh_glofas(now, dry_run, partido))
    result.update(refresh_overture(now, dry_run, partido))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--catalog", type=Path, default=C.CATALOG)
    args = parser.parse_args(argv)
    result = refresh(args.catalog.resolve(), datetime.now(timezone.utc),
                     args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if any(r["status"] == "error" for r in result.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
