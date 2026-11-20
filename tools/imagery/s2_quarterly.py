#!/usr/bin/env python3
"""The clearest Sentinel-2 L2A date of each quarter, as references.

One STAC Item per calendar quarter in ``catalog/imagenes/sentinel2_trimestral``.
No pixel is computed or copied. For each quarter:

1. Search Element 84 Earth Search for Sentinel-2 L2A scenes that touch the
   partido bbox, and group them by solar day.
2. Keep the days whose scene footprints cover the whole partido, and of
   those the day whose cloudiest scene has the lowest ``eo:cloud_cover``.
   ``sentinel-2-c1-l2a`` (Collection 1) is used when it has such a day;
   otherwise the older ``sentinel-2-l2a``. Over this bbox C1 has no scene
   in 2017 and gaps in 2022. If neither covers the partido, the day that
   covers most of it wins. The Item records the collection in
   ``pergamino:source_collection``.
3. Write an Item whose ``visual-<tile>-<HHMM>`` assets point at that day's
   upstream ``TCI.tif`` COGs, whose ``derived_from`` links point at the
   Earth Search items (every band and the SCL), and whose
   ``processing:expression`` is the gdalwarp call that mosaics the day and
   clips it to the partido. The thumbnail is rendered from the COGs'
   internal overviews.

The collection also publishes ``escenas.parquet``: every scene over the
partido from FIRST_QUARTER on, in stac-geoparquet, so a reader can build a
median or a time series on their side.

Idempotent: a quarter whose Item JSON and thumbnail exist is skipped unless
``--force``. The collection JSON, ``items.parquet`` and ``escenas.parquet``
are rebuilt after every run.

    python tools/imagery/s2_quarterly.py --quarter 2024Q3
    python tools/imagery/s2_quarterly.py --latest
    python tools/imagery/s2_quarterly.py --all
    python tools/imagery/s2_quarterly.py --collection-only
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402

EARTH_SEARCH = "https://earth-search.aws.element84.com/v1"
C1 = "sentinel-2-c1-l2a"
L2A = "sentinel-2-l2a"
BBOX = (-60.944, -34.177, -60.139, -33.540)
CRS = "EPSG:32720"
RESOLUTION = 10
FIRST_QUARTER = "2017Q1"
LAG_DAYS = 14  # a quarter is added once it ended this many days ago
# A day "covers" the partido when its footprints hold this share of it. The
# footprints are simplified polygons, so an exact 1.0 would reject days
# that cover it in fact.
FULL_COVER = 0.999
THUMB_SIDE = 512
# Degrees. The display tolerance of tools/virtual/common.py.
FOOTPRINT_TOLERANCE = 0.0005
# Thumbnails rendered at once. Each waits on S3, not on the CPU.
WORKERS = int(os.environ.get("S2_WORKERS", "4"))

COLLECTION_ID = "imagenes/sentinel2_trimestral"
COLLECTION_DIR = common.CATALOG / "imagenes" / "sentinel2_trimestral"
WORK = common.SOURCES / "sentinel2"
TIMINGS = WORK / "timings.log"
PARTIDO = common.ROOT / "catalog" / "limites" / "partido_pergamino" \
    / "partido_pergamino.parquet"
PARTIDO_URL = json.loads(
    (common.ROOT / "tools" / "virtual" / "sources.json").read_text()
)["partido"]["url"]

EXT_PROCESSING = \
    "https://stac-extensions.github.io/processing/v1.2.0/schema.json"
LEGAL_NOTICE = (
    "https://sentinels.copernicus.eu/documents/247904/690755/"
    "Sentinel_Data_Legal_Notice"
)
GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "GDAL_HTTP_MULTIPLEX": "YES",
    "GDAL_HTTP_VERSION": "2",
    "GDAL_HTTP_MAX_RETRY": "5",
    "GDAL_HTTP_RETRY_DELAY": "2",
    "VSI_CACHE": "TRUE",
}


# --- quarters ----------------------------------------------------------

@dataclass(frozen=True)
class Quarter:
    year: int
    q: int

    @classmethod
    def parse(cls, text: str) -> "Quarter":
        m = re.fullmatch(r"(\d{4})[Qq]([1-4])", text.strip())
        if not m:
            raise ValueError(f"not a quarter: {text!r} (want e.g. 2024Q3)")
        return cls(int(m.group(1)), int(m.group(2)))

    @property
    def label(self) -> str:
        return f"{self.year}Q{self.q}"

    @property
    def item_id(self) -> str:
        return f"{self.year}q{self.q}"

    @property
    def start(self) -> date:
        return date(self.year, 3 * self.q - 2, 1)

    @property
    def end(self) -> date:
        """The last day of the quarter."""
        return self.next().start - timedelta(days=1)

    def next(self) -> "Quarter":
        return Quarter(self.year + (self.q == 4), self.q % 4 + 1)

    def start_iso(self) -> str:
        return f"{self.start.isoformat()}T00:00:00Z"

    def end_iso(self) -> str:
        return f"{self.end.isoformat()}T23:59:59Z"


def latest_quarter(now: datetime, lag_days: int = LAG_DAYS) -> Quarter:
    """The newest quarter that ended at least ``lag_days`` before ``now``.

    The lag leaves time for late scenes to reach Earth Search.
    """
    today = now.astimezone(timezone.utc).date()
    q = Quarter(today.year, (today.month - 1) // 3 + 1)
    while not (q.end + timedelta(days=lag_days) < today):
        q = Quarter(q.year - (q.q == 1), (q.q - 2) % 4 + 1)
    return q


def quarters_between(first: Quarter, last: Quarter) -> list[Quarter]:
    out = []
    q = first
    while (q.year, q.q) <= (last.year, last.q):
        out.append(q)
        q = q.next()
    return out


# --- search ------------------------------------------------------------

_SEARCHES: dict[tuple[Quarter, str], list] = {}


def search(quarter: Quarter, collection: str) -> list:
    """The deduplicated pystac Items of one collection in a quarter.

    Cached per run: the Item build and the scene index read the same
    results.
    """
    key = (quarter, collection)
    if key not in _SEARCHES:
        from pystac_client import Client

        found = Client.open(EARTH_SEARCH).search(
            collections=[collection], bbox=BBOX,
            datetime=f"{quarter.start_iso()}/{quarter.end_iso()}", limit=200,
        )
        _SEARCHES[key] = dedupe(list(found.items()))
    return _SEARCHES[key]


def choose(quarter: Quarter, area):
    """(source collection, its Items, the clearest Day) for a quarter.

    C1 when it has a day that covers the partido, else ``sentinel-2-l2a``.
    C1 has no scene here in 2017 and gaps in 2022. With no full-coverage
    day in either, the widest day wins.
    """
    best: tuple[str | None, list, Day | None] = (None, [], None)
    for collection in (C1, L2A):
        items = search(quarter, collection)
        day = clearest(days_of(items, area))
        if day is None:
            continue
        if day.full:
            return collection, items, day
        if best[2] is None or day.coverage > best[2].coverage:
            best = (collection, items, day)
    return best


def dedupe(items):
    """One item per tile and acquisition time, the most recently created.

    ``sentinel-2-l2a`` holds reprocessed duplicates of some scenes (ids
    ending ``_0_L2A`` and ``_1_L2A``).
    """
    keep: dict[tuple, Any] = {}
    for item in items:
        props = item.properties
        key = (tile_of(item), item.datetime.replace(microsecond=0))
        stamp = props.get("created") or props.get("s2:generation_time") or ""
        if key not in keep or stamp > (
            keep[key].properties.get("created")
            or keep[key].properties.get("s2:generation_time") or ""
        ):
            keep[key] = item
    return sorted(keep.values(), key=lambda i: (i.datetime, i.id))


def tile_of(item) -> str:
    props = item.properties
    code = props.get("grid:code") or props.get("s2:mgrs_tile") or ""
    return code.removeprefix("MGRS-")


# --- the clearest day --------------------------------------------------

def partido():
    """The partido polygon, from the catalog's own GeoParquet."""
    import pyarrow.parquet as pq
    import shapely

    table = pq.read_table(PARTIDO, columns=["geometry"])
    return shapely.from_wkb(table.column("geometry")[0].as_py())


