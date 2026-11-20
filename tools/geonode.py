#!/usr/bin/env python3
"""Read the municipality's GeoNode: dataset records, and change signals.

The catalog mirrors the vector datasets of https://geonode.pergamino.gob.ar,
a GeoNode 4.4 instance. Two public interfaces are used:

- the REST API at ``/api/v2/datasets`` for each dataset's metadata and its
  ``last_updated`` timestamp
- the WFS at ``/geoserver/ows`` for the features, and ``resultType=hits``
  for the feature count

GeoNode updates ``last_updated`` when a dataset or its metadata is saved
through GeoNode. An edit made directly in the database behind GeoServer does
not change it. The refresh therefore also compares the WFS feature count,
and the extract compares a content hash, so a silent edit is still caught on
the next forced run.

``tools/sources.json`` maps each mirrored collection to its dataset. Write it
with ``python3 tools/geonode.py sources``. The mapping rules are in
``tools/generate/grouping.py``.

    python3 tools/geonode.py sources          # rewrite tools/sources.json
    python3 tools/geonode.py probe arbolado   # last_updated and count
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCES = HERE / "sources.json"

BASE = "https://geonode.pergamino.gob.ar"
API = f"{BASE}/api/v2"
OWS = f"{BASE}/geoserver/ows"
USER_AGENT = ("pergamino-ide-refresh "
              "(+https://github.com/nlebovits/pergamino-ide-catalog)")
ATTEMPTS = 4

# maintenance_frequency (ISO 19115 MD_MaintenanceFrequencyCode) to the
# smallest gap, in days, between two versions of one collection. A dataset
# the municipality saves several times a week still gets at most one version
# a week, because the refresh runs weekly.
MIN_DAYS = {
    "continual": 7,
    "daily": 7,
    "weekly": 7,
    "fortnightly": 14,
    "monthly": 28,
    "quarterly": 28,
    "biannually": 28,
    "annually": 28,
    "asNeeded": 7,
    "irregular": 7,
    "notPlanned": 7,
    "unknown": 7,
}


def get(url: str, params: dict | None = None, *, raw: bool = False):
    """GET a URL with retries. JSON unless ``raw``."""
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, safe='{}[]:')}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read()
            return body if raw else json.loads(body)
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == ATTEMPTS:
                raise RuntimeError(f"GET {url} failed: {exc}") from exc
            time.sleep(10 * attempt)
    raise AssertionError("unreachable")


def datasets() -> list[dict]:
    """Every dataset record, in GeoNode's order."""
    out: list[dict] = []
    page = 1
    while True:
        body = get(f"{API}/datasets", {"page_size": 100, "page": page})
        out += body["datasets"]
        if not body.get("links", {}).get("next"):
            return out
        page += 1


def dataset(pk: int, *, attributes: bool = False) -> dict:
    params = {"include[]": "attribute_set"} if attributes else None
    return get(f"{API}/datasets/{pk}", params)["dataset"]


def name_of(record: dict) -> str:
    """The bare layer name: ``geonode:arbolado`` gives ``arbolado``."""
    return record["alternate"].split(":")[-1]


def page_url(pk: int) -> str:
    """The dataset's page in GeoNode's own client, for the ``via`` link."""
    return f"{BASE}/catalogue/#/dataset/{pk}"


def wfs_url(alternate: str) -> str:
    query = urllib.parse.urlencode({
        "service": "WFS", "version": "2.0.0", "request": "GetFeature",
        "typeNames": alternate,
    }, safe=":")
    return f"{OWS}?{query}"


def hits(alternate: str) -> int:
    """The WFS feature count, from ``resultType=hits``."""
    body = get(OWS, {
        "service": "WFS", "version": "2.0.0", "request": "GetFeature",
        "typeNames": alternate, "resultType": "hits",
    }, raw=True).decode()
    found = re.search(r'numberMatched="(\d+)"', body)
    if not found:
        raise RuntimeError(f"no numberMatched for {alternate}: {body[:300]}")
    return int(found.group(1))


def wfs_typenames() -> set[str]:
    """Every feature type the WFS serves, as ``workspace:name``."""
    body = get(OWS, {"service": "WFS", "version": "2.0.0",
                     "request": "GetCapabilities"}, raw=True).decode()
    return set(re.findall(r"<wfs:Name>([^<]+)</wfs:Name>", body)) | set(
        re.findall(r"<Name>([^<]+)</Name>", body))


@dataclass(frozen=True)
class SourceState:
    last_updated: str
    count: int


def probe(entry: dict) -> SourceState:
    """The change signals for one collection's dataset."""
    record = dataset(entry["pk"])
    return SourceState(clean_stamp(record["last_updated"]),
                       hits(entry["alternate"]))


def clean_stamp(stamp: str) -> str:
    """GeoNode writes microseconds; the catalog keeps whole seconds."""
    return re.sub(r"\.\d+", "", stamp).replace("+00:00", "Z")


def load_sources() -> dict:
    return json.loads(SOURCES.read_text())


def eligible(record: dict, served: set[str]) -> str | None:
    """None when the dataset can be mirrored, else the reason it cannot."""
    from generate.grouping import EXCLUDED

    name = name_of(record)
    constraints = (record.get("constraints_other") or "").lower()
    if record.get("subtype") != "vector":
        return f"subtype {record.get('subtype')}"
    if name in EXCLUDED:
        return "excluded in grouping.EXCLUDED"
    if not record.get("is_published"):
        return "not published in GeoNode"
    if "uso interno" in constraints:
        return "GeoNode marks it for internal use"
    if record["alternate"] not in served:
        return "the WFS does not serve it"
    return None


def write_sources() -> int:
    """Rewrite tools/sources.json from GeoNode and the grouping rules."""
    sys.path.insert(0, str(HERE))
    from generate.grouping import LAYER_TO_GROUP, leaf_name

    served = wfs_typenames()
    records = {name_of(r): r for r in datasets()}
    collections, skipped, unmapped = {}, {}, []
    for name, record in sorted(records.items()):
        why = eligible(record, served)
        if why:
            skipped[name] = why
            continue
        group = LAYER_TO_GROUP.get(name)
        if group is None:
            unmapped.append(name)
            continue
        frequency = record.get("maintenance_frequency") or "unknown"
        collections[f"{group}/{leaf_name(group, name)}"] = {
            "alternate": record["alternate"],
            "pk": int(record["pk"]),
            "uuid": record["uuid"],
            "update_frequency": frequency,
            "min_days": MIN_DAYS.get(frequency, 7),
        }
    missing = sorted(set(LAYER_TO_GROUP) - set(records))
    doc = {
        "geonode": BASE,
        "wfs": OWS,
        "collections": collections,
        "not_mirrored": skipped,
    }
    SOURCES.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {SOURCES.relative_to(ROOT)}: {len(collections)} collections, "
          f"{len(skipped)} datasets not mirrored")
    for name in unmapped:
        print(f"  new dataset with no group: {name}", file=sys.stderr)
    for name in missing:
        print(f"  grouped layer absent from GeoNode: {name}", file=sys.stderr)
    return 1 if unmapped or missing else 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sources")
    p = sub.add_parser("probe")
    p.add_argument("collection")
    args = parser.parse_args()
    if args.cmd == "sources":
        return write_sources()
    sources = load_sources()["collections"]
    matches = [k for k in sources if k == args.collection
               or k.endswith("/" + args.collection)]
    if len(matches) != 1:
        sys.exit(f"no single collection matches {args.collection!r}")
    print(matches[0], probe(sources[matches[0]]))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    raise SystemExit(main())
