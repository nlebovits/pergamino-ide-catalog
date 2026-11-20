"""Virtual collections over Overture Maps.

Each Overture type becomes one collection under ``externos/overture/``. Its
items are the upstream GeoParquet part files whose bbox meets the partido,
referenced in place: one item per part, as the overture-portolan mirror does.
The clip is a DuckDB file of views, ``externos/overture/pergamino_overture.ddb``,
shared by the four collections so one ATTACH reaches every layer.

Resolution, in order (recorded per collection in ``pergamino:resolved_via``):

1. ``overture-portolan``: the metadata-only mirror this catalog derives from.
   Its canonical link names the release; its items name the part files. Used
   only when every selected part answers 200.
2. ``overture-stac``: Overture's own STAC. ``latest`` names the release and
   the release's ``collections.parquet`` indexes every part with its bbox.

Overture keeps a few releases and deletes older ones, and part names carry a
per-release UUID, so a pinned href dies within months. ``refresh.py`` runs
this resolution weekly.
"""
from __future__ import annotations

import gzip
import json
import shutil
import struct
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlparse

import common as C

OVERTURE = C.CONFIG["overture"]
SUBDIR = C.CATALOG / C.GROUP / "overture"
SUBCATALOG_TITLE = "Overture Maps"
DDB_NAME = "pergamino_overture.ddb"
STAC_HOST = "https://stac.overturemaps.org"
ATTRIBUTION = "https://docs.overturemaps.org/attribution/"

TITLES = {
    "building": ("Edificios (Overture Maps)",
                 "Huellas de edificios de Overture Maps dentro del partido "
                 "de Pergamino, referenciadas sin copiar los datos."),
    "place": ("Lugares de interés (Overture Maps)",
              "Lugares de interés (comercios, servicios, instituciones) de "
              "Overture Maps dentro del partido de Pergamino, referenciados "
              "sin copiar los datos."),
    "segment": ("Segmentos de transporte (Overture Maps)",
                "Segmentos de calles, caminos, vías férreas y vías "
                "navegables de Overture Maps dentro del partido de "
                "Pergamino, referenciados sin copiar los datos."),
    "land_use": ("Uso del suelo (Overture Maps)",
                 "Polígonos de uso del suelo de Overture Maps dentro del "
                 "partido de Pergamino, referenciados sin copiar los datos."),
}

GUIDES = {
    "buildings": "https://docs.overturemaps.org/guides/buildings/",
    "places": "https://docs.overturemaps.org/guides/places/",
    "transportation": "https://docs.overturemaps.org/guides/transportation/",
    "base": "https://docs.overturemaps.org/guides/base/",
}


def schema_page(layer: dict) -> str:
    return ("https://docs.overturemaps.org/schema/reference/"
            f"{layer['theme']}/{layer['type']}/")


# --- bbox helpers ----------------------------------------------------------


def intersects(a, b) -> bool:
    """True when two [xmin, ymin, xmax, ymax] boxes meet."""
    return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]


def bbox_of(value) -> list[float]:
    if isinstance(value, dict):
        return [value["xmin"], value["ymin"], value["xmax"], value["ymax"]]
    return list(value)


def part_id(href: str) -> str:
    """'00066' from '.../part-00066-<uuid>-c000.zstd.parquet'."""
    name = urlparse(href).path.rsplit("/", 1)[-1]
    return name.split("-")[1]


# --- resolution ------------------------------------------------------------


def release_from_canonical(href: str) -> str | None:
    """The release segment of a stac.overturemaps.org collection URL."""
    path = urlparse(href).path.strip("/").split("/")
    return path[0] if path and path[0][:2] == "20" else None


def mirror_collection_url(layer: dict) -> str:
    return urljoin(OVERTURE["mirror"],
                   f"{layer['theme']}/{layer['type']}/collection.json")


def canonical_url(release: str, layer: dict) -> str:
    return (f"{STAC_HOST}/{release}/{layer['theme']}/{layer['type']}/"
            "collection.json")


