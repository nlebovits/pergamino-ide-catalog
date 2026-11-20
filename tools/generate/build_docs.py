#!/usr/bin/env python3
"""Generate README.md and AGENTS.md for the root, each group and each
GeoNode collection.

Every sentence about a dataset comes from one of three committed sources,
so the docs regenerate deterministically and offline:

- the collection's ``collection.json``
- the GeoNode record, as stored in ``tools/generate/data/geonode.json``
  (``tools/snapshot.py``), quoted rather than paraphrased
- the facts measured from the data, in ``tools/generate/data/measured.json``
  (``tools/generate/measure.py``)

The docs quote no row counts and no dates of the current data, because both
change on every refresh. ``tests/test_no_data_numbers.py`` and
``tests/test_no_stale_dates.py`` enforce that. Every ```sql block in an
AGENTS.md runs in CI (``tests/test_queries.py``).

The imagery (``imagenes/``) and the virtual collections have their own
generators. The virtual collections sit in the thematic groups, marked by
``pergamino:virtual``; this script lists them in their group's README and
AGENTS.md, but does not write their own docs.

    python3 tools/generate/build_docs.py catalog
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from build_catalogs import EXTRA_GROUPS  # noqa: E402
from group_descriptions import GROUP_DOCS  # noqa: E402
from grouping import GROUPS  # noqa: E402
from publish import load_config  # noqa: E402

BASE = load_config()["public_base"].rstrip("/")
DATA = HERE / "data"
SOURCES = json.loads((HERE.parent / "sources.json").read_text())["collections"]
RECORDS = json.loads((DATA / "geonode.json").read_text())
MEASURED = json.loads((DATA / "measured.json").read_text())

GEOMETRY = {"point": "puntos", "line": "líneas", "polygon": "polígonos",
            "none": "sin geometría"}
FREQUENCY = {
    "continual": "continua", "daily": "diaria", "weekly": "semanal",
    "fortnightly": "quincenal", "monthly": "mensual",
    "quarterly": "trimestral", "biannually": "semestral",
    "annually": "anual", "asNeeded": "cuando es necesario",
    "irregular": "irregular", "notPlanned": "no planificada",
    "unknown": "desconocida",
}
BARRIOS = "limites/barrios_y_pueblos"
LICENSE_QUOTE = (
    "> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales "
    "estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite "
    "utilizar, compartir y adaptar este material siempre que reconozca "
    "atribución y permita la misma licencia en sus derivados.")
WARNING_QUOTE = (
    "> La información contenida en la IDE se encuentra en constante "
    "actualización por parte de las distintas áreas responsables de su "
    "generación, por lo tanto, podria contener diferencias e inconsistencias "
    "en relación al objeto o fenómeno representado, tanto espacial como "
    "temporalmente.")
NO_COLUMN_DOCS = (
    "La fuente no publica descripciones de columnas: GeoNode devuelve una "
    "descripción vacía para cada atributo. Por eso las columnas no tienen "
    "descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega "
    "este catálogo.")


def write(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


def clean(value: str | None) -> str:
    import html
    import re

    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    value = re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()
    empty = {"", "no information provided", "ninguna", "ninguna.", "none"}
    return "" if value.lower() in empty else value


def ident(name: str) -> str:
    """A column name, quoted for DuckDB."""
    return '"' + name.replace('"', '""') + '"'


def data_url(collection: str) -> str:
    return f"{BASE}/{collection}/{collection.split('/')[-1]}.parquet"


def load_collection(catalog: Path, collection: str) -> dict:
    return json.loads((catalog / collection / "collection.json").read_text())


def group_collections(catalog: Path, group: str) -> list[dict]:
    return [json.loads(p.read_text())
            for p in sorted((catalog / group).glob("*/collection.json"))]


def is_virtual(col: dict) -> bool:
    """A collection over another catalog's data (tools/virtual/)."""
    return "pergamino:virtual" in col


def kind_label(col: dict) -> str:
    """The Geometría cell: measured for GeoNode layers, the source otherwise."""
    if is_virtual(col):
        raster = "upstream_catalog" in col["pergamino:virtual"]
        return "ráster externo" if raster else "vectores externos"
    facts = MEASURED.get(col["id"], {"geometry": "none"})
    return GEOMETRY[facts["geometry"]]


