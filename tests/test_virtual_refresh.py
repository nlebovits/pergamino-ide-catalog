#!/usr/bin/env python3
"""The refresh decisions for the virtual collections, offline.

tools/virtual/refresh.py decides, per collection, whether upstream moved and
a rebuild is due. Those decisions are pure functions over what is stored and
what was resolved, so they are tested here with no network. Also checks that
the clip SQL keeps the bbox prefilter, which is what makes the views cheap,
and that every recipe reads the boundary from the one URL constant.

Run: python3 tests/test_virtual_refresh.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "virtual"))

try:
    import common as C  # noqa: E402
    import overture as O  # noqa: E402
    from refresh import decide_glofas, decide_overture  # noqa: E402
except ImportError as exc:  # a dependency of the builder is missing
    print(f"SKIP: {exc}")
    raise SystemExit(0)

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


OLD = "2026-10-21.0"
NEW = "2026-11-18.0"


def href(release: str, n: str) -> str:
    return (f"https://overturemaps-us-west-2.s3.us-west-2.amazonaws.com/"
            f"release/{release}/theme=buildings/type=building/"
            f"part-{n}-abc-c000.zstd.parquet")


def stored(release: str, parts: list[str]) -> dict:
    return {"release": release, "resolved_via": "overture-stac",
            "hrefs": sorted(href(release, p) for p in parts)}


def resolved(release: str, parts: list[str], via: str) -> dict:
    return {"release": release, "resolved_via": via,
            "parts": [{"id": p, "href": href(release, p)} for p in parts]}


def alive(s: dict, code: int = 200) -> dict:
    return {h: code for h in s["hrefs"]}


# --- Overture --------------------------------------------------------------

s = stored(NEW, ["00066", "00067"])

status, detail, rebuild = decide_overture(
    s, resolved(NEW, ["00066", "00067"], "overture-stac"), None, alive(s),
    dry_run=False)
check((status, rebuild) == ("ok", False), "unchanged release is ok")
check("overture-stac" in detail, "the resolution path is reported")

status, detail, rebuild = decide_overture(
    stored(OLD, ["00066"]), resolved(NEW, ["00066", "00067"],
                                     "overture-stac"),
    None, alive(stored(OLD, ["00066"])), dry_run=True)
check((status, rebuild) == ("due", False), "new release in a dry run: due")
check(OLD in detail and NEW in detail, "both releases named")

status, _, rebuild = decide_overture(
    stored(OLD, ["00066"]), resolved(NEW, ["00066"], "overture-portolan"),
    None, alive(stored(OLD, ["00066"])), dry_run=False)
check((status, rebuild) == ("ok", True), "new release: rebuild")

old = stored(OLD, ["00066"])
status, detail, rebuild = decide_overture(
    old, resolved(OLD, ["00066"], "overture-portolan"), None,
    alive(old, 404), dry_run=True)
check(status == "due" and "do not answer 200" in detail,
      "a dead stored href is due even when the release is unchanged")

status, _, rebuild = decide_overture(
    s, resolved(NEW, ["00066"], "overture-stac"), None, alive(s),
    dry_run=False)
check(rebuild, "a changed part list rebuilds")

status, detail, rebuild = decide_overture(
    s, resolved(OLD, ["00066"], "overture-portolan"), None, alive(s),
    dry_run=False)
check((status, rebuild) == ("ok", False),
      "a lagging mirror never steps a live collection back")
check("kept" in detail, "the lag is reported")

status, _, rebuild = decide_overture(
    s, resolved(OLD, ["00066"], "overture-portolan"), None, alive(s, 404),
    dry_run=False)
check(rebuild, "an older but live release replaces dead hrefs")

status, detail, rebuild = decide_overture(
    s, None, "HTTP 503", alive(s), dry_run=False)
check((status, rebuild) == ("error", False), "unresolvable is an error")
check("503" in detail, "the cause is reported")

# --- GloFAS ----------------------------------------------------------------

COG = "https://data.source.coop/nlebovits/jrc-glofas/a/b.tif"
check(decide_glofas(COG, COG, None, 200, False)[:2] == ("ok", "COG answers 200"),
      "a live COG is ok")
check(decide_glofas(COG, COG, None, 404, False)[0] == "error",
      "a dead COG is an error")
check(decide_glofas(COG, None, "boom", 0, False)[0] == "error",
      "an unresolvable item is an error")
check(decide_glofas(COG, COG + "2", None, 200, True)[0] == "due",
      "a moved COG is due in a dry run")
check(decide_glofas(COG, COG + "2", None, 200, False)[2] is True,
      "a moved COG rebuilds")

# --- part resolution helpers -------------------------------------------------

check(O.part_id(href(NEW, "00066")) == "00066", "part id from a filename")
check(O.release_from_canonical(
    f"https://stac.overturemaps.org/{NEW}/buildings/building/collection.json"
) == NEW, "release from a canonical link")
check(O.single_file(resolved(NEW, ["00004"], "overture-stac")),
      "one part is a single-file collection")
check(not O.single_file(resolved(NEW, ["00066", "00067"], "overture-stac")),
      "two parts are items")
check(O.stored_parts({"assets": {"data": {"href": href(NEW, "00004")}},
                      "links": []}, ROOT) == [href(NEW, "00004")],
      "a collection-level data asset is the stored part")
check(O.intersects([0, 0, 2, 2], [1, 1, 3, 3]), "overlapping boxes meet")
check(not O.intersects([0, 0, 1, 1], [2, 2, 3, 3]), "distant boxes do not")

# --- recipes -----------------------------------------------------------------

sql = O.clip_sql([href(NEW, "00066")], [-61.0, -34.2, -60.1, -33.5])
check("o.bbox.xmin <= -60.1" in sql and "o.bbox.ymax >= -34.2" in sql,
      "the clip keeps the bbox prefilter on the covering column")
check(C.PARTIDO_URL in sql, "the clip reads the boundary URL constant")
check("ST_Intersects" in sql, "the clip tests the real geometry")

config = json.loads((ROOT / "tools" / "virtual" / "sources.json").read_text())
check(config["partido"]["url"] == C.PARTIDO_URL,
      "PARTIDO_URL comes from sources.json")

virtual_files = [p for coll in C.virtual_collections(ROOT / "catalog")
                 for p in sorted(coll.parent.rglob("*.json"))]
check(len(virtual_files) > 0, "the catalog has virtual collections")
for path in virtual_files:
    if "styles" in path.parts:
        continue
    doc = json.loads(path.read_text())
    for key, asset in doc.get("assets", {}).items():
        expr = asset.get("processing:expression", {}).get("expression", "")
        if expr and C.PARTIDO_URL not in expr:
            errors.append(f"{path.relative_to(ROOT)}: asset {key} recipe "
                          "does not read PARTIDO_URL")
        if "external" in asset.get("roles", []):
            if "file:size" in asset or "file:checksum" in asset:
                errors.append(f"{path.relative_to(ROOT)}: external asset "
                              f"{key} carries file:size or file:checksum")

if errors:
    print("\n".join(f"error  {e}" for e in errors))
    raise SystemExit(1)
print("OK: virtual refresh decisions hold")
