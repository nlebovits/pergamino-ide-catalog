#!/usr/bin/env python3
"""Write one vector collection's ``collection.json`` from its sources.

Everything in the file comes from three places, and nothing is hand-edited:

- the GeoNode dataset record (title, abstract, attribution, keywords,
  maintenance frequency, ``last_updated``)
- the collection's files in ``catalog/<group>/<leaf>/``: the GeoParquet for
  columns, row count, geometry type and extent, and the PMTiles, style,
  legend and thumbnail when they exist
- the version history already in ``collection.json`` (``stac_versions.py``)

``build`` is idempotent. Run it again with the same inputs and the file does
not change, apart from ``updated``.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "generate"))

import geonode  # noqa: E402
import stac_versions as stac  # noqa: E402
from assets import normalize_assets  # noqa: E402
from group_descriptions import HAND_WRITTEN  # noqa: E402
from grouping import TITLES  # noqa: E402

SCHEMA = "https://schemas.portolan-sdi.org/portolan/v0.3.0/schema.json"
EXTENSIONS = [
    SCHEMA,
    "https://stac-extensions.github.io/file/v2.1.0/schema.json",
    "https://stac-extensions.github.io/table/v1.2.0/schema.json",
    stac.VERSION_EXT,
    "https://stac-extensions.github.io/web-map-links/v1.3.0/schema.json",
]
LICENSE = "CC-BY-SA-4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
ROOT_TITLE = "IDE Pergamino - Infraestructura de Datos Espaciales"
PMTILES_MAX_ZOOM = 15

PROVIDER_MUNI = {
    "name": "Municipalidad de Pergamino",
    "description": (
        "Dirección de Sistemas de Información Georreferenciada (DSIG), "
        "Subsecretaría de Modernización, Innovación y Tecnología"
    ),
    "roles": ["producer", "licensor"],
    "url": "https://pergamino.ar/servicios/ide-pergamino/",
}
PROVIDER_HOST = {
    "name": "Source Cooperative",
    "roles": ["host"],
    "url": "https://source.coop/nlebovits/pergamino-ide",
    "email": "nlebovits@pm.me",
}
# The organisations GeoNode names in ``attribution`` after the municipality.
ORIGINATORS = {
    "INTA": ("Instituto Nacional de Tecnología Agropecuaria (INTA)",
             "https://www.argentina.gob.ar/inta"),
    "IGN": ("Instituto Geográfico Nacional (IGN)", "https://www.ign.gob.ar/"),
    "INDEC": ("Instituto Nacional de Estadística y Censos (INDEC)",
              "https://www.indec.gob.ar/"),
    "CONICET": ("Consejo Nacional de Investigaciones Científicas y Técnicas "
                "(CONICET)", "https://www.conicet.gov.ar/"),
    "INA": ("Instituto Nacional del Agua (INA)",
            "https://www.argentina.gob.ar/ina"),
    "BAHRA": ("Base de Asentamientos Humanos de la República Argentina "
              "(BAHRA)", "http://www.bahra.gob.ar/"),
    "CARTOARBA": ("Agencia de Recaudación de la Provincia de Buenos Aires "
                  "(ARBA)", "https://carto.arba.gov.ar/"),
    "ARBA": ("Agencia de Recaudación de la Provincia de Buenos Aires (ARBA)",
             "https://carto.arba.gov.ar/"),
    "Correo Argentino": ("Correo Oficial de la República Argentina",
                         "https://www.correoargentino.com.ar/"),
    "IDECOM": ("IDECOM - Ente Nacional de Comunicaciones (ENACOM)",
               "https://www.enacom.gob.ar/"),
    "ABS-IATASA": ("UTE IATASA - ABS S.A.", None),
    "PBA": ("Provincia de Buenos Aires", None),
    "UNNOBA": ("Universidad Nacional del Noroeste de la Provincia de Buenos "
               "Aires", "https://unnoba.edu.ar/"),
    "RENABAP": ("Registro Nacional de Barrios Populares (RENABAP)",
                "https://www.argentina.gob.ar/habitat/renabap"),
}

# Column descriptions this build can state, because the build makes them.
OWN_COLUMNS = {
    "geometry": "Geometría del objeto en WKB, EPSG:4326.",
    "bbox": ("Caja envolvente de la geometría (xmin, ymin, xmax, ymax), "
             "columna de cobertura de GeoParquet 1.1 para filtros "
             "espaciales."),
}

# GeoNode answers these when a field was left empty.
EMPTY = {"", "no information provided", "ninguna", "ninguna.", "none"}


def text(value: str | None) -> str:
    """GeoNode's raw_* text, unescaped and with whitespace collapsed."""
    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    value = re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()
    return "" if value.lower() in EMPTY else value


