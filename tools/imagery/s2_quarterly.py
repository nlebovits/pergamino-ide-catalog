#!/usr/bin/env python3
"""Quarterly cloud-free Sentinel-2 L2A mosaics over the Partido de Pergamino.

One STAC Item per calendar quarter in ``catalog/imagenes/sentinel2_trimestral``.
For each quarter:

1. Search Element 84 Earth Search for Sentinel-2 L2A scenes that touch the
   partido bbox. ``sentinel-2-c1-l2a`` (Collection 1, processing baseline
   05.00) is used whenever it has scenes for the quarter; otherwise the
   older ``sentinel-2-l2a``. Over this bbox C1 starts in January 2018, so
   2017 comes from ``sentinel-2-l2a``.
2. Load B02, B03, B04, B08 and SCL with odc-stac at 10 m in EPSG:32720
   (UTM 20S, the zone that holds the whole partido), grouped by solar day,
   as dask arrays in 1024 px chunks.
3. Mask every pixel whose SCL class is 0 (no data), 1 (saturated or
   defective), 3 (cloud shadow), 8 (cloud, medium probability), 9 (cloud,
   high probability) or 10 (thin cirrus), and every band value of 0.
4. Take the per-pixel median of what is left over the quarter.
5. Write ``data.tif`` (4-band uint16 COG, nodata 0, DEFLATE predictor 2),
   ``visual.tif`` (8-bit RGB JPEG COG with an internal mask) and
   ``thumbnail.jpg``, then the Item JSON.

Digital numbers follow the Collection 1 convention throughout: reflectance =
DN * 0.0001 - 0.1. Scenes from ``sentinel-2-l2a`` before processing baseline
04.00 declare an offset of 0, so their non-zero DNs are raised by 1000 before
the median. The shift is computed from each scene's own ``raster:bands``
offset, not assumed.

Idempotent: a quarter whose Item JSON and COGs exist is skipped unless
``--force``. The collection JSON and ``items.parquet`` are rebuilt from the
Item JSON on disk after every run.

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
import shutil
import sys
import time
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
CHUNK = 1024
FIRST_QUARTER = "2017Q1"
MAX_SCENE_CLOUD = 90  # percent, the scene's own eo:cloud_cover
# Dask threads. Each one holds every scene of the quarter for one chunk, so
# memory grows with threads x scenes x CHUNK^2: 32 threads at 2048 px passed
# 22 GB on 2019Q2. The median is per pixel, so neither value changes the
# output.
THREADS = int(os.environ.get("S2_THREADS", "8"))
LAG_DAYS = 14  # a quarter is added once it ended this many days ago

# STAC asset key -> (Sentinel-2 band, common name). Wavelengths are read
# from the source collection's item_assets at build time.
BANDS = [
    ("blue", "B02"),
    ("green", "B03"),
    ("red", "B04"),
    ("nir", "B08"),
]
SCL_MASKED = (0, 1, 3, 8, 9, 10)
SCL_NAMES = {
    0: "no data",
    1: "saturated or defective",
    3: "cloud shadows",
    8: "cloud medium probability",
    9: "cloud high probability",
    10: "thin cirrus",
}

# The Collection 1 convention every mosaic is written in.
SCALE = 0.0001
OFFSET = -0.1

# Visual stretch: BOA reflectance 0.0 -> 1 and VISUAL_MAX -> 255, linear,
# then a gamma of 1/VISUAL_GAMMA. Fixed for every quarter, so quarters can
# be compared by eye.
VISUAL_MAX = 0.20
VISUAL_GAMMA = 1.4

COLLECTION_ID = "imagenes/sentinel2_trimestral"
COLLECTION_DIR = common.CATALOG / "imagenes" / "sentinel2_trimestral"
WORK = common.SOURCES / "sentinel2"
TIMINGS = WORK / "timings.log"

LEGAL_NOTICE = (
    "https://sentinels.copernicus.eu/documents/247904/690755/"
    "Sentinel_Data_Legal_Notice"
)


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

def search(quarter: Quarter):
    """(source collection id, deduplicated pystac Items) for a quarter.

    Scenes whose ``eo:cloud_cover`` exceeds MAX_SCENE_CLOUD are dropped
    before loading: each costs a full read and adds almost no clear pixel.
    If that would drop every scene, all are kept.
    """
    from pystac_client import Client

    client = Client.open(EARTH_SEARCH)
    window = f"{quarter.start_iso()}/{quarter.end_iso()}"
    for collection in (C1, L2A):
        found = client.search(
            collections=[collection], bbox=BBOX, datetime=window, limit=200
        )
        items = dedupe(list(found.items()))
        if items:
            clearer = [
                i for i in items
                if i.properties.get("eo:cloud_cover", 0) <= MAX_SCENE_CLOUD
            ]
            return collection, (clearer or items)
    return None, []


def dedupe(items):
    """One item per tile and acquisition time, the most recently created.

    ``sentinel-2-l2a`` holds reprocessed duplicates of some scenes (ids
    ending ``_0_L2A`` and ``_1_L2A``).
    """
    keep: dict[tuple, Any] = {}
    for item in items:
        props = item.properties
        tile = props.get("grid:code") or props.get("s2:mgrs_tile")
        key = (tile, item.datetime.replace(microsecond=0))
        stamp = props.get("created") or props.get("s2:generation_time") or ""
        if key not in keep or stamp > (
            keep[key].properties.get("created")
            or keep[key].properties.get("s2:generation_time") or ""
        ):
            keep[key] = item
    return sorted(keep.values(), key=lambda i: (i.datetime, i.id))


def dn_shift(item) -> int:
    """DNs to add so an item's values follow the Collection 1 offset."""
    bands = item.assets["red"].extra_fields.get("raster:bands") or [{}]
    offset = bands[0].get("offset", 0.0) or 0.0
    return int(round((offset - OFFSET) / SCALE))


