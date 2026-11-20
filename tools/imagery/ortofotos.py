#!/usr/bin/env python3
"""The municipality's 2022 10 cm orthophotos, one STAC Item per GeoNode tile.

Builds ``catalog/imagenes/ortofotos_10cm_2022``:

- Lists the GeoNode raster datasets and keeps the 2022 10 cm orthophotos
  (``is_ortho``: the name carries ``10cm`` and the abstract says 2022).
- Downloads each original from ``/datasets/<alternate>/dataset_download``.
  GeoServer refuses that download for the largest tiles ("Download Limits
  Exceeded"); those are fetched from WCS 2.0.1 in 6144 px pieces aligned to
  the native pixel grid and assembled.
- Publishes the downloaded file byte for byte when it already meets every
  raster requirement of the spec (valid COG, square 512 px tiles, a full
  overview pyramid, embedded statistics in the leading header, a mask). A
  file that does not, including every WCS assembly, is re-encoded once as a
  JPEG COG with an internal mask and exact embedded statistics.
- Writes one Item per tile with the valid-data footprint as geometry, a
  thumbnail, the collection overview (8-bit RGB in EPSG:3857 at 1 m, with an
  internal mask), the collection thumbnail and ``items.parquet``.

Idempotent: a tile whose Item exists and whose GeoNode ``last_updated``
equals the Item's ``pergamino:source_updated`` is not downloaded again.

    python tools/imagery/ortofotos.py            # everything that changed
    python tools/imagery/ortofotos.py --only centro_10cm --force
    python tools/imagery/ortofotos.py --overview-only
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402

GEONODE = "https://geonode.pergamino.gob.ar"
WCS = f"{GEONODE}/geoserver/ows"
COLLECTION_ID = "imagenes/ortofotos_10cm_2022"
COLLECTION_DIR = common.CATALOG / "imagenes" / "ortofotos_10cm_2022"
RAW = common.SOURCES / "ortofotos" / "raw"
PUBLIC = (
    "https://data.source.coop/nlebovits/pergamino-ide/imagenes/"
    "ortofotos_10cm_2022"
)
USER_AGENT = "pergamino-ide-catalog imagery builder"

WCS_PIECE = 6144  # px; GeoServer's read limit refuses 8192 x 8192
JPEG_QUALITY = 75
OVERVIEW_RES = 1.0  # metres, EPSG:3857
OVERVIEW_FILE = "overview.tif"

START = "2022-01-01T00:00:00Z"
END = "2022-12-31T23:59:59Z"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

# The tiles that frame the city of Pergamino, for the collection thumbnail.
CITY_PREFIXES = ("centro", "norte_", "sur_", "este_", "oeste_", "aeroclub",
                 "zona_industrial_sur")


# --- GeoNode -----------------------------------------------------------

def http_get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_raster_records() -> list[dict[str, Any]]:
    """Every GeoNode dataset of subtype raster, across all pages."""
    records: list[dict[str, Any]] = []
    url = (f"{GEONODE}/api/v2/datasets?page_size=100&"
           + urllib.parse.quote("filter{subtype}") + "=raster")
    while url:
        page = json.loads(http_get(url))
        records.extend(page.get("datasets", []))
        url = (page.get("links") or {}).get("next")
    return records


def is_ortho(record: dict[str, Any]) -> bool:
    """A 2022 10 cm orthophoto tile, judged from the record itself.

    Every orthophoto record names itself ``*_10cm*`` and carries the
    abstract "Vuelos fotogramétricos del año 2022 realizados con VANT...".
    """
    return (
        record.get("subtype") == "raster"
        and "10cm" in (record.get("name") or "")
        and "2022" in (record.get("raw_abstract") or "")
    )


def item_id(record: dict[str, Any]) -> str:
    """A stable id from the GeoNode name, without GeoNode's suffixes.

    ``pinzon_10cm_9eb85c09...`` carries a 32-hex upload suffix and
    ``rancagua_10cm_cog`` a format suffix; neither names the place.
    """
    name = record["name"]
    name = re.sub(r"_[0-9a-f]{32}$", "", name)
    name = re.sub(r"_cog$", "", name)
    return name


def area_of(record: dict[str, Any]) -> str | None:
    """The covered area as GeoNode states it, or None when it states none."""
    text = (record.get("raw_supplemental_information") or "").strip()
    prefix = "Área cubierta:"
    if not text.startswith(prefix):
        return None
    return text[len(prefix):].strip().rstrip(".").replace("  ", " ")


def title_of(record: dict[str, Any]) -> str:
    area = area_of(record)
    if area is None:
        place = item_id(record).replace("_10cm", "").replace("_", " ")
        area = place.title()
    return f"Ortofoto 2022: {area}"


def dataset_page(record: dict[str, Any]) -> str:
    return f"{GEONODE}/catalogue/#/dataset/{record['pk']}"


def download_url(record: dict[str, Any]) -> str:
    return f"{GEONODE}/datasets/{record['alternate']}/dataset_download"


# --- download ----------------------------------------------------------

def download(record: dict[str, Any]) -> tuple[Path, str]:
    """Fetch a tile. Returns (local path, method).

    The method is ``dataset_download`` or ``wcs``. A previous download is
    reused when its sidecar records the same ``last_updated``.
    """
    RAW.mkdir(parents=True, exist_ok=True)
    name = record["name"]
    tif = RAW / f"{name}.tif"
    sidecar = RAW / f"{name}.json"
    if tif.exists() and sidecar.exists():
        meta = json.loads(sidecar.read_text())
        if meta.get("last_updated") == record.get("last_updated"):
            return tif, meta["method"]
    part = RAW / f"{name}.part"
    req = urllib.request.Request(download_url(record),
                                 headers={"User-Agent": USER_AGENT})
    # GeoServer answers an oversize request with an error body, sometimes
    # under 200 and sometimes under 500; both are read and judged below.
    try:
        with urllib.request.urlopen(req, timeout=600) as resp, \
                part.open("wb") as f:
            shutil.copyfileobj(resp, f, 1 << 20)
    except urllib.error.HTTPError as exc:
        part.write_bytes(exc.read())
    with part.open("rb") as f:
        magic = f.read(4)
    if magic in (b"II*\x00", b"MM\x00*"):
        part.replace(tif)
        method = "dataset_download"
    else:
        body = part.read_text(errors="replace")[:500]
        part.unlink()
        if "Download Limits Exceeded" not in body:
            raise RuntimeError(f"{name}: download returned {body!r}")
        wcs_download(record, tif)
        method = "wcs"
    sidecar.write_text(json.dumps({
        "pk": record["pk"], "uuid": record["uuid"], "name": name,
        "last_updated": record.get("last_updated"), "method": method,
        "fetched": common.utc_now(),
    }, indent=2) + "\n")
    return tif, method


def describe_coverage(coverage_id: str) -> dict[str, Any]:
    """Native grid of a coverage: size, origin corner and pixel size."""
    url = (f"{WCS}?service=WCS&version=2.0.1&request=DescribeCoverage"
           f"&coverageId={coverage_id}")
    root = ET.fromstring(http_get(url))
    ns = {"gml": "http://www.opengis.net/gml/3.2"}
    lower = [float(v) for v in root.find(".//gml:lowerCorner", ns).text.split()]
    upper = [float(v) for v in root.find(".//gml:upperCorner", ns).text.split()]
    high = [int(v) for v in root.find(".//gml:high", ns).text.split()]
    offsets = root.findall(".//gml:offsetVector", ns)
    # axisLabels="Lat Long": the first offset vector steps longitude.
    res_x = abs(float(offsets[0].text.split()[1]))
    res_y = abs(float(offsets[1].text.split()[0]))
    return {
        "width": high[0] + 1, "height": high[1] + 1,
        "west": lower[1], "north": upper[0],
        "res_x": res_x, "res_y": res_y,
    }


def wcs_download(record: dict[str, Any], dst: Path) -> None:
    """Assemble a coverage from grid-aligned WCS pieces into one GeoTIFF.

    Each request asks for a WCS_PIECE square whose bounds sit a quarter
    pixel inside the pixel edges, so GeoServer returns exactly the native
    pixels with no resampling. The pieces are mosaicked with a VRT and
    written as a tiled DEFLATE GeoTIFF; ``recog`` re-encodes it.
    """
    coverage = record["alternate"].replace(":", "__")
    grid = describe_coverage(coverage)
    work = Path(tempfile.mkdtemp(prefix=f"wcs_{record['name']}_",
                                 dir=RAW))
    jobs = []
    for row in range(0, grid["height"], WCS_PIECE):
        for col in range(0, grid["width"], WCS_PIECE):
            w = min(WCS_PIECE, grid["width"] - col)
            h = min(WCS_PIECE, grid["height"] - row)
            jobs.append((row, col, w, h))

    def fetch(job):
        row, col, w, h = job
        rx, ry = grid["res_x"], grid["res_y"]
        west = grid["west"] + col * rx + rx / 4
        east = grid["west"] + (col + w) * rx - rx / 4
        north = grid["north"] - row * ry - ry / 4
        south = grid["north"] - (row + h) * ry + ry / 4
        url = (f"{WCS}?service=WCS&version=2.0.1&request=GetCoverage"
               f"&coverageId={coverage}&format=image/tiff"
               f"&geotiff:compression=Deflate"
               f"&subset=Lat({south:.12f},{north:.12f})"
               f"&subset=Long({west:.12f},{east:.12f})")
        out = work / f"r{row:06d}_c{col:06d}.tif"
        for attempt in range(5):
            try:
                body = http_get(url, timeout=600)
                if body[:4] not in (b"II*\x00", b"MM\x00*"):
                    raise RuntimeError(body[:300].decode(errors="replace"))
                out.write_bytes(body)
                break
            except Exception:  # noqa: BLE001 - retried, then raised
                if attempt == 4:
                    raise
                time.sleep(10 * (attempt + 1))
        import rasterio

        with rasterio.open(out) as src:
            if (src.width, src.height) != (w, h):
                raise RuntimeError(
                    f"{out.name}: got {src.width}x{src.height}, want {w}x{h}"
                )
        return out

    with ThreadPoolExecutor(max_workers=3) as pool:
        pieces = list(pool.map(fetch, jobs))
    vrt = work / "mosaic.vrt"
    common.run(["gdalbuildvrt", "-q", str(vrt), *map(str, pieces)])
    common.run([
        "gdal_translate", "-q", "-of", "GTiff", "-co", "TILED=YES",
        "-co", "COMPRESS=DEFLATE", "-co", "BIGTIFF=YES",
        "-co", "NUM_THREADS=ALL_CPUS", str(vrt), str(dst),
    ])
    shutil.rmtree(work)


# --- conformance of the downloaded file ---------------------------------

def compliance(path: Path) -> list[str]:
    """Reasons a file cannot be published as is; empty when it can."""
    import rasterio
    from rasterio.enums import MaskFlags
    from rio_cogeo.cogeo import cog_validate

    reasons = []
    valid, errors, _ = cog_validate(str(path), quiet=True)
    if not valid or errors:
        reasons.append("not a valid COG")
    with rasterio.Env(GDAL_PAM_ENABLED="NO"), rasterio.open(path) as src:
        if src.count != 3 or set(src.dtypes) != {"uint8"}:
            reasons.append("not 3-band 8-bit")
        if not src.profile.get("tiled") or src.block_shapes[0] != (512, 512):
            reasons.append("tiles are not 512x512")
        factors = src.overviews(1)
        if not factors:
            reasons.append("no internal overviews")
        else:
            last = max(factors)
            if max(src.width, src.height) / last > 512:
                reasons.append("overviews stop before one tile")
        for bidx in range(1, src.count + 1):
            tags = src.tags(bidx)
            if not all(k in tags for k in common.STAT_KEYS.values()):
                reasons.append(f"band {bidx} lacks embedded statistics")
                break
        if all(f == [MaskFlags.all_valid] for f in src.mask_flag_enums):
            reasons.append("no mask, alpha or nodata")
    if not reasons and not common.stats_in_header(path):
        reasons.append("statistics are not in the leading header")
    return reasons


def source_quality(path: Path) -> int | None:
    """The JPEG quality GDAL recorded when the source was written, if any."""
    import rasterio

    with rasterio.open(path) as src:
        value = src.tags(ns="IMAGE_STRUCTURE").get("JPEG_QUALITY")
    return int(value) if value else None


def recog(src_path: Path, dst: Path, mask_from_zero: bool,
          quality: int = JPEG_QUALITY) -> None:
    """Re-encode a 3-band 8-bit raster as a JPEG COG with an internal mask.

    Streams the raster in strips, takes the mask from the source dataset
    mask or, for WCS output (which drops the mask and writes 0 instead),
    from pixels where all three bands are 0. Exact statistics over the
    masked pixels go into the band metadata of an intermediate GeoTIFF, and
    the COG driver writes them into the leading header.

    ``quality`` should be the source's own JPEG quality: a higher one only
    inflates the file around artefacts already there, a lower one loses
    detail the source still has.
    """
    import numpy as np
    import rasterio
    from rasterio.enums import ColorInterp
    from rasterio.shutil import copy as rio_copy
    from rasterio.windows import Window

    tmp = dst.with_suffix(".tmp.tif")
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK="YES"), \
            rasterio.open(src_path) as src:
        profile = {
            "driver": "GTiff", "width": src.width, "height": src.height,
            "count": 3, "dtype": "uint8", "crs": src.crs,
            "transform": src.transform, "tiled": True, "blockxsize": 512,
            "blockysize": 512, "compress": "deflate", "BIGTIFF": "YES",
            "photometric": "RGB",
        }
        n = np.zeros(3)
        s = np.zeros(3)
        ss = np.zeros(3)
        lo = np.full(3, 255.0)
        hi = np.zeros(3)
        valid_count = 0
        with rasterio.open(tmp, "w", **profile) as out:
            step = 2048
            for row in range(0, src.height, step):
                h = min(step, src.height - row)
                win = Window(0, row, src.width, h)
                rgb = src.read([1, 2, 3], window=win)
                if mask_from_zero:
                    valid = np.any(rgb != 0, axis=0)
                else:
                    valid = src.dataset_mask(window=win) > 0
                out.write(rgb, window=win)
                out.write_mask((valid * 255).astype("uint8"), window=win)
                if valid.any():
                    vals = rgb[:, valid].astype("float64")
                    n += vals.shape[1]
                    s += vals.sum(axis=1)
                    ss += (vals * vals).sum(axis=1)
                    lo = np.minimum(lo, vals.min(axis=1))
                    hi = np.maximum(hi, vals.max(axis=1))
                    valid_count += int(valid.sum())
            total = src.width * src.height
            out.colorinterp = [ColorInterp.red, ColorInterp.green,
                               ColorInterp.blue]
            for b in range(3):
                mean = s[b] / n[b]
                std = float(np.sqrt(max(ss[b] / n[b] - mean * mean, 0.0)))
                out.update_tags(b + 1, **{
                    "STATISTICS_MINIMUM": repr(float(lo[b])),
                    "STATISTICS_MAXIMUM": repr(float(hi[b])),
                    "STATISTICS_MEAN": repr(float(mean)),
                    "STATISTICS_STDDEV": repr(std),
                    "STATISTICS_VALID_PERCENT":
                        repr(100.0 * valid_count / total),
                })
    with rasterio.Env(GDAL_NUM_THREADS="ALL_CPUS"):
        rio_copy(tmp, dst, driver="COG", COMPRESS="JPEG",
                 QUALITY=str(quality), BLOCKSIZE="512",
                 OVERVIEW_RESAMPLING="AVERAGE", STATISTICS="AUTO",
                 BIGTIFF="IF_NEEDED", NUM_THREADS="ALL_CPUS")
    tmp.unlink()
    dst.with_suffix(".tif.aux.xml").unlink(missing_ok=True)


# --- items -------------------------------------------------------------

PASSTHROUGH = "copia byte a byte de la descarga de GeoNode"
REENCODED = ("recodificado una vez como COG JPEG, con la calidad JPEG que "
             "declara el original (75 cuando el original no la declara)")


def build_tile(record: dict[str, Any], force: bool = False,
               metadata_only: bool = False) -> dict:
    """Download, conform and describe one tile. Returns the Item.

    ``metadata_only`` rewrites the Item and thumbnail from the COG already
    on disk, without downloading or re-encoding.
    """
    iid = item_id(record)
    out_dir = COLLECTION_DIR / iid
    cog = out_dir / f"{iid}.tif"
    item_path = out_dir / f"{iid}.json"
    if item_path.exists() and cog.exists() and not (force or metadata_only):
        item = json.loads(item_path.read_text())
        if (item["properties"].get("pergamino:source_updated")
                == record.get("last_updated")):
            return item
    t0 = time.time()
    raw, method = download(record)
    out_dir.mkdir(parents=True, exist_ok=True)
    reasons = [] if method == "wcs" else compliance(raw)
    if metadata_only and cog.exists():
        encoding = PASSTHROUGH if (method == "dataset_download"
                                   and not reasons) else REENCODED
    elif method == "dataset_download" and not reasons:
        shutil.copyfile(raw, cog)
        encoding = PASSTHROUGH
    else:
        quality = (source_quality(raw) if method == "dataset_download"
                   else None) or JPEG_QUALITY
        recog(raw, cog, mask_from_zero=(method == "wcs"), quality=quality)
        encoding = REENCODED
    left = compliance(cog)
    if left:
        raise RuntimeError(f"{iid}: output still fails: {left}")
    common.jpeg_thumbnail(cog, out_dir / "thumbnail.jpg", max_side=384)
    item = item_json(record, cog, raw, method, reasons, encoding)
    common.write_json(item_path, item)
    print(f"{iid}: {method}, {encoding}, {time.time() - t0:.0f}s",
          flush=True)
    return item


def item_json(record, cog: Path, raw: Path, method: str, reasons: list[str],
              encoding: str) -> dict[str, Any]:
    iid = item_id(record)
    geom = common.footprint(cog)
    stats = common.embedded_stats(cog)
    bands = [
        {"name": name, "data_type": "uint8", "statistics": s}
        for name, s in zip(("red", "green", "blue"), stats)
    ]
    quoted = " ".join(
        t for t in (
            record.get("raw_abstract"),
            record.get("raw_data_quality_statement"),
            record.get("raw_supplemental_information")
            if area_of(record) else None,
        ) if t
    )
    if method == "wcs":
        origin = (
            "GeoNode rechaza la descarga directa de este mosaico por su "
            "tamaño; se armó desde el WCS 2.0.1 de GeoServer en piezas "
            "alineadas a la grilla nativa"
        )
    else:
        origin = "Descargado de GeoNode (dataset_download)"
    assets: dict[str, Any] = {
        "data": {
            "href": f"./{iid}.tif",
            "type": common.COG_TYPE,
            "title": "Ortofoto RGB de 8 bits (COG)",
            "description": (
                f"{origin}; {encoding}. RGB de 8 bits en EPSG:4326, JPEG "
                "YCbCr, teselas de 512 px, overviews internas, máscara "
                "interna para el área sin imagen y estadísticas por banda "
                "embebidas en la cabecera."
            ),
            "roles": ["data", "visual"],
            "bands": bands,
            **common.file_fields(cog),
        },
        "thumbnail": {
            "href": "./thumbnail.jpg",
            "type": "image/jpeg",
            "title": "Vista previa",
            "description": "JPEG del mosaico reducido; blanco fuera de la "
                           "máscara.",
            "roles": ["thumbnail"],
            **common.file_fields(cog.parent / "thumbnail.jpg"),
        },
    }
    if method == "dataset_download":
        # The size and checksum are those of the bytes this href returned
        # when the tile was fetched. The refresh re-fetches the tile when
        # GeoNode's last_updated moves, which keeps them current.
        assets["source"] = {
            "href": download_url(record),
            "type": "image/tiff; application=geotiff",
            "title": "Original en GeoNode (GeoTIFF)",
            "description": "Descarga del mosaico original desde GeoNode.",
            "roles": ["source"],
            **common.file_fields(raw),
        }
    props = {
        "title": title_of(record),
        "description": quoted,
        "datetime": None,
        "start_datetime": START,
        "end_datetime": END,
        **common.proj_fields(cog),
        "pergamino:geonode_pk": int(record["pk"]),
        "pergamino:geonode_uuid": record["uuid"],
        "pergamino:geonode_alternate": record["alternate"],
        "pergamino:geonode_title": record["title"],
        "pergamino:source_updated": record.get("last_updated"),
        "pergamino:source_method": method,
        "pergamino:jpeg_quality": source_quality(cog),
        "pergamino:attribution": record.get("attribution"),
    }
    if reasons:
        props["pergamino:reencoded_because"] = reasons
    return {
        "type": "Feature",
        "stac_version": "1.1.0",
        "stac_extensions": [common.EXT_FILE, common.EXT_PROJ],
        "id": iid,
        "collection": COLLECTION_ID,
        **common.geometry_fields(geom),
        "properties": props,
        "assets": assets,
        "links": [
            {"rel": "root", "href": "../../../catalog.json",
             "type": "application/json"},
            {"rel": "parent", "href": "../collection.json",
             "type": "application/json"},
            {"rel": "collection", "href": "../collection.json",
             "type": "application/json"},
            {"rel": "via", "href": dataset_page(record), "type": "text/html",
             "title": f"GeoNode: {record['title']}"},
            {"rel": "license", "href": LICENSE_URL, "type": "text/html",
             "title": "CC BY-SA 4.0"},
        ],
    }


# --- overview and collection -------------------------------------------

def tile_href(item: dict[str, Any]) -> str:
    """A GDAL path for an item's COG: local when present, else public."""
    local = COLLECTION_DIR / item["id"] / f"{item['id']}.tif"
    if local.exists():
        return str(local)
    return f"/vsicurl/{PUBLIC}/{item['id']}/{item['id']}.tif"


