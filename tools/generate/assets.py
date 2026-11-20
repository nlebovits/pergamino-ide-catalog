"""Asset roles, titles and descriptions for a vector collection.

Portolan v0.3.0 asks every asset for a ``title`` and a ``description``
(PORTO-CORE-088), and every PMTiles asset for the ``visual`` role
(PORTO-FMT-062). The CLI wrote neither consistently, so this module sets them
from the asset's kind. It only states what the build itself guarantees about
each file, never anything about the data's content.

``normalize_assets`` is idempotent. It keeps a title or description that is
already present, so a hand-written one survives a rebuild.
"""

PARQUET = "application/vnd.apache.parquet"
PMTILES = "application/vnd.pmtiles"
STYLE = "application/vnd.mapbox.style+json"


def kind_of(key: str, asset: dict) -> str:
    """Classify an asset by media type and role."""
    media = asset.get("type", "")
    roles = asset.get("roles") or []
    if media == PMTILES:
        return "tiles"
    if media == PARQUET and "data" in roles:
        return "data"
    if media == STYLE or "style" in roles:
        return "style"
    if "thumbnail" in roles:
        return "thumbnail"
    if "legend" in roles:
        return "legend"
    if "documentation" in roles:
        return "documentation"
    return "other"


TEXT = {
    "data": (
        "Datos (GeoParquet)",
        "Todos los registros de la capa en GeoParquet, con geometría WKB en "
        "EPSG:4326 y una columna de cobertura `bbox`.",
    ),
    "tiles": (
        "Teselas vectoriales (PMTiles)",
        "Teselas vectoriales MVT generadas a partir del GeoParquet de esta "
        "colección, para visualización web.",
    ),
    "style": (
        "Estilo MapLibre",
        "Estilo MapLibre por defecto para las teselas de esta colección, "
        "derivado del estilo SLD que publica la fuente.",
    ),
    "thumbnail": (
        "Vista previa",
        "Imagen de la capa dibujada con el estilo por defecto sobre un mapa "
        "base.",
    ),
    "legend": (
        "Leyenda de la fuente",
        "Leyenda de la capa tal como la publica el servidor de la fuente.",
    ),
    "documentation": (
        "Documentación",
        "README de la colección: contenido, procedencia, licencia y acceso.",
    ),
}


def normalize_assets(collection: dict) -> dict:
    """Set roles, titles and descriptions on every asset, in place."""
    for key, asset in collection.get("assets", {}).items():
        kind = kind_of(key, asset)
        if kind == "tiles":
            asset["roles"] = ["visual"]
        if kind in TEXT:
            title, description = TEXT[kind]
            asset.setdefault("title", title)
            asset.setdefault("description", description)
    return collection
