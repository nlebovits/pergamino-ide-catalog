"""The collections a catalog browser shows first.

portolan-browser builds its featured row from the collections whose
``keywords`` carry ``FEATURED_KEYWORD``; it never keys on a collection id.
Each collection builder passes its keywords through ``with_featured``, so a
rebuild keeps the keyword and nothing else needs to remember it. The order
of the row is the browser's to set.

``tests/test_refresh.py`` checks that these collections, and only these,
carry the keyword.
"""
from __future__ import annotations

FEATURED_KEYWORD = "destacado"

FEATURED: tuple[str, ...] = (
    "imagenes/ortofotos_10cm_2022",
    "catastro/edificaciones_automaticas",
    "ambiente-y-agro/glofas_profundidad_rp100",
)


def with_featured(collection: str, keywords: list[str]) -> list[str]:
    """keywords, with FEATURED_KEYWORD appended when the collection is
    featured and removed when it is not."""
    out = [k for k in keywords if k != FEATURED_KEYWORD]
    if collection in FEATURED:
        out.append(FEATURED_KEYWORD)
    return out
