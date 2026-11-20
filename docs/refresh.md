# Scheduled refresh

`.github/workflows/refresh.yml` keeps the catalog current with the
municipality's GeoNode (`https://geonode.pergamino.gob.ar`). Each change at
the source becomes a new version. Every earlier version stays readable, and
the bucket holds one copy of each.

## Layout

Each collection has one current file and one file per earlier version:

| Path | Content | Changes |
|---|---|---|
| `<group>/<leaf>/<leaf>.parquet` | The current version | Every new version |
| `<group>/<leaf>/<leaf>.pmtiles` | Tiles for the current version | Every new version |
| `<group>/<leaf>/versions/<version>.parquet` | An earlier version | Never |
| `<group>/<leaf>/publico_<layer>.parquet` | The first version, from the earlier GeoServer | Never |
| `<group>/<leaf>/collection.json` | Every version: dates, row count, checksum | Every new version |

The version label is the UTC date of the extract. A forced second run on one
day gets `<date>-2`.

The catalog was first built from the municipality's earlier GeoServer
(`https://ide.pergamino.gob.ar:8443/geoserver/wfs`). Every collection that
existed then keeps that extract as its first version, at the URL it was
first published under. Its asset description says where it came from.
`tools/generate/migrate_geonode.py` moved the catalog to GeoNode once, and
is kept so the move can be read and repeated.

Read the current data at the fixed URL:

```sql
SELECT count(*)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/cpa/cpa.parquet');
```

In `collection.json`, the asset named after the leaf is the current
version, and each `version-<version>` asset (role `archive`) is an earlier
one.

## What a run does

The workflow starts at 07:00 UTC every Monday.

1. `tools/refresh.py` probes each dataset in `tools/sources.json`. It reads
   the dataset's `last_updated` from the GeoNode API and the row count from
   a WFS `resultType=hits` request. That is two small requests per
   collection.
2. A collection is due when both conditions hold:
   - `last_updated` moved past the current version, or the row count
     changed.
   - At least `min_days` passed since the current version.
3. For each due collection, `tools/extract.py` extracts the WFS layer with
   `portolan extract wfs`. It repairs invalid geometries, reprojects to
   EPSG:4326 when GeoServer ignored the requested CRS, and sorts the rows
   on a Hilbert curve. It refuses the extract when the WFS row count moved
   during it.
4. The tool compares an order-independent hash of every row with the
   current version. Equal rows record the check in `state/checks.json`,
   refresh the metadata from GeoNode, and publish no new version.
5. `tools/check_styles.py` checks the style against the new rows. A styled
   column that is gone, a category that held rows and now holds none, or a
   new value with no category holds that collection back.
6. The tool downloads the outgoing current file from the bucket, checks it
   against the checksum `collection.json` records, and writes it to
   `versions/<old version>.parquet`. It writes the new `<leaf>.parquet` and
   `<leaf>.pmtiles`.
7. `tools/build_collection.py` moves the old version to a
   `version-<version>` asset and records the new one as the current asset.
   Title, description, keywords and providers come from the GeoNode record,
   which `tools/snapshot.py` stores in `tools/generate/data/geonode.json`.
8. `tools/generate/measure.py` re-measures each changed collection, and the
   docs regenerate (`tools/generate/build_docs.py`).
9. The workflow renders a thumbnail for each new version. A render that
   fails the blank-render gate keeps the previous image.
10. The workflow runs the catalog gates, then `tools/publish.py`, which
    uploads every archive first, then the data, then the metadata. It then
    runs every documented query against the bucket.
11. A second job commits the published `catalog/`, `state/` and
    `tools/generate/data/` to `main`.

A collection that fails at any step is rolled back. Its `catalog/` folder
returns to its state before the run. The other collections still publish.
The job then fails and opens or updates the issue "Scheduled refresh needs
attention".

The same run refreshes the imagery (`tools/imagery/refresh.py`) and the
virtual collections (`tools/virtual/refresh.py`), and compares GeoNode's
dataset list with `tools/sources.json`.

## A new or removed GeoNode dataset

The refresh never adds a dataset by itself. Every layer gets a data review
before it is mirrored, because a municipal layer can hold records about
private people. A new dataset is reported as a notice in the refresh issue.

To add one:

1. Extract it to a scratch directory and review its columns and values.
2. Add it to a group in `tools/generate/grouping.py`, or to `EXCLUDED`.
   Record no reason for an exclusion in the repository.
3. Run `python3 tools/geonode.py sources`, then
   `python3 tools/refresh.py --only <id>`.
4. Render and look at its thumbnail (`tools/generate/thumbs/render.sh`).

A dataset that GeoNode removes stays in the catalog with its last version,
and the notice says so. Remove it from `grouping.py` to take it out of the
STAC tree. Its files stay in the bucket, because publishing never deletes.

