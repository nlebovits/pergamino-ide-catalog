"""Generate README.md and AGENTS.md for the root catalog and each sub-catalog.

Catalog-level READMEs are tables of contents, per the Portolan documentation
best practices. Collection-level docs are generated separately by the CLI from
each collection's own metadata.

Everything here is derived from collection.json and the harvested upstream
metadata, so it regenerates deterministically.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grouping import GROUPS  # noqa: E402
from group_descriptions import GROUP_DOCS  # noqa: E402

DST = sys.argv[1]
META = json.load(open(sys.argv[2], encoding="utf-8"))

BASE = "https://data.source.coop/nlebovits/pergamino-ide"

ORIGIN_NOTE = {
    "INTA": "INTA", "IGN": "IGN", "INDEC": "INDEC", "CONICET": "CONICET",
    "INA": "INA", "BAHRA": "BAHRA", "CARTOARBA": "ARBA", "ARBA": "ARBA",
    "Correo Argentino": "Correo Argentino", "IDECOM": "IDECOM/ENACOM",
    "ABS-IATASA": "IATASA-ABS", "UNNOBA": "UNNOBA", "PBA": "Prov. Buenos Aires",
}


def load_collections(group):
    out = []
    gdir = os.path.join(DST, group)
    cat = json.load(open(os.path.join(gdir, "catalog.json"), encoding="utf-8"))
    for ln in cat["links"]:
        if ln.get("rel") != "child":
            continue
        leaf = ln["href"].split("/")[1]
        col = json.load(open(os.path.join(gdir, leaf, "collection.json"),
                             encoding="utf-8"))
        out.append((leaf, col))
    return out


def upstream_layer(col):
    for ln in col.get("links", []):
        if ln.get("rel") == "via" and "typename" in (ln.get("href") or ""):
            return ln["href"].split("typename=")[-1].split("&")[0].replace("%3A", ":")
    return ""


def third_party(layer_key):
    attr = (META.get(layer_key, {}) or {}).get("gn_attribution", "") or ""
    parts = [p.strip() for p in attr.split(",")[1:] if p.strip()]
    return [ORIGIN_NOTE.get(p, p) for p in parts]


def rowcount(col):
    n = col.get("table:row_count")
    if n is None:
        for a in (col.get("assets") or {}).values():
            if "data" in (a.get("roles") or []):
                n = a.get("table:row_count")
    return n


def geom_of(col):
    g = col.get("geoparquet:geometry_type") or ""
    return g.replace("Multi", "Multi ").strip() or "-"


def write_group_readme(group):
    title, desc = GROUP_DOCS[group]
    cols = load_collections(group)
    L = [f"# {title}", "", desc, "",
         f"{len(cols)} colecciones. Forma parte del espejo cloud-native de la "
         f"[IDE Pergamino](../README.md).", "",
         "## Colecciones", "",
         "| Colección | Registros | Geometría | Descripción |",
         "|---|--:|---|---|"]
    for leaf, col in cols:
        n = rowcount(col)
        n = f"{n:,}".replace(",", ".") if isinstance(n, int) else "-"
        d = (col.get("description") or "").replace("|", "/").replace("\n", " ")
        if len(d) > 120:
            d = d[:117] + "..."
        L.append(f"| [{col['title']}](./{leaf}/) | {n} | {geom_of(col)} | {d} |")

    tp = {}
    for leaf, col in cols:
        key = upstream_layer(col).split(":")[-1]
        for o in third_party(key):
            tp.setdefault(o, []).append(col["title"])
    if tp:
        L += ["", "## Datos de terceros", "",
              "Estas colecciones son datos producidos por otros organismos y "
              "rehospedados por la Municipalidad de Pergamino. La atribución "
              "corresponde al organismo de origen.", ""]
        for org, names in sorted(tp.items()):
            L.append(f"- **{org}** — {', '.join(sorted(names))}")

    L += ["", "## Acceso", "",
          "```python", "import duckdb",
          'duckdb.sql("INSTALL spatial; LOAD spatial;")',
          "", "df = duckdb.sql(\"\"\"",
          '  SELECT * FROM read_parquet(',
          f"    '{BASE}/{group}/{cols[0][0]}/{os.path.basename(next(a['href'] for a in (cols[0][1].get('assets') or {}).values() if 'data' in (a.get('roles') or [])))}')",
          "  LIMIT 10",
          '""").df()', "```", "",
          "## Procedencia y licencia", "",
          "Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — "
          "Dirección de Sistemas de Información Georreferenciada, Municipalidad "
          "de Pergamino.", "",
          "Licencia: CC BY-SA 4.0, según la declaración del municipio para su "
          "IDE. Las colecciones de terceros conservan la atribución a su "
          "organismo de origen.", ""]
    open(os.path.join(DST, group, "README.md"), "w", encoding="utf-8").write("\n".join(L))


