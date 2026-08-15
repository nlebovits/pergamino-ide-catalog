"""Apply per-collection metadata that `portolan add` cannot derive.

Run this LAST, after every `add` invocation. `add` regenerates collection.json
and, through the hierarchical metadata.yaml resolution, overwrites each
collection's title with the catalog root's title. It also rewrites
stac_extensions with the schema version the CLI ships rather than the one the
current spec release defines.

Everything here is idempotent and derived from the harvested upstream metadata,
so it can be re-run after any add.
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grouping import GROUPS  # noqa: E402
from group_descriptions import HAND_WRITTEN  # noqa: E402

SCHEMA = "https://schemas.portolan-sdi.org/portolan/v0.1.1/schema.json"
DST = sys.argv[1]
META = json.load(open(sys.argv[2], encoding="utf-8"))

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
ORIGINATORS = {
    "INTA": ("Instituto Nacional de Tecnología Agropecuaria (INTA)", "https://www.argentina.gob.ar/inta"),
    "IGN": ("Instituto Geográfico Nacional (IGN)", "https://www.ign.gob.ar/"),
    "INDEC": ("Instituto Nacional de Estadística y Censos (INDEC)", "https://www.indec.gob.ar/"),
    "CONICET": ("Consejo Nacional de Investigaciones Científicas y Técnicas (CONICET)", "https://www.conicet.gov.ar/"),
    "INA": ("Instituto Nacional del Agua (INA)", "https://www.argentina.gob.ar/ina"),
    "BAHRA": ("Base de Asentamientos Humanos de la República Argentina (BAHRA)", "http://www.bahra.gob.ar/"),
    "CARTOARBA": ("Agencia de Recaudación de la Provincia de Buenos Aires (ARBA)", "https://carto.arba.gov.ar/"),
    "ARBA": ("Agencia de Recaudación de la Provincia de Buenos Aires (ARBA)", "https://carto.arba.gov.ar/"),
    "Correo Argentino": ("Correo Oficial de la República Argentina", "https://www.correoargentino.com.ar/"),
    "IDECOM": ("IDECOM - Ente Nacional de Comunicaciones (ENACOM)", "https://www.enacom.gob.ar/"),
    "ABS-IATASA": ("UTE IATASA - ABS S.A.", None),
    "PBA": ("Provincia de Buenos Aires", None),
    "UNNOBA": ("Universidad Nacional del Noroeste de la Provincia de Buenos Aires", "https://unnoba.edu.ar/"),
}

# Titles that would otherwise render as a raw slug.
TITLE_OVERRIDES = {
    "reductores_de_velocidad": "Reductores de velocidad",
}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def leaf_name(group, layer):
    prefix = group.split("-")[0] + "_"
    if layer.startswith(prefix) and len(layer) > len(prefix):
        return layer[len(prefix):]
    return layer


def title_for(layer):
    if layer in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[layer]
    if layer in HAND_WRITTEN:
        return HAND_WRITTEN[layer][0]
    m = META.get(layer, {}) or {}
    for key in ("gn_title", "wfs_title"):
        t = (m.get(key) or "").strip()
        if t and t.lower().replace(" ", "_") != layer.lower():
            return t
    return layer.replace("_", " ").capitalize()


def description_for(layer, existing):
    if layer in HAND_WRITTEN:
        return HAND_WRITTEN[layer][1]
    m = META.get(layer, {}) or {}
    for key in ("gn_abstract", "wfs_abstract"):
        v = (m.get(key) or "").strip()
        if v:
            return v
    return existing


def providers_for(layer):
    attr = (META.get(layer, {}) or {}).get("gn_attribution", "") or ""
    parts = [p.strip() for p in attr.split(",")[1:] if p.strip()]
    extra = []
    for p in parts:
        if p in ORIGINATORS:
            name, url = ORIGINATORS[p]
            e = {"name": name, "roles": ["producer", "licensor"]}
            if url:
                e["url"] = url
            extra.append(e)
    if not extra:
        return [dict(PROVIDER_MUNI), dict(PROVIDER_HOST)]
    muni = dict(PROVIDER_MUNI)
    muni["roles"] = ["processor"]
    return extra + [muni, dict(PROVIDER_HOST)]


def main():
    changed = 0
    for group, layers in GROUPS.items():
        gdir = os.path.join(DST, group)
        child_links = []
        for layer in sorted(layers):
            leaf = leaf_name(group, layer)
            cpath = os.path.join(gdir, leaf, "collection.json")
            if not os.path.exists(cpath):
                print(f"  missing: {group}/{leaf}", file=sys.stderr)
                continue
            col = json.load(open(cpath, encoding="utf-8"))
            col["id"] = f"{group}/{leaf}"
            col["title"] = title_for(layer)
            col["description"] = description_for(layer, col.get("description", ""))
            col["providers"] = providers_for(layer)
            col["updated"] = now()

            ext = [e for e in col.get("stac_extensions", []) if "portolan" not in e]
            col["stac_extensions"] = sorted(set(ext + [SCHEMA]))

            links = []
            for ln in col.get("links", []):
                if ln.get("rel") == "self":
                    continue
                if ln.get("rel") == "root":
                    ln["href"] = "../../catalog.json"
                elif ln.get("rel") == "parent":
                    ln["href"] = "../catalog.json"
                links.append(ln)
            col["links"] = links

            json.dump(col, open(cpath, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
            changed += 1
            child_links.append({
                "rel": "child",
                "href": f"./{leaf}/collection.json",
                "type": "application/json",
                "title": col["title"],
            })

        gcat_path = os.path.join(gdir, "catalog.json")
        gcat = json.load(open(gcat_path, encoding="utf-8"))
        gcat["links"] = [l for l in gcat["links"] if l.get("rel") != "child"]
        insert = next((i for i, l in enumerate(gcat["links"])
                       if l.get("rel") in ("agents", "describedby")), len(gcat["links"]))
        gcat["links"][insert:insert] = child_links
        gcat["stac_extensions"] = [SCHEMA]
        gcat["updated"] = now()
        json.dump(gcat, open(gcat_path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)

    # The root must declare the same profile schema version as everything under
    # it. Rashid resolves the profile from the root and validates every object
    # against that one, so a root left on an older version fails the whole tree.
    rpath = os.path.join(DST, "catalog.json")
    root = json.load(open(rpath, encoding="utf-8"))
    root["stac_extensions"] = [SCHEMA]
    root["id"] = "pergamino-ide"
    root["title"] = "IDE Pergamino - Infraestructura de Datos Espaciales"
    root["updated"] = now()
    root["links"] = [l for l in root.get("links", []) if l.get("rel") != "self"]
    have = {(l.get("rel"), l.get("href")) for l in root["links"]}
    for extra in (
        {"rel": "agents", "href": "./AGENTS.md", "type": "text/markdown",
         "title": "Guía para agentes de IA"},
        {"rel": "describedby", "href": "./README.md", "type": "text/markdown",
         "title": "Documentación"},
        {"rel": "via", "href": "https://geonode.pergamino.gob.ar/",
         "type": "text/html", "title": "IDE Pergamino (fuente original)"},
    ):
        if (extra["rel"], extra["href"]) not in have:
            root["links"].append(extra)
    json.dump(root, open(rpath, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"applied metadata to {changed} collections, "
          f"{len(GROUPS)} sub-catalogs, and the root")


if __name__ == "__main__":
    main()
