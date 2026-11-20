#!/usr/bin/env python3
"""Record each extract as a version, in the Collection itself.

One copy of every extract exists in the bucket:

- ``<group>/<leaf>/<leaf>.parquet`` is the current version. Its URL never
  changes.
- ``<group>/<leaf>/versions/<version>.parquet`` holds each earlier version.
  A refresh archives the outgoing current file there before it replaces it,
  and the file never changes after that.
- The first version of a collection that existed before the move to GeoNode
  stays where it was published, at ``publico_<layer>.parquet``. It came from
  the municipality's earlier GeoServer, and moving it would break every link
  to it.

``collection.json`` describes all of them. The asset named after the leaf is
the current version. Each earlier version is an asset named
``version-<version>`` with the role ``archive``. Every version asset carries:

- ``version``: the UTC date of the extract (``2026-11-23``, or
  ``2026-11-23-2`` for a forced second run that day)
- ``created``: when this catalog extracted the rows
- ``pergamino:source_updated``: GeoNode's ``last_updated`` for the dataset
- ``table:row_count``, ``file:size``, ``file:checksum``
- ``pergamino:content_hash``: an order-independent hash of the rows, which
  the refresh uses to skip an extract that changed nothing

The Collection's ``version`` names the current version (STAC version
extension, PORTO-CORE-008).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

VERSION_EXT = "https://stac-extensions.github.io/version/v1.2.0/schema.json"
PARQUET = "application/vnd.apache.parquet"
ARCHIVE_PREFIX = "version-"
VERSION_FIELDS = (
    "version", "created", "pergamino:source_updated", "table:row_count",
    "pergamino:content_hash", "pergamino:repaired_geometries",
    "pergamino:null_geometries", "file:size", "file:checksum",
)


def multihash(path: Path) -> str:
    """The sha2-256 multihash the file extension uses for file:checksum."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return "1220" + digest.hexdigest()


def file_fields(path: Path) -> dict:
    return {"file:size": path.stat().st_size, "file:checksum": multihash(path)}


def leaf(collection: str) -> str:
    return collection.split("/")[-1]


def current_href(collection: str) -> str:
    return f"./{leaf(collection)}.parquet"


def archive_href(version: str) -> str:
    return f"./versions/{version}.parquet"


def public_url(public_base: str, collection: str, href: str) -> str:
    """The public URL of an asset href relative to its collection."""
    return f"{public_base.rstrip('/')}/{collection}/{href.removeprefix('./')}"


def load(catalog: Path, collection: str) -> dict:
    return json.loads((catalog / collection / "collection.json").read_text())


def current(catalog: Path, collection: str) -> dict | None:
    """The current version asset, or None before the first version."""
    path = catalog / collection / "collection.json"
    if not path.exists():
        return None
    asset = load(catalog, collection)["assets"].get(leaf(collection), {})
    return asset if "version" in asset else None


def versions(catalog: Path, collection: str) -> list[str]:
    """Every version, oldest first. Versions sort as dates."""
    path = catalog / collection / "collection.json"
    if not path.exists():
        return []
    assets = load(catalog, collection)["assets"]
    found = [a["version"] for key, a in assets.items()
             if key.startswith(ARCHIVE_PREFIX)
             or (key == leaf(collection) and "version" in a)]
    return sorted(found)


def next_version(catalog: Path, collection: str, day: str) -> str:
    """``day``, or ``day-2``, ``day-3``... when a forced rerun repeats a day."""
    taken = set(versions(catalog, collection))
    label, n = day, 1
    while label in taken:
        n += 1
        label = f"{day}-{n}"
    return label


def archive(assets: dict, collection: str, href: str | None = None) -> None:
    """Turn the current version asset into ``version-<its version>``.

    The outgoing asset keeps its size and checksum, so a reader can prove the
    archive holds the bytes that were current. ``href`` overrides where the
    archive lives, for the first version that predates this scheme.
    """
    old = assets.get(leaf(collection))
    if not old or "version" not in old:
        return
    label = old["version"]
    assets[f"{ARCHIVE_PREFIX}{label}"] = {
        "href": href or archive_href(label),
        "type": PARQUET,
        "title": f"Versión {label}",
        "description": old.get("pergamino:archive_note") or (
            f"Los registros de la capa tal como se extrajeron en la versión "
            f"{label}. El archivo no cambia."),
        "roles": ["archive"],
        **{k: old[k] for k in VERSION_FIELDS if k in old},
    }


def newest_update(catalog: Path) -> str | None:
    """The latest ``updated`` of any Collection under ``catalog``."""
    stamps = [json.loads(p.read_text()).get("updated")
              for p in catalog.glob("**/collection.json")]
    stamps = [s for s in stamps if s]
    return max(stamps) if stamps else None


def stamp_catalog(catalog: Path) -> None:
    """Set the root Catalog's ``updated`` to the newest Collection's."""
    newest = newest_update(catalog)
    path = catalog / "catalog.json"
    doc = json.loads(path.read_text())
    if newest is None or doc.get("updated") == newest:
        return
    doc["updated"] = newest
    write_json(path, doc)


def write_json(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
