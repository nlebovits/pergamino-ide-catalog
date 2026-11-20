#!/usr/bin/env python3
"""Move every collection from the old GeoServer to GeoNode, once.

The catalog was first built from the WFS at
``https://ide.pergamino.gob.ar:8443/geoserver/wfs``. The municipality now
publishes through GeoNode, and this script re-sources each collection from
it. It ran once, on the date of the second version of every collection that
existed before. It is kept so the migration can be read and repeated.

Input is a raw extract of every mirrored layer, written beforehand with

    portolan extract wfs https://geonode.pergamino.gob.ar/geoserver/ows \\
        sources/geonode --raw --auto --output-crs EPSG:4326 \\
        --wfs-version 2.0.0 --layers <every alternate in sources.json>

For each collection in ``tools/sources.json`` it:

1. Repairs, sorts and hashes the raw extract (``tools/extract.py``) into
   ``catalog/<group>/<leaf>/<leaf>.parquet``, and builds its PMTiles.
2. Keeps the existing style when GeoNode's style says the same thing, and
   takes GeoNode's style when the municipality changed it. A graduated SLD,
   which the CLI does not convert, becomes a ``step`` style.
3. Replaces the legend with the one GeoNode serves.
4. Records the old file, still published at ``publico_<layer>.parquet``, as
   the collection's first version, and the GeoNode extract as the current
   one (``tools/stac_versions.py``).
5. Deletes the CLI's ``versions.json`` and ``.portolan/`` files, which
   described the old layout.

Collections whose dataset is not in ``sources.json`` leave the catalog. Their
files stay in the bucket, because publishing never deletes.

    python3 tools/generate/migrate_geonode.py sources/geonode
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(HERE))

import build_collection  # noqa: E402
import extract  # noqa: E402
import geonode  # noqa: E402
import stac_versions as stac  # noqa: E402
import snapshot  # noqa: E402
from styles import place_style  # noqa: E402

CATALOG = ROOT / "catalog"
FIRST_COMMIT = "ced500a"
OLD_WFS = "https://ide.pergamino.gob.ar:8443/geoserver/wfs"


def old_collection(collection: str) -> dict | None:
    """The collection.json as the first commit published it, if any."""
    proc = subprocess.run(
        ["git", "show", f"{FIRST_COMMIT}:catalog/{collection}/collection.json"],
        cwd=ROOT, capture_output=True, text=True)
    return json.loads(proc.stdout) if proc.returncode == 0 else None


def first_version(collection: str) -> tuple[dict, str] | None:
    """The old data asset as a version, and its href, if one exists."""
    old = old_collection(collection)
    if old is None:
        return None
    key, asset = next((k, a) for k, a in old["assets"].items()
                      if "data" in (a.get("roles") or [])
                      and a.get("type") == stac.PARQUET)
    created = old.get("updated")
    version = {
        "version": created[:10],
        "created": created,
        "table:row_count": old.get("table:row_count"),
        "file:size": asset["file:size"],
        "file:checksum": asset["file:checksum"],
        "pergamino:archive_note": (
            "Primera versión de la colección, extraída del GeoServer "
            f"anterior de la IDE Pergamino ({OLD_WFS}, capa "
            f"publico:{key.removeprefix('publico_')}). Es anterior a la "
            "publicación de la capa en GeoNode y no cambia."),
    }
    return version, asset["href"]


def clean_old_files(folder: Path, leaf: str) -> None:
    """Remove the files that described the old layout."""
    for name in ("versions.json",):
        (folder / name).unlink(missing_ok=True)
    shutil.rmtree(folder / ".portolan", ignore_errors=True)
    for path in folder.glob("publico_*.pmtiles"):
        path.unlink()
    for path in folder.glob("publico_*.thumb.*"):
        path.rename(folder / f"{leaf}.thumb{path.suffix}")


def migrate_one(collection: str, entry: dict, record: dict,
                staging: Path, stamp: str) -> str:
    leaf = stac.leaf(collection)
    folder = CATALOG / collection
    layer = staging / entry["alternate"].replace(":", "_")
    if not layer.is_dir():
        raise RuntimeError(f"no raw extract at {layer}")
    with tempfile.TemporaryDirectory(prefix=f"migrate-{leaf}-") as tmp:
        work = Path(tmp) / "layer"
        shutil.copytree(layer, work)
        result = extract.process(work, Path(tmp) / "out", leaf)
        fresh_style = result.style or extract.graduated_style(
            entry["alternate"], leaf, Path(tmp) / "out")
        if fresh_style is not None:
            extract.repair_style(entry["alternate"], fresh_style,
                                 result.parquet)
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(result.parquet, folder / f"{leaf}.parquet")
        style = place_style(folder, fresh_style, leaf)
        if result.legend:
            (folder / "legends").mkdir(exist_ok=True)
            shutil.copyfile(result.legend, folder / "legends" / "source.png")
    clean_old_files(folder, leaf)
    extract.make_pmtiles(folder / f"{leaf}.parquet",
                         folder / f"{leaf}.pmtiles", leaf)

    archive_href = None
    first = first_version(collection)
    path = folder / "collection.json"
    if first is not None and path.exists():
        doc = json.loads(path.read_text())
        version, archive_href = first
        doc["assets"] = {leaf: {"href": archive_href, **version}}
        stac.write_json(path, doc)
    elif path.exists():
        path.unlink()

    source_updated = geonode.clean_stamp(record["last_updated"])
    build_collection.build(
        CATALOG, collection, entry, record, updated=stamp,
        new_version={
            "version": stamp[:10],
            "created": stamp,
            "pergamino:source_updated": source_updated,
            "pergamino:content_hash": result.content_hash,
            "pergamino:repaired_geometries": result.repaired,
            "pergamino:null_geometries": result.null_geometries,
        },
        archive_href=archive_href)
    return (f"{result.rows} rows, style {style}, "
            f"{'second version' if first else 'first version'}")


def drop_unmapped(collections: dict) -> list[str]:
    """Remove collection folders that sources.json no longer lists."""
    dropped = []
    for path in sorted(CATALOG.glob("*/*/collection.json")):
        collection = str(path.parent.relative_to(CATALOG))
        doc = json.loads(path.read_text())
        # Imagery and the virtual collections are not GeoNode layers.
        if collection.startswith("imagenes/") or "pergamino:virtual" in doc:
            continue
        if collection not in collections:
            shutil.rmtree(path.parent)
            dropped.append(collection)
    return dropped


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("staging", type=Path)
    parser.add_argument("--only", help="comma-separated collection ids")
    args = parser.parse_args()

    sources = geonode.load_sources()["collections"]
    records = snapshot.refresh(sorted(sources))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    names = [n.strip() for n in args.only.split(",")] if args.only else \
        sorted(sources)
    failed = []
    for name in names:
        entry = sources[name]
        try:
            detail = migrate_one(name, entry, records[entry["alternate"]],
                                 args.staging, stamp)
            print(f"ok    {name:55} {detail}", flush=True)
        except Exception as exc:  # noqa: BLE001 - report and go on
            failed.append(name)
            print(f"FAIL  {name:55} {exc}", flush=True)
    if not args.only:
        for name in drop_unmapped(sources):
            print(f"drop  {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
