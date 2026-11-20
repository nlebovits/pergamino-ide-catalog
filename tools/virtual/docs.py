"""README.md and AGENTS.md for the virtual collections, in Spanish.

Every claim here is quoted from the upstream (JRC README.txt and
copyright.txt, Overture's attribution page, the overture-portolan column
descriptions) or measured by the builder (columns, nodata, classes present).
Measurements that change with the data go into STAC fields, never into prose:
a gate rejects counts, percentages and current-data dates in the guides.
"""
from __future__ import annotations

from pathlib import Path

import common as C
import glofas as G
import overture as O

DUCKDB_PRELUDE = ("INSTALL spatial; LOAD spatial;\n"
                  "INSTALL httpfs; LOAD httpfs;")

JRC_CC = ("Any copyright and/or sui generis right on the dataset is licensed "
          "under the Creative Commons Attribution 4.0 International "
          "(CC BY 4.0) licence [2]. Reuse is allowed provided appropriate "
          "credit is given and any changes are indicated.")
JRC_ODBL = ("A02. License information, restrictions on use: Open Data "
            "Commons Open Database License v1.0")
JRC_CITATION = ("Baugh, Calum; Colonese, Juan; D'Angelo, Claudia; Francesco, "
                "Dottori; Neal, Jeffrey; Prudhomme; Christe; Salamon, Peter "
                "(2024): Modelled flood inundation for different return "
                "period scenarios at the global scale. European Commission, "
                "Joint Research Centre (JRC)")
JRC_NOT_OFFICIAL = ("NOTE: this dataset is not an official flood hazard map "
                    "(for details and limitations please refer to related "
                    "publications).")
JRC_ARTEFACTS = ("Very high water depths may result from limitations in the "
                 "hydraulic modelling approach, in combination with the "
                 "spatial resolution, or from artificial sinks in the DEM.")
JRC_CLASSES = ("Water depth classification: 1: <1 m 2: 1–<3 m 3: 3–<10 m "
               "4: >10 m")


def _write(path: Path, lines: list[str]) -> None:
    C.write_text(path, "\n".join(lines).rstrip() + "\n")


def _bash(*commands: str) -> list[str]:
    return ["```bash", *commands, "```"]


# --- shared -------------------------------------------------------------------

ATTRIBUTION_NOTE = (
    "Esta colección es **virtual**: describe datos que publica otro catálogo "
    "y no copia sus bytes. El recurso `data` apunta al archivo original con "
    "una URL absoluta y lleva el rol `external`. El recorte al partido lo "
    "hace un archivo pequeño de este catálogo al leer los datos.")

PARTIDO_NOTE = (
    f"El recorte usa el límite oficial del partido publicado en "
    f"`{C.PARTIDO_URL}` (colección `limites/partido_pergamino`).")


# --- GloFAS ---------------------------------------------------------------


def _glofas_urls(layer: dict) -> tuple[str, str]:
    cid = layer["collection"]
    return cid, C.public_url(f"{cid}/{C.leaf(cid)}.vrt")


def _glofas_content(layer: dict) -> list[str]:
    if layer["kind"] == "depth":
        return [
            "Cada celda guarda la profundidad del agua en metros, en "
            "`float32`. Las celdas sin inundación y las que quedan fuera del "
            "partido valen `-9999` (nodata).",
        ]
    if layer["kind"] == "hazard":
        lines = [
            "Cada celda guarda una clase de profundidad en `uint8`; `255` es "
            "nodata. El README del JRC define las clases así:", "",
            f"> {JRC_CLASSES}", "",
            "| Valor | Clase |", "|--:|---|",
        ]
        for cls in G.HAZARD_CLASSES:
            lines.append(f"| {cls['value']} | {cls['title']} |")
        lines += ["", "El README de nlebovits/jrc-glofas describe las "
                  "clases como 0–4 con nombres de peligro (*No hazard*, "
                  "*Low*…). Esta colección sigue la definición del JRC."]
        return lines
    return [
        "Cada celda vale `1` donde hay agua permanente; `255` es nodata. El "
        "JRC usa esta máscara para completar los mapas de peligro, de modo "
        "que esas celdas no cuentan como inundación.",
    ]