def resolve_from_mirror(layer: dict, bbox: list[float]) -> dict:
    """Parts over bbox per overture-portolan. Raises when unusable."""
    url = mirror_collection_url(layer)
    coll = C.get_json(url)
    canonical = next((ln["href"] for ln in coll.get("links", [])
                      if ln.get("rel") == "canonical"), None)
    release = release_from_canonical(canonical or "")
    if not release:
        raise RuntimeError(f"{url}: no canonical release link")
    item_urls = [urljoin(url, ln["href"]) for ln in coll.get("links", [])
                 if ln.get("rel") == "item"]
    if not item_urls:
        raise RuntimeError(f"{url}: no item links")

    # The mirror's extent lists one bbox per item, in item order. Use it to
    # pick candidates, then confirm each against the item itself. When the
    # counts disagree the hint is unusable and every item is read.
    hints = coll.get("extent", {}).get("spatial", {}).get("bbox", [])
    if len(hints) == len(item_urls):
        candidates = [u for u, b in zip(item_urls, hints)
                      if intersects(b, bbox)]
    else:
        candidates = item_urls
    with ThreadPoolExecutor(max_workers=16) as pool:
        items = list(pool.map(C.get_json, candidates))

    parts = []
    for item in items:
        if not intersects(item["bbox"], bbox):
            continue
        data = item["assets"]["data"]
        s3 = next((a["href"] for a in (data.get("alternate") or {}).values()
                   if a.get("href", "").startswith("s3://")), None)
        parts.append({"id": part_id(data["href"]), "href": data["href"],
                      "s3": s3, "bbox": item["bbox"]})
    if not parts:
        raise RuntimeError(f"{url}: no part meets the partido bbox")
    dead = [p["href"] for p in parts if C.probe(p["href"]) != 200]
    if dead:
        raise RuntimeError(f"{len(dead)} mirror href(s) do not answer 200, "
                           f"first {dead[0]}")
    return {"release": release, "parts": sorted(parts, key=lambda p: p["id"]),
            "resolved_via": "overture-portolan", "mirror": url}


def latest_release() -> str:
    return C.get_json(OVERTURE["stac"])["latest"]


def resolve_from_stac(layer: dict, bbox: list[float],
                      release: str | None = None) -> dict:
    """Parts over bbox per Overture's STAC index of the latest release."""
    import duckdb

    release = release or latest_release()
    index = f"{STAC_HOST}/{release}/collections.parquet"
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    rows = con.execute(
        f"""
        SELECT id, assets.aws.href, assets.aws.alternate.s3.href,
               bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax
        FROM read_parquet({C.sql_quote(index)})
        WHERE collection = ?
          AND bbox.xmin <= ? AND bbox.xmax >= ?
          AND bbox.ymin <= ? AND bbox.ymax >= ?
        ORDER BY id
        """,
        [layer["type"], bbox[2], bbox[0], bbox[3], bbox[1]],
    ).fetchall()
    if not rows:
        raise RuntimeError(f"{index}: no {layer['type']} part over the bbox")
    parts = [{"id": part_id(href), "href": href, "s3": s3,
              "bbox": [x0, y0, x1, y1]}
             for _, href, s3, x0, y0, x1, y1 in rows]
    return {"release": release, "parts": parts,
            "resolved_via": "overture-stac",
            "mirror": mirror_collection_url(layer)}


def resolve(layer: dict, bbox: list[float]) -> dict:
    """Prefer the mirror; fall back to Overture's STAC. Notes why."""
    try:
        res = resolve_from_mirror(layer, bbox)
        res["note"] = "overture-portolan hrefs answer 200"
        return res
    except Exception as exc:  # noqa: BLE001 - any failure means fall back
        res = resolve_from_stac(layer, bbox)
        res["note"] = f"overture-portolan unusable ({exc})"
        return res


# --- PMTiles -----------------------------------------------------------------


def pmtiles_url(release: str, layer: dict) -> str:
    return OVERTURE["pmtiles"].format(release=release, theme=layer["theme"])