def virtual_section(cols: list[dict]) -> list[str]:
    """Group README lines for the virtual collections, if the group has any."""
    virtual = [c for c in cols if is_virtual(c)]
    if not virtual:
        return []
    producers: dict[str, list[str]] = {}
    for col in virtual:
        producers.setdefault(col["providers"][0]["name"], []).append(
            f"`{col['id'].split('/')[-1]}`")
    L = ["", "## Datos de otros catálogos", "",
         "Estas colecciones no vienen de GeoNode. Describen la parte de un "
         "conjunto de datos publicado en otro catálogo que cae dentro del "
         "partido, sin copiar sus bytes: el recurso `data` apunta al archivo "
         "original y un recurso `recorte` lo recorta al leer. Cada una "
         "conserva la licencia de su productor; ver su README.", ""]
    for org, names in sorted(producers.items()):
        L.append(f"- **{org}**: {', '.join(sorted(names))}")
    return L


# --------------------------------------------------------------------------
# Collection docs


def queries(collection: str, doc: dict, facts: dict) -> list[tuple[str, str]]:
    """(title, sql) for every example query this collection supports."""
    url = data_url(collection)
    spatial = facts["geometry"] != "none"
    drop = " EXCLUDE (geometry, bbox)" if spatial else ""
    out = [("Primeros registros", "\n".join([
        f"SELECT *{drop}",
        f"FROM read_parquet('{url}')",
        "LIMIT 5;"]))]
    for column in list(facts["categories"])[:2]:
        out.append((f"Registros por `{column}`", "\n".join([
            f"SELECT {ident(column)}, count(*) AS registros",
            f"FROM read_parquet('{url}')",
            "GROUP BY ALL",
            "ORDER BY registros DESC;"])))
    if spatial and facts["in_city"]:
        out.append(("Registros por barrio", "\n".join([
            "SELECT b.nombre AS barrio, count(*) AS registros",
            f"FROM read_parquet('{url}') AS t",
            f"JOIN read_parquet('{data_url(BARRIOS)}') AS b",
            "  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)",
            "GROUP BY b.nombre",
            "ORDER BY registros DESC",
            "LIMIT 10;"])))
    if spatial:
        x0, y0, x1, y1 = doc["extent"]["spatial"]["bbox"][0]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = max((x1 - x0) / 10, 0.005), max((y1 - y0) / 10, 0.005)
        out.append(("Filtro por ventana, con la columna `bbox`", "\n".join([
            "SELECT count(*) AS registros",
            f"FROM read_parquet('{url}')",
            f"WHERE bbox.xmin >= {cx - dx:.4f} AND bbox.xmax <= {cx + dx:.4f}",
            f"  AND bbox.ymin >= {cy - dy:.4f} AND bbox.ymax <= {cy + dy:.4f};",
        ])))
    for key, target in facts["joins"].items():
        out.append((f"Unión con `{target}` por `{key}`", "\n".join([
            f"SELECT t.{ident(key)}, count(*) AS registros",
            f"FROM read_parquet('{url}') AS t",
            f"JOIN read_parquet('{data_url(target)}') AS r",
            f"  ON CAST(t.{ident(key)} AS VARCHAR) = "
            f"CAST(r.{ident(key)} AS VARCHAR)",
            "GROUP BY ALL",
            "ORDER BY registros DESC",
            "LIMIT 10;"])))
    return out


def providers_text(doc: dict) -> str:
    producers = [p["name"] for p in doc["providers"]
                 if "producer" in p.get("roles", [])]
    return ", ".join(producers)


def first_version_note(doc: dict) -> str | None:
    for key, asset in doc["assets"].items():
        if key.startswith("version-") and "publico_" in asset["href"]:
            return (f"La primera versión proviene del GeoServer anterior de "
                    f"la IDE Pergamino y sigue publicada en "
                    f"`{asset['href']}`.")
    return None