def build_overview(items: list[dict[str, Any]]) -> Path:
    """8-bit RGB overview of every tile in EPSG:3857 at 1 m.

    gdalwarp reads each tile's internal overviews and honours its mask; the
    alpha band it writes becomes the COG's internal mask. Areas with no tile
    are left unwritten (sparse), so the file stays small.
    """
    out = COLLECTION_DIR / OVERVIEW_FILE
    work = Path(tempfile.mkdtemp(prefix="overview_", dir=RAW.parent))
    warped = work / "warped.tif"
    srcs = [tile_href(i) for i in sorted(items, key=lambda i: i["id"])]
    common.run([
        "gdalwarp", "-q", "-overwrite", "-t_srs", "EPSG:3857",
        "-tr", str(OVERVIEW_RES), str(OVERVIEW_RES), "-tap",
        "-r", "average", "-dstalpha", "-multi", "-wo", "NUM_THREADS=ALL_CPUS",
        "-wo", "SKIP_NOSOURCE=YES", "-co", "TILED=YES",
        "-co", "COMPRESS=DEFLATE", "-co", "SPARSE_OK=TRUE",
        "-co", "BIGTIFF=YES", *srcs, str(warped),
    ])
    common.run([
        "gdal_translate", "-q", "-of", "COG", "-b", "1", "-b", "2",
        "-b", "3", "-mask", "4", "-co", "COMPRESS=JPEG",
        "-co", "QUALITY=80", "-co", "BLOCKSIZE=512",
        "-co", "SPARSE_OK=TRUE", "-co", "STATISTICS=YES",
        "-co", "OVERVIEW_RESAMPLING=AVERAGE", "-co", "BIGTIFF=IF_SAFER",
        "-co", "NUM_THREADS=ALL_CPUS", str(warped), str(out),
    ])
    shutil.rmtree(work)
    out.with_suffix(".tif.aux.xml").unlink(missing_ok=True)
    return out