@dataclass
class Day:
    day: date
    scenes: list
    coverage: float  # share of the partido the day's footprints hold
    cloud: float  # eo:cloud_cover of the cloudiest scene, percent

    @property
    def full(self) -> bool:
        return self.coverage >= FULL_COVER


def days_of(items, area) -> list[Day]:
    """Every solar day of the quarter, with its coverage and cloud cover.

    Only scenes with a visual asset count: the Item references it.
    """
    import shapely
    from shapely.geometry import shape

    by_day: dict[date, list] = defaultdict(list)
    for item in items:
        if "visual" in item.assets:
            by_day[item.datetime.date()].append(item)
    out = []
    for day, scenes in sorted(by_day.items()):
        union = shapely.union_all([shape(s.geometry) for s in scenes])
        coverage = area.intersection(union).area / area.area
        cloud = max(s.properties.get("eo:cloud_cover", 100.0) for s in scenes)
        out.append(Day(day, scenes, coverage, cloud))
    return out


def clearest(days: list[Day]) -> Day | None:
    """The full-coverage day with the lowest cloud, else the widest day."""
    if not days:
        return None
    full = [d for d in days if d.full]
    if full:
        return min(full, key=lambda d: (d.cloud, d.day))
    return max(days, key=lambda d: (d.coverage, -d.cloud))