def write_group_agents(group):
    title, desc = GROUP_DOCS[group]
    cols = load_collections(group)
    L = [f"# Guía para agentes — {title}", "", desc, "",
         "Cada colección tiene su propio `AGENTS.md` con esquema, claves de "
         "unión y consultas probadas. Este archivo es el índice del grupo.", "",
         "## Colecciones", ""]
    for leaf, col in cols:
        n = rowcount(col)
        n = f"{n:,}".replace(",", ".") if isinstance(n, int) else "?"
        L.append(f"- [`{col['id']}`](./{leaf}/AGENTS.md) — {col['title']}, "
                 f"{n} registros, {geom_of(col)}")
    L += ["", "## Notas de acceso", "",
          "- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con "
          "columna de cobertura `bbox` y ordenamiento espacial Hilbert. "
          "Los filtros espaciales aprovechan las estadísticas por grupo de filas.",
          "- Las capas tienen además PMTiles para visualización web y un estilo "
          "MapLibre en `styles/default.json` derivado del SLD oficial del "
          "GeoServer municipal.",
          "- Los nombres de columna están en español y varias capas traen "
          "`fuente` y `actualizacion` a nivel de registro, que es la señal de "
          "vigencia más confiable.", ""]
    open(os.path.join(DST, group, "AGENTS.md"), "w", encoding="utf-8").write("\n".join(L))


def write_root():
    total = sum(len(GROUPS[g]) for g in GROUPS)
    L = ["# IDE Pergamino — Infraestructura de Datos Espaciales", "",
         "Espejo cloud-native de la IDE del Municipio de Pergamino, Provincia "
         "de Buenos Aires, Argentina.", "",
         f"{total} colecciones en {len(GROUPS)} grupos temáticos, en GeoParquet "
         "y PMTiles, consultables directamente desde la nube.", "",
         "## Grupos", "",
         "| Grupo | Colecciones | Contenido |", "|---|--:|---|"]
    for g in GROUPS:
        t, d = GROUP_DOCS[g]
        d1 = d.split(".")[0]
        L.append(f"| [{t}](./{g}/) | {len(GROUPS[g])} | {d1} |")
    L += ["", "## Acceso rápido", "",
          "```python", "import duckdb",
          'duckdb.sql("INSTALL spatial; LOAD spatial;")', "",
          "# Los barrios de Pergamino",
          'duckdb.sql("""',
          f"  SELECT * FROM read_parquet('{BASE}/limites/barrios/publico_barrios.parquet')",
          '""").df()', "```", "",
          "## Procedencia", "",
          "Los datos son producidos y publicados por la **Dirección de Sistemas "
          "de Información Georreferenciada (DSIG)** de la Municipalidad de "
          "Pergamino, a través de su GeoServer y su portal GeoNode:", "",
          "- Geoportal: https://geonode.pergamino.gob.ar/",
          "- Geoservicios: https://ide.pergamino.gob.ar:8443/geoserver/",
          "- Página institucional: https://pergamino.ar/servicios/ide-pergamino/",
          "",
          "Este catálogo **no es la fuente original**. Es un espejo optimizado "
          "para consulta en la nube. Para el dato autoritativo y actualizado, "
          "consultar la IDE de Pergamino.", "",
          "Varias capas son datos de organismos nacionales y provinciales "
          "(INTA, IGN, INDEC, RENABAP, CONICET, INA, ARBA, BAHRA, Correo "
          "Argentino) rehospedados por el municipio. Cada colección atribuye a "
          "su organismo de origen.", "",
          "## Licencia", "",
          "**CC BY-SA 4.0**, según la declaración de la Municipalidad de "
          "Pergamino para su IDE:", "",
          "> Los datos dispuestos en nuestra Infraestructura de Datos "
          "Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, "
          "lo cual permite utilizar, compartir y adaptar este material siempre "
          "que reconozca atribución y permita la misma licencia en sus "
          "derivados.", "",
          "La licencia cubre los datos, no la marca institucional del "
          "municipio. Las capas de terceros conservan los términos de su "
          "organismo de origen.", "",
          "## Advertencia del publicador", "",
          "> La información contenida en la IDE se encuentra en constante "
          "actualización por parte de las distintas áreas responsables de su "
          "generación, por lo tanto, podria contener diferencias e "
          "inconsistencias en relación al objeto o fenómeno representado, "
          "tanto espacial como temporalmente.", "",
          "GeoNode declara `maintenance_frequency: notPlanned` para más de la "
          "mitad del catálogo. La mayor parte de los datos no tiene una "
          "actualización programada.", "",
          ]
    L += ["", "## Cobertura", "",
          "Este espejo replica la mayor parte de las capas vectoriales "
          "publicadas por la IDE de Pergamino. Un pequeño número no se "
          "replica. Para consultas sobre la cobertura, escribir a "
          "nlebovits@pm.me.", ""]
    open(os.path.join(DST, "README.md"), "w", encoding="utf-8").write("\n".join(L))


