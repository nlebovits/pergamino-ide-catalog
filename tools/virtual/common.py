"""Shared pieces of the virtual-collection builder.

A virtual collection lists the part of a dataset in another catalog that falls
inside the partido de Pergamino, without copying its bytes. Each one lives in
the thematic group it belongs to, beside the municipal layers: its id is the
``collection`` field of its layer in ``sources.json``, such as
``catastro/edificios_overture``. It carries ``pergamino:virtual``, which is how
the tools and the gates tell it from a GeoNode collection. Everything here is
used by both ``build.py`` (write every collection from scratch) and
``refresh.py`` (re-resolve upstream hrefs weekly).

The one value most likely to change is the partido boundary URL. It lives in
``sources.json`` under ``partido.url`` and is read into ``PARTIDO_URL`` here;
every published recipe is written from that constant.
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG = ROOT / "catalog"
CONFIG_PATH = Path(__file__).resolve().parent / "sources.json"
CONFIG = json.loads(CONFIG_PATH.read_text())

# The partido boundary every recipe clips to. Switch it in sources.json.
PARTIDO_URL: str = CONFIG["partido"]["url"]

PUBLIC_BASE = "https://data.source.coop/nlebovits/pergamino-ide"

USER_AGENT = "pergamino-ide-catalog virtual-collections"

EXT = {
    "portolan": "https://schemas.portolan-sdi.org/portolan/v0.3.0/schema.json",
    "file": "https://stac-extensions.github.io/file/v2.1.0/schema.json",
    "proj": "https://stac-extensions.github.io/projection/v2.0.0/schema.json",
    "render": "https://stac-extensions.github.io/render/v2.0.0/schema.json",
    "processing":
        "https://stac-extensions.github.io/processing/v1.2.0/schema.json",
    "classification":
        "https://stac-extensions.github.io/classification/v2.0.0/schema.json",
    "table": "https://stac-extensions.github.io/table/v1.2.0/schema.json",
    "wml": "https://stac-extensions.github.io/web-map-links/v1.3.0/schema.json",
    "alternate":
        "https://stac-extensions.github.io/alternate-assets/v1.2.0/schema.json",
}

COG_TYPE = "image/tiff; application=geotiff; profile=cloud-optimized"
PARQUET_TYPE = "application/vnd.apache.parquet"
PMTILES_TYPE = "application/vnd.pmtiles"
STYLE_TYPE = "application/vnd.mapbox.style+json"
VRT_TYPE = "application/xml"
DUCKDB_TYPE = "application/vnd.duckdb"

# Roles of the small local file that performs the clip. `metadata` is the
# standard role a client already knows not to render; `recipe` says what the
# file is. Neither is data: the bytes stay upstream.
RECIPE_ROLES = ["metadata", "recipe"]

# Simplification of the partido polygon for display only (style mask, item
# footprints). The clip itself always uses the full boundary.
DISPLAY_TOLERANCE = 0.0005


@dataclass(frozen=True)
class Partido:
    """The boundary, loaded once."""

    geometry: object  # shapely Polygon
    source: str

    @property
    def bbox(self) -> list[float]:
        return [round(v, 8) for v in self.geometry.bounds]

    @property
    def wkb_hex(self) -> str:
        return self.geometry.wkb_hex


def host_provider() -> dict:
    """The catalog's own host provider, copied from the partido collection.

    Read rather than restated so that every collection names its host the
    same way the rest of the catalog does.
    """
    path = CATALOG / "limites" / "partido_pergamino" / "collection.json"
    providers = json.loads(path.read_text())["providers"]
    return copy.deepcopy(providers[-1])


# --- http --------------------------------------------------------------


def _request(url: str, method: str = "GET", headers: dict | None = None):
    hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
    return urllib.request.Request(url, method=method, headers=hdrs)


def get_bytes(url: str, timeout: int = 60) -> bytes:
    with urllib.request.urlopen(_request(url), timeout=timeout) as resp:
        return resp.read()


def get_json(url: str, timeout: int = 60) -> dict:
    return json.loads(get_bytes(url, timeout))


def probe(url: str, timeout: int = 30) -> int:
    """HTTP status of url, or 0 when unreachable.

    HEAD first. Some servers refuse HEAD (the JRC catalogue answers 405), so
    a 403/405 falls back to a one-byte ranged GET.
    """
    for method, headers in (("HEAD", None), ("GET", {"Range": "bytes=0-0"})):
        try:
            with urllib.request.urlopen(
                _request(url, method, headers), timeout=timeout
            ) as resp:
                return resp.status
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in (403, 405):
                continue
            return exc.code
        except (urllib.error.URLError, TimeoutError, OSError):
            return 0
    return 0


# --- the partido -------------------------------------------------------


def load_partido(url: str | None = None) -> Partido:
    """The partido polygon: the local catalog file, else its public URL.

    The refresh and a local build both have the catalog checkout, so the
    local file answers. A CI job without data files reads the bucket.
    """
    import pyarrow.parquet as pq
    import shapely

    def read(source) -> Partido:
        table = pq.read_table(source, columns=["geometry"])
        return shapely.from_wkb(table.column("geometry")[0].as_py())

    local = ROOT / CONFIG["partido"]["local"]
    if url is None and local.exists():
        return Partido(read(local), str(local))
    candidate = url or PARTIDO_URL
    try:
        return Partido(read(io.BytesIO(get_bytes(candidate))), candidate)
    except Exception as exc:  # noqa: BLE001 - say which source failed
        raise SystemExit(f"cannot load the partido boundary from "
                         f"{candidate}: {exc}") from exc


def display_geometry(partido: Partido):
    return partido.geometry.simplify(DISPLAY_TOLERANCE,
                                     preserve_topology=True)


def rounded_coords(geom, ndigits: int = 6) -> dict:
    """GeoJSON mapping of geom with coordinates rounded, for stable files."""
    import shapely

    return json.loads(shapely.to_geojson(
        shapely.set_precision(geom, 10 ** -ndigits)))


def mask_geometry(partido: Partido) -> dict:
    """The world minus the partido, as a GeoJSON Polygon.

    MapLibre's `within` filter does not apply to polygons, so the style hides
    everything outside the partido by drawing this mask over it.
    """
    import shapely

    simple = shapely.set_precision(display_geometry(partido), 1e-6)
    hole = shapely.geometry.polygon.orient(simple, sign=-1.0)
    world = [[-180, -85], [180, -85], [180, 85], [-180, 85], [-180, -85]]
    return {
        "type": "Polygon",
        "coordinates": [world, [list(c) for c in hole.exterior.coords]],
    }


def partido_outline(partido: Partido) -> dict:
    return rounded_coords(display_geometry(partido))


# --- files -------------------------------------------------------------


def dump_json(doc: dict) -> str:
    # No trailing newline: the convention of every other JSON file in
    # catalog/, so a rebuild leaves the root catalog.json byte-stable.
    return json.dumps(doc, indent=2, ensure_ascii=False)


def write_text(path: Path, text: str) -> bool:
    """Write text when it differs. True when the file changed."""
    if path.exists() and path.read_text() == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return True


def write_json(path: Path, doc: dict) -> bool:
    return write_text(path, dump_json(doc))


def file_fields(path: Path) -> dict:
    """file:size and a sha2-256 multihash file:checksum for a local file."""
    data = path.read_bytes()
    return {
        "file:size": len(data),
        "file:checksum": "1220" + hashlib.sha256(data).hexdigest(),
    }


def now_rfc3339(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def keep_updated(path: Path, doc: dict, now: datetime | None,
                 force: bool = False) -> dict:
    """Set doc["updated"]: kept from disk when nothing else changed.

    A rebuild that produces the same document leaves the file untouched, so
    rerunning the builder is a no-op in git. ``force`` stamps the time anyway,
    which is what a sync does (core.md, Source Provenance: the sync time on
    every catalog and collection it checks).
    """
    doc = copy.deepcopy(doc)
    stamp = now_rfc3339(now)
    if path.exists() and not force:
        old = json.loads(path.read_text())
        previous = old.pop("updated", None)
        current = {k: v for k, v in doc.items() if k != "updated"}
        if previous and old == current:
            stamp = previous
    doc["updated"] = stamp
    return doc


# --- links -------------------------------------------------------------

ROOT_TITLE = "IDE Pergamino - Infraestructura de Datos Espaciales"


def structural_links(depth: int, parent_title: str) -> list[dict]:
    """root and parent links for an object `depth` levels below the root."""
    up = "../" * depth
    return [
        {"rel": "root", "href": f"{up}catalog.json",
         "type": "application/json", "title": ROOT_TITLE},
        {"rel": "parent", "href": "../catalog.json",
         "type": "application/json", "title": parent_title},
    ]


def leaf(cid: str) -> str:
    """The folder name of a collection: ``glofas_peligro_rp10``."""
    return cid.rsplit("/", 1)[-1]


def folder(cid: str) -> Path:
    """Where a collection lives. Reads CATALOG at call time (tests swap it)."""
    return CATALOG / cid


def group_title(cid: str) -> str:
    """The title of the thematic group that holds a collection."""
    path = CATALOG / cid.split("/", 1)[0] / "catalog.json"
    return json.loads(path.read_text())["title"]


def collection_links(cid: str) -> list[dict]:
    """root and parent links of a collection inside its thematic group."""
    return structural_links(2, group_title(cid))


def is_virtual(doc: dict) -> bool:
    return "pergamino:virtual" in doc


def is_glofas(doc: dict) -> bool:
    """GloFAS collections record their upstream catalog; Overture ones do not."""
    return "upstream_catalog" in doc.get("pergamino:virtual", {})


def virtual_collections(catalog: Path | None = None) -> list[Path]:
    """Every collection.json under the catalog that is virtual."""
    base = catalog or CATALOG
    return [p for p in sorted(base.glob("*/*/collection.json"))
            if is_virtual(json.loads(p.read_text()))]


def doc_links() -> list[dict]:
    return [
        {"rel": "agents", "href": "./AGENTS.md", "type": "text/markdown",
         "title": "Guía para agentes"},
        {"rel": "describedby", "href": "./README.md",
         "type": "text/markdown", "title": "Documentación"},
    ]


def public_url(rel_path: str) -> str:
    return f"{PUBLIC_BASE}/{rel_path}"


def sql_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"
