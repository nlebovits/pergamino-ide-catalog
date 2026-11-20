#!/usr/bin/env python3
"""Keep a copy of the GeoNode records the catalog's metadata comes from.

``tools/generate/data/geonode.json`` holds, for each mirrored dataset, the
fields of its GeoNode record that the collection's ``collection.json``,
README and AGENTS.md are written from. Committing the copy has two effects:

- The docs regenerate offline, so ``tests/test_regen.py`` can check them in
  CI without a network.
- A metadata change upstream shows up as a diff in git, next to the
  collection it changed.

The refresh rewrites the copy for every collection it rebuilds.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geonode  # noqa: E402

PATH = HERE / "generate" / "data" / "geonode.json"
FIELDS = (
    "pk", "uuid", "alternate", "title", "raw_abstract", "raw_purpose",
    "raw_supplemental_information", "raw_data_quality_statement",
    "raw_constraints_other", "attribution", "keywords", "category",
    "date", "date_type", "maintenance_frequency", "last_updated", "srid",
    "subtype",
)


def trim(record: dict) -> dict:
    out = {k: record.get(k) for k in FIELDS}
    out["keywords"] = [{"name": k.get("name")} for k in out["keywords"] or []]
    category = out.get("category") or {}
    out["category"] = {"identifier": category.get("identifier"),
                       "gn_description": category.get("gn_description")}
    return out


def load() -> dict:
    """The stored records, by alternate."""
    return json.loads(PATH.read_text()) if PATH.exists() else {}


def save(records: dict) -> None:
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(dict(sorted(records.items())), indent=2,
                               ensure_ascii=False) + "\n")


def refresh(collections: list[str]) -> dict:
    """Fetch the records of ``collections`` from GeoNode and store them.

    Returns every stored record, by alternate. Records of collections not
    named are left as they were.
    """
    sources = geonode.load_sources()["collections"]
    wanted = {sources[c]["alternate"]: sources[c]["pk"] for c in collections}
    records = load()
    if len(wanted) > 20:
        fresh = {r["alternate"]: r for r in geonode.datasets()
                 if r["alternate"] in wanted}
    else:
        fresh = {alt: geonode.dataset(pk) for alt, pk in wanted.items()}
    missing = set(wanted) - set(fresh)
    if missing:
        raise RuntimeError(f"GeoNode has no record for {sorted(missing)}")
    for alternate, record in fresh.items():
        records[alternate] = trim(record)
    save(records)
    return records