def pmtiles_layer_zoom(url: str, layer_name: str) -> tuple[int, int]:
    """(minzoom, maxzoom) of one vector layer in a remote PMTiles v3."""
    def rng(a: int, b: int) -> bytes:
        req = C._request(url, headers={"Range": f"bytes={a}-{b}"})
        import urllib.request
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()

    header = rng(0, 126)
    if header[:7] != b"PMTiles" or header[7] != 3:
        raise RuntimeError(f"{url}: not a PMTiles v3 archive")
    md_off, md_len = struct.unpack_from("<QQ", header, 24)
    raw = rng(md_off, md_off + md_len - 1)
    if header[97] == 2:
        raw = gzip.decompress(raw)
    meta = json.loads(raw)
    for vl in meta.get("vector_layers") or []:
        if vl["id"] == layer_name:
            return int(vl.get("minzoom", header[100])), \
                int(vl.get("maxzoom", header[101]))
    raise RuntimeError(f"{url}: no vector layer {layer_name!r}")


# --- recipes -----------------------------------------------------------------


def bbox_predicate(bbox: list[float], alias: str = "o") -> str:
    xmin, ymin, xmax, ymax = bbox
    return (f"{alias}.bbox.xmin <= {xmax} AND {alias}.bbox.xmax >= {xmin} "
            f"AND {alias}.bbox.ymin <= {ymax} AND {alias}.bbox.ymax >= {ymin}")


def parquet_list(hrefs: list[str]) -> str:
    if len(hrefs) == 1:
        return C.sql_quote(hrefs[0])
    return "[" + ", ".join(C.sql_quote(h) for h in hrefs) + "]"


def clip_sql(hrefs: list[str], bbox: list[float],
             partido_url: str | None = None) -> str:
    """The clip: bbox prefilter on the covering, then ST_Intersects.

    The prefilter compares the `bbox` covering column with constants, so
    DuckDB prunes row groups from the Parquet footer statistics before it
    reads any geometry.
    """
    url = partido_url or C.PARTIDO_URL
    return (
        "SELECT o.*\n"
        f"FROM read_parquet({parquet_list(hrefs)}, "
        "hive_partitioning = false) AS o,\n"
        f"     (SELECT geometry AS partido FROM read_parquet("
        f"{C.sql_quote(url)})) AS p\n"
        f"WHERE {bbox_predicate(bbox)}\n"
        "  AND ST_Intersects(o.geometry, p.partido)"
    )


def write_ddb(views: dict[str, str], out: Path) -> None:
    """A DuckDB file holding only views.

    Written in the v1.0.0 storage format so any DuckDB from 1.0 on can
    ATTACH it. Creating a view binds it, which reads the Parquet footers and
    the partido file, so this needs the network.
    """
    import duckdb

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / out.name
        con = duckdb.connect()
        con.execute("INSTALL spatial; LOAD spatial; "
                    "INSTALL httpfs; LOAD httpfs;")
        con.execute(f"ATTACH {C.sql_quote(str(work))} AS ov "
                    "(STORAGE_VERSION 'v1.0.0')")
        for name, sql in views.items():
            con.execute(f"CREATE VIEW ov.{name} AS\n{sql}")
        con.execute("DETACH ov")
        con.close()
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work, out)


# --- measurement -------------------------------------------------------------


def measure(parts: list[dict], partido: C.Partido) -> dict:
    """Columns, geometry types, and rows inside the partido, per part.

    Reads the geometry from a WKB literal, not the boundary URL, so the
    measurement does not depend on where the boundary is published.
    """
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
    con.execute("CREATE TEMP TABLE p AS SELECT ST_GeomFromHEXWKB(?) AS g",
                [partido.wkb_hex])
    bbox = partido.bbox
    columns = con.execute(
        "DESCRIBE SELECT * FROM read_parquet("
        f"{C.sql_quote(parts[0]['href'])}, hive_partitioning = false)"
    ).fetchall()
    rows = {}
    geom_types: set[str] = set()
    for part in parts:
        n, types = con.execute(
            f"""
            SELECT count(*), list(DISTINCT ST_GeometryType(o.geometry))
            FROM read_parquet({C.sql_quote(part['href'])},
                              hive_partitioning = false) AS o, p
            WHERE {bbox_predicate(bbox)}
              AND ST_Intersects(o.geometry, p.g)
            """
        ).fetchone()
        rows[part["id"]] = n
        geom_types.update(t for t in (types or []) if t)
    return {
        "columns": [(name, ctype) for name, ctype, *_ in columns],
        "rows": rows,
        "geometry_types": sorted(geom_types),
    }