def collection_readme(catalog: Path, collection: str) -> None:
    doc = load_collection(catalog, collection)
    entry = SOURCES[collection]
    record = RECORDS[entry["alternate"]]
    facts = MEASURED[collection]
    leaf = collection.split("/")[-1]
    page = f"https://geonode.pergamino.gob.ar/catalogue/#/dataset/{entry['pk']}"
    L = [f"# {doc['title']}", "", doc["description"], "",
         "| | |", "|---|---|",
         f"| Identificador | `{collection}` |",
         f"| Geometría | {GEOMETRY[facts['geometry']]} |",
         f"| Fuente | [{doc['title']} en GeoNode]({page}), capa WFS "
         f"`{entry['alternate']}` |",
         "| Licencia | [CC-BY-SA-4.0]"
         "(https://creativecommons.org/licenses/by-sa/4.0/) |",
         "| Actualización declarada por la fuente | "
         f"{FREQUENCY.get(entry['update_frequency'], entry['update_frequency'])} |",
         ""]
    for title, field in (("Propósito", "raw_purpose"),
                         ("Calidad de los datos", "raw_data_quality_statement"),
                         ("Información complementaria",
                          "raw_supplemental_information"),
                         ("Restricciones de uso declaradas",
                          "raw_constraints_other")):
        value = clean(record.get(field))
        if value:
            L += [f"## {title}", "", "Según el registro de GeoNode:", "",
                  f"> {value}", ""]
    L += ["## Esquema", "", "| Columna | Tipo |", "|---|---|"]
    for column in doc["table:columns"]:
        L.append(f"| `{column['name']}` | {column['type']} |")
    L += ["", NO_COLUMN_DOCS, "",
          "## Acceso", "",
          "```python", "import duckdb", "",
          "con = duckdb.connect()",
          'con.sql("INSTALL spatial; LOAD spatial; '
          'INSTALL httpfs; LOAD httpfs;")',
          f"con.sql(\"SELECT * FROM read_parquet('{data_url(collection)}') "
          "LIMIT 10\").show()",
          "```", "",
          "Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).",
          ""]
    if f"{leaf}-tiles" in doc["assets"]:
        L += ["## Visualización", "",
              f"Las teselas vectoriales están en `./{leaf}.pmtiles` (capa "
              f"`{leaf}`). El estilo por defecto, `styles/default.json`, "
              "deriva del estilo SLD que publica GeoNode para esta capa."]
        if "legends/source" in doc["assets"]:
            L += ["", "Leyenda tal como la publica la fuente:", "",
                  "![Leyenda](./legends/source.png)"]
        L.append("")
    L += ["## Versiones", "",
          "Cada extracción que cambia los datos es una versión nueva. La "
          f"versión actual está en `./{leaf}.parquet`. Las anteriores son "
          "los activos `version-*` de `collection.json`, con el número de "
          "registros y la suma de verificación de cada una. Sus archivos no "
          "cambian."]
    note = first_version_note(doc)
    if note:
        L += ["", note]
    L += ["", "## Procedencia", "",
          f"Productor: {providers_text(doc)}. Publicado por la Dirección de "
          "Sistemas de Información Georreferenciada (DSIG) de la "
          f"Municipalidad de Pergamino en [GeoNode]({page}).", ""]
    attribution = clean(record.get("attribution"))
    if attribution:
        L += [f"Atribución declarada en GeoNode: \"{attribution}\".", ""]
    if len(doc["providers"]) > 2:
        L += ["Es un dato de otro organismo, rehospedado por el municipio. "
              "La atribución corresponde al organismo de origen.", ""]
    L += ["Este catálogo es un espejo. Para el dato autoritativo, consultar "
          "la IDE de Pergamino.", "",
          "## Licencia", "",
          "CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de "
          "Pergamino para su IDE:", "", LICENSE_QUOTE, "",
          "## Advertencia del publicador", "", WARNING_QUOTE, ""]
    write(catalog / collection / "README.md", L)


