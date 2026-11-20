# pergamino-ide-catalog

Source repository for the **IDE Pergamino** Portolan catalog, a cloud-native
mirror of the spatial data infrastructure published by the Municipalidad de
Pergamino, Buenos Aires, Argentina.

- **Published catalog**: https://source.coop/nlebovits/pergamino-ide
- **STAC root**: https://data.source.coop/nlebovits/pergamino-ide/catalog.json
- **Upstream source**: https://geonode.pergamino.gob.ar/

This repository holds the catalog metadata, documentation, styles, and the
tooling that generates them. It is not the data. The GeoParquet and PMTiles
files live in object storage and are gitignored, because git keeps every version
of a binary forever and one large file committed once is paid for by every clone
from then on.

## Layout

```
catalog/                  the published tree, synced 1:1 to object storage
  catalog.json            root, links 13 thematic sub-catalogs
  <theme>/                sub-catalog: catalog.json, README.md, AGENTS.md
    <collection>/         collection.json, README.md, AGENTS.md, styles/, legends/
tools/sources.json        the GeoNode dataset behind each collection
tools/refresh.py          the weekly refresh: probe, extract, version
tools/generate/           the docs, catalogs, styles and thumbnails
tools/publish.py          the only thing that uploads
tests/                    the gates CI runs
docs/refresh.md           how the weekly refresh works, and how to run it
docs/conformance.md       the accepted-deviations ledger
```

Everything under `catalog/` is published. Nothing outside it ever is. That
boundary is enforced structurally: `tools/publish.py` walks `publish_dir` and has
no flag that widens the walk.

## What is in the catalog

The vector layers the municipality publishes in GeoNode, in 13 thematic
groups: cadastre, roads, transport, water and sanitation, energy and
connectivity, health, education, security, demographics, environment and
agriculture, administrative boundaries, municipal services, and commerce and
culture. `tools/sources.json` lists the dataset behind each collection.

Each layer is GeoParquet 1.1.0 with Hilbert spatial ordering and a bbox
covering column, plus PMTiles for web display and a MapLibre style derived
from the SLD that GeoNode publishes for it. Every collection AGENTS.md has
example queries, and CI runs each one.

## Weekly refresh

`.github/workflows/refresh.yml` runs every Monday. It asks GeoNode whether
each dataset changed, re-extracts the ones that did, and publishes each
change as a new version. Earlier versions stay readable under `versions/`.
See [docs/refresh.md](./docs/refresh.md).

## Working on it

Validation is the floor, not the goal. Run the gates before committing:

```bash
python3 tests/run_all.py
```

`rashid` is the conformance gate; `stac-check` is advisory. Where they disagree —
`stac-check` recommends a `self` link that Portolan forbids — rashid wins, and
the disagreement is recorded rather than silenced.

Publishing is a two-step, and the dry run has no confirmation flag by accident:

```bash
python3 tools/publish.py            # dry run, prints the diff
python3 tools/publish.py --confirm  # uploads
```

**Publishing never deletes.** Removing a file from `catalog/` leaves the object
in the bucket. Stale objects have to be removed deliberately.

## Editing

Do not hand-edit generated output. `README.md` and `AGENTS.md` under `catalog/`
are generated from collection metadata, the GeoNode records in
`tools/generate/data/geonode.json`, and the facts measured from the data in
`tools/generate/data/measured.json`. Edit the source and regenerate with
`python3 tools/generate/build_docs.py catalog`. A CI gate rebuilds and diffs, so a hand edit shows up
as a failure rather than surviving quietly.

## Licence

The catalog **data** is published by the Municipalidad de Pergamino under
CC BY-SA 4.0. Collections sourced from third parties — INTA, IGN, INDEC,
RENABAP, CONICET, INA, ARBA, BAHRA, Correo Argentino — carry the attribution of
their originating agency and are not relicensed.

The tooling in this repository is under the licence in [LICENSE](./LICENSE).