# --- the Item ----------------------------------------------------------

def tci_hrefs(day: Day) -> list[str]:
    return [s.assets["visual"].href for s in sorted(day.scenes, key=tile_of)]


def recipe(day: Day, out_name: str) -> str:
    """The published gdalwarp call: mosaic the day, clip to the partido."""
    sources = " ".join(f"/vsicurl/{h}" for h in tci_hrefs(day))
    return (f"gdalwarp -t_srs {CRS} -tr {RESOLUTION} {RESOLUTION} -tap "
            f"-cutline /vsicurl/{PARTIDO_URL} -crop_to_cutline -dstalpha "
            f"-co COMPRESS=DEFLATE -co TILED=YES {sources} {out_name}")


def render_thumbnail(day: Day, cutline: Path, out: Path) -> None:
    """A JPEG of the day over the partido, read from the COG overviews.

    gdalwarp picks the overview level that matches the small output size,
    so it reads a few hundred KB per scene, not the 10 m pixels.
    """
    with tempfile.TemporaryDirectory(dir=_work()) as tmp:
        small = Path(tmp) / "small.tif"
        cmd = ["gdalwarp", "-q", "-overwrite", "-t_srs", CRS,
               "-ts", str(THUMB_SIDE), "0", "-r", "average",
               "-cutline", str(cutline), "-crop_to_cutline", "-dstalpha",
               *(f"/vsicurl/{h}" for h in tci_hrefs(day)), str(small)]
        subprocess.run(cmd, check=True, env={**os.environ, **GDAL_ENV})
        common.jpeg_thumbnail(small, out, max_side=THUMB_SIDE)


def build_item(quarter: Quarter, source: str, day: Day, area,
               thumb: Path) -> dict[str, Any]:
    import shapely
    from shapely.geometry import shape

    scenes = sorted(day.scenes, key=tile_of)
    union = shapely.union_all([shape(s.geometry) for s in scenes])
    # The footprint is for search and display. At the full boundary detail
    # it makes each Item JSON about 160 KB.
    geom = shapely.set_precision(
        area.intersection(union).simplify(FOOTPRINT_TOLERANCE,
                                          preserve_topology=True), 1e-6)
    when = min(s.datetime for s in scenes)
    year = when.year
    tiles = ", ".join(tile_of(s) for s in scenes)
    out_name = f"sentinel2_{quarter.item_id}.tif"
    props = {
        "title": f"Sentinel-2, {when.date().isoformat()} "
                 f"({quarter.year} T{quarter.q})",
        "description": (
            f"La fecha más despejada del trimestre {quarter.year} "
            f"T{quarter.q} que cubre el Partido de Pergamino: "
            f"{when.date().isoformat()}, teselas MGRS {tiles}. Los recursos "
            "apuntan a los COG de color verdadero de Earth Search; los "
            "vínculos derived_from llevan a cada escena, con todas sus "
            "bandas."
        ),
        "datetime": when.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "constellation": "sentinel-2",
        "instruments": ["msi"],
        "gsd": RESOLUTION,
        "eo:cloud_cover": round(day.cloud, 4),
        "processing:lineage": (
            f"Escenas Sentinel-2 L2A de {source} en Earth Search, sin "
            "modificar. Se eligió el día solar cuyas huellas cubren el "
            "partido y cuya escena más nubosa tiene el menor eo:cloud_cover "
            "del trimestre."
        ),
        "pergamino:source_collection": source,
        "pergamino:scene_ids": [s.id for s in scenes],
        "pergamino:partido_coverage": round(day.coverage, 4),
        "pergamino:attribution": f"Copernicus Sentinel data {year}",
    }
    links = [
        {"rel": "root", "href": "../../../catalog.json",
         "type": "application/json"},
        {"rel": "parent", "href": "../collection.json",
         "type": "application/json"},
        {"rel": "collection", "href": "../collection.json",
         "type": "application/json"},
        {"rel": "license", "href": LEGAL_NOTICE, "type": "application/pdf",
         "title": "Legal notice on the use of Copernicus Sentinel Data and "
                  "Service Information"},
    ]
    assets: dict[str, Any] = {}
    for scene in scenes:
        tile = tile_of(scene)
        # Tile and UTC time of acquisition: on a day with two passes the
        # same tile appears twice, and each scene keeps its own asset.
        key = f"visual-{tile}-{scene.datetime:%H%M}"
        links.append({
            "rel": "derived_from",
            "href": scene.get_self_href()
            or f"{EARTH_SEARCH}/collections/{source}/items/{scene.id}",
            "type": common.GEOJSON,
            "title": scene.id,
        })
        assets[key] = {
            "href": scene.assets["visual"].href,
            "type": common.COG_TYPE,
            "title": f"Color verdadero, tesela {tile}, "
                     f"{scene.datetime:%H:%M} UTC (COG de Earth Search)",
            "description": (
                f"TCI de la escena {scene.id}: RGB de 8 bits a 10 m en la "
                "proyección UTM de la tesela, nodata 0, con overviews "
                "internas. Archivo de Earth Search, no una copia."
            ),
            "roles": ["data", "visual", "external"],
        }
    first = next(k for k in assets if k.startswith("visual-"))
    assets[first]["processing:expression"] = {
        "format": "gdal",
        "expression": recipe(day, out_name),
    }
    assets["thumbnail"] = {
        "href": "./thumbnail.jpg",
        "type": "image/jpeg",
        "title": "Vista previa",
        "description": (
            "Mosaico de los recursos visuales del día, recortado al partido "
            "y reducido. Contains modified Copernicus Sentinel data "
            f"{year}."
        ),
        "roles": ["thumbnail"],
        **common.file_fields(thumb),
    }
    return {
        "type": "Feature",
        "stac_version": "1.1.0",
        "stac_extensions": [common.EXT_FILE, common.EXT_EO, EXT_PROCESSING],
        "id": quarter.item_id,
        "collection": COLLECTION_ID,
        **common.geometry_fields(geom),
        "properties": props,
        "assets": assets,
        "links": links,
    }