def column_descriptions(mirror_url: str) -> dict[str, str]:
    """Column descriptions as overture-portolan states them, by name."""
    try:
        coll = C.get_json(mirror_url)
    except Exception:  # noqa: BLE001 - descriptions are optional
        return {}
    return {c["name"]: c["description"]
            for c in coll.get("table:columns", []) if c.get("description")}


# --- documents ---------------------------------------------------------------


def release_datetime(release: str) -> str:
    return f"{release.split('.')[0]}T00:00:00Z"


def item_geometry(partido: C.Partido, bbox: list[float]) -> dict:
    import shapely

    piece = C.display_geometry(partido).intersection(shapely.box(*bbox))
    return C.rounded_coords(piece)


def single_file(res: dict) -> bool:
    """One upstream part: the data asset sits on the collection.

    core.md (Collections) puts a single file at collection level with no
    items (rashid PTL-COL-001). Several parts are several files, one item
    each. A collection can switch between the two shapes from one Overture
    release to the next.
    """
    return len(res["parts"]) == 1


def data_asset(res: dict, part: dict, partido: C.Partido) -> dict:
    """The external GeoParquet part, with the clip as its expression."""
    data = {
        "href": part["href"],
        "type": C.PARQUET_TYPE,
        "roles": ["data", "external"],
        "title": f"GeoParquet, parte {part['id']} (externa)",
        "description": (
            f"Archivo de la publicación {res['release']} de Overture Maps. "
            "Cubre una región mayor que el partido; la expresión de "
            "procesamiento lee solo lo que cae dentro."),
        "processing:expression": {
            "format": "duckdb-sql",
            "expression": clip_sql([part["href"]], partido.bbox),
        },
    }
    if part.get("s3"):
        data["alternate"] = {"s3": {
            "href": part["s3"],
            "title": "S3, us-west-2, sin credenciales",
        }}
    return data


def stored_parts(collection: dict, folder: Path) -> list[str]:
    """Upstream part hrefs a built collection points at, in either shape."""
    data = collection.get("assets", {}).get("data")
    if data:
        return [data["href"]]
    hrefs = []
    for link in collection.get("links", []):
        if link.get("rel") == "item":
            item = json.loads((folder / link["href"]).read_text())
            hrefs.append(item["assets"]["data"]["href"])
    return sorted(hrefs)


def build_item(layer: dict, res: dict, part: dict, partido: C.Partido,
               rows: int) -> dict:
    import shapely

    geom = item_geometry(partido, part["bbox"])
    data = data_asset(res, part, partido)
    iid = f"parte-{part['id']}"
    return {
        "type": "Feature",
        "stac_version": "1.1.0",
        "stac_extensions": [C.EXT["processing"], C.EXT["alternate"],
                            C.EXT["table"]],
        "id": iid,
        "collection": f"{C.GROUP}/overture/{layer['id']}",
        "geometry": geom,
        "bbox": [round(v, 6) for v in shapely.from_geojson(
            json.dumps(geom)).bounds],
        "properties": {
            "title": f"Parte {part['id']}",
            "datetime": release_datetime(res["release"]),
            "table:row_count": rows,
            "pergamino:upstream_bbox": [round(v, 6) for v in part["bbox"]],
        },
        "links": [
            {"rel": "root", "href": "../../../../catalog.json",
             "type": "application/json", "title": C.ROOT_TITLE},
            {"rel": "parent", "href": "../collection.json",
             "type": "application/json",
             "title": TITLES[layer["type"]][0]},
            {"rel": "collection", "href": "../collection.json",
             "type": "application/json",
             "title": TITLES[layer["type"]][0]},
        ],
        "assets": {"data": data},
    }