def collection_thumbnail(items: list[dict[str, Any]]) -> Path:
    """The overview cropped to the city tiles, as a 768 px JPEG."""
    import numpy as np
    import rasterio
    from PIL import Image
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    city = [i for i in items if i["id"].startswith(CITY_PREFIXES)] or items
    box = common.union_bbox(city)
    out = COLLECTION_DIR / "thumbnail.jpg"
    with rasterio.open(COLLECTION_DIR / OVERVIEW_FILE) as src:
        merc = transform_bounds("EPSG:4326", src.crs, *box)
        win = from_bounds(*merc, transform=src.transform)
        scale = max(win.width, win.height) / 768
        shape = (int(win.height / scale), int(win.width / scale))
        rgb = src.read([1, 2, 3], window=win, out_shape=(3, *shape),
                       boundless=True, fill_value=0)
        mask = src.dataset_mask(window=win, out_shape=shape, boundless=True)
    rgb = np.where(mask[None] > 0, rgb, 255).astype("uint8")
    Image.fromarray(np.moveaxis(rgb, 0, -1)).save(out, "JPEG", quality=82,
                                                  optimize=True)
    return out


def update_collection(overview: bool = True) -> dict[str, Any]:
    """Rebuild collection.json, items.parquet, the overview and thumbnail."""
    items = common.load_items(COLLECTION_DIR)
    path = COLLECTION_DIR / "collection.json"
    doc = json.loads(path.read_text())
    if overview and items:
        build_overview(items)
        collection_thumbnail(items)
    if items:
        mirror = COLLECTION_DIR / "items.parquet"
        common.write_item_mirror(items, mirror)
        doc["assets"]["items"].update(common.file_fields(mirror))
        doc["extent"]["spatial"]["bbox"] = [common.union_bbox(items)]
    for key, name in (("overview", OVERVIEW_FILE),
                      ("thumbnail", "thumbnail.jpg")):
        local = COLLECTION_DIR / name
        if local.exists():
            doc["assets"][key].update(common.file_fields(local))
    ov = COLLECTION_DIR / OVERVIEW_FILE
    if ov.exists():
        doc["assets"]["overview"]["bands"] = [
            {"name": n, "data_type": "uint8", "statistics": s}
            for n, s in zip(("red", "green", "blue"),
                            common.embedded_stats(ov))
        ]
        doc["assets"]["overview"].update(common.proj_fields(ov))
    keep = [ln for ln in doc["links"] if ln["rel"] != "item"]
    doc["links"] = keep[:2] + common.item_links(COLLECTION_DIR, items) \
        + keep[2:]
    doc["updated"] = common.utc_now()
    common.write_json(path, doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--only", action="append", default=[],
                        help="item id to build; repeatable")
    parser.add_argument("--force", action="store_true",
                        help="rebuild tiles even when unchanged upstream")
    parser.add_argument("--metadata-only", action="store_true",
                        help="rewrite Items from the COGs on disk")
    parser.add_argument("--overview-only", action="store_true",
                        help="only rebuild the collection-level files")
    parser.add_argument("--no-overview", action="store_true",
                        help="skip the overview and collection thumbnail")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args(argv)

    if not args.overview_only:
        records = [r for r in fetch_raster_records() if is_ortho(r)]
        if args.only:
            records = [r for r in records if item_id(r) in args.only]
        failed = []

        def one(record):
            try:
                build_tile(record, force=args.force,
                           metadata_only=args.metadata_only)
            except Exception as exc:  # noqa: BLE001 - report, keep going
                print(f"{item_id(record)}: FAILED {exc}", flush=True)
                failed.append(item_id(record))

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(one, records))
        if failed:
            print("failed: " + ", ".join(failed), file=sys.stderr)
            update_collection(overview=False)
            return 1
    update_collection(overview=not args.no_overview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