def collection_agents(catalog: Path, collection: str) -> None:
    doc = load_collection(catalog, collection)
    entry = SOURCES[collection]
    facts = MEASURED[collection]
    leaf = collection.split("/")[-1]
    L = [f"# Guía para agentes — {doc['title']}", "",
         f"`{collection}`: {GEOMETRY[facts['geometry']]}. "
         f"{doc['description']}", "",
         "## Acceso", "",
         f"- Datos: `{data_url(collection)}`. GeoParquet 1.1, geometría WKB "
         "en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.",
         ]
    if f"{leaf}-tiles" in doc["assets"]:
        L.append(f"- Teselas: `{BASE}/{collection}/{leaf}.pmtiles`, capa "
                 f"`{leaf}`, zoom 0 a 15.")
    L += [f"- Metadatos: `{BASE}/{collection}/collection.json`. El número "
          "de registros está en `table:row_count`, y cada versión anterior "
          "en un activo `version-*`.",
          f"- Fuente: capa WFS `{entry['alternate']}` de GeoNode.", "",
          "## Esquema", ""]
    for column in doc["table:columns"]:
        L.append(f"- `{column['name']}` ({column['type']})")
    L += ["", NO_COLUMN_DOCS, ""]
    if facts["categories"]:
        L += ["Valores medidos en los datos, de más a menos frecuente, de las "
              "columnas de texto con pocas categorías:", "", "```text"]
        for column, values in facts["categories"].items():
            L.append(f"{column}: " + " | ".join(values))
        L += ["```", ""]
    L += ["## Consultas de ejemplo", "",
          "Cada bloque corre tal cual en el CLI de DuckDB después de "
          "`INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.", ""]
    for title, sql in queries(collection, doc, facts):
        L += [f"### {title}", "", "```sql", sql, "```", ""]
    L += ["## Notas de calidad", "",
          "- Las geometrías inválidas de la fuente se reparan con "
          "`shapely.make_valid`. `pergamino:repaired_geometries` en el activo "
          "de datos dice cuántas se repararon en cada versión.",
          "- La fecha de los metadatos es de publicación en GeoNode, no del "
          "contenido. Si la capa tiene columnas como `fuente` o "
          "`actualizacion`, son la mejor señal de vigencia.", ""]
    if facts["joins"] or facts["in_city"]:
        L += ["## Colecciones relacionadas", ""]
        for key, target in facts["joins"].items():
            L.append(f"- `{target}`, por `{key}`. Hay valores de `{key}` que "
                     "coinciden en las dos colecciones.")
        if facts["in_city"]:
            L.append(f"- `{BARRIOS}`, por intersección espacial.")
        L.append("")
    write(catalog / collection / "AGENTS.md", L)


# --------------------------------------------------------------------------
# Group and root docs


def group_readme(catalog: Path, group: str) -> None:
    title, desc = GROUP_DOCS[group]
    cols = group_collections(catalog, group)
    local = [c for c in cols if not is_virtual(c)]
    L = [f"# {title}", "", desc, "",
         "Forma parte del espejo cloud-native de la "
         "[IDE Pergamino](../README.md).", "",
         "## Colecciones", "",
         "| Colección | Geometría | Descripción |", "|---|---|---|"]
    for col in cols:
        leaf = col["id"].split("/")[-1]
        d = col["description"].replace("|", "/").replace("\n", " ")
        if len(d) > 140:
            d = d[:137].rstrip() + "..."
        L.append(f"| [{col['title']}](./{leaf}/) | "
                 f"{kind_label(col)} | {d} |")
    L += virtual_section(cols)
    third = {}
    for col in cols:
        if is_virtual(col):
            continue
        for p in col["providers"][:-2]:
            third.setdefault(p["name"], []).append(col["title"])
    if third:
        L += ["", "## Datos de terceros", "",
              "Estas colecciones son datos producidos por otros organismos y "
              "rehospedados por la Municipalidad de Pergamino. La atribución "
              "corresponde al organismo de origen.", ""]
        for org, names in sorted(third.items()):
            L.append(f"- **{org}**: {', '.join(sorted(names))}")
    L += ["", "## Acceso", "",
          "Cada colección tiene su README con el esquema, y su AGENTS.md con "
          "consultas probadas. Por ejemplo:", "",
          "```python", "import duckdb", "",
          "con = duckdb.connect()",
          'con.sql("INSTALL spatial; LOAD spatial; '
          'INSTALL httpfs; LOAD httpfs;")',
          f"con.sql(\"SELECT * FROM read_parquet('{data_url(local[0]['id'])}') "
          "LIMIT 10\").show()",
          "```", "",
          "## Procedencia y licencia", "",
          "Fuente: [GeoNode de la IDE Pergamino]"
          "(https://geonode.pergamino.gob.ar/), Dirección de Sistemas de "
          "Información Georreferenciada, Municipalidad de Pergamino.", "",
          "Licencia: CC BY-SA 4.0, según la declaración del municipio para su "
          "IDE. Las colecciones de terceros conservan la atribución a su "
          "organismo de origen."]
    if any(is_virtual(c) for c in cols):
        L += ["", "Las colecciones de *Datos de otros catálogos* no vienen de "
              "GeoNode ni llevan la licencia del municipio: cada una declara "
              "la de su productor."]
    write(catalog / group / "README.md", L)