def build_style(layer: dict, res: dict, partido: C.Partido,
                zooms: tuple[int, int], mirror_style: dict | None) -> dict:
    """The mirror's default layers over this release's PMTiles, masked."""
    url = pmtiles_url(res["release"], layer)
    if mirror_style:
        layers = []
        for ly in mirror_style.get("layers", []):
            if ly.get("type") == "background":
                continue
            ly = dict(ly)
            ly["source"] = "data"
            layers.append(ly)
    else:
        layers = [{"id": f"{layer['type']}-line", "type": "line",
                   "source": "data", "source-layer": layer["type"],
                   "paint": {"line-color": "#555555"}}]
    return {
        "version": 8,
        "name": TITLES[layer["type"]][0],
        "sources": {
            "data": {"type": "vector", "url": f"pmtiles://{url}",
                     "minzoom": 0, "maxzoom": zooms[1],
                     "attribution": "© OpenStreetMap contributors, "
                                    "Overture Maps Foundation"},
            "mascara": {"type": "geojson",
                        "data": C.mask_geometry(partido)},
            "partido": {"type": "geojson",
                        "data": C.partido_outline(partido)},
        },
        "layers": layers + [
            {"id": "mascara", "type": "fill", "source": "mascara",
             "paint": {"fill-color": "#ffffff", "fill-opacity": 0.85}},
            {"id": "partido", "type": "line", "source": "partido",
             "paint": {"line-color": "#333333", "line-width": 1.2}},
        ],
    }


def mirror_style_doc(layer: dict) -> dict | None:
    url = urljoin(mirror_collection_url(layer), "styles/default.json")
    try:
        return C.get_json(url)
    except Exception:  # noqa: BLE001 - fall back to a plain style
        return None


def thumbnail_asset(thumb: Path) -> dict:
    return {
        "href": f"./{thumb.name}",
        "type": "image/jpeg",
        "roles": ["thumbnail"],
        "title": "Vista previa",
        "description": (
            "El recorte dibujado con el estilo por defecto sobre un mapa "
            "base, con la máscara aplicada."),
        **C.file_fields(thumb),
    }


