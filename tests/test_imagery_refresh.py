#!/usr/bin/env python3
"""The imagery refresh decides correctly what is due. Offline.

Covers the decision logic of tools/imagery/refresh.py: which quarter of
Sentinel-2 is due and when, which orthophoto tiles changed upstream, and
the statuses refresh() reports in a dry run. GeoNode is replaced by canned
records, so no network is touched and no raster is built.

Run: python3 tests/test_imagery_refresh.py
"""
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "imagery"))

import ortofotos  # noqa: E402
import refresh  # noqa: E402
from s2_quarterly import Quarter, latest_quarter, quarters_between  # noqa: E402

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def at(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=timezone.utc)


# --- quarters ----------------------------------------------------------
q = Quarter.parse("2024Q3")
check((q.start.isoformat(), q.end.isoformat()) == ("2024-07-01", "2024-09-30"),
      f"2024Q3 spans {q.start}..{q.end}")
check(q.item_id == "2024q3", f"item id {q.item_id}")
check(Quarter.parse("2024q4").next() == Quarter(2025, 1), "Q4 rolls over")
check(Quarter.parse("2024Q1").end.isoformat() == "2024-03-31", "Q1 end")
try:
    Quarter.parse("2024Q5")
    errors.append("2024Q5 parsed")
except ValueError:
    pass

# A quarter is due once it ended at least 14 days ago.
check(latest_quarter(at("2026-11-20")) == Quarter(2026, 3),
      "on 2026-11-20 the latest due quarter is 2026Q3")
check(latest_quarter(at("2026-10-14")) == Quarter(2026, 2),
      "13 days after 2026Q3 ends it is not yet due")
check(latest_quarter(at("2026-10-15")) == Quarter(2026, 3),
      "14 days after 2026Q3 ends it is due")
check(latest_quarter(at("2027-01-10")) == Quarter(2026, 3),
      "early January still waits for Q4")
check(latest_quarter(at("2027-01-15")) == Quarter(2026, 4),
      "mid January takes Q4 of the previous year")
span = quarters_between(Quarter(2017, 1), Quarter(2026, 3))
check(len(span) == 39 and span[0].label == "2017Q1"
      and span[-1].label == "2026Q3", "2017Q1..2026Q3 is 39 quarters")

# --- Sentinel-2 plan ---------------------------------------------------
now = at("2026-11-20")
check(refresh.s2_plan(now, {"2026q2"}) == Quarter(2026, 3),
      "a missing newest quarter is due")
check(refresh.s2_plan(now, {"2026q3"}) is None,
      "a present newest quarter is not due")
check(refresh.s2_plan(now, set(), excluded={"2026Q3"}) is None,
      "an excluded quarter is not retried")

# --- orthophoto plan ---------------------------------------------------
ABSTRACT = ("Vuelos fotogramétricos del año 2022 realizados con VANT a pedido "
            "de la Municipalidad de Pergamino.")


def record(pk, name, updated, subtype="raster", abstract=ABSTRACT):
    return {
        "pk": str(pk), "uuid": f"uuid-{pk}", "name": name,
        "alternate": f"geonode:{name}", "title": f"{name}_2022",
        "subtype": subtype, "raw_abstract": abstract,
        "last_updated": updated,
    }


def item(pk, iid, updated):
    return {
        "type": "Feature", "id": iid,
        "properties": {
            "title": iid, "pergamino:geonode_pk": pk,
            "pergamino:source_updated": updated,
        },
    }


records = [
    record(418, "centro_10cm", "2026-07-28T11:27:17.695603Z"),
    record(419, "oeste_1_10cm", "2026-12-01T09:00:00.000000Z"),
    record(500, "nuevo_10cm", "2026-12-02T09:00:00Z"),
    record(438, "open_buildings_height_8m", "2026-08-14T13:23:30Z",
           abstract="Raster de alturas de edificios"),
    record(374, "pinzon_10cm_9eb85c09bda4f8ac207e7e4a0b79c5e7",
           "2026-06-23T14:11:49.354243Z"),
]
items = [
    item(418, "centro_10cm", "2026-07-28T11:27:17.695603Z"),
    item(419, "oeste_1_10cm", "2026-07-28T12:29:35.025398Z"),
    item(374, "pinzon_10cm", "2026-06-23T14:11:49.354243Z"),
    item(399, "sur_4_10cm", "2026-06-29T15:24:59.692538Z"),
]
plan = refresh.ortho_plan(records, items)
check([r["name"] for r in plan["changed"]] == ["oeste_1_10cm"],
      f"changed: {[r['name'] for r in plan['changed']]}")
check([r["name"] for r in plan["new"]] == ["nuevo_10cm"],
      f"new: {[r['name'] for r in plan['new']]}")
