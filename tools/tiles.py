"""Which attributes a collection's vector tiles keep.

By default the PMTiles carry every column of the GeoParquet. A collection
listed here keeps only the listed columns in its tiles; its GeoParquet still
keeps all of them. The list is for maps: what a style colours or filters by,
and what a viewer shows in a tooltip.

``catastro/edificaciones_automaticas`` has 33 attributes per footprint, most
of them cadastral keys that no map draws. portolan-browser draws it as the 3D
map of its home page: it extrudes by ``altura_promedio`` and shows
``altura_maxima`` and the barrio (``nombre``, ``localidad``) in a tooltip.
``styles/default.json`` colours by ``confidence``.

This lives apart from tools/sources.json because tools/geonode.py rewrites
that file from GeoNode. ``tests/test_refresh.py`` checks that every column a
collection's style reads is kept.
"""
from __future__ import annotations

TILE_COLUMNS: dict[str, list[str]] = {
    "catastro/edificaciones_automaticas": [
        "altura_minima",
        "altura_promedio",
        "altura_maxima",
        "nombre",
        "localidad",
        "confidence",
    ],
}


def tile_columns(collection: str) -> list[str] | None:
    """The columns the collection's tiles keep, or None for all of them."""
    return TILE_COLUMNS.get(collection)