def build_collection(layer: dict, res: dict, partido: C.Partido,
                     m: dict, canonical: dict, zooms: tuple[int, int],
                     thumb: Path | None) -> dict:
    cid = f"{C.GROUP}/overture/{layer['id']}"
    folder = SUBDIR / layer["id"]
    title, description = TITLES[layer["type"]]
    pm = pmtiles_url(res["release"], layer)
    descriptions = column_descriptions(res["mirror"])
    columns = []
    for name, ctype in m["columns"]:
        col = {"name": name, "type": ctype}
        if descriptions.get(name):
            col["description"] = descriptions[name]
        columns.append(col)

    license_id = canonical.get("license") or "other"
    license_links = [
        {k: v for k, v in ln.items() if k in ("rel", "href", "type", "title")}
        for ln in canonical.get("links", []) if ln.get("rel") == "license"
    ]
    if not license_links:
        license_links = [{"rel": "license", "href": ATTRIBUTION,
                          "type": "text/html",
                          "title": "Overture Maps: licencias y atribución"}]
    for ln in license_links:
        ln.setdefault("type", "text/html")
        ln.setdefault("title", "Overture Maps: licencias y atribución")

    style_path = folder / "styles" / "default.json"
    assets = {
        "visual": {
            "href": pm,
            "type": C.PMTILES_TYPE,
            "roles": ["visual", "external"],
            "title": f"Teselas vectoriales de Overture ({layer['theme']})",
            "description": (
                "PMTiles que publica Overture Maps para todo el mundo. La "
                "capa de esta colección es "
                f"`{layer['type']}`; el estilo por defecto oculta lo que cae "
                "fuera del partido."),
        },
        "recorte": {
            "href": f"../{DDB_NAME}",
            "type": C.DUCKDB_TYPE,
            "roles": C.RECIPE_ROLES,
            "title": f"Vistas DuckDB del recorte (vista `{layer['view']}`)",
            "description": (
                "Base DuckDB que contiene solo vistas, una por colección de "
                "este subcatálogo. Cada vista lee las partes externas con un "
                "prefiltro sobre la columna `bbox` y `ST_Intersects` contra "
                "el límite oficial del partido. Se abre con `ATTACH ... "
                "(READ_ONLY)` después de cargar `spatial` y `httpfs`."),
        },
        "style": {
            "href": "./styles/default.json",
            "type": C.STYLE_TYPE,
            "roles": ["style", "default"],
            "title": "Por defecto, con máscara del partido",
            "description": (
                "Las capas del estilo por defecto de overture-portolan sobre "
                "las PMTiles de esta publicación, con una máscara que cubre "
                "todo lo que queda fuera del partido."),
            **C.file_fields(style_path),
        },
    }
    if thumb is not None and thumb.exists():
        assets["thumbnail"] = thumbnail_asset(thumb)

    links = C.structural_links(3, SUBCATALOG_TITLE) + C.doc_links() + [
        {"rel": "via", "href": GUIDES[layer["theme"]], "type": "text/html",
         "title": f"Guía de Overture: {layer['theme']}"},
        {"rel": "via", "href": schema_page(layer), "type": "text/html",
         "title": f"Esquema de Overture: {layer['type']}"},
        {"rel": "canonical", "href": canonical_url(res["release"], layer),
         "type": "application/json",
         "title": f"Overture STAC, publicación {res['release']}"},
        {"rel": "derived_from", "href": res["mirror"],
         "type": "application/json",
         "title": "Colección en overture-portolan"},
        {"rel": "pmtiles", "href": pm, "type": C.PMTILES_TYPE,
         "title": f"Teselas vectoriales de Overture ({layer['theme']})",
         "pmtiles:layers": [layer["type"]]},
    ] + license_links
    single = single_file(res)
    if single:
        assets = {"data": data_asset(res, res["parts"][0], partido),
                  **assets}
    for part in ([] if single else res["parts"]):
        iid = f"parte-{part['id']}"
        links.append({"rel": "item", "href": f"./{iid}/{iid}.json",
                      "type": "application/geo+json",
                      "title": f"Parte {part['id']}"})

    stamp = release_datetime(res["release"])
    return {
        "type": "Collection",
        "id": cid,
        "stac_version": "1.1.0",
        "stac_extensions": [C.EXT["portolan"], C.EXT["file"],
                            C.EXT["table"], C.EXT["wml"]] + (
            [C.EXT["processing"], C.EXT["alternate"]] if single else []),
        "title": title,
        "description": description,
        "keywords": ["Overture Maps", layer["theme"], layer["type"],
                     "Pergamino"],
        "license": license_id,
        "providers": [
            {"name": "Overture Maps Foundation",
             "roles": ["producer", "licensor"],
             "url": "https://overturemaps.org/"},
            C.host_provider(),
        ],
        "extent": {
            "spatial": {"bbox": [partido.bbox]},
            "temporal": {"interval": [[stamp, stamp]]},
        },
        "table:columns": columns,
        "table:row_count": sum(m["rows"].values()),
        "pmtiles:layers": [layer["type"]],
        "links": links,
        "assets": assets,
        "pergamino:virtual": {
            "overture_release": res["release"],
            "resolved_via": res["resolved_via"],
            "geometry_types": m["geometry_types"],
            "view": layer["view"],
            "upstream_parts": {p["id"]: [round(v, 6) for v in p["bbox"]]
                               for p in res["parts"]},
            "recipe": C.public_url(f"{C.GROUP}/overture/{DDB_NAME}"),
        },
    }


