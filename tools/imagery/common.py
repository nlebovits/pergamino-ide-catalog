"""Helpers shared by the imagery builders.

Both imagery collections model one STAC Item per COG and publish a
stac-geoparquet item mirror, so the pieces they share live here: file
checksums in multihash form, valid-data footprints, embedded COG statistics,
the item mirror, and the collection's item links and extent.

Nothing here talks to the network.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"
SOURCES = ROOT / "sources"

COG_TYPE = "image/tiff; application=geotiff; profile=cloud-optimized"
GEOJSON = "application/geo+json"

EXT_FILE = "https://stac-extensions.github.io/file/v2.1.0/schema.json"
EXT_PROJ = "https://stac-extensions.github.io/projection/v2.0.0/schema.json"
EXT_EO = "https://stac-extensions.github.io/eo/v2.0.0/schema.json"
EXT_RASTER = "https://stac-extensions.github.io/raster/v2.0.0/schema.json"
EXT_PORTOLAN = "https://schemas.portolan-sdi.org/portolan/v0.3.0/schema.json"

HOST = {
    "name": "Source Cooperative",
    "roles": ["host"],
    "url": "https://source.coop/nlebovits/pergamino-ide",
    "email": "nlebovits@pm.me",
}


def utc_now() -> str:
    """The current time as an RFC 3339 string with second precision."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def multihash(path: Path) -> str:
    """sha2-256 multihash of a file, as the file extension expects."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return "1220" + digest.hexdigest()


def file_fields(path: Path) -> dict[str, Any]:
    """file:size and file:checksum for a local file."""
    return {"file:size": path.stat().st_size, "file:checksum": multihash(path)}


def write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def run(cmd: list[str]) -> None:
    """Run a command and fail loudly, with its stderr, if it fails."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{proc.stderr.strip()}")


# --- rasters -----------------------------------------------------------

STAT_KEYS = {
    "minimum": "STATISTICS_MINIMUM",
    "maximum": "STATISTICS_MAXIMUM",
    "mean": "STATISTICS_MEAN",
    "stddev": "STATISTICS_STDDEV",
    "valid_percent": "STATISTICS_VALID_PERCENT",
}


def embedded_stats(path: Path) -> list[dict[str, float]]:
    """The per-band statistics embedded in a GeoTIFF's GDAL_METADATA tag.

    PAM is off, so a sidecar .aux.xml cannot stand in for embedded values.
    """
    import rasterio

    out = []
    with rasterio.Env(GDAL_PAM_ENABLED="NO"), rasterio.open(path) as src:
        for bidx in range(1, src.count + 1):
            tags = src.tags(bidx)
            out.append({
                key: round(float(tags[tag]), 4)
                for key, tag in STAT_KEYS.items() if tag in tags
            })
    return out