def gn_layer(entry: dict) -> str:
    return entry["alternate"].split(":")[-1]


def title_for(entry: dict, record: dict) -> str:
    layer = gn_layer(entry)
    if layer in HAND_WRITTEN:
        return HAND_WRITTEN[layer][0]
    title = text(record.get("title"))
    if title and title.lower().replace(" ", "_") != layer.lower():
        return title
    return layer.replace("_", " ").capitalize()


def description_for(entry: dict, record: dict) -> str:
    layer = gn_layer(entry)
    if layer in HAND_WRITTEN:
        return HAND_WRITTEN[layer][1]
    return text(record.get("raw_abstract") or record.get("abstract"))


def originators(record: dict) -> list[str]:
    """The third-party organisations GeoNode's attribution names."""
    parts = [p.strip() for p in (record.get("attribution") or "").split(",")]
    return [p for p in parts[1:] if p in ORIGINATORS]


def providers_for(record: dict) -> list[dict]:
    extra = []
    for key in originators(record):
        name, url = ORIGINATORS[key]
        entry = {"name": name, "roles": ["producer", "licensor"]}
        if url:
            entry["url"] = url
        extra.append(entry)
    if not extra:
        return [dict(PROVIDER_MUNI), dict(PROVIDER_HOST)]
    muni = dict(PROVIDER_MUNI, roles=["processor"])
    return extra + [muni, dict(PROVIDER_HOST)]


def keywords_for(record: dict) -> list[str]:
    seen, out = set(), []
    for kw in record.get("keywords") or []:
        name = text(kw.get("name"))
        if name and name.lower() not in seen:
            seen.add(name.lower())
            out.append(name)
    return out


def parquet_facts(path: Path) -> dict:
    """Columns, row count, geometry types and bbox, read from the file."""
    import pyarrow.parquet as pq

    handle = pq.ParquetFile(path)
    schema = handle.schema_arrow
    facts = {"rows": handle.metadata.num_rows, "columns": [],
             "bbox": None, "geometry_types": []}
    for field in schema:
        column = {"name": field.name, "type": str(field.type)}
        if field.name in OWN_COLUMNS:
            column["description"] = OWN_COLUMNS[field.name]
        facts["columns"].append(column)
    geo = (schema.metadata or {}).get(b"geo")
    if geo:
        column = json.loads(geo)["columns"].get("geometry", {})
        bbox = column.get("bbox")
        if bbox:
            facts["bbox"] = [round(v, 7) for v in bbox]
        facts["geometry_types"] = column.get("geometry_types", [])
    return facts


def union(boxes: list[list[float]]) -> list[float] | None:
    boxes = [b for b in boxes if b]
    if not boxes:
        return None
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]


def extent_bbox(folder: Path, facts: dict, old: dict,
                assets: dict) -> list[float]:
    """The bbox of every published version, not only the current one.

    Each archived version stays an asset, so the extent covers its rows too.
    Its bbox comes from the archived file when it is here, and otherwise from
    the extent the document already records, which covered it when it was
    archived.
    """
    boxes = [facts["bbox"]]
    for key, asset in assets.items():
        if not key.startswith(stac.ARCHIVE_PREFIX):
            continue
        path = folder / asset["href"].removeprefix("./")
        if path.exists():
            boxes.append(parquet_facts(path)["bbox"])
        elif old:
            boxes.append(old["extent"]["spatial"]["bbox"][0])
    return union(boxes) or [-180, -90, 180, 90]