def build_quarter(quarter: Quarter, force: bool = False,
                  area=None, cutline: Path | None = None) -> str:
    """Build one quarter. Returns 'built', 'skipped' or 'empty'."""
    out_dir = COLLECTION_DIR / quarter.item_id
    item_path = out_dir / f"{quarter.item_id}.json"
    thumb = out_dir / "thumbnail.jpg"
    if item_path.exists() and thumb.exists() and not force:
        return "skipped"
    area = area if area is not None else partido()
    source, _, day = choose(quarter, area)
    if day is None:
        log(f"{quarter.label} no scenes in {C1} or {L2A}; excluded")
        return "empty"
    out_dir.mkdir(parents=True, exist_ok=True)
    if cutline is None:
        with tempfile.TemporaryDirectory(dir=_work()) as tmp:
            render_thumbnail(day, write_cutline(area, Path(tmp)), thumb)
    else:
        render_thumbnail(day, cutline, thumb)
    common.write_json(item_path, build_item(quarter, source, day, area, thumb))
    log(f"{quarter.label} {source} {day.day} scenes={len(day.scenes)} "
        f"cloud={day.cloud:.2f}% coverage={day.coverage:.4f}")
    return "built"


def write_cutline(area, directory: Path) -> Path:
    from shapely.geometry import mapping

    path = directory / "partido.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {}, "geometry": mapping(area)}]}))
    return path


def _work() -> Path:
    WORK.mkdir(parents=True, exist_ok=True)
    return WORK