def subcatalog(layers: list[dict]) -> dict:
    links = C.structural_links(2, "Datos de otros catálogos")
    for layer in layers:
        links.append({"rel": "child",
                      "href": f"./{layer['id']}/collection.json",
                      "type": "application/json",
                      "title": TITLES[layer["type"]][0]})
    links += C.doc_links() + [
        {"rel": "via", "href": "https://docs.overturemaps.org/",
         "type": "text/html", "title": "Documentación de Overture Maps"},
    ]
    return {
        "type": "Catalog",
        "id": f"{C.GROUP}/overture",
        "stac_version": "1.1.0",
        "stac_extensions": [C.EXT["portolan"]],
        "title": SUBCATALOG_TITLE,
        "description": (
            "Edificios, lugares de interés, segmentos de transporte y uso "
            "del suelo de Overture Maps dentro del partido de Pergamino, "
            "referenciados sin copiar los datos. Un archivo DuckDB de vistas "
            "recorta cada capa al partido al consultarla."),
        "links": links,
    }


def write_collection(layer: dict, res: dict, partido: C.Partido, docs,
                     now, force_updated: bool = False) -> dict:
    """Measure, then write one collection, its items, style, and docs."""
    folder = SUBDIR / layer["id"]
    folder.mkdir(parents=True, exist_ok=True)
    m = measure(res["parts"], partido)
    canonical = C.get_json(canonical_url(res["release"], layer))
    pm = pmtiles_url(res["release"], layer)
    zooms = pmtiles_layer_zoom(pm, layer["type"])
    C.write_json(folder / "styles" / "default.json",
                 build_style(layer, res, partido, zooms,
                             mirror_style_doc(layer)))

    keep = set()
    for part in ([] if single_file(res) else res["parts"]):
        item = build_item(layer, res, part, partido, m["rows"][part["id"]])
        path = folder / item["id"] / f"{item['id']}.json"
        C.write_json(path, item)
        keep.add(item["id"])
    for stale in folder.glob("parte-*"):
        if stale.is_dir() and stale.name not in keep:
            shutil.rmtree(stale)

    thumb = folder / f"{layer['id']}.thumb.jpg"
    doc = build_collection(layer, res, partido, m, canonical, zooms, thumb)
    docs.write_overture(layer, doc, folder, res)
    path = folder / "collection.json"
    C.write_json(path, C.keep_updated(path, doc, now, force=force_updated))
    print(f"  overture/{layer['id']}: {res['release']} via "
          f"{res['resolved_via']}, parts {[p['id'] for p in res['parts']]}")
    return doc


def views_for(resolutions: dict[str, dict], bbox: list[float],
              partido_url: str | None = None) -> dict[str, str]:
    views = {}
    for layer in OVERTURE["layers"]:
        res = resolutions[layer["id"]]
        views[layer["view"]] = clip_sql([p["href"] for p in res["parts"]],
                                        bbox, partido_url)
    return views


def write_recipe(resolutions: dict[str, dict], partido: C.Partido,
                 partido_url: str | None = None) -> str:
    """Write the shared .ddb. Returns a status line."""
    url = partido_url or C.PARTIDO_URL
    if C.probe(url) != 200:
        return (f"skipped {DDB_NAME}: {url} does not answer 200, and a view "
                "cannot be created over a file DuckDB cannot read")
    write_ddb(views_for(resolutions, partido.bbox, url), SUBDIR / DDB_NAME)
    return f"wrote {DDB_NAME}"


def build(partido: C.Partido, docs, now,
          partido_url: str | None = None) -> list[str]:
    layers = OVERTURE["layers"]
    resolutions = {ly["id"]: resolve(ly, partido.bbox) for ly in layers}
    written = []
    for layer in layers:
        doc = write_collection(layer, resolutions[layer["id"]], partido,
                               docs, now)
        written.append(doc["id"])
    print("  " + write_recipe(resolutions, partido, partido_url))
    cat_path = SUBDIR / "catalog.json"
    C.write_json(cat_path, C.keep_updated(cat_path, subcatalog(layers), now))
    docs.write_overture_group(layers, SUBDIR, resolutions)
    return written
