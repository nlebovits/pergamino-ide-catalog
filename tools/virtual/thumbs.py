#!/usr/bin/env python3
"""Render the preview of every externos collection, from upstream bytes.

    export PATH=<node 24.12+>/bin:$PATH
    CHIITILER_PROCESSES=0 npx chiitiler tile-server --port 13581 &
    python3 tools/virtual/thumbs.py [--only externos/glofas/peligro_rp100]

Each preview is the collection's default styling over a basemap, framed to
the 3:2 card with ``tools/generate/thumbs/frame.py``, with the partido mask
drawn on top. chiitiler (MapLibre GL Native) does the drawing:

- GloFAS: the clip VRT is coloured with GDAL (the render ramp, or the class
  colour hints), warped to EPSG:3857, and drawn as an image source.
- Overture: the clipped GeoParquet, inlined as GeoJSON and drawn with the
  collection's own style layers. Overture's PMTiles thin features out below
  z14, so tiles at a thumbnail's zoom would misrepresent the data.

An image is kept only when a 256 px probe of the data layers on white differs
from a blank white render; the same gate as tools/generate/thumbs/render.sh.
Then the thumbnail asset, with file:size and file:checksum, is written into
collection.json.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "generate" / "thumbs"))

import common as C  # noqa: E402
import glofas as G  # noqa: E402
import overture as O  # noqa: E402
from frame import frame  # noqa: E402

CHIITILER = os.environ.get("CHIITILER_URL", "http://localhost:13581")
# Carto's light tiles now answer 200 with an "API KEY REQUIRED" image, so the
# basemap is Esri's light gray canvas, the first working candidate of the
# portolan-thumbnails skill (pick_basemap.sh).
BASEMAP = ("https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/"
           "World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}")
SIZE = 1024
QUALITY = 85

VIRIDIS = [(0.0, (68, 1, 84)), (0.25, (59, 82, 139)), (0.5, (33, 145, 140)),
           (0.75, (94, 201, 98)), (1.0, (253, 231, 37))]


def post_clip(style: dict, bbox: list[float], size: int, out: Path,
              fmt: str = "jpeg") -> None:
    query = (f"bbox={','.join(f'{v:.6f}' for v in bbox)}&size={size}"
             f"&quality={QUALITY}")
    req = urllib.request.Request(
        f"{CHIITILER}/clip.{fmt}?{query}", method="POST",
        data=json.dumps({"style": style}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        out.write_bytes(resp.read())


def base_layers(with_basemap: bool) -> tuple[dict, list[dict]]:
    sources, layers = {}, [{"id": "bg", "type": "background",
                            "paint": {"background-color": "#ffffff"}}]
    if with_basemap:
        sources["basemap"] = {"type": "raster", "tiles": [BASEMAP],
                              "tileSize": 256}
        layers.append({"id": "basemap", "type": "raster",
                       "source": "basemap",
                       "paint": {"raster-opacity": 0.55}})
    return sources, layers


# --- rasters -----------------------------------------------------------------


def color_table(doc: dict) -> tuple[list[str], bool]:
    """gdaldem color-relief lines, and whether values are exact classes."""
    data = doc["assets"]["data"]
    lines = ["nv 0 0 0 0"]
    classes = data.get("classification:classes")
    if classes:
        for cls in classes:
            h = cls["color_hint"]
            r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
            lines.append(f"{cls['value']} {r} {g} {b} 255")
        return lines, True
    render = next(iter(doc["renders"].values()))
    lo, hi = render["rescale"][0]
    for t, (r, g, b) in VIRIDIS:
        lines.append(f"{lo + t * (hi - lo):.4f} {r} {g} {b} 255")
    return lines, False


def raster_image(doc: dict, folder: Path, work: Path) -> tuple[Path, list]:
    """Colour the clip VRT and warp it to EPSG:3857. (png, corners)."""
    vrt = folder / doc["assets"]["recorte"]["href"].removeprefix("./")
    lines, exact = color_table(doc)
    table = work / "colors.txt"
    table.write_text("\n".join(lines) + "\n")
    rgba = work / "rgba.tif"
    cmd = ["gdaldem", "color-relief", "-q", "-alpha"]
    if exact:
        cmd.append("-exact_color_entry")
    env = {**os.environ, **G.GDAL_ENV}
    subprocess.run(cmd + [str(vrt), str(table), str(rgba)], check=True,
                   env=env)
    merc = work / "merc.tif"
    subprocess.run(["gdalwarp", "-q", "-overwrite", "-t_srs", "EPSG:3857",
                    "-r", "near", str(rgba), str(merc)], check=True, env=env)
    png = work / "raster.png"
    subprocess.run(["gdal_translate", "-q", "-of", "PNG", str(merc),
                    str(png)], check=True, env=env)
    info = json.loads(subprocess.run(
        ["gdalinfo", "-json", str(merc)], check=True, capture_output=True,
        text=True, env=env).stdout)
    corners = info["wgs84Extent"]["coordinates"][0]
    lons = [c[0] for c in corners]
    lats = [c[1] for c in corners]
    w, e, s, n = min(lons), max(lons), min(lats), max(lats)
    return png, [[w, n], [e, n], [e, s], [w, s]]


def raster_style(doc: dict, folder: Path, work: Path,
                 with_basemap: bool) -> dict:
    png, corners = raster_image(doc, folder, work)
    mask = json.loads((folder / "styles" / "default.json").read_text())
    sources, layers = base_layers(with_basemap)
    sources["raster"] = {"type": "image", "url": f"file://{png}",
                         "coordinates": corners}
    layers.append({"id": "raster", "type": "raster", "source": "raster",
                   "paint": {"raster-resampling": "nearest"}})
    sources.update(mask["sources"])
    layers.extend(mask["layers"])
    return {"version": 8, "sources": sources, "layers": layers}


# --- vectors -----------------------------------------------------------------


def style_fields(layers: list[dict]) -> list[str]:
    """Attribute names a style reads with ["get", name]."""
    found: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, list):
            if len(node) == 2 and node[0] == "get" and \
                    isinstance(node[1], str):
                found.add(node[1])
            for child in node:
                walk(child)
        elif isinstance(node, dict):
            for child in node.values():
                walk(child)

    walk(layers)
    return sorted(found)


def clipped_geojson(doc: dict, partido: C.Partido, fields: list[str],
                    tolerance: float) -> dict:
    """The clip as a FeatureCollection, with the fields the style reads.

    Geometry is simplified below a quarter of a thumbnail pixel, which keeps
    the request small without changing what is drawn.
    """
    import duckdb

    folder = C.CATALOG / doc["id"]
    parts = O.stored_parts(doc, folder)
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
    con.execute("CREATE TEMP TABLE p AS SELECT ST_GeomFromHEXWKB(?) AS g",
                [partido.wkb_hex])
    cols = "".join(f", o.{f}" for f in fields)
    # Simplifying collapses short features to EMPTY. One empty geometry makes
    # MapLibre Native drop the whole GeoJSON source, so they are filtered.
    rows = con.execute(
        f"""
        SELECT ST_AsGeoJSON(g){cols.replace('o.', '')}
        FROM (
            SELECT ST_ReducePrecision(
                       ST_SimplifyPreserveTopology(o.geometry, {tolerance}),
                       0.00001) AS g{cols}
            FROM read_parquet({O.parquet_list(parts)},
                              hive_partitioning = false) AS o, p
            WHERE {O.bbox_predicate(partido.bbox)}
              AND ST_Intersects(o.geometry, p.g)
        )
        WHERE NOT ST_IsEmpty(g)
        """
    ).fetchall()
    features = []
    for row in rows:
        if row[0] is None:
            continue
        props = {f: v for f, v in zip(fields, row[1:]) if v is not None}
        features.append({"type": "Feature", "properties": props,
                         "geometry": json.loads(row[0])})
    return {"type": "FeatureCollection", "features": features}


def vector_style(doc: dict, folder: Path, partido: C.Partido,
                 bbox: list[float], with_basemap: bool) -> dict:
    """The collection's style, drawn from the clip itself.

    Overture's PMTiles thin features out below z14 (places and addresses
    start at z14; buildings are sparse at z13), so tiles at a thumbnail's
    zoom misrepresent the data. The clipped GeoParquet, inlined as GeoJSON
    under the style's own layers, shows every feature.
    """
    style = json.loads((folder / "styles" / "default.json").read_text())
    data_layers = []
    for ly in style["layers"]:
        if ly.get("source") != "data" or ly.get("type") == "symbol":
            continue
        if ly.get("type") == "line" and "Polygon" in json.dumps(
                ly.get("filter", [])):
            # Polygon outlines (white on buildings) cover polygons smaller
            # than a pixel at thumbnail scale and erase them.
            continue
        ly = copy.deepcopy(ly)
        ly.pop("source-layer", None)
        data_layers.append(ly)
    tolerance = (bbox[2] - bbox[0]) / SIZE / 4
    sources, layers = base_layers(with_basemap)
    # tolerance 0: the source's default simplification drops polygons
    # smaller than a pixel, which at this scale is every building.
    sources["data"] = {"type": "geojson", "tolerance": 0,
                       "data": clipped_geojson(
                           doc, partido, style_fields(data_layers),
                           tolerance)}
    layers.extend(data_layers)
    for name in ("mascara", "partido"):
        sources[name] = style["sources"][name]
    layers.extend(ly for ly in style["layers"]
                  if ly.get("source") in ("mascara", "partido"))
    return {"version": 8, "sources": sources, "layers": layers}


def probe_style(style: dict) -> dict:
    """The data layers alone on white: what the blank gate compares."""
    keep = {"bg", "raster"} | {ly["id"] for ly in style["layers"]
                               if ly.get("source") == "data"}
    return {"version": 8,
            "sources": {k: v for k, v in style["sources"].items()
                        if k in ("data", "raster")},
            "layers": [ly for ly in style["layers"] if ly["id"] in keep]}


BLANK = {"version": 8, "sources": {}, "layers": [
    {"id": "bg", "type": "background",
     "paint": {"background-color": "#ffffff"}}]}


def render(doc: dict, partido: C.Partido) -> str:
    folder = C.CATALOG / doc["id"]
    name = doc["id"].rsplit("/", 1)[-1]
    fb, _, _ = frame(doc["extent"]["spatial"]["bbox"][0])
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        if doc["id"].startswith(f"{C.GROUP}/glofas/"):
            full = raster_style(doc, folder, work, True)
        else:
            full = vector_style(doc, folder, partido, fb, True)
        post_clip(probe_style(full), fb, 256, work / "probe.png", "png")
        post_clip(BLANK, fb, 256, work / "blank.png", "png")
        same = (hashlib.sha256((work / "probe.png").read_bytes()).digest()
                == hashlib.sha256((work / "blank.png").read_bytes())
                .digest())
        if same:
            return "FAIL-empty"
        out = folder / f"{name}.thumb.jpg"
        post_clip(full, fb, SIZE, out)

    module = G if doc["id"].startswith(f"{C.GROUP}/glofas/") else O
    path = folder / "collection.json"
    current = json.loads(path.read_text())
    current["assets"]["thumbnail"] = module.thumbnail_asset(out)
    C.write_json(path, C.keep_updated(path, current, None))
    return f"ok {out.stat().st_size} bytes"


def collections(only: list[str] | None) -> list[dict]:
    out = []
    for path in sorted((C.CATALOG / C.GROUP).rglob("collection.json")):
        doc = json.loads(path.read_text())
        if not only or any(doc["id"] == o or doc["id"].startswith(o + "/")
                           for o in only):
            out.append(doc)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args(argv)
    partido = C.load_partido()
    failed = 0
    for doc in collections(args.only):
        try:
            status = render(doc, partido)
        except Exception as exc:  # noqa: BLE001 - report and continue
            status = f"FAIL {type(exc).__name__}: {exc}"
        failed += status.startswith("FAIL")
        print(f"{doc['id']}\t{status}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