## How often each collection updates

`min_days` comes from each dataset's `maintenance_frequency` in GeoNode
(`MIN_DAYS` in `tools/geonode.py`). The refresh runs weekly, so no
collection gets more than one version a week.

| `maintenance_frequency` | `min_days` |
|---|---|
| `continual`, `daily`, `weekly`, `asNeeded`, `irregular`, `notPlanned`, `unknown` | 7 |
| `fortnightly` | 14 |
| `monthly` and longer | 28 |

## Dates in the metadata

| Field | Where | Meaning |
|---|---|---|
| `version` | Each version asset, Collection | The version label |
| `created` | Each version asset | When this catalog extracted the rows |
| `pergamino:source_updated` | Each version asset, Collection | GeoNode's `last_updated` for the dataset |
| `pergamino:update_frequency` | Collection | GeoNode's `maintenance_frequency` |
| `updated` | Collection | When the Collection last changed |
| `updated` | Root and group catalogs | The newest Collection `updated` below them |

`extent.temporal` is open. GeoNode records no content dates for its vector
datasets, and an extract date says when the catalog read the data, not what
period the data describes.

## Numbers and dates in the documentation

The READMEs and AGENTS.md files quote no numbers measured from the data and
no extraction dates. A refresh changes both. The docs describe what the
data holds and give queries. The current row count is `table:row_count` in
each `collection.json`.

Every fact the docs state about a dataset comes from the GeoNode record or
from `tools/generate/data/measured.json`, which `measure.py` writes from the
data. Two gates enforce the rules on the generated docs:

- `tests/test_no_data_numbers.py` fails on a thousands-separated number, a
  percentage, or any count that a `collection.json` records.
- `tests/test_no_stale_dates.py` fails on an ISO date or a dated
  "extracted" claim.

## Publishing a metadata change

`.github/workflows/publish.yml` publishes `catalog/` when a change to it
lands on `main`. Fix a style, run `python3 tools/refresh.py --restamp
<id>`, merge, and the bucket follows. The workflow runs the gates, then
`tools/check_sync.py`, then `tools/publish.py`. A CI checkout has no data
files, so it uploads metadata only. It never deletes. It shares the
`catalog-write` concurrency group with the refresh, so the two never run at
once.

A change that adds or renames a data file needs that file in the bucket
before the change merges, because CI runs the documented queries against
the bucket. Publish it by hand first.

## Credentials

The workflows sign in to the Source data proxy with GitHub OIDC. No key is
stored. Set this up once:

1. On source.coop, open the `nlebovits` profile, then the gear icon, then
   **Service Accounts**. Create an account.
2. Give it **Read and write** access to the `pergamino-ide` product.
3. Under **Signs in with**, add a **GitHub workflow** for the repository
   `nlebovits/pergamino-ide-catalog` and the environment `source-coop`.
4. In the GitHub repository settings, create the environment `source-coop`.
   Limit its deployment branches to `main`. Do not add required reviewers,
   because the weekly run would wait for an approval.
5. Add a repository variable `SOURCE_SA_ID` that holds the service account
   ID.

The proxy addresses the bucket as `s3://nlebovits/pergamino-ide` at the
endpoint `https://data.source.coop`. The workflows set
`PUBLISH_WRITE_PREFIX` and `AWS_ENDPOINT_URL_S3` for that. A maintainer who
publishes by hand keeps the raw-bucket `write_prefix` in
`catalog.publish.yaml` and selects a profile with `AWS_PROFILE` or the
optional `profile` key.

## Running it by hand

```bash
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
pipx install rashid==0.4.0
sudo apt-get install -y tippecanoe imagemagick
.venv/bin/python tools/refresh.py --dry-run
.venv/bin/python tools/refresh.py --only limites/cpa
```

`--force` ignores `min_days` and the source signals. It still records no
version when the rows are unchanged.

Thumbnails need Node.js 24.12 or newer and a running chiitiler. See
`tools/generate/thumbs/render.sh` and the workflow step that starts it.

## When a run fails

- **"the bucket is at version X, which this checkout does not have"**: a
  run published and then failed to commit. Download the run's
  `refreshed-metadata` artifact, copy it over `catalog/`, `state/` and
  `tools/generate/data/`, and commit it. Then run the refresh again.
- **"does not match the checksum of version X"**: the current file in the
  bucket changed outside the refresh. Find out what wrote it before you do
  anything else.
- **A style failure**: the new rows broke a legend. Fix the style, check it
  against the new data, and run the refresh for that collection.
- **"the source changed mid-extract"**: the publisher edited during the
  extract. The next run retries.
- **"probe failed"**: GeoNode did not answer. The next run retries.