def write_glofas(layer: dict, doc: dict, folder: Path) -> None:
    cid, vrt = _glofas_urls(layer)
    cog = doc["assets"]["data"]["href"]
    name = C.leaf(cid)
    readme = [
        f"# {doc['title']}", "", doc["description"], "",
        ATTRIBUTION_NOTE, "",
        "## Contenido", "",
        *_glofas_content(layer), "",
        "Resolución de 3 segundos de arco (unos 90 m), EPSG:4326. La tesela "
        f"`{G.GLOFAS['tile']}` del JRC cubre 10° × 10°; el partido entero "
        "cae dentro de ella.", "",
        "## Acceso", "",
        f"- Recorte (VRT de GDAL): `{vrt}`",
        f"- Tesela completa (COG externo): `{cog}`", "",
        "El VRT es texto: indica a GDAL qué ventana de la tesela leer y con "
        "qué límite recortarla. Abrirlo descarga solo esa ventana. Para "
        "guardar una copia local:", "",
        *_bash(f"gdal_translate -of COG \\\n  /vsicurl/{vrt} \\\n  {name}.tif"),
        "", "En QGIS: *Capa → Añadir capa ráster*, origen *Protocolo HTTP(S)*, "
        "con la URL del VRT.", "",
        "## Procedencia", "",
        "- Productor: European Commission, Joint Research Centre (JRC), "
        "Copernicus Emergency Management Service, *Global river flood "
        f"hazard maps* ({G.DOI}).",
        f"- Descarga original: {G.JRC_STORE}",
        "- Conversión a COG: catálogo Portolan nlebovits/jrc-glofas en "
        f"Source Cooperative ({G.UPSTREAM_PAGE}), colección "
        f"`{layer['upstream']}`.",
        "- Este catálogo: solo el VRT del recorte, el estilo y la vista "
        "previa.", "",
        "## Advertencias del productor", "",
        f"> {JRC_NOT_OFFICIAL}", "",
        f"> {JRC_ARTEFACTS}", "",
        "## Licencia", "",
        "El JRC da dos declaraciones distintas para este conjunto de datos, "
        "y esta colección no elige entre ellas (`license: other`, con un "
        "enlace a cada texto). El archivo `copyright.txt` de la descarga "
        "dice:", "",
        f"> {JRC_CC}", "",
        "El `README.txt` de la misma descarga, y el registro del Catálogo de "
        "Datos del JRC, dicen:", "",
        f"> {JRC_ODBL}", "",
        "La colección de nlebovits/jrc-glofas declara `proprietary`, un "
        "valor que STAC 1.1 desaconseja y que Portolan no admite; no se "
        "copia aquí.", "",
        "Cita recomendada por el JRC (README.txt, A01):", "",
        f"> {JRC_CITATION}", "",
    ]
    _write(folder / "README.md", readme)

    agents = [
        f"# Guía para agentes — {doc['title']}", "",
        doc["description"], "",
        "## Qué hay", "",
        *_glofas_content(layer), "",
        "## Leer el recorte", "",
        f"El VRT `{vrt}` lee la tesela externa por `/vsicurl/` y devuelve "
        "solo la ventana del partido, con nodata fuera del límite.", "",
        *_bash(f"gdalinfo -stats /vsicurl/{vrt}",
               f"gdal_translate -of COG \\\n  /vsicurl/{vrt} \\\n  {name}.tif"),
        "", "Con Python:", "",
        "```python",
        "import rasterio",
        f'with rasterio.open("/vsicurl/{vrt}") as src:',
        "    banda = src.read(1, masked=True)",
        "```", "",
        "## Rehacer el recorte", "",
        "El VRT se genera así; el límite se lee de su URL publicada:", "",
        *_bash(f"gdalwarp -of VRT \\\n  -cutline /vsicurl/{C.PARTIDO_URL} "
               f"\\\n  -crop_to_cutline \\\n  /vsicurl/{cog} \\\n  {name}.vrt"),
        "", "## Notas", "",
        "- Las estadísticas de la banda en `collection.json` (recurso "
        "`recorte`) describen la ventana del partido, no la tesela.",
        "- Los `file:size` y `file:checksum` de los items de "
        "nlebovits/jrc-glofas no coinciden con los bytes que sirve el "
        "servidor (comprobado con HEAD). Esta colección no los copia.",
        "- Los mapas modelan crecidas de ríos de cuencas grandes. No "
        "representan anegamientos por lluvia local. Las inundaciones "
        "observadas en el partido son `ambiente-y-agro/inundacion_1995` y "
        "`ambiente-y-agro/inundacion_2016`, en este mismo grupo.",
        f"- {JRC_NOT_OFFICIAL}", "",
        "## Comparar períodos de retorno", "",
        "Todos los VRT de GloFAS comparten la grilla, así que se pueden "
        "apilar sin remuestrear. Las siete profundidades:", "",
        *_bash(
            "gdalbuildvrt -separate profundidad.vrt \\\n" + " \\\n".join(
                f"  /vsicurl/{_glofas_urls(ly)[1]}"
                for ly in G.GLOFAS["layers"] if ly["kind"] == "depth")),
        "", "## Colecciones relacionadas", "",
        "- Las demás colecciones `ambiente-y-agro/glofas_*`: misma tesela, "
        "otros períodos de retorno.",
        "- `limites/partido_pergamino`: el límite que define el recorte.",
    ]
    _write(folder / "AGENTS.md", agents)