check(plan["removed"] == ["sur_4_10cm"], f"removed: {plan['removed']}")

# Equal instants written differently are not a change.
same = refresh.ortho_plan(
    [record(418, "centro_10cm", "2026-07-28T11:27:17.695603+00:00")],
    [item(418, "centro_10cm", "2026-07-28T11:27:17.695603Z")],
)
check(not same["changed"], "an equal timestamp in another notation changed")

check(not ortofotos.is_ortho(records[3]), "open_buildings is not an ortho")
check(ortofotos.is_ortho(records[0]), "centro is an ortho")
check(ortofotos.item_id(records[4]) == "pinzon_10cm", "upload hash stripped")
check(ortofotos.item_id({"name": "rancagua_10cm_cog"}) == "rancagua_10cm",
      "_cog suffix stripped")
check(ortofotos.title_of({"name": "la_violeta_10cm",
                          "raw_supplemental_information":
                              "No information provided"})
      == "Ortofoto 2022: La Violeta", "title falls back to the name")
check(ortofotos.title_of({"name": "centro_10cm",
                          "raw_supplemental_information":
                              "Área cubierta: Barrio Centro"})
      == "Ortofoto 2022: Barrio Centro", "title quotes the covered area")

# --- refresh() in a dry run, against a scratch catalog ----------------
with tempfile.TemporaryDirectory() as tmp:
    cat = Path(tmp)
    ortho_dir = cat / "imagenes" / "ortofotos_10cm_2022"
    s2_dir = cat / "imagenes" / "sentinel2_trimestral"
    for d in (ortho_dir, s2_dir):
        d.mkdir(parents=True)
        (d / "collection.json").write_text(json.dumps({"links": []}))
    for it in items[:3]:
        (ortho_dir / it["id"]).mkdir()
        (ortho_dir / it["id"] / f"{it['id']}.json").write_text(json.dumps(it))
    (s2_dir / "2026q2").mkdir()
    (s2_dir / "2026q2" / "2026q2.json").write_text(json.dumps(
        {"type": "Feature", "id": "2026q2", "properties": {"title": "x"}}))

    saved = ortofotos.fetch_raster_records
    ortofotos.fetch_raster_records = lambda: records
    try:
        out = refresh.refresh(cat, now, dry_run=True)
    finally:
        ortofotos.fetch_raster_records = saved
    o = out.get(refresh.ORTHO_ID, {})
    s = out.get(refresh.S2_ID, {})
    check(o.get("status") == "due", f"ortho dry run: {o}")
    check("oeste_1_10cm" in o.get("detail", "")
          and "nuevo_10cm" in o.get("detail", ""), f"ortho detail: {o}")
    check(s.get("status") == "due" and "2026Q3" in s.get("detail", ""),
          f"s2 dry run: {s}")

    # Up to date: nothing is due.
    (s2_dir / "2026q3").mkdir()
    (s2_dir / "2026q3" / "2026q3.json").write_text(json.dumps(
        {"type": "Feature", "id": "2026q3", "properties": {"title": "x"}}))
    ortofotos.fetch_raster_records = lambda: records[:1] + records[4:]
    for extra in items[1:3]:
        if extra["id"] == "oeste_1_10cm":
            (ortho_dir / "oeste_1_10cm" / "oeste_1_10cm.json").unlink()
            (ortho_dir / "oeste_1_10cm").rmdir()
    try:
        out = refresh.refresh(cat, now, dry_run=True)
    finally:
        ortofotos.fetch_raster_records = saved
    check(out[refresh.ORTHO_ID]["status"] == "ok",
          f"up-to-date ortho: {out[refresh.ORTHO_ID]}")
    check(out[refresh.S2_ID]["status"] == "ok",
          f"up-to-date s2: {out[refresh.S2_ID]}")

    # A failing fetch is reported as an error, not raised.
    def boom():
        raise OSError("GeoNode unreachable")

    ortofotos.fetch_raster_records = boom
    try:
        out = refresh.refresh(cat, now, dry_run=True)
    finally:
        ortofotos.fetch_raster_records = saved
    check(out[refresh.ORTHO_ID]["status"] == "error"
          and "unreachable" in out[refresh.ORTHO_ID]["detail"],
          f"error status: {out[refresh.ORTHO_ID]}")

    # A catalog without the collections skips them.
    out = refresh.refresh(cat / "missing", now, dry_run=True)
    check(all(v["status"] == "skipped" for v in out.values()),
          f"missing collections: {out}")

if errors:
    print("\n".join(f"error  {e}" for e in errors))
    raise SystemExit(1)
print("OK: imagery refresh decisions")