def write_root_agents():
    L = ["# Guía para agentes — IDE Pergamino", "",
         "Espejo cloud-native de la IDE del Municipio de Pergamino "
         "(Buenos Aires, Argentina). "
         f"{sum(len(v) for v in GROUPS.values())} colecciones en "
         f"{len(GROUPS)} grupos temáticos.", "",
         "## Cómo está organizado", "",
         "El catálogo raíz enlaza a 13 subcatálogos temáticos; cada uno enlaza "
         "a sus colecciones. Los identificadores son rutas: `catastro/parcela`, "
         "`demografia/nbi`, `ambiente-y-agro/arbolado`.", ""]
    for g in GROUPS:
        t, _ = GROUP_DOCS[g]
        L.append(f"- [`{g}/`](./{g}/AGENTS.md) — {t}, {len(GROUPS[g])} colecciones")
    L += ["", "## Formato", "",
          "- **GeoParquet 1.1.0**, geometría WKB en `geometry`, EPSG:4326, "
          "columna de cobertura `bbox` (struct xmin/ymin/xmax/ymax), "
          "ordenamiento espacial Hilbert, compresión ZSTD.",
          "- **PMTiles** para visualización web, con estilo MapLibre en "
          "`styles/default.json` derivado del SLD oficial del municipio.",
          "- Nombres de columna en español.", "",
          "## Consulta", "",
          "```python", "import duckdb",
          'duckdb.sql("INSTALL spatial; LOAD spatial;")',
          'duckdb.sql("""',
          "  SELECT nombre, ST_Area(geometry) AS area",
          f"  FROM read_parquet('{BASE}/limites/barrios/publico_barrios.parquet')",
          "  ORDER BY area DESC LIMIT 5",
          '""").df()', "```", "",
          "## Claves de unión útiles", "",
          "- `partida` — número de partida inmobiliaria, une las capas "
          "catastrales entre sí.",
          "- `id_calle` — identificador de calle municipal, une "
          "`vialidad/callejero` con `vialidad/callejero_listado`.",
          "- `clavera` / `radio_id` — radio censal INDEC, une las capas de "
          "`demografia/` entre sí.",
          "- `cpa` — Código Postal Argentino, único por lado de manzana; "
          "`vialidad/callejero` trae `cpa_par` y `cpa_impar`.", "",
          "## Advertencias", "",
          "- **`limites/zonas_electorales_celp` no es electoral en sentido "
          "político.** CELP es la Cooperativa Eléctrica Limitada de Pergamino; "
          "son los distritos de su gobernanza interna.",
          "- **Las capas `cobertura_agua_*` y `cobertura_cloacas_*` usan "
          "períodos de gestión de gobierno, no ventanas de validez del dato.** "
          "`cobertura_agua_de_2023_a_2027` es la cobertura de la gestión "
          "actual, no una proyección.",
          "- **`demografia/nbi`** se titula upstream \"Niveles Básicos "
          "Insatisfechos\"; el término correcto es *Necesidades* Básicas "
          "Insatisfechas (INDEC).",
          "- La fecha de los metadatos es de republicación, no del contenido. "
          "Varias capas traen `fuente` y `actualizacion` por registro, que es "
          "la señal de vigencia más confiable. `ambiente-y-agro/arbolado` y "
          "`vialidad/tipo_de_vereda` provienen del censo de 2013.",
          "- Cerca de 46 colecciones son datos de terceros (INTA, IGN, INDEC, "
          "RENABAP, CONICET, INA, ARBA, BAHRA, Correo Argentino) rehospedados "
          "por el municipio. Atribuir al organismo de origen, no al municipio.", ""]
    open(os.path.join(DST, "AGENTS.md"), "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    for g in GROUPS:
        write_group_readme(g)
        write_group_agents(g)
        print(f"  {g}: README.md + AGENTS.md")
    write_root()
    write_root_agents()
    print("  root: README.md + AGENTS.md")
