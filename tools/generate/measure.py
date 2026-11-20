#!/usr/bin/env python3
"""Measure the facts the collection docs state about each dataset.

Every statement a collection's README or AGENTS.md makes about its data is
read from the data here, never written by hand. The result goes to
``tools/generate/data/measured.json``, which is committed, so the docs
regenerate in CI without the data files (``tests/test_regen.py``).

Per collection it records:

- ``geometry``: point, line or polygon, from the GeoParquet metadata
- ``categories``: for each text column with between 2 and 15 distinct
  non-empty values, those values, most frequent first. A column qualifies
  only when its values repeat (at least two rows per value on average), and
  never when its name says it holds a name, a contact, an address or free
  text (``PRIVATE``). The docs print these values, and a short layer can
  carry a person's name or phone in a column that looks categorical.
- ``joins``: for each join key the root guide names, the collections it
  links to, and only when at least one key value matches
- ``in_city``: whether the collection's extent overlaps the city of
  Pergamino, which decides whether a per-barrio query makes sense

    python3 tools/generate/measure.py catalog            # every collection
    python3 tools/generate/measure.py catalog limites/cpa
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATH = HERE / "data" / "measured.json"
sys.path.insert(0, str(HERE.parent))

MAX_CATEGORIES = 15
PRIVATE = re.compile(
    r"tel|fono|celular|mail|contacto|titular|responsable|resp_|encargad|"
    r"delegado|promotor|actualizador|domicilio|direccion|nombre|observ|"
    r"comentario|web|redes|asunto|consulta|detalle|descripcion|dni|cuit",
    re.I)
# The join keys catalog/AGENTS.md documents, and the collection that holds
# the reference list for each one.
JOIN_KEYS = {
    "partida": "catastro/parcela",
    "id_calle": "vialidad/callejero",
    "clavera": "demografia/radios_censales_indec_2010",
    "link": "demografia/redatam_censo_2022_radios",
}
BARRIOS = "limites/barrios_y_pueblos"
# The city of Pergamino, from the extent of its barrios.
CITY = (-60.64, -33.93, -60.51, -33.86)


def kind(types: list[str]) -> str:
    joined = " ".join(types)
    if "Polygon" in joined:
        return "polygon"
    if "LineString" in joined:
        return "line"
    if "Point" in joined:
        return "point"
    return "none"


def overlaps(a, b) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def data_path(catalog: Path, collection: str) -> str:
    """The local data file, or its public URL when it is not here.

    The refresh re-measures a changed collection, whose file is local. Its
    join targets are usually not, in a CI checkout.
    """
    from publish import load_config

    leaf = collection.split("/")[-1]
    local = catalog / collection / f"{leaf}.parquet"
    if local.exists():
        return str(local)
    base = load_config()["public_base"].rstrip("/")
    return f"{base}/{collection}/{leaf}.parquet"


def measure_one(con, catalog: Path, collection: str) -> dict:
    path = data_path(catalog, collection)
    doc = json.loads((catalog / collection / "collection.json").read_text())
    geo_types = doc.get("geoparquet:geometry_type") or []
    if isinstance(geo_types, str):
        geo_types = [geo_types]
    bbox = doc["extent"]["spatial"]["bbox"][0]
    columns = con.execute(
        "SELECT column_name, column_type FROM (DESCRIBE SELECT * FROM "
        "read_parquet(?))", [path]).fetchall()
    categories = {}
    total = con.execute("SELECT count(*) FROM read_parquet(?)",
                        [path]).fetchone()[0]
    for name, ctype in columns:
        if ctype != "VARCHAR" or PRIVATE.search(name):
            continue
        rows = con.execute(
            f'SELECT trim("{name}") AS v, count(*) AS n FROM read_parquet(?) '
            f'WHERE "{name}" IS NOT NULL AND trim("{name}") <> \'\' '
            f'GROUP BY 1 ORDER BY n DESC, v LIMIT {MAX_CATEGORIES + 1}',
            [path]).fetchall()
        repeats = sum(n for _, n in rows) >= 2 * len(rows)
        if 2 <= len(rows) <= MAX_CATEGORIES and repeats and all(
                len(v) <= 60 for v, _ in rows) and total:
            categories[name] = [v for v, _ in rows]
    names = {name for name, _ in columns}
    joins = {}
    for key, target in JOIN_KEYS.items():
        if key not in names or target == collection:
            continue
        other = data_path(catalog, target)
        other_cols = {r[0] for r in con.execute(
            "SELECT column_name FROM (DESCRIBE SELECT * FROM read_parquet(?))",
            [other]).fetchall()}
        if key not in other_cols:
            continue
        matched = con.execute(
            f"SELECT count(*) FROM (SELECT DISTINCT CAST({key} AS VARCHAR) k "
            f"FROM read_parquet(?)) a JOIN (SELECT DISTINCT CAST({key} AS "
            f"VARCHAR) k FROM read_parquet(?)) b USING (k)",
            [path, other]).fetchone()[0]
        if matched:
            joins[key] = target
    return {
        "geometry": kind(geo_types),
        "categories": categories,
        "joins": joins,
        "in_city": collection != BARRIOS and overlaps(bbox, CITY),
    }


def main() -> int:
    import duckdb

    catalog = Path(sys.argv[1])
    wanted = sys.argv[2:]
    measured = json.loads(PATH.read_text()) if PATH.exists() else {}
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    sources = json.loads((HERE.parent / "sources.json").read_text())
    names = wanted or sorted(sources["collections"])
    for collection in names:
        measured[collection] = measure_one(con, catalog, collection)
    measured = {k: v for k, v in sorted(measured.items())
                if k in sources["collections"]}
    PATH.write_text(json.dumps(measured, indent=2, ensure_ascii=False) + "\n")
    print(f"measured {len(names)} collection(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