def group_agents(catalog: Path, group: str) -> None:
    title, desc = GROUP_DOCS[group]
    cols = group_collections(catalog, group)
    L = [f"# Guía para agentes — {title}", "", desc, "",
         "Cada colección tiene su propio `AGENTS.md` con el esquema, los "
         "valores medidos y consultas probadas. Este archivo es el índice del "
         "grupo.", "", "## Colecciones", ""]
    for col in cols:
        leaf = col["id"].split("/")[-1]
        L.append(f"- [`{col['id']}`](./{leaf}/AGENTS.md): {col['title']}, "
                 f"{kind_label(col)}")
    L += ["", "## Notas de acceso", "",
          "- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, "
          "con columna de cobertura `bbox` y orden espacial Hilbert. Un "
          "filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.",
          "- Las capas tienen además PMTiles y un estilo MapLibre en "
          "`styles/default.json`, derivado del estilo SLD que publica GeoNode.",
          "- Los nombres de columna están en español, tal como los publica la "
          "fuente."]
    virtual = [c["id"] for c in cols if is_virtual(c)]
    if virtual:
        L += ["- Las colecciones "
              + ", ".join(f"`{v}`" for v in virtual)
              + " son virtuales: no tienen un GeoParquet propio. Su "
              "`AGENTS.md` dice cómo leer el recorte (un VRT de GDAL o un "
              "archivo de vistas DuckDB), y la consulta lee los datos del "
              "servidor del productor."]
    write(catalog / group / "AGENTS.md", L)


def extra_groups(catalog: Path) -> list[tuple[str, dict]]:
    out = []
    for group in EXTRA_GROUPS:
        path = catalog / group / "catalog.json"
        if path.exists():
            out.append((group, json.loads(path.read_text())))
    return out


def root_readme(catalog: Path) -> None:
    L = ["# IDE Pergamino — Infraestructura de Datos Espaciales", "",
         "Espejo cloud-native de la IDE del Municipio de Pergamino, Provincia "
         "de Buenos Aires, Argentina. Las capas vectoriales que publica el "
         "municipio en GeoNode están aquí en GeoParquet y PMTiles, "
         "consultables directamente desde la nube.", "",
         "## Grupos", "", "| Grupo | Contenido |", "|---|---|"]
    for group in GROUPS:
        t, d = GROUP_DOCS[group]
        L.append(f"| [{t}](./{group}/) | {d.split('. ')[0].rstrip('.')} |")
    for group, cat in extra_groups(catalog):
        L.append(f"| [{cat['title']}](./{group}/) | "
                 f"{cat['description'].split('. ')[0].rstrip('.')} |")
    L += ["", "## Acceso rápido", "",
          "```python", "import duckdb", "",
          "con = duckdb.connect()",
          'con.sql("INSTALL spatial; LOAD spatial; '
          'INSTALL httpfs; LOAD httpfs;")',
          f"con.sql(\"SELECT nombre FROM read_parquet('{data_url(BARRIOS)}')"
          "\").show()",
          "```", "",
          "## Procedencia", "",
          "Los datos vectoriales son producidos y publicados por la "
          "**Dirección de Sistemas de Información Georreferenciada (DSIG)** "
          "de la Municipalidad de Pergamino, en su portal GeoNode:", "",
          "- Geoportal: https://geonode.pergamino.gob.ar/",
          "- Geoservicios: https://geonode.pergamino.gob.ar/geoserver/ows",
          "- Página institucional: https://pergamino.ar/servicios/ide-pergamino/",
          "",
          "Este catálogo **no es la fuente original**. Es un espejo optimizado "
          "para consulta en la nube. Para el dato autoritativo y actualizado, "
          "consultar la IDE de Pergamino. Un proceso semanal compara cada capa "
          "con GeoNode y publica una versión nueva cuando los datos cambian.",
          "",
          "Varias capas son datos de organismos nacionales y provinciales "
          "rehospedados por el municipio. Cada colección atribuye a su "
          "organismo de origen.", "",
          "## Licencia", "",
          "**CC BY-SA 4.0**, según la declaración de la Municipalidad de "
          "Pergamino para su IDE:", "", LICENSE_QUOTE, "",
          "La licencia cubre los datos, no la marca institucional del "
          "municipio. Las capas de terceros conservan los términos de su "
          "organismo de origen.", "",
          "## Advertencia del publicador", "", WARNING_QUOTE, "",
          "## Cobertura", "",
          "Este espejo replica la mayor parte de las capas vectoriales que "
          "GeoNode publica. Un pequeño número no se replica. Para consultas "
          "sobre la cobertura, escribir a nlebovits@pm.me."]
    write(catalog / "README.md", L)