def recorded_facts(old: dict) -> dict:
    """The facts an existing collection.json records about its data.

    A CI checkout has no data files, which are not in git. A rebuild that
    changes only metadata reads the facts from the document instead.
    """
    types = old.get("geoparquet:geometry_type") or []
    return {"rows": old["table:row_count"], "columns": old["table:columns"],
            "bbox": old["extent"]["spatial"]["bbox"][0],
            "geometry_types": [types] if isinstance(types, str) else types}


def links_for(collection: str, entry: dict, title: str, group_title: str,
              has_pmtiles: bool, leaf: str) -> list[dict]:
    links = [
        {"rel": "root", "href": "../../catalog.json",
         "type": "application/json", "title": ROOT_TITLE},
        {"rel": "parent", "href": "../catalog.json",
         "type": "application/json", "title": group_title},
        {"rel": "license", "href": LICENSE_URL, "type": "text/html",
         "title": "Creative Commons Atribución-CompartirIgual 4.0"},
        {"rel": "via", "href": geonode.page_url(entry["pk"]),
         "type": "text/html",
         "title": f"{title} en GeoNode (IDE Pergamino)"},
        {"rel": "related", "href": geonode.wfs_url(entry["alternate"]),
         "type": "application/gml+xml; version=3.2",
         "title": f"Servicio WFS de origen ({entry['alternate']})"},
        {"rel": "describedby", "href": "./README.md",
         "type": "text/markdown", "title": "Documentación"},
        {"rel": "agents", "href": "./AGENTS.md", "type": "text/markdown",
         "title": "Guía para agentes de IA"},
    ]
    if has_pmtiles:
        links.append({"rel": "pmtiles", "href": f"./{leaf}.pmtiles",
                      "type": "application/vnd.pmtiles",
                      "title": "Teselas vectoriales",
                      "pmtiles:layers": [leaf]})
    return links


def file_asset(path: Path, **fields) -> dict:
    asset = dict(fields)
    asset.update(stac.file_fields(path))
    return asset


