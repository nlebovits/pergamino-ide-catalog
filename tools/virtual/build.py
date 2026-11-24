#!/usr/bin/env python3
"""Regenerate every virtual collection from sources.json.

    python3 tools/virtual/build.py                  # everything
    python3 tools/virtual/build.py --only glofas    # one upstream
    python3 tools/virtual/thumbs.py                 # then the previews

Needs the network (upstream STAC, Parquet footers, COG headers), GDAL on PATH,
and duckdb, pyarrow and shapely. Each collection lives in its thematic group,
at the ``collection`` id its layer gives in sources.json. Writes:

- per collection: collection.json, README.md, AGENTS.md, styles/default.json;
- GloFAS: one clip VRT per collection (committed: deterministic text);
- Overture: items, and one ``<collection>.ddb`` per collection (gitignored:
  a binary, regenerated here and published by tools/publish.py).

Then it reruns tools/generate/build_catalogs.py and build_docs.py, so each
group catalog links its virtual collections and each group README and
AGENTS.md lists them.

A rerun that finds nothing new leaves every file byte-identical, `updated`
included. ``--partido-url`` overrides the boundary URL the DuckDB views read;
use it only to test before the URL in sources.json is live, and never publish
a .ddb built with it.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# tools/, for the package imports below. A bare ``import common`` would share
# one sys.modules entry with tools/imagery/common.py; see tools/refresh.py hook.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from virtual import common as C  # noqa: E402
from virtual import docs, glofas, overture  # noqa: E402

GENERATE = Path(__file__).resolve().parent.parent / "generate"


def relink_groups(catalog: Path) -> None:
    """Rebuild the group catalogs and their docs, which list the collections."""
    for script in ("build_catalogs.py", "build_docs.py"):
        subprocess.run([sys.executable, str(GENERATE / script), str(catalog)],
                       check=True)


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

    if args.only in (None, "glofas"):
        glofas.build(partido, docs, now)
    if args.only in (None, "overture"):
        overture.build(partido, docs, now, args.partido_url)
    relink_groups(C.CATALOG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