# --- compute -----------------------------------------------------------

def _progress_class():
    from dask.callbacks import Callback

    class Progress(Callback):
        """Print the share of finished dask tasks once a minute."""

        def _start_state(self, dsk, state):
            self.total = sum(len(state[k]) for k in
                             ("ready", "waiting", "running", "finished"))
            self.last = time.time()

        def _posttask(self, key, result, dsk, state, worker_id):
            if time.time() - self.last >= 60:
                self.last = time.time()
                done = len(state["finished"])
                print(f"    {done}/{self.total} tasks", flush=True)

    return Progress


def _Progress():
    return _progress_class()()


def median_mosaic(items):
    """Per-pixel median of clear observations, and the number of solar days.

    Returns (uint16 array [4, h, w] with 0 as nodata, odc GeoBox, days).
    """
    import dask
    import numpy as np
    import odc.stac

    shifts = {dn_shift(i) for i in items}
    if len(shifts) != 1:
        raise RuntimeError(f"mixed DN offsets in one quarter: {shifts}")
    shift = shifts.pop()

    odc.stac.configure_rio(
        cloud_defaults=True,
        GDAL_HTTP_MAX_RETRY="8",
        GDAL_HTTP_RETRY_DELAY="3",
        GDAL_HTTP_MULTIPLEX="YES",
        GDAL_HTTP_VERSION="2",
        GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
    )
    ds = odc.stac.load(
        items,
        bands=[b for b, _ in BANDS] + ["scl"],
        crs=CRS,
        resolution=RESOLUTION,
        bbox=BBOX,
        groupby="solar_day",
        chunks={"x": CHUNK, "y": CHUNK},
        resampling="nearest",
    )
    days = int(ds.sizes["time"])
    cloudy = ds["scl"].isin(list(SCL_MASKED))
    medians = []
    for band, _ in BANDS:
        values = ds[band]
        clear = (~cloudy) & (values != 0)
        medians.append(
            values.astype("float32").where(clear).median("time", skipna=True)
        )
    with dask.config.set(scheduler="threads", num_workers=THREADS), \
            _Progress():
        stacked = dask.compute(*[m.data for m in medians])
    arr = np.stack(stacked)
    valid = np.all(np.isfinite(arr), axis=0)
    out = np.zeros(arr.shape, dtype="uint16")
    rounded = np.rint(np.nan_to_num(arr, nan=0.0)) + shift
    rounded = np.clip(rounded, 1, 65535)
    out[:, valid] = rounded[:, valid].astype("uint16")
    return out, valid, ds.odc.geobox, days, shift


def band_stats(arr, valid) -> list[dict[str, float]]:
    """Exact per-band statistics over valid pixels, GDAL's definitions."""
    total = valid.size
    out = []
    for band in arr:
        vals = band[valid].astype("float64")
        out.append({
            "minimum": float(vals.min()),
            "maximum": float(vals.max()),
            "mean": float(vals.mean()),
            "stddev": float(vals.std()),
            "valid_percent": float(100.0 * vals.size / total),
        })
    return out


