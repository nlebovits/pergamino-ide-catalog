#!/usr/bin/env python3
"""Regenerate every collection under catalog/externos/ from sources.json.

    python3 tools/virtual/build.py                  # everything
    python3 tools/virtual/build.py --only glofas    # one upstream
    python3 tools/virtual/thumbs.py                 # then the previews

Needs the network (upstream STAC, Parquet footers, COG headers), GDAL on PATH,
and duckdb, pyarrow and shapely. Writes:

- externos/catalog.json and the glofas/ and overture/ sub-catalogs;
- per collection: collection.json, README.md, AGENTS.md, styles/default.json;
- GloFAS: one clip VRT per collection (committed: deterministic text);
- Overture: items, and externos/overture/pergamino_overture.ddb (gitignored:
  a binary, regenerated here and published by tools/publish.py).

A rerun that finds nothing new leaves every file byte-identical, `updated`
included. ``--partido-url`` overrides the boundary URL the DuckDB views read;
use it only to test before the URL in sources.json is live, and never publish
a .ddb built with it.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common as C  # noqa: E402
import docs  # noqa: E402
import glofas  # noqa: E402
import overture  # noqa: E402

GROUP_LINK = {
    "rel": "child",
    "href": f"./{C.GROUP}/catalog.json",
    "type": "application/json",
    "title": docs.GROUP_TITLE,
}


def link_group_in_root(root: Path) -> bool:
    """Add the externos child link to the root catalog if it is missing."""
    path = root / "catalog.json"
    cat = json.loads(path.read_text())
    if any(ln.get("href") == GROUP_LINK["href"] for ln in cat["links"]):
        return False
    last_child = max(i for i, ln in enumerate(cat["links"])
                     if ln.get("rel") == "child")
    cat["links"].insert(last_child + 1, dict(GROUP_LINK))
    return C.write_json(path, cat)


def write_group(root: Path, now: datetime) -> None:
    folder = root / C.GROUP
    path = folder / "catalog.json"
    C.write_json(path, C.keep_updated(path, docs.group_catalog(), now))
    docs.write_group(folder)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--only", choices=["glofas", "overture"])
    parser.add_argument("--partido-url", default=None,
                        help="boundary URL for the DuckDB views (testing)")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    partido = C.load_partido(args.partido_url)
    print(f"partido from {partido.source}")
    if args.partido_url and args.partido_url != C.PARTIDO_URL:
        print(f"WARNING: views read {args.partido_url}, not the published "
              f"constant {C.PARTIDO_URL}. Do not publish this .ddb.")

    write_group(C.CATALOG, now)
    if args.only in (None, "glofas"):
        glofas.build(partido, docs, now)
    if args.only in (None, "overture"):
        overture.build(partido, docs, now, args.partido_url)
    if link_group_in_root(C.CATALOG):
        print("linked externos/ from the root catalog")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