def stats_in_header(path: Path) -> bool:
    """True when the GDAL_METADATA tag of the first IFD precedes the pixels.

    The spec wants the statistics in the leading header block, so that they
    arrive with a reader's first range request. A COG written by GDAL keeps
    every IFD and its tag values before the first tile; an in-place edit
    appends the tag at the end of the file instead.
    """
    import struct

    sizes = {1: 1, 2: 1, 3: 2, 4: 4, 16: 8}  # BYTE ASCII SHORT LONG LONG8
    codes = {1: "B", 2: "B", 3: "H", 4: "I", 16: "Q"}
    with path.open("rb") as handle:
        order = handle.read(2)
        fmt = "<" if order == b"II" else ">"
        magic = struct.unpack(fmt + "H", handle.read(2))[0]
        if magic == 42:
            handle.seek(struct.unpack(fmt + "I", handle.read(4))[0])
            count = struct.unpack(fmt + "H", handle.read(2))[0]
            entry, word = "HHI4s", 4
        elif magic == 43:  # BigTIFF
            handle.read(4)
            handle.seek(struct.unpack(fmt + "Q", handle.read(8))[0])
            count = struct.unpack(fmt + "Q", handle.read(8))[0]
            entry, word = "HHQ8s", 8
        else:
            return False
        tags = {}
        for _ in range(count):
            raw = handle.read(struct.calcsize(fmt + entry))
            tag, typ, n, value = struct.unpack(fmt + entry, raw)
            tags[tag] = (typ, n, value)
        if 42112 not in tags or 324 not in tags:
            return False

        def values(typ, n, value):
            """Every element of a tag, inline or at its offset."""
            size = sizes.get(typ, 1)
            code = f"{fmt}{n}{codes[typ]}"
            if n * size <= word:
                return struct.unpack(code, value[:n * size])
            offset = struct.unpack(fmt + ("I" if word == 4 else "Q"), value)[0]
            handle.seek(offset)
            return struct.unpack(code, handle.read(n * size))

        typ, n, value = tags[42112]
        if n * sizes.get(typ, 1) <= word:
            return False  # an inline tag cannot hold the statistics
        meta_offset = struct.unpack(fmt + ("I" if word == 4 else "Q"),
                                    value)[0]
        # A sparse file stores empty tiles at offset 0.
        written = [v for v in values(*tags[324]) if v]
        if not written:
            return False
        first_tile = min(written)
    return 0 < meta_offset < first_tile


def footprint(path: Path, max_side: int = 1024, simplify_px: float = 2.0):
    """Valid-data footprint of a raster as a shapely geometry in EPSG:4326.

    Reads the dataset mask (internal mask, alpha, or nodata) at a reduced
    size, polygonizes it, simplifies by two pixels of that reduced
    grid, and clips to the raster's own bounds so simplification never
    claims ground outside the grid.
    """
    import numpy as np
    import rasterio
    from rasterio.features import shapes
    from rasterio.warp import transform_geom
    from shapely.geometry import box, mapping, shape
    from shapely.ops import unary_union

    with rasterio.open(path) as src:
        scale = max(src.width, src.height) / max_side
        scale = max(scale, 1.0)
        out_w = max(1, int(round(src.width / scale)))
        out_h = max(1, int(round(src.height / scale)))
        mask = src.dataset_mask(out_shape=(out_h, out_w))
        transform = src.transform * src.transform.scale(
            src.width / out_w, src.height / out_h
        )
        crs = src.crs
        bounds = box(*src.bounds)
        pixel = abs(transform.a)
    valid = (mask > 0).astype("uint8")
    polys = [
        shape(geom)
        for geom, value in shapes(valid, mask=valid, transform=transform)
        if value == 1
    ]
    if not polys:
        return None
    geom = unary_union(polys).buffer(0)
    geom = geom.simplify(pixel * simplify_px, preserve_topology=True)
    geom = geom.intersection(bounds)
    if not np.isfinite(geom.area) or geom.is_empty:
        return None
    wgs = transform_geom(crs, "EPSG:4326", mapping(geom), precision=7)
    return shape(wgs).buffer(0)


def geometry_fields(geom) -> dict[str, Any]:
    """STAC geometry and bbox for a shapely geometry, rounded to 7 places."""
    from shapely.geometry import mapping

    gj = json.loads(json.dumps(mapping(geom)))
    minx, miny, maxx, maxy = geom.bounds
    return {
        "geometry": gj,
        "bbox": [round(minx, 7), round(miny, 7), round(maxx, 7), round(maxy, 7)],
    }


def proj_fields(path: Path) -> dict[str, Any]:
    """projection v2.0.0 fields read from the file."""
    import rasterio

    with rasterio.open(path) as src:
        epsg = src.crs.to_epsg()
        return {
            "proj:code": f"EPSG:{epsg}",
            "proj:shape": [src.height, src.width],
            "proj:transform": [round(v, 12) for v in list(src.transform)[:6]],
            "proj:bbox": [round(v, 9) for v in src.bounds],
        }