def build(catalog: Path, collection: str, entry: dict, record: dict, *,
          updated: str, new_version: dict | None = None,
          archive_href: str | None = None) -> dict:
    """Write ``catalog/<collection>/collection.json`` and return it.

    ``new_version`` holds the version fields of the file now at
    ``<leaf>.parquet`` (``version``, ``created``, ``pergamino:*``). When it
    is given, the outgoing current version is archived first, at
    ``archive_href`` or at ``versions/<its version>.parquet``. When it is
    None, the current version asset keeps its version fields and only its
    metadata is refreshed.
    """
    folder = catalog / collection
    leaf = stac.leaf(collection)
    group = collection.split("/")[0]
    path = folder / "collection.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    assets = dict(old.get("assets", {}))

    parquet = folder / f"{leaf}.parquet"
    local = parquet.exists()
    if not local and (new_version is not None or not old):
        raise FileNotFoundError(f"{parquet} is needed for a new version")
    facts = parquet_facts(parquet) if local else recorded_facts(old)
    if new_version is not None:
        stac.archive(assets, collection, archive_href)
        current = {k: v for k, v in assets.get(leaf, {}).items()
                   if k not in stac.VERSION_FIELDS}
        current.update(new_version)
    else:
        current = dict(assets.get(leaf, {}))
    current.update({
        "href": stac.current_href(collection),
        "type": stac.PARQUET,
        "roles": ["data"],
        "table:row_count": facts["rows"],
        **(stac.file_fields(parquet) if local else {}),
    })
    current.pop("pergamino:archive_note", None)

    keep = {k: v for k, v in assets.items()
            if k.startswith(stac.ARCHIVE_PREFIX)}
    out_assets = {leaf: current, **keep}

    pmtiles = folder / f"{leaf}.pmtiles"
    tiles_key = f"{leaf}-tiles"
    if pmtiles.exists():
        out_assets[tiles_key] = file_asset(
            pmtiles, href=f"./{leaf}.pmtiles", type="application/vnd.pmtiles",
            roles=["visual"])
    elif tiles_key in assets and new_version is None:
        out_assets[tiles_key] = dict(assets[tiles_key])
    has_tiles = tiles_key in out_assets
    style = folder / "styles" / "default.json"
    if style.exists():
        out_assets["styles/default"] = file_asset(
            style, href="./styles/default.json",
            type="application/vnd.mapbox.style+json",
            roles=["style", "default"])
    legend = folder / "legends" / "source.png"
    if legend.exists():
        out_assets["legends/source"] = file_asset(
            legend, href="./legends/source.png", type="image/png",
            roles=["legend"])
    thumbs = sorted(folder.glob("*.thumb.jpg")) + sorted(
        folder.glob("*.thumb.png"))
    if thumbs:
        thumb = thumbs[0]
        media = "image/jpeg" if thumb.suffix == ".jpg" else "image/png"
        out_assets["thumbnail"] = file_asset(
            thumb, href=f"./{thumb.name}", type=media, roles=["thumbnail"])
    readme = folder / "README.md"
    if readme.exists():
        out_assets["documentation"] = file_asset(
            readme, href="./README.md", type="text/markdown",
            roles=["documentation"])
    # A hand-written title or description survives a rebuild. The tiles,
    # data and documentation assets always take the standard text.
    for key, asset in out_assets.items():
        if key in (leaf, f"{leaf}-tiles", "documentation"):
            continue
        prior = assets.get(key, {})
        for field in ("title", "description"):
            if field in prior and field not in asset:
                asset[field] = prior[field]

    title = title_for(entry, record)
    extensions = list(EXTENSIONS)
    doc = {
        "type": "Collection",
        "id": collection,
        "stac_version": "1.1.0",
        "stac_extensions": extensions,
        "title": title,
        "description": description_for(entry, record),
        "keywords": keywords_for(record),
        "license": LICENSE,
        "providers": providers_for(record),
        "extent": {
            "spatial": {"bbox": [extent_bbox(folder, facts, old,
                                             out_assets)]},
            # GeoNode records no content time for any vector dataset, and
            # the version dates say when the catalog read the data, not
            # when the data describes. The interval stays open.
            "temporal": {"interval": [[None, None]]},
        },
        "links": links_for(collection, entry, title, TITLES[group],
                           has_tiles, leaf),
        "version": current.get("version"),
        "updated": updated,
        "pergamino:geonode_pk": entry["pk"],
        "pergamino:geonode_uuid": entry["uuid"],
        "pergamino:source_updated": current.get("pergamino:source_updated"),
        "pergamino:update_frequency": entry["update_frequency"],
        "table:primary_geometry": "geometry",
        "table:row_count": facts["rows"],
        "table:columns": facts["columns"],
        "geoparquet:geometry_type": (
            facts["geometry_types"][0] if len(facts["geometry_types"]) == 1
            else facts["geometry_types"] or None),
        "geoparquet:feature_count": facts["rows"],
        "assets": out_assets,
    }
    if has_tiles:
        doc.update({"pmtiles:min_zoom": 0,
                    "pmtiles:max_zoom": PMTILES_MAX_ZOOM,
                    "pmtiles:tile_type": "mvt",
                    "pmtiles:layers": [leaf]})
    if doc["version"] is None:
        doc.pop("version")
    if doc["geoparquet:geometry_type"] is None:
        doc.pop("geoparquet:geometry_type")
    normalize_assets(doc)
    folder.mkdir(parents=True, exist_ok=True)
    stac.write_json(path, doc)
    return doc