def log(line: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{stamp} {line}", flush=True)
    with (_work() / TIMINGS.name).open("a") as handle:
        handle.write(f"{stamp} {line}\n")


# --- collection --------------------------------------------------------

def write_scene_index(collection_dir: Path, last: Quarter) -> Path:
    """escenas.parquet: every scene over the partido, in time order.

    Each quarter lists the scenes of the collection its Item uses.
    """
    from stac_geoparquet.arrow import parse_stac_items_to_arrow, to_parquet

    area = partido()
    scenes = []
    for quarter in quarters_between(Quarter.parse(FIRST_QUARTER), last):
        _, items, _ = choose(quarter, area)
        scenes.extend(i.to_dict(transform_hrefs=False) for i in items)
    scenes.sort(key=lambda s: (s["properties"]["datetime"], s["id"]))
    out = collection_dir / "escenas.parquet"
    to_parquet(parse_stac_items_to_arrow(scenes), out,
               schema_version="1.1.0", compression="zstd",
               write_statistics=True)
    return out


def update_collection(collection_dir: Path | None = None,
                      now: datetime | None = None) -> dict:
    """Rebuild collection.json, items.parquet and escenas.parquet."""
    collection_dir = collection_dir or COLLECTION_DIR
    now = now or datetime.now(timezone.utc)
    items = common.load_items(collection_dir)
    path = collection_dir / "collection.json"
    doc = json.loads(path.read_text()) if path.exists() else collection_stub()
    if items:
        mirror = collection_dir / "items.parquet"
        common.write_item_mirror(items, mirror)
        times = sorted(i["properties"]["datetime"] for i in items)
        doc["extent"] = {
            "spatial": {"bbox": [common.union_bbox(items)]},
            "temporal": {"interval": [[times[0], times[-1]]]},
        }
        latest = max(items, key=lambda i: i["properties"]["datetime"])
        (collection_dir / "thumbnail.jpg").write_bytes(
            (collection_dir / latest["id"] / "thumbnail.jpg").read_bytes())
        years = sorted({int(t[:4]) for t in times})
        doc["assets"]["items"].update(common.file_fields(mirror))
        scenes = write_scene_index(collection_dir, latest_quarter(now))
        doc["assets"]["escenas"].update(common.file_fields(scenes))
        doc["assets"]["thumbnail"].update(
            common.file_fields(collection_dir / "thumbnail.jpg"))
        doc["assets"]["thumbnail"]["description"] = (
            f"Vista previa del trimestre más reciente ({latest['id']}). "
            f"Contains modified Copernicus Sentinel data {years[-1]}."
        )
        span = (str(years[0]) if years[0] == years[-1]
                else f"{years[0]}-{years[-1]}")
        doc["pergamino:attribution"] = f"Copernicus Sentinel data {span}"
    keep = [ln for ln in doc["links"] if ln["rel"] != "item"]
    doc["links"] = keep[:2] + common.item_links(collection_dir, items) + keep[2:]
    doc["updated"] = common.utc_now()
    common.write_json(path, doc)
    return doc


def exclude_quarter(quarter: Quarter,
                    collection_dir: Path | None = None) -> None:
    """Record a quarter with no scene in the collection.

    Listing it in ``pergamino:excluded_quarters`` keeps the refresh from
    retrying it every week and tells a reader the gap is deliberate.
    """
    path = (collection_dir or COLLECTION_DIR) / "collection.json"
    doc = json.loads(path.read_text())
    excluded = set(doc.get("pergamino:excluded_quarters", []))
    excluded.add(quarter.label)
    doc["pergamino:excluded_quarters"] = sorted(excluded)
    common.write_json(path, doc)


def collection_stub() -> dict[str, Any]:
    """The hand-maintained parts of collection.json, used on first build."""
    raise SystemExit(
        f"{COLLECTION_DIR / 'collection.json'} is missing; it is committed "
        "with the repository"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--quarter", action="append",
                       help="a quarter such as 2024Q3; repeatable")
    group.add_argument("--all", action="store_true",
                       help=f"every quarter from {FIRST_QUARTER} to the latest")
    group.add_argument("--latest", action="store_true",
                       help="the newest quarter that ended "
                            f"{LAG_DAYS} or more days ago")
    group.add_argument("--collection-only", action="store_true",
                       help="only rebuild collection.json and the parquet "
                            "files")
    parser.add_argument("--force", action="store_true",
                        help="rebuild quarters that already exist")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    if args.collection_only:
        quarters = []
    elif args.all:
        quarters = quarters_between(Quarter.parse(FIRST_QUARTER),
                                    latest_quarter(now))
    else:
        quarters = ([latest_quarter(now)] if args.latest
                    else [Quarter.parse(q) for q in args.quarter])

    area = partido()
    failed = []
    with tempfile.TemporaryDirectory(dir=_work()) as tmp:
        cutline = write_cutline(area, Path(tmp))

        def one(quarter: Quarter) -> tuple[Quarter, str]:
            try:
                return quarter, build_quarter(quarter, args.force, area,
                                              cutline)
            except Exception as exc:  # noqa: BLE001 - report at the end
                log(f"{quarter.label} FAILED {type(exc).__name__}: {exc}")
                return quarter, "failed"

        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            for quarter, status in pool.map(one, quarters):
                if status == "skipped":
                    print(f"{quarter.label} exists; skipped", flush=True)
                elif status == "empty":
                    exclude_quarter(quarter)
                elif status == "failed":
                    failed.append(quarter.label)
    update_collection(now=now)
    if failed:
        print("failed: " + ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
