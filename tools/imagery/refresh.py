#!/usr/bin/env python3
"""Weekly refresh hook for the imagery collections.

``refresh(catalog, now, dry_run)`` is what the scheduled job calls. It
returns one entry per imagery collection::

    {"imagenes/ortofotos_10cm_2022": {"status": "ok", "detail": "..."},
     "imagenes/sentinel2_trimestral": {"status": "due", "detail": "..."}}

Statuses:

- ``ok``: up to date, or brought up to date by this run.
- ``due``: there is work to do and ``dry_run`` held it back, or upstream
  removed a tile, which needs a person to decide.
- ``skipped``: the collection is not in this catalog.
- ``error``: the check or the rebuild raised; ``detail`` says what.

Orthophotos: each GeoNode raster dataset that ``ortofotos.is_ortho`` keeps
is matched to its Item by ``pergamino:geonode_pk``. A tile is rebuilt when
GeoNode's ``last_updated`` differs from the Item's
``pergamino:source_updated``, and built when no Item has its pk. Only those
tiles are downloaded and re-encoded; the overview, the thumbnail and
``items.parquet`` are then rebuilt from every Item, reading tiles that are
not on disk from the published bucket.

Sentinel-2: the newest quarter that ended at least 14 days ago is built if
no Item holds it and it is not listed in ``pergamino:excluded_quarters``.

    python tools/imagery/refresh.py --dry-run
    python tools/imagery/refresh.py --now 2026-11-20T00:00:00Z
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# tools/, for the package imports below. A bare ``import common`` would share
# one sys.modules entry with tools/virtual/common.py; see tools/refresh.py hook.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from imagery import common, ortofotos, s2_quarterly  # noqa: E402

ORTHO_ID = ortofotos.COLLECTION_ID
S2_ID = s2_quarterly.COLLECTION_ID


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ortho_plan(records: list[dict[str, Any]],
               items: list[dict[str, Any]]) -> dict[str, list]:
    """What to rebuild, given GeoNode records and the Items on disk.

    Returns ``changed`` and ``new`` (GeoNode records) and ``removed`` (Item
    ids whose pk no longer appears among the orthophoto records).
    """
    by_pk = {
        int(item["properties"]["pergamino:geonode_pk"]): item
        for item in items
        if "pergamino:geonode_pk" in item.get("properties", {})
    }
    changed, new, seen = [], [], set()
    for record in records:
        if not ortofotos.is_ortho(record):
            continue
        pk = int(record["pk"])
        seen.add(pk)
        item = by_pk.get(pk)
        if item is None:
            new.append(record)
            continue
        stored = _parse_time(item["properties"].get("pergamino:source_updated"))
        upstream = _parse_time(record.get("last_updated"))
        if stored != upstream:
            changed.append(record)
    removed = sorted(item["id"] for pk, item in by_pk.items() if pk not in seen)
    return {"changed": changed, "new": new, "removed": removed}


def s2_plan(now: datetime, present: set[str],
            excluded: set[str] | None = None,
            lag_days: int = s2_quarterly.LAG_DAYS):
    """The quarter to build, or None when the newest one is in hand."""
    quarter = s2_quarterly.latest_quarter(now, lag_days)
    if quarter.item_id in present or quarter.label in (excluded or set()):
        return None
    return quarter


def _names(records: list[dict[str, Any]]) -> str:
    return ", ".join(sorted(ortofotos.item_id(r) for r in records))


def refresh_orthos(catalog: Path, dry_run: bool) -> dict[str, str]:
    coll = catalog / "imagenes" / "ortofotos_10cm_2022"
    if not (coll / "collection.json").exists():
        return {"status": "skipped", "detail": f"{coll} has no collection.json"}
    ortofotos.COLLECTION_DIR = coll
    items = common.load_items(coll)
    plan = ortho_plan(ortofotos.fetch_raster_records(), items)
    todo = plan["changed"] + plan["new"]
    notes = []
    if plan["changed"]:
        notes.append(f"changed upstream: {_names(plan['changed'])}")
    if plan["new"]:
        notes.append(f"new upstream: {_names(plan['new'])}")
    if plan["removed"]:
        notes.append(
            "gone from GeoNode, remove by hand if intended: "
            + ", ".join(plan["removed"])
        )
    if not todo:
        status = "due" if plan["removed"] else "ok"
        detail = "; ".join(notes) or f"{len(items)} tiles match GeoNode"
        return {"status": status, "detail": detail}
    if dry_run:
        return {"status": "due", "detail": "; ".join(notes)}
    for record in todo:
        ortofotos.build_tile(record, force=True)
    ortofotos.update_collection(overview=True)
    status = "due" if plan["removed"] else "ok"
    return {"status": status,
            "detail": f"rebuilt {_names(todo)}; " + "; ".join(notes)}


def refresh_s2(catalog: Path, now: datetime, dry_run: bool) -> dict[str, str]:
    coll = catalog / "imagenes" / "sentinel2_trimestral"
    path = coll / "collection.json"
    if not path.exists():
        return {"status": "skipped", "detail": f"{coll} has no collection.json"}
    s2_quarterly.COLLECTION_DIR = coll
    present = {item["id"] for item in common.load_items(coll)}
    excluded = set(json.loads(path.read_text())
                   .get("pergamino:excluded_quarters", []))
    quarter = s2_plan(now, present, excluded)
    if quarter is None:
        latest = s2_quarterly.latest_quarter(now)
        return {"status": "ok",
                "detail": f"{latest.label} is the newest due quarter and is "
                          "present"}
    if dry_run:
        return {"status": "due",
                "detail": f"{quarter.label} ended {quarter.end.isoformat()} "
                          "and is not built"}
    result = s2_quarterly.build_quarter(quarter)
    if result == "empty":
        s2_quarterly.exclude_quarter(quarter, coll)
    s2_quarterly.update_collection(coll)
    return {"status": "ok", "detail": f"{quarter.label}: {result}"}


def refresh(catalog: Path, now: datetime, dry_run: bool) -> dict[str, dict]:
    """Check both imagery collections and rebuild what changed upstream."""
    results: dict[str, dict] = {}
    for cid, fn in ((ORTHO_ID, lambda: refresh_orthos(catalog, dry_run)),
                    (S2_ID, lambda: refresh_s2(catalog, now, dry_run))):
        try:
            results[cid] = fn()
        except Exception as exc:  # noqa: BLE001 - reported, not raised
            results[cid] = {"status": "error",
                            "detail": f"{type(exc).__name__}: {exc}"}
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="report what is due without building it")
    parser.add_argument("--catalog", type=Path, default=common.CATALOG)
    parser.add_argument("--now", help="RFC 3339 time to plan against")
    args = parser.parse_args(argv)
    now = (_parse_time(args.now) if args.now
           else datetime.now(timezone.utc))
    results = refresh(args.catalog.resolve(), now, args.dry_run)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 1 if any(r["status"] == "error" for r in results.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
