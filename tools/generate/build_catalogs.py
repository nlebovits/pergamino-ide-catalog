#!/usr/bin/env python3
"""Rebuild the child links of the root catalog and of every group catalog.

A group's children are the collection folders under it, in name order. The
root's children are the groups in ``grouping.GROUPS`` order, then the groups
that hold other kinds of collection (``EXTRA_GROUPS``) when their folder
exists. Every other link, and every other field, is kept as it is, except
``updated``, which becomes the newest ``updated`` below the catalog.

    python3 tools/generate/build_catalogs.py catalog
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from group_descriptions import GROUP_DOCS  # noqa: E402
from grouping import GROUPS, TITLES  # noqa: E402

SCHEMA = "https://schemas.portolan-sdi.org/portolan/v0.3.0/schema.json"
# Groups built by their own tools: imagery (tools/imagery/) and the virtual
# collections over other catalogs (tools/virtual/).
EXTRA_GROUPS = ["imagenes", "externos"]


def write_json(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def child(href: str, title: str) -> dict:
    return {"rel": "child", "href": href, "type": "application/json",
            "title": title}


def relink(doc: dict, children: list[dict]) -> None:
    """Replace the child links, keeping every other link in place."""
    links = [link for link in doc["links"] if link.get("rel") != "child"]
    at = next((i for i, link in enumerate(links)
               if link.get("rel") in ("agents", "describedby")), len(links))
    doc["links"] = links[:at] + children + links[at:]


def newest(paths: list[Path]) -> str | None:
    stamps = [json.loads(p.read_text()).get("updated") for p in paths]
    stamps = [s for s in stamps if s]
    return max(stamps) if stamps else None


def build_group(catalog: Path, group: str) -> None:
    folder = catalog / group
    path = folder / "catalog.json"
    doc = json.loads(path.read_text())
    if group in GROUP_DOCS:
        doc["title"], doc["description"] = GROUP_DOCS[group]
    doc["stac_extensions"] = [SCHEMA]
    collections = sorted(folder.glob("*/collection.json"))
    children = []
    for coll in collections:
        title = json.loads(coll.read_text())["title"]
        children.append(child(f"./{coll.parent.name}/collection.json", title))
    relink(doc, children)
    stamp = newest(collections)
    if stamp:
        doc["updated"] = stamp
    write_json(path, doc)


def build_root(catalog: Path) -> None:
    path = catalog / "catalog.json"
    doc = json.loads(path.read_text())
    doc["stac_extensions"] = [SCHEMA]
    groups = list(GROUPS) + [g for g in EXTRA_GROUPS
                             if (catalog / g / "catalog.json").exists()]
    children = []
    for group in groups:
        title = TITLES.get(group) or json.loads(
            (catalog / group / "catalog.json").read_text())["title"]
        children.append(child(f"./{group}/catalog.json", title))
    relink(doc, children)
    stamp = newest(sorted(catalog.glob("**/collection.json")))
    if stamp:
        doc["updated"] = stamp
    write_json(path, doc)


def main() -> int:
    catalog = Path(sys.argv[1])
    for group in GROUPS:
        build_group(catalog, group)
    build_root(catalog)
    print(f"relinked {len(GROUPS)} groups and the root")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
