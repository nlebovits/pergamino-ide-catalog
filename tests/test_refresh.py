#!/usr/bin/env python3
"""The refresh pipeline's offline contract.

Five parts of the refresh decide what a reader later sees, and each one is
checked here without network access:

- ``refresh.decide``: a collection is due only when GeoNode's
  ``last_updated`` or the row count moved, and only after ``min_days``.
- ``check_styles.check``: a missing column, a category that held rows and
  now holds none, or a new unstyled value each fail. A category that was
  already empty does not.
- ``build_collection.build``: with no local data file, as in CI, a metadata
  rebuild keeps the recorded facts, the current version's checksum, and the
  tiles asset. A new version without the data file is refused.
- ``build_collection.extent_bbox``: the extent covers every archived version
  as well as the current one.
- ``publish.collect_uploads``: archives upload first, then data, then
  metadata.
- ``extract.make_pmtiles``: tippecanoe gets ``--drop-rate=g``, so a small
  point layer keeps every point at every zoom.

Needs pyarrow, duckdb and geoparquet-io.

Run: python3 tests/test_refresh.py
"""
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


missing = [m for m in ("duckdb", "pyarrow") if find_spec(m) is None]
if missing:
    print(f"error  {', '.join(missing)} not installed; this gate checks nothing")
    print("       pip install -r tools/requirements.txt")
    raise SystemExit(1)

import pyarrow as pa  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402

import build_collection  # noqa: E402
import check_styles  # noqa: E402
import publish  # noqa: E402
from geonode import SourceState  # noqa: E402
from refresh import decide  # noqa: E402

# --- decide ---------------------------------------------------------------
NOW = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
WEEKLY = {"min_days": 7}
CURRENT = {"version": "2026-11-09", "created": "2026-11-09T07:00:00Z",
           "pergamino:source_updated": "2026-11-01T10:00:00Z",
           "table:row_count": 100}

due, why = decide("g/c", WEEKLY, SourceState("2026-11-20T10:00:00Z", 100),
                  None, {}, NOW)
check(due, f"a collection with no version is due ({why})")

due, why = decide("g/c", WEEKLY, SourceState("2026-11-01T10:00:00Z", 100),
                  CURRENT, {}, NOW)
check(not due, f"unchanged source and count is not due ({why})")

due, why = decide("g/c", WEEKLY, SourceState("2026-11-20T10:00:00Z", 100),
                  CURRENT, {}, NOW)
check(due, f"a newer last_updated after min_days is due ({why})")

due, why = decide("g/c", WEEKLY, SourceState("2026-11-01T10:00:00Z", 101),
                  CURRENT, {}, NOW)
check(due, f"a changed row count is due ({why})")

recent = dict(CURRENT, created="2026-11-20T07:00:00Z")
due, why = decide("g/c", WEEKLY, SourceState("2026-11-21T10:00:00Z", 100),
                  recent, {}, NOW)
check(not due and "next due" in why,
      f"a change inside min_days waits ({why})")

state = {"g/c": {"source_updated": "2026-11-20T10:00:00Z", "count": 100}}
due, why = decide("g/c", WEEKLY, SourceState("2026-11-20T10:00:00Z", 100),
                  CURRENT, state, NOW)
check(not due, f"a check that found equal rows is remembered ({why})")