def write_cog(arr, valid, geobox, dst: Path, *, nodata, compress: dict,
              descriptions: list[str], colorinterp=None) -> None:
    """Write an array as a COG with exact statistics in its leading header.

    The statistics are set as band metadata on an intermediate tiled
    GeoTIFF and the COG driver copies them into the GDAL_METADATA tag while
    it writes the header, before any tile.
    """
    import rasterio
    from rasterio.shutil import copy as rio_copy

    tmp = dst.with_suffix(".tmp.tif")
    count, height, width = arr.shape
    profile = {
        "driver": "GTiff", "width": width, "height": height, "count": count,
        "dtype": arr.dtype.name, "crs": str(geobox.crs),
        "transform": geobox.transform, "tiled": True,
        "blockxsize": 512, "blockysize": 512, "compress": "deflate",
        "BIGTIFF": "IF_SAFER",
    }
    if nodata is not None:
        profile["nodata"] = nodata
    stats = band_stats(arr, valid)
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK="YES"):
        with rasterio.open(tmp, "w", **profile) as out:
            out.write(arr)
            if nodata is None:
                out.write_mask((valid * 255).astype("uint8"))
            if colorinterp:
                out.colorinterp = colorinterp
            for i, (s, desc) in enumerate(zip(stats, descriptions), start=1):
                out.set_band_description(i, desc)
                out.update_tags(i, **{
                    common.STAT_KEYS[k]: repr(v) for k, v in s.items()
                })
        rio_copy(tmp, dst, driver="COG", BLOCKSIZE="512", STATISTICS="AUTO",
                 BIGTIFF="IF_SAFER", **compress)
    tmp.unlink()
    dst.with_suffix(".tif.aux.xml").unlink(missing_ok=True)


def to_visual(data, valid):
    """8-bit RGB from the uint16 mosaic, with the fixed documented stretch."""
    import numpy as np

    rgb = data[[2, 1, 0]].astype("float32") * SCALE + OFFSET
    scaled = np.clip(rgb / VISUAL_MAX, 0.0, 1.0) ** (1.0 / VISUAL_GAMMA)
    out = (1 + np.rint(scaled * 254)).astype("uint8")
    out[:, ~valid] = 0
    return out


# --- STAC --------------------------------------------------------------

def source_band_meta(source) -> dict[str, dict[str, Any]]:
    """eo fields per band from the source collection's item_assets."""
    from pystac_client import Client

    coll = Client.open(EARTH_SEARCH).get_collection(source).to_dict()
    out = {}
    for key, s2name in BANDS:
        eo = (coll["item_assets"][key].get("eo:bands") or [{}])[0]
        out[key] = {
            "name": s2name,
            "eo:common_name": key,
            "eo:center_wavelength": eo.get("center_wavelength"),
            "eo:full_width_half_max": eo.get("full_width_half_max"),
        }
    return out


