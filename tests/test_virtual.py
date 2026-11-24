#!/usr/bin/env python3
"""The virtual collections still point at something, and their clips work.

Every virtual collection (one with ``pergamino:virtual``, in its thematic
group) references bytes another catalog hosts. Nothing local breaks when those move, so this gate asks the network:

- every absolute https href in an asset or a link answers 2xx (HEAD, with a
  one-byte ranged GET where a server refuses HEAD);
- every GloFAS clip VRT opens with gdalinfo, and its window is the partido:
  the raster size matches the collection extent divided by the pixel size,
  and the `proj:shape` the collection records.

It needs the network and, for the VRTs, the GDAL command-line tools. With
VIRTUAL_CHECK_REMOTE=0, or when data.source.coop does not resolve, it SKIPs.

Run: python3 tests/test_virtual.py
"""
import json
import os
import shutil
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
sys.path.insert(0, str(ROOT / "tools"))

from virtual.common import is_glofas, probe, virtual_collections  # noqa: E402

COLLECTIONS = virtual_collections(CATALOG)

# A window can differ from extent / pixel size by the pixels GDAL adds when it
# snaps the cutline's bounds outward to the source grid.
PIXEL_SLACK = 2

if os.environ.get("VIRTUAL_CHECK_REMOTE") == "0":
    print("SKIP: VIRTUAL_CHECK_REMOTE=0; external hrefs not checked.")
    raise SystemExit(0)
if not COLLECTIONS:
    print("SKIP: the catalog has no virtual collection.")
    raise SystemExit(0)
try:
    socket.getaddrinfo("data.source.coop", 443)
except OSError:
    print("SKIP: no network; external hrefs not checked.")
    raise SystemExit(0)

errors: list[str] = []


def documents() -> list[Path]:
    """Each virtual collection and its items, not its styles."""
    out = []
    for coll in COLLECTIONS:
        out += [p for p in sorted(coll.parent.rglob("*.json"))
                if "styles" not in p.relative_to(coll.parent).parts]
    return out


hrefs: dict[str, str] = {}
for path in documents():
    doc = json.loads(path.read_text())
    where = str(path.relative_to(ROOT))
    for link in doc.get("links", []):
        href = link.get("href", "")
        if href.startswith("https://"):
            hrefs.setdefault(href, f"{where} rel:{link.get('rel')}")
    for key, asset in (doc.get("assets") or {}).items():
        href = asset.get("href", "")
        if href.startswith("https://"):
            hrefs.setdefault(href, f"{where} asset:{key}")

with ThreadPoolExecutor(max_workers=16) as pool:
    codes = dict(zip(hrefs, pool.map(probe, hrefs)))
for href, code in sorted(codes.items()):
    if not 200 <= code < 300:
        errors.append(f"{hrefs[href]}: {href} answers {code or 'nothing'}")

vrts = 0
if shutil.which("gdalinfo") is None:
    print("note   gdalinfo is not on PATH; clip VRTs not opened")
else:
    env = {**os.environ, "GDAL_PAM_ENABLED": "NO",
           "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR"}
    for path in COLLECTIONS:
        doc = json.loads(path.read_text())
        if not is_glofas(doc):
            continue
        clip = doc["assets"]["recorte"]
        vrt = path.parent / clip["href"].removeprefix("./")
        proc = subprocess.run(["gdalinfo", "-json", str(vrt)],
                              capture_output=True, text=True, env=env)
        rel = vrt.relative_to(ROOT)
        if proc.returncode != 0:
            errors.append(f"{rel}: gdalinfo failed: {proc.stderr.strip()}")
            continue
        vrts += 1
        info = json.loads(proc.stdout)
        width, height = info["size"]
        gt = info["geoTransform"]
        xmin, ymin, xmax, ymax = doc["extent"]["spatial"]["bbox"][0]
        want_w = (xmax - xmin) / gt[1]
        want_h = (ymax - ymin) / -gt[5]
        if abs(width - want_w) > PIXEL_SLACK or \
                abs(height - want_h) > PIXEL_SLACK:
            errors.append(f"{rel}: window {width}x{height}, partido is "
                          f"{want_w:.1f}x{want_h:.1f} pixels")
        if clip.get("proj:shape") != [height, width]:
            errors.append(f"{rel}: proj:shape {clip.get('proj:shape')} "
                          f"but the VRT is {height}x{width}")

if errors:
    print("\n".join(f"error  {e}" for e in errors))
    raise SystemExit(1)
print(f"OK: {len(codes)} external href(s) answer, {vrts} clip VRT(s) open "
      "on the partido window")