# --- Overture --------------------------------------------------------------

# One example query per type, using columns the builder checks are present.
EXAMPLES = {
    "building": ("Edificios por subtipo", ["subtype"],
                 "SELECT subtype, count(*) AS edificios\n"
                 "FROM ov.edificios\nGROUP BY subtype\n"
                 "ORDER BY edificios DESC;"),
    "place": ("Lugares por categoría principal", ["basic_category"],
              "SELECT basic_category, count(*) AS lugares\n"
              "FROM ov.lugares\nGROUP BY basic_category\n"
              "ORDER BY lugares DESC\nLIMIT 15;"),
    "segment": ("Longitud de la red por clase, en km", ["subtype", "class"],
                "SELECT subtype, class,\n"
                "       round(sum(ST_Length_Spheroid(geometry)) / 1000, 1)"
                " AS km\n"
                "FROM ov.segmentos\nGROUP BY subtype, class\n"
                "ORDER BY km DESC;"),
    "land_use": ("Superficie por subtipo, en hectáreas", ["subtype"],
                 "SELECT subtype,\n"
                 "       round(sum(ST_Area_Spheroid(geometry)) / 10000) "
                 "AS ha\n"
                 "FROM ov.uso_del_suelo\nGROUP BY subtype\n"
                 "ORDER BY ha DESC;"),
}


def _attach(layer: dict, alias: str = "ov") -> str:
    return f"ATTACH '{O.ddb_url(layer['collection'])}' AS {alias} (READ_ONLY);"


def _sql(layer: dict, body: str) -> list[str]:
    return ["```sql", DUCKDB_PRELUDE, _attach(layer), body, "```"]


def _layer(type_: str) -> dict:
    return next(ly for ly in O.OVERTURE["layers"] if ly["type"] == type_)


def _join_example() -> list[str]:
    """Places inside a building: two .ddb files, one ATTACH each."""
    places, buildings = _layer("place"), _layer("building")
    return [
        "```sql", DUCKDB_PRELUDE,
        _attach(places, "lug"), _attach(buildings, "edi"),
        "SELECT l.basic_category, count(*) AS lugares\n"
        f"FROM lug.{places['view']} AS l\n"
        f"JOIN edi.{buildings['view']} AS e\n"
        "  ON ST_Intersects(l.geometry, e.geometry)\n"
        "GROUP BY l.basic_category\n"
        "ORDER BY lugares DESC\nLIMIT 10;",
        "```"]


def example_for(layer: dict, columns: set[str]) -> tuple[str, str]:
    title, needed, body = EXAMPLES[layer["type"]]
    missing = [c for c in needed if c not in columns]
    if missing:
        raise SystemExit(f"{layer['id']}: example needs {missing}, absent "
                         "from the upstream schema; update docs.EXAMPLES")
    return title, body


