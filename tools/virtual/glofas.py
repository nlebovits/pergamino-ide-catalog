"""Virtual collections over the JRC GloFAS flood hazard maps.

Each GloFAS layer becomes one collection in ``ambiente-y-agro/``, named
``glofas_<layer>`` (the ``collection`` of its layer in sources.json), beside the
observed floods. The data asset is the upstream COG tile that covers the
partido, referenced in place.
The clip is a warped GDAL VRT committed beside the collection: a few lines of
XML that read the upstream COG through /vsicurl/ with the partido as cutline.

One collection per layer, not one item per layer: core.md (Raster
Collections) says a collection holding a single COG exposes it as a
collection-level asset with no item directory, and the return periods are
different variables, not scenes of one.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urljoin

import common as C

GLOFAS = C.CONFIG["glofas"]

DOI = "https://doi.org/10.2905/JRC.VD32YWG"
JRC_STORE = ("https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/"
             "flood_hazard/")
UPSTREAM_PAGE = "https://source.coop/nlebovits/jrc-glofas"

LICENSE_LINKS = [
    {"rel": "license", "href": "https://creativecommons.org/licenses/by/4.0/",
     "type": "text/html",
     "title": "CC BY 4.0 (copyright.txt del JRC)"},
    {"rel": "license", "href": "https://opendatacommons.org/licenses/odbl/1-0/",
     "type": "text/html",
     "title": "ODbL 1.0 (README.txt del JRC y Catálogo de Datos del JRC)"},
]

PROVIDERS = [
    {
        "name": "European Commission, Joint Research Centre (JRC)",
        "description": "Copernicus Emergency Management Service (CEMS), "
                       "Global Flood Awareness System (GloFAS).",
        "roles": ["producer", "licensor"],
        "url": "https://joint-research-centre.ec.europa.eu/",
    },
    {
        "name": "JRC GloFAS en Source Cooperative (nlebovits/jrc-glofas)",
        "description": "Convierte los GeoTIFF del JRC en COG y los publica. "
                       "Los bytes que referencia esta colección están allí.",
        "roles": ["processor"],
        "url": UPSTREAM_PAGE,
    },
]

# JRC README.txt, F02: "Water depth classification: 1: <1 m 2: 1–<3 m
# 3: 3–<10 m 4: >10 m". Colours are this catalog's choice.
HAZARD_CLASSES = [
    {"value": 1, "name": "menos_de_1_m", "title": "Menos de 1 m",
     "description": "Profundidad del agua menor a 1 m.",
     "color_hint": "C6DBEF"},
    {"value": 2, "name": "de_1_a_3_m", "title": "De 1 m a menos de 3 m",
     "description": "Profundidad del agua de 1 m a menos de 3 m.",
     "color_hint": "6BAED6"},
    {"value": 3, "name": "de_3_a_10_m", "title": "De 3 m a menos de 10 m",
     "description": "Profundidad del agua de 3 m a menos de 10 m.",
     "color_hint": "2171B5"},
    {"value": 4, "name": "mas_de_10_m", "title": "Más de 10 m",
     "description": "Profundidad del agua mayor a 10 m.",
     "color_hint": "08306B"},
]
WATER_CLASSES = [
    {"value": 1, "name": "agua_permanente", "title": "Agua permanente",
     "description": "Cuerpo de agua permanente usado por el JRC para "
                    "completar los mapas de peligro.",
     "color_hint": "1F78B4"},
]

DEPTH_COLORMAP = "viridis"

GDAL_ENV = {
    "GDAL_PAM_ENABLED": "NO",
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.tiff,.vrt,.parquet",
}


def _env() -> dict:
    return {**os.environ, **GDAL_ENV}


# --- upstream ------------------------------------------------------------


def upstream_collection_url(layer: dict) -> str:
    return urljoin(GLOFAS["catalog"], f"{layer['upstream']}/collection.json")


def resolve_cog(layer: dict) -> tuple[str, str]:
    """(collection URL, absolute COG href) of the tile over the partido."""
    coll_url = upstream_collection_url(layer)
    coll = C.get_json(coll_url)
    tile = GLOFAS["tile"]
    item_link = next(
        ln for ln in coll["links"]
        if ln.get("rel") == "item" and f"/{tile}/" in ln.get("href", "")
    )
    item_url = urljoin(coll_url, item_link["href"])
    item = C.get_json(item_url)
    data = next(a for a in item["assets"].values()
                if "data" in (a.get("roles") or []))
    return coll_url, urljoin(item_url, data["href"])


# --- the clip --------------------------------------------------------------


def gdalwarp_args(cog_href: str, cutline: str, out: str) -> list[str]:
    return ["gdalwarp", "-q", "-overwrite", "-of", "VRT",
            "-cutline", cutline, "-crop_to_cutline",
            f"/vsicurl/{cog_href}", out]


def recipe_command(cog_href: str, vrt_name: str) -> str:
    """The published gdalwarp call, reading the partido from its URL."""
    return (f"gdalwarp -of VRT -cutline /vsicurl/{C.PARTIDO_URL} "
            f"-crop_to_cutline /vsicurl/{cog_href} {vrt_name}")


def write_vrt(partido: C.Partido, cog_href: str, out: Path) -> None:
    """Write the clip VRT. The cutline is embedded in it as WKT.

    The cutline is read from a local GeoJSON of the full boundary, so a build
    does not depend on the boundary URL being live; the geometry is the same.
    """
    import shapely

    with tempfile.TemporaryDirectory() as tmp:
        cut = Path(tmp) / "partido.geojson"
        cut.write_text(json.dumps({
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {},
                          "geometry": json.loads(
                              shapely.to_geojson(partido.geometry))}],
        }))
        work = Path(tmp) / out.name
        subprocess.run(gdalwarp_args(cog_href, str(cut), str(work)),
                       check=True, env=_env())
        C.write_text(out, work.read_text())


def measure(vrt: Path) -> dict:
    """Size, transform and band statistics of the clip, from GDAL."""
    proc = subprocess.run(["gdalinfo", "-json", "-stats", str(vrt)],
                          check=True, capture_output=True, text=True,
                          env=_env())
    info = json.loads(proc.stdout)
    band = info["bands"][0]
    meta = (band.get("metadata") or {}).get("", {})
    stats = None
    if "minimum" in band:
        stats = {
            "minimum": round(band["minimum"], 4),
            "maximum": round(band["maximum"], 4),
            "mean": round(band["mean"], 4),
            "stddev": round(band["stdDev"], 4),
            "valid_percent": round(
                float(meta.get("STATISTICS_VALID_PERCENT", 0)), 3),
        }
    width, height = info["size"]
    gt = info["geoTransform"]
    return {
        "shape": [height, width],
        "transform": [gt[1], gt[2], gt[0], gt[4], gt[5], gt[3]],
        "data_type": band["type"].lower(),
        "nodata": band.get("noDataValue"),
        "statistics": stats,
    }


# --- metadata --------------------------------------------------------------


def titles(layer: dict) -> tuple[str, str]:
    kind = layer["kind"]
    if kind == "depth":
        return (f"Profundidad de inundación, retorno de {layer['rp']} años",
                "Profundidad del agua en metros para una crecida fluvial con "
                f"un período de retorno de {layer['rp']} años, modelada por "
                "el JRC (CEMS-GloFAS) a 3 segundos de arco, recortada al "
                "partido de Pergamino sin copiar los datos.")
    if kind == "hazard":
        return (f"Clases de profundidad de inundación, retorno de "
                f"{layer['rp']} años",
                "Profundidad del agua agrupada en cuatro clases para una "
                f"crecida fluvial con un período de retorno de {layer['rp']} "
                "años, modelada por el JRC (CEMS-GloFAS), recortada al "
                "partido de Pergamino sin copiar los datos.")
    return ("Cuerpos de agua permanentes (GloFAS)",
            "Máscara de los cuerpos de agua permanentes que el JRC usa para "
            "completar los mapas de peligro de GloFAS, recortada al partido "
            "de Pergamino sin copiar los datos.")


# GDAL type names -> STAC 1.1 data_type values.
DATA_TYPES = {"byte": "uint8", "uint16": "uint16", "int16": "int16",
              "uint32": "uint32", "int32": "int32", "float32": "float32",
              "float64": "float64", "int8": "int8"}


def raster_fields(layer: dict, m: dict, with_stats: bool) -> dict:
    """Asset-level raster fields: bands, and nodata plus classes.

    A single-band classified asset carries its classes on the asset itself,
    beside its nodata (formats.md, Classified rasters; rashid PTL-CLS-005).
    """
    band = {"name": "b1", "data_type": DATA_TYPES[m["data_type"]]}
    fields: dict = {}
    if layer["kind"] == "depth":
        if m["nodata"] is not None:
            band["nodata"] = m["nodata"]
        band["unit"] = "m"
    else:
        if m["nodata"] is not None:
            fields["nodata"] = m["nodata"]
        fields["classification:classes"] = (
            HAZARD_CLASSES if layer["kind"] == "hazard" else WATER_CLASSES)
    if with_stats and m["statistics"]:
        band["statistics"] = m["statistics"]
    return {"bands": [band], **fields}


def mask_style(partido: C.Partido, name: str) -> dict:
    """A style with no data source: the mask and the outline only.

    The COG is drawn from its render definition; the style hides what lies
    outside the partido and traces the boundary.
    """
    return {
        "version": 8,
        "name": name,
        "sources": {
            "mascara": {"type": "geojson",
                        "data": C.mask_geometry(partido)},
            "partido": {"type": "geojson",
                        "data": C.partido_outline(partido)},
        },
        "layers": [
            {"id": "mascara", "type": "fill", "source": "mascara",
             "paint": {"fill-color": "#ffffff", "fill-opacity": 0.85}},
            {"id": "partido", "type": "line", "source": "partido",
             "paint": {"line-color": "#333333", "line-width": 1.2}},
        ],
    }


def thumbnail_asset(thumb: Path) -> dict:
    return {
        "href": f"./{thumb.name}",
        "type": "image/jpeg",
        "roles": ["thumbnail"],
        "title": "Vista previa",
        "description": (
            "La ventana del partido dibujada con la rampa o las clases "
            "por defecto sobre un mapa base, con la máscara aplicada."),
        **C.file_fields(thumb),
    }


def build_collection(layer: dict, partido: C.Partido, coll_url: str,
                     cog: str, m: dict, rescale_max: float,
                     thumb: Path | None) -> dict:
    cid = layer["collection"]
    folder = C.folder(cid)
    title, description = titles(layer)
    vrt_name = f"{C.leaf(cid)}.vrt"
    vrt_url = C.public_url(f"{cid}/{vrt_name}")

    ext = [C.EXT["portolan"], C.EXT["file"], C.EXT["proj"],
           C.EXT["processing"]]
    if layer["kind"] == "depth":
        ext.append(C.EXT["render"])
    else:
        ext.append(C.EXT["classification"])

    data_asset = {
        "href": cog,
        "type": C.COG_TYPE,
        "roles": ["data", "external"],
        "title": "Tesela COG de GloFAS (externa)",
        "description": (
            f"Tesela {GLOFAS['tile']} de la capa `{layer['upstream']}` del "
            "catálogo nlebovits/jrc-glofas. Cubre 10° × 10°; el partido es "
            "una ventana dentro de ella. Los bytes no se copian a este "
            "catálogo."),
        **raster_fields(layer, m, with_stats=False),
        "processing:expression": {
            "format": "gdalwarp",
            "expression": recipe_command(cog, vrt_name),
        },
    }
    vrt_asset = {
        "href": f"./{vrt_name}",
        "type": C.VRT_TYPE,
        "roles": C.RECIPE_ROLES,
        "title": "Recorte al partido (GDAL VRT)",
        "description": (
            "VRT de GDAL que lee la tesela externa por /vsicurl/ y la recorta "
            "al límite oficial del partido. Abrirlo con GDAL, QGIS o rasterio "
            "lee solo la ventana del partido. Las estadísticas de la banda "
            "describen esa ventana."),
        "proj:code": "EPSG:4326",
        "proj:shape": m["shape"],
        "proj:transform": [round(v, 12) for v in m["transform"]],
        **raster_fields(layer, m, with_stats=True),
        **C.file_fields(folder / vrt_name),
    }
    style_path = folder / "styles" / "default.json"
    assets = {
        "data": data_asset,
        "recorte": vrt_asset,
        "style": {
            "href": "./styles/default.json",
            "type": C.STYLE_TYPE,
            "roles": ["style", "default"],
            "title": "Máscara del partido",
            "description": (
                "Estilo MapLibre que cubre todo lo que queda fuera del "
                "partido y traza su límite. El ráster se dibuja con la "
                "definición `renders` o con las clases de la banda."),
            **C.file_fields(style_path),
        },
    }
    if thumb is not None and thumb.exists():
        assets["thumbnail"] = thumbnail_asset(thumb)

    doc = {
        "type": "Collection",
        "id": cid,
        "stac_version": "1.1.0",
        "stac_extensions": ext,
        "title": title,
        "description": description,
        "keywords": ["inundación", "peligro", "GloFAS", "JRC", "Copernicus",
                     "Pergamino"],
        "license": "other",
        "providers": PROVIDERS + [C.host_provider()],
        "extent": {
            "spatial": {"bbox": [partido.bbox]},
            "temporal": {"interval": [[None, None]]},
        },
        "links": C.collection_links(cid) + C.doc_links() + [
            {"rel": "via", "href": DOI, "type": "text/html",
             "title": "Global river flood hazard maps (JRC, DOI)"},
            {"rel": "via", "href": JRC_STORE, "type": "text/html",
             "title": "Descarga original del JRC (CEMS-GLOFAS/flood_hazard)"},
            {"rel": "derived_from", "href": coll_url,
             "type": "application/json",
             "title": f"Colección {layer['upstream']} en nlebovits/jrc-glofas"},
        ] + LICENSE_LINKS,
        "assets": assets,
        "pergamino:virtual": {
            "upstream_catalog": GLOFAS["catalog"],
            "upstream_collection": layer["upstream"],
            "tile": GLOFAS["tile"],
            "recipe": vrt_url,
        },
    }
    if layer["kind"] == "depth":
        doc["renders"] = {
            "profundidad": {
                "title": "Profundidad (m)",
                "assets": ["data"],
                "nodata": m["nodata"],
                "rescale": [[0, rescale_max]],
                "colormap_name": DEPTH_COLORMAP,
            }
        }
    return doc


def build(partido: C.Partido, docs, now) -> list[str]:
    """Write every GloFAS collection. Returns the collection ids written."""
    layers = GLOFAS["layers"]
    resolved = {}
    measured = {}
    for layer in layers:
        cid = layer["collection"]
        folder = C.folder(cid)
        folder.mkdir(parents=True, exist_ok=True)
        coll_url, cog = resolve_cog(layer)
        resolved[layer["id"]] = (coll_url, cog)
        vrt = folder / f"{C.leaf(cid)}.vrt"
        write_vrt(partido, cog, vrt)
        measured[layer["id"]] = measure(vrt)
        print(f"  {cid}: {measured[layer['id']]['shape']}")

    depth_max = max(
        measured[ly["id"]]["statistics"]["maximum"]
        for ly in layers
        if ly["kind"] == "depth" and measured[ly["id"]]["statistics"]
    )
    rescale_max = float(int(depth_max) + 1)

    written = []
    for layer in layers:
        cid = layer["collection"]
        folder = C.folder(cid)
        C.write_json(folder / "styles" / "default.json",
                     mask_style(partido, titles(layer)[0]))
        coll_url, cog = resolved[layer["id"]]
        thumb = folder / f"{C.leaf(cid)}.thumb.jpg"
        doc = build_collection(layer, partido, coll_url, cog,
                               measured[layer["id"]], rescale_max, thumb)
        docs.write_glofas(layer, doc, folder)
        path = folder / "collection.json"
        C.write_json(path, C.keep_updated(path, doc, now))
        written.append(doc["id"])
    return written
