"""Frame a collection's bbox into a 3:2 window and build a render-ready style.

Two things here are load-bearing.

The source must declare `minzoom` and `maxzoom`. Without them MapLibre assumes
the source reaches zoom 22, requests a tile the archive does not contain, and
draws nothing — which is what produces an all-basemap thumbnail.

A white background layer sits beneath the basemap. A failed basemap fetch then
leaves white rather than transparent, and transparent becomes black in JPEG.
"""

import json
import math
import os
import sys

TARGET_ASPECT = 1.5     # 3:2, matching the browser card
MARGIN = 0.05
MAX_CONTEXT = 2.5       # never pad the short axis beyond this multiple of the data
MIN_SPAN_DEG = 0.009    # ~1 km floor, for single points and straight lines


def frame(bbox):
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = max(x1 - x0, 1e-12), max(y1 - y0, 1e-12)

    # degenerate axes get a floor before anything else
    w = max(w, MIN_SPAN_DEG)
    h = max(h, MIN_SPAN_DEG)
    dw, dh = w, h

    w *= (1 + 2 * MARGIN)
    h *= (1 + 2 * MARGIN)

    # work in projected proportions so the frame looks 3:2 on screen
    ky = math.cos(math.radians(cy)) or 1e-6
    aspect = (w * ky) / h
    if aspect < TARGET_ASPECT:
        need = (TARGET_ASPECT * h) / ky
        w = min(need, dw * MAX_CONTEXT * (1 + 2 * MARGIN))
    else:
        need = (w * ky) / TARGET_ASPECT
        h = min(need, dh * MAX_CONTEXT * (1 + 2 * MARGIN))

    nx0, nx1 = cx - w / 2, cx + w / 2
    ny0, ny1 = cy - h / 2, cy + h / 2

    # clamp into the world by shifting, never squashing
    if ny0 < -85.0:
        ny1 += -85.0 - ny0
        ny0 = -85.0
    if ny1 > 85.0:
        ny0 -= ny1 - 85.0
        ny1 = 85.0

    fill = (dw * dh) / max((nx1 - nx0) * (ny1 - ny0), 1e-12)
    return [nx0, ny0, nx1, ny1], fill, (w * ky) / h


def build_style(style, pmtiles_abs, minz, maxz, basemap_url, opacity, use_basemap):
    sources, layers = {}, []
    layers.append({"id": "bg", "type": "background",
                   "paint": {"background-color": "#ffffff"}})
    if use_basemap:
        sources["basemap"] = {"type": "raster", "tiles": [basemap_url],
                              "tileSize": 256}
        layers.append({"id": "basemap", "type": "raster", "source": "basemap",
                       "paint": {"raster-opacity": opacity}})

    keys = list((style.get("sources") or {}).keys()) or ["data"]
    for k in keys:
        old = (style.get("sources") or {}).get(k, {})
        sources[k] = {
            "type": old.get("type", "vector"),
            "tiles": [f"pmtiles://{pmtiles_abs}/{{z}}/{{x}}/{{y}}"],
            "minzoom": minz,
            "maxzoom": maxz,
        }
    # Symbol layers are dropped from the render style only. MapLibre GL Native
    # fails on them here ("unknown pbf field type") even with a glyphs endpoint
    # declared, and labels are illegible at 350x230 card size regardless. They
    # stay in styles/default.json, where a browser renders them fine.
    layers.extend(l for l in style.get("layers", []) if l.get("type") != "symbol")
    out = {k: v for k, v in style.items() if k != "glyphs"}
    out["sources"] = sources
    out["layers"] = layers
    return out


def main():
    coll = sys.argv[1]
    outdir = sys.argv[2]
    use_basemap = (os.environ.get("USE_BASEMAP", "true") == "true")
    # Carto's light basemap now answers every request with an "API KEY
    # REQUIRED" placeholder tile, so the default is Esri's light grey canvas.
    basemap = os.environ.get(
        "BASEMAP_URL",
        "https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/"
        "World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}")
    opacity = float(os.environ.get("BASEMAP_OPACITY", "0.55"))

    c = json.load(open(os.path.join(coll, "collection.json"), encoding="utf-8"))
    bbox = c["extent"]["spatial"]["bbox"][0]
    # FRAME_BBOX="xmin,ymin,xmax,ymax" frames a dense window instead of the
    # whole extent, for a layer whose features vanish at the partido scale.
    if os.environ.get("FRAME_BBOX"):
        bbox = [float(v) for v in os.environ["FRAME_BBOX"].split(",")]
    fb, fill, aspect = frame(bbox)

    pm = [f for f in os.listdir(coll) if f.endswith(".pmtiles")]
    if not pm:
        print("NO_PMTILES")
        return 1
    pm_abs = os.path.abspath(os.path.join(coll, pm[0]))

    maxz = int(os.environ.get("MAXZ", "15"))
    style = json.load(open(os.path.join(coll, "styles", "default.json"),
                           encoding="utf-8"))

    os.makedirs(outdir, exist_ok=True)
    full = build_style(style, pm_abs, 0, maxz, basemap, opacity, use_basemap)
    probe = build_style(style, pm_abs, 0, maxz, basemap, opacity, False)
    blank = {"version": 8, "sources": {}, "layers": [
        {"id": "bg", "type": "background",
         "paint": {"background-color": "#ffffff"}}]}

    for name, obj in (("full", full), ("probe", probe), ("blank", blank)):
        json.dump(obj, open(os.path.join(outdir, f"{name}.json"), "w"))

    print(json.dumps({"bbox": ",".join(f"{v:.6f}" for v in fb),
                      "fill": round(fill, 4),
                      "aspect": round(aspect, 3)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