def write_overture(layer: dict, doc: dict, folder: Path, res: dict) -> None:
    columns = {c["name"] for c in doc["table:columns"]}
    ex_title, ex_body = example_for(layer, columns)
    view = layer["view"]
    schema_rows = ["| Columna | Tipo | Descripción (Overture) |",
                   "|---|---|---|"]
    for col in doc["table:columns"]:
        desc = (col.get("description") or "").replace("|", "\\|")
        desc = desc.replace("\n", " ")
        schema_rows.append(f"| `{col['name']}` | `{col['type']}` | {desc} |")
    lic = doc["license"]
    lic_text = (
        "**ODbL 1.0**, según el catálogo STAC de Overture "
        "(`license: ODbL-1.0`). La página de atribución de Overture dice "
        "para este tema: \"License for theme: ODbL\"."
        if lic == "ODbL-1.0" else
        "Overture no declara una licencia única para este tema: su catálogo "
        "STAC usa `license: other` y enlaza la página de atribución, donde "
        "cada fuente tiene la suya. Esta colección copia esa declaración.")
    if "data" in doc["assets"]:
        parts_text = (
            "El recurso `data` de la colección es el archivo GeoParquet de "
            "la publicación vigente que contiene el partido; cubre una región "
            "mucho mayor.")
        where_expr = (
            "El recurso `data` de `collection.json` lleva en "
            "`processing:expression` la consulta equivalente.")
    else:
        parts_text = (
            "Los items son los archivos GeoParquet de la publicación vigente "
            "cuyo rectángulo toca el partido; cada uno cubre una región mucho "
            "mayor.")
        where_expr = (
            "Cada item lleva en `assets.data[\"processing:expression\"]` la "
            "consulta equivalente sobre su parte.")
    readme = [
        f"# {doc['title']}", "", doc["description"], "",
        ATTRIBUTION_NOTE, "",
        "## Contenido", "",
        f"Tipo `{layer['type']}` del tema `{layer['theme']}` de Overture "
        f"Maps. {parts_text} La publicación usada y la ruta por la que se resolvió "
        "están en `pergamino:virtual` dentro de `collection.json`.", "",
        "## Acceso", "",
        f"El archivo `{O.ddb_url(layer['collection'])}` contiene solo la "
        f"vista `{view}` de esta colección:", "",
        *_sql(layer, f"SELECT * FROM ov.{view} LIMIT 10;"), "",
        "Para el mapa, las PMTiles de Overture (recurso `visual`) con el "
        "estilo `styles/default.json`, que oculta lo que cae fuera del "
        "partido.", "",
        "## Esquema", "",
        "Nombres y tipos leídos del GeoParquet; descripciones tomadas de "
        "overture-portolan, que las copia del esquema de Overture.", "",
        *schema_rows, "",
        "## Procedencia", "",
        "- Productor: Overture Maps Foundation (https://overturemaps.org/).",
        f"- Guía: {O.GUIDES[layer['theme']]}",
        f"- Esquema: {O.schema_page(layer)}",
        "- Catálogo del que deriva: overture-portolan "
        f"(`{res['mirror']}`); si sus URLs no responden, el catálogo STAC "
        "de Overture (`https://stac.overturemaps.org/catalog.json`).", "",
        "## Licencia", "", lic_text, "",
        f"Atribución: {O.ATTRIBUTION}", "",
    ]
    _write(folder / "README.md", readme)

    agents = [
        f"# Guía para agentes — {doc['title']}", "",
        doc["description"], "",
        "## Consulta", "",
        "La vista ya aplica el recorte: prefiltro sobre la columna `bbox` "
        "(DuckDB descarta grupos de filas con las estadísticas del footer) y "
        "`ST_Intersects` con el límite oficial del partido. Requiere "
        "`spatial` y `httpfs`.", "",
        f"### {ex_title}", "",
        *_sql(layer, ex_body), "",
        *([] if layer["type"] != "place" else [
            "### Lugares dentro de un edificio", "",
            "Cada colección de Overture tiene su propio archivo de vistas; "
            "para unir dos capas, adjuntar los dos:", "",
            *_join_example(), ""]),
        "### Sin el archivo de vistas", "",
        f"{where_expr} Las URLs de las partes cambian con cada publicación "
        "de Overture, así que conviene leerlas del STAC o usar la vista.",
        "",
        "## Notas", "",
        f"- Columnas en inglés, con la semántica de Overture: ver "
        f"{O.schema_page(layer)}.",
        "- `geometry` está en EPSG:4326. Para medir en metros usar "
        "`ST_Length_Spheroid` o `ST_Area_Spheroid`.",
        "- `sources` registra la fuente de cada atributo; la licencia de "
        f"cada fuente está en {O.ATTRIBUTION}.",
        "- Overture borra las publicaciones viejas a los pocos meses. Las "
        "URLs de las partes se actualizan con `tools/virtual/refresh.py`.",
        "",
        "## Colecciones relacionadas", "",
        "- Las demás capas de Overture Maps en este catálogo: "
        + ", ".join(f"`{ly['collection']}`" for ly in O.OVERTURE["layers"]
                    if ly["id"] != layer["id"]) + ".",
        "- `limites/partido_pergamino`: el límite que define el recorte.",
    ]
    _write(folder / "AGENTS.md", agents)