def root_agents(catalog: Path) -> None:
    L = ["# Guía para agentes — IDE Pergamino", "",
         "Espejo cloud-native de la IDE del Municipio de Pergamino "
         "(Buenos Aires, Argentina), con las capas vectoriales que el "
         "municipio publica en GeoNode.", "",
         "## Cómo está organizado", "",
         "El catálogo raíz enlaza a subcatálogos temáticos, y cada uno enlaza "
         "a sus colecciones. Los identificadores son rutas: "
         "`catastro/parcela`, `demografia/nbi`, `ambiente-y-agro/arbolado`.",
         ""]
    for group in GROUPS:
        t, _ = GROUP_DOCS[group]
        L.append(f"- [`{group}/`](./{group}/AGENTS.md): {t}")
    for group, cat in extra_groups(catalog):
        L.append(f"- [`{group}/`](./{group}/AGENTS.md): {cat['title']}")
    L += ["", "## Formato", "",
          "- **GeoParquet 1.1**, geometría WKB en `geometry`, EPSG:4326, "
          "columna de cobertura `bbox` (struct xmin/ymin/xmax/ymax), "
          "orden espacial Hilbert, compresión ZSTD.",
          "- **PMTiles** para visualización web, con estilo MapLibre en "
          "`styles/default.json` derivado del estilo SLD que publica GeoNode.",
          "- Nombres de columna en español, tal como los publica la fuente.",
          "- Cada `collection.json` registra sus versiones como activos "
          "`version-*`. La versión actual de una colección siempre está en "
          "`<grupo>/<colección>/<colección>.parquet`.", "",
          "## Consulta", "",
          "```sql",
          "SELECT nombre, ST_Area(ST_Transform(geometry, 'EPSG:4326', "
          "'EPSG:22175', always_xy := true)) / 10000 AS hectareas",
          f"FROM read_parquet('{data_url(BARRIOS)}')",
          "ORDER BY hectareas DESC",
          "LIMIT 5;",
          "```", "",
          "## Claves de unión", "",
          "Medidas en los datos: se listan las que tienen valores en común "
          "entre colecciones. Cada `AGENTS.md` de colección muestra la unión "
          "concreta.", ""]
    keys = {}
    for collection, facts in MEASURED.items():
        for key, target in facts["joins"].items():
            keys.setdefault((key, target), []).append(collection)
    for (key, target), colls in sorted(keys.items()):
        L.append(f"- `{key}` une `{target}` con: "
                 + ", ".join(f"`{c}`" for c in sorted(colls)) + ".")
    L += ["", "## Advertencias", "",
          "- **`limites/zonas_electorales_celp` no es electoral en sentido "
          "político.** GeoNode la describe como \"Capa de zonas electorales "
          "de la Cooperativa Eléctrica Limitada de Pergamino\".",
          "- **`demografia/nbi`**: la descripción en GeoNode dice \"Niveles "
          "Básicos Insatisfechos\". El término del INDEC, que usa el título, "
          "es *Necesidades* Básicas Insatisfechas.",
          "- La fecha de los metadatos es de publicación, no del contenido. "
          "Varias capas traen `fuente` y `actualizacion` por registro, que es "
          "la señal de vigencia más confiable. `ambiente-y-agro/arbolado` "
          "proviene del censo de arbolado de 2013.",
          "- Varias colecciones son datos de terceros (INTA, IGN, INDEC, "
          "RENABAP, CONICET, INA, ARBA, BAHRA, Correo Argentino) rehospedados "
          "por el municipio. Atribuir al organismo de origen, no al "
          "municipio."]
    write(catalog / "AGENTS.md", L)


def main() -> int:
    catalog = Path(sys.argv[1])
    for collection in sorted(SOURCES):
        if (catalog / collection / "collection.json").exists():
            collection_readme(catalog, collection)
            collection_agents(catalog, collection)
    for group in GROUPS:
        group_readme(catalog, group)
        group_agents(catalog, group)
    root_readme(catalog)
    root_agents(catalog)
    print(f"wrote docs for {len(SOURCES)} collections, {len(GROUPS)} groups "
          "and the root")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