def jpeg_thumbnail(cog: Path, out: Path, max_side: int = 512,
                   background: int = 255) -> None:
    """A JPEG preview from a COG's overviews, masked pixels filled.

    Fill with white so that an irregular footprint reads as a shape on a
    page, not as a black frame.
    """
    import numpy as np
    import rasterio
    from PIL import Image

    with rasterio.open(cog) as src:
        scale = max(src.width, src.height) / max_side
        w = max(1, int(round(src.width / scale)))
        h = max(1, int(round(src.height / scale)))
        rgb = src.read([1, 2, 3], out_shape=(3, h, w))
        mask = src.dataset_mask(out_shape=(h, w))
    rgb = np.where(mask[None, :, :] > 0, rgb, background).astype("uint8")
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.moveaxis(rgb, 0, -1)).save(
        out, "JPEG", quality=82, optimize=True
    )


# --- item mirror and collection bookkeeping ----------------------------

def _hilbert(x: int, y: int, order: int = 16) -> int:
    """Index of (x, y) on a Hilbert curve over a 2**order grid."""
    d = 0
    s = 1 << (order - 1)
    while s > 0:
        rx = 1 if x & s else 0
        ry = 1 if y & s else 0
        d += s * s * ((3 * rx) ^ ry)
        if ry == 0:
            if rx == 1:
                x = s - 1 - x
                y = s - 1 - y
            x, y = y, x
        s >>= 1
    return d


def hilbert_order(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Items sorted by the Hilbert index of their bbox centre, then id."""
    if not items:
        return items
    xs = [(i["bbox"][0] + i["bbox"][2]) / 2 for i in items]
    ys = [(i["bbox"][1] + i["bbox"][3]) / 2 for i in items]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span_x = (x1 - x0) or 1.0
    span_y = (y1 - y0) or 1.0
    top = (1 << 16) - 1

    def key(pair):
        item, x, y = pair
        hx = int((x - x0) / span_x * top)
        hy = int((y - y0) / span_y * top)
        return (_hilbert(hx, hy), item["id"])

    return [p[0] for p in sorted(zip(items, xs, ys), key=key)]


def write_item_mirror(items: list[dict[str, Any]], out: Path) -> None:
    """Write the stac-geoparquet item mirror, spatially ordered.

    The rows follow the Hilbert order of the item bbox centres, and the
    file carries a GeoParquet 1.1 bbox covering column so a reader can skip
    row groups on footer statistics alone. stac-geoparquet writes each
    Arrow batch as one row group, and a batch holds at most 65,536 rows,
    under the 150,000-row cap.
    """
    from stac_geoparquet.arrow import parse_stac_items_to_arrow, to_parquet

    ordered = hilbert_order(items)
    reader = parse_stac_items_to_arrow(ordered)
    out.parent.mkdir(parents=True, exist_ok=True)
    to_parquet(reader, out, schema_version="1.1.0", compression="zstd",
               write_statistics=True)


def load_items(collection_dir: Path) -> list[dict[str, Any]]:
    """Every item JSON one directory below the collection."""
    items = []
    for path in sorted(collection_dir.glob("*/*.json")):
        doc = json.loads(path.read_text())
        if doc.get("type") == "Feature":
            items.append(doc)
    return items


def item_links(collection_dir: Path, items: list[dict[str, Any]]):
    links = []
    for item in sorted(items, key=lambda i: i["id"]):
        links.append({
            "rel": "item",
            "href": f"./{item['id']}/{item['id']}.json",
            "type": GEOJSON,
            "title": item["properties"]["title"],
        })
    return links


def union_bbox(items: Iterable[dict[str, Any]]) -> list[float]:
    boxes = [i["bbox"] for i in items]
    return [
        min(b[0] for b in boxes), min(b[1] for b in boxes),
        max(b[2] for b in boxes), max(b[3] for b in boxes),
    ]


def item_interval(item: dict[str, Any]) -> tuple[str, str]:
    props = item["properties"]
    start = props.get("start_datetime") or props.get("datetime")
    end = props.get("end_datetime") or props.get("datetime")
    return start, end


def finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(v) for v in values)