def build_item(quarter: Quarter, source: str, items, days: int, shift: int,
               out_dir: Path) -> dict[str, Any]:
    data = out_dir / "data.tif"
    visual = out_dir / "visual.tif"
    thumb = out_dir / "thumbnail.jpg"
    geom = common.footprint(data)
    stats = common.embedded_stats(data)
    vstats = common.embedded_stats(visual)
    meta = source_band_meta(source)
    bands = []
    for (key, _), s in zip(BANDS, stats):
        band = {k: v for k, v in meta[key].items() if v is not None}
        band.update({
            "description": f"Reflectancia de superficie (BOA), {key}",
            "data_type": "uint16",
            "nodata": 0,
            "unit": "1",
            "raster:scale": SCALE,
            "raster:offset": OFFSET,
            "raster:spatial_resolution": RESOLUTION,
            "statistics": s,
        })
        bands.append(band)
    vbands = [
        {"name": name, "data_type": "uint8", "statistics": s}
        for name, s in zip(("red", "green", "blue"), vstats)
    ]
    # Every scene of a calendar quarter falls in the quarter's own year.
    attribution = f"Contains modified Copernicus Sentinel data {quarter.year}"
    valid_percent = round(stats[0]["valid_percent"], 2)
    props = {
        "title": f"Sentinel-2, mediana trimestral {quarter.year} T{quarter.q}",
        "description": (
            f"Mediana por píxel de las observaciones sin nubes de Sentinel-2 "
            f"L2A entre {quarter.start.isoformat()} y "
            f"{quarter.end.isoformat()}, sobre el rectángulo del Partido de "
            f"Pergamino. {attribution}."
        ),
        "datetime": None,
        "start_datetime": quarter.start_iso(),
        "end_datetime": quarter.end_iso(),
        "constellation": "sentinel-2",
        "instruments": ["msi"],
        "gsd": RESOLUTION,
        **common.proj_fields(data),
        "pergamino:source_collection": source,
        "pergamino:max_scene_cloud_cover": MAX_SCENE_CLOUD,
        "pergamino:scene_count": len(items),
        "pergamino:scene_ids": [i.id for i in items],
        "pergamino:acquisition_days": days,
        "pergamino:dn_shift": shift,
        "pergamino:valid_percent": valid_percent,
        "pergamino:attribution": attribution,
        "created": common.utc_now(),
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
    for item in items:
        self_href = item.get_self_href() or (
            f"{EARTH_SEARCH}/collections/{source}/items/{item.id}"
        )
        links.append({
            "rel": "derived_from", "href": self_href, "type": common.GEOJSON,
            "title": item.id,
        })
    assets = {
        "data": {
            "href": "./data.tif",
            "type": common.COG_TYPE,
            "title": "Mosaico de reflectancia, 4 bandas (COG)",
            "description": (
                "B02, B03, B04 y B08 a 10 m en EPSG:32720, uint16, nodata 0. "
                "Reflectancia = DN * 0.0001 - 0.1 (convención de Sentinel-2 "
                "Collection 1). Estadísticas por banda embebidas en la "
                "cabecera."
            ),
            "roles": ["data", "reflectance"],
            "bands": bands,
            **common.file_fields(data),
        },
        "visual": {
            "href": "./visual.tif",
            "type": common.COG_TYPE,
            "title": "Color verdadero, 8 bits (COG)",
            "description": (
                "B04, B03 y B02 en RGB de 8 bits, JPEG, con máscara interna "
                "donde el mosaico no tiene datos. Estiramiento fijo para "
                f"todos los trimestres: reflectancia 0 a {VISUAL_MAX} lineal "
                f"a 1-255 con gamma 1/{VISUAL_GAMMA}."
            ),
            "roles": ["visual"],
            "bands": vbands,
            **common.file_fields(visual),
        },
        "thumbnail": {
            "href": "./thumbnail.jpg",
            "type": "image/jpeg",
            "title": "Vista previa",
            "description": "JPEG del recurso visual reducido, sin mapa base.",
            "roles": ["thumbnail"],
            **common.file_fields(thumb),
        },
    }
    item = {
        "type": "Feature",
        "stac_version": "1.1.0",
        "stac_extensions": [
            common.EXT_FILE, common.EXT_PROJ, common.EXT_EO, common.EXT_RASTER,
        ],
        "id": quarter.item_id,
        "collection": COLLECTION_ID,
        **common.geometry_fields(geom),
        "properties": props,
        "assets": assets,
        "links": links,
    }
    return item


def build_quarter(quarter: Quarter, force: bool = False) -> str:
    """Build one quarter. Returns 'built', 'skipped' or 'empty'."""
    out_dir = COLLECTION_DIR / quarter.item_id
    item_path = out_dir / f"{quarter.item_id}.json"
    done = all(p.exists() for p in (
        item_path, out_dir / "data.tif", out_dir / "visual.tif",
        out_dir / "thumbnail.jpg",
    ))
    if done and not force:
        return "skipped"
    t0 = time.time()
    source, items = search(quarter)
    if not items:
        log(f"{quarter.label} no scenes in {C1} or {L2A}; excluded")
        return "empty"
    t1 = time.time()
    data, valid, geobox, days, shift = median_mosaic(items)
    t2 = time.time()
    if not valid.any():
        log(f"{quarter.label} {len(items)} scenes but no clear pixel; "
            "excluded")
        return "empty"
    out_dir.mkdir(parents=True, exist_ok=True)
    names = [f"{s2} ({key})" for key, s2 in BANDS]
    write_cog(
        data, valid, geobox, out_dir / "data.tif", nodata=0,
        compress={"COMPRESS": "DEFLATE", "PREDICTOR": "2", "LEVEL": "6",
                  "OVERVIEW_RESAMPLING": "AVERAGE"},
        descriptions=names,
    )
    from rasterio.enums import ColorInterp

    write_cog(
        to_visual(data, valid), valid, geobox, out_dir / "visual.tif",
        nodata=None,
        compress={"COMPRESS": "JPEG", "QUALITY": "85",
                  "OVERVIEW_RESAMPLING": "AVERAGE"},
        descriptions=["B04 (red)", "B03 (green)", "B02 (blue)"],
        colorinterp=[ColorInterp.red, ColorInterp.green, ColorInterp.blue],
    )
    common.jpeg_thumbnail(out_dir / "visual.tif", out_dir / "thumbnail.jpg",
                          max_side=512)
    item = build_item(quarter, source, items, days, shift, out_dir)
    common.write_json(item_path, item)
    t3 = time.time()
    log(f"{quarter.label} {source} scenes={len(items)} days={days} "
        f"valid={item['properties']['pergamino:valid_percent']}% "
        f"search={t1 - t0:.0f}s median={t2 - t1:.0f}s "
        f"write={t3 - t2:.0f}s total={t3 - t0:.0f}s")
    return "built"


def log(line: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{stamp} {line}", flush=True)
    WORK.mkdir(parents=True, exist_ok=True)
    with TIMINGS.open("a") as handle:
        handle.write(f"{stamp} {line}\n")


# --- collection --------------------------------------------------------

def update_collection(collection_dir: Path | None = None) -> dict:
    """Rebuild collection.json and items.parquet from the Item JSON on disk."""
    collection_dir = collection_dir or COLLECTION_DIR
    items = common.load_items(collection_dir)
    path = collection_dir / "collection.json"
    doc = json.loads(path.read_text()) if path.exists() else collection_stub()
    if items:
        mirror = collection_dir / "items.parquet"
        common.write_item_mirror(items, mirror)
        starts = sorted(common.item_interval(i)[0] for i in items)
        ends = sorted(common.item_interval(i)[1] for i in items)
        doc["extent"] = {
            "spatial": {"bbox": [common.union_bbox(items)]},
            "temporal": {"interval": [[starts[0], ends[-1]]]},
        }
        latest = max(items, key=lambda i: i["properties"]["start_datetime"])
        shutil.copyfile(collection_dir / latest["id"] / "thumbnail.jpg",
                        collection_dir / "thumbnail.jpg")
        years = sorted({int(i["properties"]["start_datetime"][:4])
                        for i in items})
        doc["assets"]["items"].update(common.file_fields(mirror))
        doc["assets"]["thumbnail"].update(
            common.file_fields(collection_dir / "thumbnail.jpg"))
        doc["assets"]["thumbnail"]["description"] = (
            f"Vista previa del mosaico más reciente ({latest['id']})."
        )
        span = (str(years[0]) if years[0] == years[-1]
                else f"{years[0]}-{years[-1]}")
        doc["pergamino:attribution"] = (
            f"Contains modified Copernicus Sentinel data {span}"
        )
    keep = [ln for ln in doc["links"] if ln["rel"] != "item"]
    doc["links"] = keep[:2] + common.item_links(collection_dir, items) + keep[2:]
    doc["updated"] = common.utc_now()
    common.write_json(path, doc)
    return doc


def exclude_quarter(quarter: Quarter,
                    collection_dir: Path | None = None) -> None:
    """Record a quarter with no scene or no clear pixel in the collection.

    The spec has no use for an all-nodata scene, so such a quarter gets no
    Item. Listing it in ``pergamino:excluded_quarters`` keeps the refresh
    from retrying it every week and tells a reader the gap is deliberate.
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
                       help="only rebuild collection.json and items.parquet")
    parser.add_argument("--force", action="store_true",
                        help="rebuild quarters that already exist")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    if args.collection_only:
        quarters = []
    elif args.all:
        quarters = quarters_between(Quarter.parse(FIRST_QUARTER),
                                    latest_quarter(now))
    elif args.latest:
        quarters = [latest_quarter(now)]
    else:
        quarters = [Quarter.parse(q) for q in args.quarter]

    failed = []
    for quarter in quarters:
        try:
            status = build_quarter(quarter, force=args.force)
            if status == "skipped":
                print(f"{quarter.label} exists; skipped", flush=True)
            elif status == "empty":
                exclude_quarter(quarter)
        except Exception as exc:  # noqa: BLE001 - keep going, report at end
            log(f"{quarter.label} FAILED {type(exc).__name__}: {exc}")
            failed.append(quarter.label)
    update_collection()
    if failed:
        print("failed: " + ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
