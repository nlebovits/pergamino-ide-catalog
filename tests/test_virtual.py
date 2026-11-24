#!/usr/bin/env python3
"""The virtual collections still point at something, and their clips work.

Every virtual collection (one with ``pergamino:virtual``, in its thematic
group) references bytes another catalog hosts. Nothing local breaks when those move, so this gate asks the network:

- every absolute https href in an asset or a link answers 2xx (HEAD, with a
  one-byte ranged GET where a server refuses HEAD);
- every GloFAS clip VRT opens with gdalinfo, and its window is the partido:
  the raster size matches the collection extent divided by the pixel size,
  and the `proj:shape` the collection records.

An href fails when its server gives a definite answer that is not 2xx: a 404,
a 410, any other 4xx, or a redirect that ends nowhere. An href whose host does
not answer (a timeout, a DNS failure, a refused or reset connection, a TLS
failure) or answers 5xx is a third-party outage, not a broken link: it prints
a WARNING with the URL and the error and does not fail the gate. With
VIRTUAL_STRICT=1 an outage fails too. The weekly refresh workflow runs this
gate that way, so an outage that lasts is still reported.

It needs the network and, for the VRTs, the GDAL command-line tools. With
VIRTUAL_CHECK_REMOTE=0, or when data.source.coop does not resolve, it SKIPs.

Run: python3 tests/test_virtual.py
     VIRTUAL_STRICT=1 python3 tests/test_virtual.py
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

from virtual.common import (  # noqa: E402
    is_glofas, probe_detail, virtual_collections,
)

# A window can differ from extent / pixel size by the pixels GDAL adds when it
# snaps the cutline's bounds outward to the source grid.
PIXEL_SLACK = 2

OK, UNREACHABLE, BROKEN = "ok", "unreachable", "broken"


def classify(code: int) -> str:
    """What a probe status means for the gate.

    0 is no answer at all; 5xx is a server that cannot answer right now. Both
    are outages. Every other non-2xx is the server saying the link is wrong.
    """
    if 200 <= code < 300:
        return OK
    if code == 0 or code >= 500:
        return UNREACHABLE
    return BROKEN


def check_hrefs(hrefs: dict[str, str], strict: bool,
                probe=probe_detail) -> tuple[list[str], list[str], int]:
    """Probe every href. Returns (errors, warnings, how many answered 2xx).

    ``hrefs`` maps each URL to where it was found. ``probe`` returns
    ``(status, error)``, like ``virtual.common.probe_detail``.
    """
    with ThreadPoolExecutor(max_workers=16) as pool:
        results = dict(zip(hrefs, pool.map(probe, hrefs)))
    errors: list[str] = []
    warnings: list[str] = []
    answered = 0
    for href, (code, why) in sorted(results.items()):
        verdict = classify(code)
        if verdict == OK:
            answered += 1
            continue
        what = f"{hrefs[href]}: {href} answers {code or 'nothing'}"
        if why:
            what += f" ({why})"
        if verdict == UNREACHABLE and not strict:
            warnings.append(what)
        else:
            errors.append(what)
    return errors, warnings, answered


def documents(collections: list[Path]) -> list[Path]:
    """Each virtual collection and its items, not its styles."""
    out = []
    for coll in collections:
        out += [p for p in sorted(coll.parent.rglob("*.json"))
                if "styles" not in p.relative_to(coll.parent).parts]
    return out


def external_hrefs(collections: list[Path]) -> dict[str, str]:
    """Every absolute https href, mapped to the first place it appears."""
    hrefs: dict[str, str] = {}
    for path in documents(collections):
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
    return hrefs


def check_vrts(collections: list[Path], errors: list[str]) -> int:
    """Open every GloFAS clip VRT. Returns how many opened."""
    vrts = 0
    if shutil.which("gdalinfo") is None:
        print("note   gdalinfo is not on PATH; clip VRTs not opened")
        return vrts
    env = {**os.environ, "GDAL_PAM_ENABLED": "NO",
           "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR"}
    for path in collections:
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
    return vrts


def main() -> int:
    if os.environ.get("VIRTUAL_CHECK_REMOTE") == "0":
        print("SKIP: VIRTUAL_CHECK_REMOTE=0; external hrefs not checked.")
        return 0
    collections = virtual_collections(CATALOG)
    if not collections:
        print("SKIP: the catalog has no virtual collection.")
        return 0
    try:
        socket.getaddrinfo("data.source.coop", 443)
    except OSError:
        print("SKIP: no network; external hrefs not checked.")
        return 0

    strict = os.environ.get("VIRTUAL_STRICT") == "1"
    hrefs = external_hrefs(collections)
    errors, warnings, answered = check_hrefs(hrefs, strict)
    for w in warnings:
        print(f"WARNING {w}; the host did not answer, which is an outage "
              "upstream, not a broken link (VIRTUAL_STRICT=1 fails on it)")
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning title=test_virtual.py::{w}")
    vrts = check_vrts(collections, errors)

    if errors:
        print("\n".join(f"error  {e}" for e in errors))
        return 1
    unreachable = f", {len(warnings)} unreachable" if warnings else ""
    print(f"OK: {answered} of {len(hrefs)} external href(s) answer"
          f"{unreachable}, {vrts} clip VRT(s) open on the partido window")
    return 0


if __name__ == "__main__":
    sys.exit(main())