# --- check_styles ---------------------------------------------------------
STYLE = {"version": 8, "sources": {}, "layers": [{
    "id": "a", "type": "circle", "source": "data", "source-layer": "c",
    "paint": {
        "circle-color": ["match", ["get", "tipo"],
                         "A", "#f00", "B", "#0f0", "Z", "#00f", "#ccc"],
        "circle-radius": ["step", ["get", "n"], 2, 10, 4, 100, 6]}}]}

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    catalog = tmp / "catalog"
    (catalog / "g" / "c" / "styles").mkdir(parents=True)
    (catalog / "g" / "c" / "styles" / "default.json").write_text(
        json.dumps(STYLE))

    def table(name: str, tipo: list, n: list) -> str:
        path = tmp / f"{name}.parquet"
        pq.write_table(pa.table({"tipo": tipo, "n": n}), path)
        return str(path)

    # "Z" matched no row before and none after: the SLD named it anyway.
    before = table("before", ["A", "B", "A"], [1, 50, 500])
    same = table("same", ["B", "A", "A"], [2, 60, 600])
    found = check_styles.check("g/c", same, before, catalog)
    check(found == [], f"rows that keep every class pass: {found}")

    lost = table("lost", ["A", "A"], [1, 500])
    found = check_styles.check("g/c", lost, before, catalog)
    check(any("'B' matches no row" in p for p in found),
          f"a category that lost its rows fails: {found}")
    check(any("[10.0, 100.0)" in p for p in found),
          f"a step class that lost its rows fails: {found}")
    check(not any("'Z'" in p for p in found),
          f"a category that was already empty does not fail: {found}")

    new = table("new", ["A", "B", "C"], [1, 50, 500])
    found = check_styles.check("g/c", new, before, catalog)
    check(any("new value 'C'" in p for p in found),
          f"a new value with no category fails: {found}")

    path = tmp / "gone.parquet"
    pq.write_table(pa.table({"n": [1, 50, 500]}), path)
    found = check_styles.check("g/c", str(path), None, catalog)
    check(any("tipo: the column is gone" in p for p in found),
          f"a styled column that is gone fails, even without history: {found}")

# --- build_collection without local data ---------------------------------
SOURCES = json.loads((ROOT / "tools" / "sources.json").read_text())
RECORDS = json.loads(
    (ROOT / "tools" / "generate" / "data" / "geonode.json").read_text())
ID = "limites/cpa"
entry = SOURCES["collections"][ID]
record = RECORDS[entry["alternate"]]

with tempfile.TemporaryDirectory() as tmp:
    catalog = Path(tmp) / "catalog"
    folder = catalog / ID
    folder.mkdir(parents=True)
    for name in ("collection.json", "README.md"):
        shutil.copyfile(ROOT / "catalog" / ID / name, folder / name)
    shutil.copytree(ROOT / "catalog" / ID / "styles", folder / "styles")
    old = json.loads((folder / "collection.json").read_text())
    doc = build_collection.build(catalog, ID, entry, record,
                                 updated=old["updated"])
    leaf = ID.split("/")[-1]
    check(doc["table:row_count"] == old["table:row_count"],
          "a rebuild without data keeps the row count")
    check(doc["table:columns"] == old["table:columns"],
          "a rebuild without data keeps the columns")
    check(doc["assets"][leaf].get("file:checksum")
          == old["assets"][leaf].get("file:checksum"),
          "a rebuild without data keeps the current checksum")
    check(f"{leaf}-tiles" in doc["assets"],
          "a rebuild without data keeps the tiles asset")
    check(any(link["rel"] == "pmtiles" for link in doc["links"]),
          "a rebuild without data keeps the pmtiles link")
    check(doc["extent"] == old["extent"],
          "a rebuild without data keeps the extent")
    try:
        build_collection.build(catalog, ID, entry, record, updated="x",
                               new_version={"version": "2099-01-01"})
        errors.append("a new version without its data file was accepted")
    except FileNotFoundError:
        pass

# --- extent_bbox ----------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    folder = Path(tmp)
    old = {"extent": {"spatial": {"bbox": [[-61.0, -34.5, -60.0, -33.5]]}}}
    assets = {"version-2026-08-14": {"href": "./versions/x.parquet"}}
    facts = {"bbox": [-60.8, -34.1, -60.2, -33.6]}
    box = build_collection.extent_bbox(folder, facts, old, assets)
    check(box == [-61.0, -34.5, -60.0, -33.5],
          f"the extent covers an archived version not on disk: {box}")
    box = build_collection.extent_bbox(folder, facts, old, {})
    check(box == facts["bbox"],
          f"with no archive, the extent is the current bbox: {box}")

# --- publish order --------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    folder = root / "catalog" / "g" / "c"
    (folder / "versions").mkdir(parents=True)
    for name in ("collection.json", "README.md", "c.parquet", "c.pmtiles",
                 "versions/2026-11-09.parquet", "c.thumb.jpg"):
        (folder / name).write_text("x")
    (root / "catalog" / "catalog.json").write_text("{}")
    config = {"write_prefix": "s3://b/p", "public_base": "https://x/p",
              "publish_dir": "catalog"}
    keys = [u.key for u in publish.collect_uploads(config, root)]
    ranks = [publish.upload_rank(Path(k)) for k in keys]
    check(ranks == sorted(ranks), f"uploads are not in rank order: {keys}")
    check(keys[0] == "p/g/c/versions/2026-11-09.parquet",
          f"the archive uploads first: {keys}")
    check(keys[-1].endswith(".md") or keys[-1].endswith(".json"),
          f"metadata uploads last: {keys}")

# --- PMTiles drop rate ----------------------------------------------------
import extract  # noqa: E402
from geoparquet_io.core import pmtiles as gpio_pmtiles  # noqa: E402

build = getattr(gpio_pmtiles, "_build_tippecanoe_command", None)
check(build is not None,
      "gpio no longer has _build_tippecanoe_command; make_pmtiles must "
      "find another way to pass --drop-rate")
if build is not None:
    cmd = extract.tippecanoe_command(build)("out.pmtiles", "x", 0, 15,
                                            False)
    check(cmd[0] == "tippecanoe" and cmd.count(extract.DROP_RATE) == 1,
          f"the drop rate reaches tippecanoe once: {cmd}")

# --- tile columns ---------------------------------------------------------
# make_pmtiles hands the kept columns to gpio as include_cols. Every column a
# collection's style reads must be kept, and every kept column must exist.
import tiles  # noqa: E402
from geoparquet_io.api import ops as gpio_ops  # noqa: E402

seen = {}


def fake_create(src, out, **kwargs):
    seen.update(kwargs)


real_create, real_point = gpio_ops.create_pmtiles, extract.is_point_layer
gpio_ops.create_pmtiles = fake_create
extract.is_point_layer = lambda _: False
try:
    extract.make_pmtiles(Path("x.parquet"), Path("x.pmtiles"), "x",
                         ["a", "b"])
    check(seen.get("include_cols") == "a,b",
          f"kept columns reach gpio as include_cols: {seen}")
    seen.clear()
    extract.make_pmtiles(Path("x.parquet"), Path("x.pmtiles"), "x")
    check(seen.get("include_cols") is None,
          f"no column list keeps every column: {seen}")
finally:
    gpio_ops.create_pmtiles = real_create
    extract.is_point_layer = real_point


def style_fields(node) -> set[str]:
    """Every property a MapLibre style expression reads with get or has."""
    found = set()
    if isinstance(node, list):
        if len(node) == 2 and node[0] in ("get", "has") \
                and isinstance(node[1], str):
            found.add(node[1])
        for child in node:
            found |= style_fields(child)
    elif isinstance(node, dict):
        for child in node.values():
            found |= style_fields(child)
    return found


for collection, kept in tiles.TILE_COLUMNS.items():
    folder = ROOT / "catalog" / collection
    doc = json.loads((folder / "collection.json").read_text())
    names = {c["name"] for c in doc.get("table:columns", [])}
    check(set(kept) <= names,
          f"{collection}: kept tile columns missing from the data: "
          f"{sorted(set(kept) - names)}")
    for style in sorted((folder / "styles").glob("*.json")):
        used = style_fields(json.loads(style.read_text()).get("layers", []))
        check(used <= set(kept),
              f"{style.relative_to(ROOT)} reads columns the tiles drop: "
              f"{sorted(used - set(kept))}")

# --- featured collections -------------------------------------------------
# The browser's featured row reads the keyword, so the catalog must carry it
# on the featured collections and on no other.
import featured  # noqa: E402

check(featured.with_featured(featured.FEATURED[0], ["a"])
      == ["a", featured.FEATURED_KEYWORD]
      and featured.with_featured("x/y", ["a", featured.FEATURED_KEYWORD])
      == ["a"], "with_featured adds the keyword only to featured ids")
marked = set()
for path in sorted((ROOT / "catalog").glob("*/*/collection.json")):
    doc = json.loads(path.read_text())
    if featured.FEATURED_KEYWORD in doc.get("keywords", []):
        marked.add(doc["id"])
check(marked == set(featured.FEATURED),
      f"featured keyword on {sorted(marked)}, expected "
      f"{sorted(featured.FEATURED)}")

if errors:
    print("\n".join(f"error  {e}" for e in errors))
    raise SystemExit(1)
print("OK: refresh decisions, style checks, rebuilds, upload order, "
      "tile drop rate, tile columns and featured keywords hold")
