# Virtual collections

A virtual collection lists a dataset that another Portolan catalog already
publishes in a cloud-native format, restricted to the partido de Pergamino. It
copies no data bytes. Each one sits in the thematic group it belongs to,
beside the municipal layers, and carries `pergamino:virtual`, which is how
the tools and the gates find it. Each collection holds metadata,
a recipe that clips the upstream data to the partido, a style that masks
everything outside the partido, and a thumbnail rendered from the upstream
bytes. This page records how they are encoded, why, and what the Portolan
spec does not yet say about them.

## What there is, and where

| Collections | Upstream | Recipe asset |
|---|---|---|
| `ambiente-y-agro/glofas_*`, 15, one per layer, beside the observed floods `inundacion_1995` and `inundacion_2016` | JRC GloFAS flood hazard maps, through `nlebovits/jrc-glofas` on Source Cooperative | one GDAL VRT per collection |
| `catastro/edificios_overture`, `comercio-y-cultura/lugares_overture`, `vialidad/segmentos_overture`, `ambiente-y-agro/uso_del_suelo_overture` | Overture Maps, resolved through `overture-portolan` or Overture's own STAC | one DuckDB file per collection, holding its view |

The id of each collection is the `collection` field of its layer in
`tools/virtual/sources.json`. The group README of a theme lists its virtual
collections in a section of their own, with each producer's licence, and its
AGENTS.md names them.

GloFAS ships seven return periods for depth, the same seven reclassified into
hazard classes, permanent water, and a spurious-depth mask. The spurious-depth
layer is left out because it has no valid pixel inside the partido in tile
`ID75_S30_W70`. Each remaining layer is its own collection: the spec models a
single COG as a collection-level asset with no items, and return periods are
different variables, not scenes of one variable.

Overture's themes were chosen for a municipal IDE. Buildings, places, road
segments, and land use stay. Addresses are left out because the only address
part over the partido's bbox carries Chilean, Brazilian, and Uruguayan rows,
none Argentine. Divisions duplicate the catalog's own `limites/` group, and
Overture's water duplicates the municipality's `cursos_de_agua` and
`cuencas_arroyo_pergamino`. No theme was added beyond these four.

Both lists live in `tools/virtual/sources.json`, with the reason for every
exclusion.

## Encoding

### Data assets point upstream

The spec settles the main question. core.md (Asset Roles) says "a catalog
that provides metadata for data that is already available upstream in a
cloud-native format does not need a `source` asset; its `data` asset points
directly to the upstream data." So every `data` asset carries the absolute
upstream href and roles `["data", "external"]`, the role portolan-cli's
`external.py` already uses for the same purpose.

External data assets carry no `file:size` and no `file:checksum`. The bytes
belong to someone else and change on their schedule. A checksum frozen here
would turn every upstream re-publication into a false integrity failure.
The `jrc-glofas` items show the opposite risk: their declared sizes and
checksums do not match the bytes the server returns (one depth COG answers
84,041,273 bytes to a HEAD against 33,174,532 declared). Copying them would
have published wrong metadata with an air of verification.

### Provenance links

core.md (Source Provenance) makes these collections mirrors, because their
producer and host differ. Each one carries:

- `via` with `type: text/html` to the upstream's human page (PORTO-CORE-084):
  the JRC data catalogue entry and DOI for GloFAS, the Overture guide and
  schema pages for Overture;
- `canonical` to Overture's own STAC collection for the release in use. JRC
  publishes no STAC, so GloFAS has no `canonical`. `jrc-glofas` is another
  mirror, not the original source;
- `derived_from` to the Portolan collection the clip was built from
  (`jrc-glofas`, `overture-portolan`);
- for Overture, `rel: pmtiles` to Overture's published PMTiles.

### Recipes

Every clip is reproducible from the metadata alone.

- The `data` asset carries `processing:expression` (processing extension
  v1.2.0). GloFAS uses format `gdalwarp` with the full command line. Overture
  items use format `duckdb-sql` with the full `SELECT`.
- A local recipe asset, roles `["metadata", "recipe"]`, holds the same clip in
  a form a client opens directly. GloFAS gets `<collection>.vrt`, a warped
  VRT whose cutline is the partido and whose source is `/vsicurl/` on the
  upstream COG. Each Overture collection gets `<collection>.ddb`, a DuckDB
  database that holds its one view and no rows. The four collections live in
  four groups, so one shared file would sit outside three of them. Joining two
  layers attaches two files, as the `lugares_overture` guide shows.

The Overture views filter on the GeoParquet `bbox` covering column first, so
DuckDB skips row groups by their footer statistics, and then apply
`ST_Intersects` against the partido. The VRT's window is the partido's
bounding box snapped to the source grid. `tests/test_virtual.py` checks it
against the collection extent.

Every recipe reads the partido boundary from one URL, `partido.url` in
`tools/virtual/sources.json`, exposed as `common.PARTIDO_URL`:

```
https://data.source.coop/nlebovits/pergamino-ide/limites/partido_pergamino/partido_pergamino.parquet
```

That URL takes effect when the bucket migration lands. Until then the
boundary is served at `.../publico_partido_pergamino.parquet`. The builders
fall back to that legacy URL to read the geometry, and
`build.py --partido-url <legacy>` builds a test `.ddb` against it. DuckDB
binds a view when it is created, so a `.ddb` built that way reads the legacy
URL forever. The builder prints a warning, and such a file must not be
published.

The `.ddb` and every thumbnail are generated. The `.ddb` is gitignored like
any other binary, and `tools/publish.py` publishes it from `catalog/`. It
carries no `file:size` or `file:checksum`, because its bytes depend on the
DuckDB version that wrote it. It is written with `STORAGE_VERSION 'v1.0.0'`
so that DuckDB 1.x clients can attach it.

### Styles and the partido mask

Each collection's `styles/default.json` draws the data, then an inverse mask:
a world polygon with the partido as its hole, inlined as GeoJSON, followed by
the partido outline. Overture styles reuse `overture-portolan`'s default
layers over Overture's PMTiles. GloFAS styles hold the mask and outline only. Overture's PMTiles hold
places only from z14 and buildings only from about z13, so the `minzoom` of
those layers in `tools/virtual/sources.json` goes on their data layers: a map
opened at the partido's zoom shows nothing rather than an empty layer. The
thumbnails are drawn from the clip and ignore it.
Their COG is drawn from the `renders` object (viridis for depth, the JRC
class colours for hazard and water), the render-from-source path of
formats.md, so the COG keeps the `data` role and is not duplicated as
`visual`.

portolan-browser draws COGs with deck.gl in non-interleaved mode, above every
MapLibre layer. The mask therefore hides Overture features outside the partido
but cannot hide GloFAS pixels outside it. Fixing that needs either interleaved
rendering in the browser or a clipped raster, and a clipped raster is the copy
this design exists to avoid. The thumbnails do not have the problem, because
they are drawn from the VRT.

### Licences

Overture licences are copied from Overture's canonical STAC collection for
each theme, with Overture's attribution page as the `license` link.

GloFAS is `other` with two `license` links. The JRC distributes the maps with a
`copyright.txt` that grants CC BY 4.0, while the dataset README (section A02)
and the JRC data catalogue state ODbL 1.0. `jrc-glofas` declares
`proprietary`, which the spec forbids and which neither JRC text supports.
The collection README quotes both JRC texts and does not choose between them.

## Refresh

`tools/virtual/refresh.py` exposes
`refresh(catalog, now, dry_run) -> {collection_id: {"status", "detail"}}` for
the weekly job, and `python3 tools/virtual/refresh.py --dry-run` from the
command line.

- **Overture.** Overture deletes old releases a few months after each new one.
  Refresh re-resolves the latest release, through `overture-portolan` first
  and Overture's STAC (`collections.parquet`) second, and records the path in
  `pergamino:virtual.resolved_via`. A new release, a changed part list, or a
  stored href that no longer answers 200 rebuilds the collection's items,
  links, style, and `.ddb`. A missing `.ddb` (a fresh checkout) is
  rewritten too. A mirror that lags behind the stored
  release never steps a live collection back.
- **GloFAS.** Refresh re-resolves each COG through the `jrc-glofas` items and
  probes it. A moved COG rebuilds every GloFAS collection. A dead one is an
  error.

Outside a dry run every checked collection gets `updated = now`, changed or
not, as core.md asks of a mirror sync. The group catalogs take the newest
collection's stamp when `tools/generate/build_catalogs.py` relinks them. The
decision logic is pure and tested offline in `tests/test_virtual_refresh.py`.

## Conformance

<!-- CONFORMANCE -->

## Open questions for the spec

1. **Integrity fields on external assets.** The spec exempts third-party
   servers from the byte-range and CORS rules (core.md, Validation) but not
   from the expectation of `file:size` and `file:checksum`. For an asset whose
   bytes the publisher neither hosts nor controls, these fields are either
   omitted or wrong as soon as upstream re-publishes.
2. **A recipe role.** `processing:expression` records how a derived view is
   computed, but no Portolan role marks the asset that executes it (a VRT, a
   DuckDB file of views). This catalog uses `["metadata", "recipe"]`.
3. **Subset mirrors.** A virtual collection is a mirror of a spatial subset.
   Its extent, row counts, and statistics describe the subset, not the
   upstream collection. The spec does not say whether `canonical` should
   point at an upstream collection whose extent is the whole world.
4. **Local items over remote parts.** See the draft comment below.

## Draft comment for portolan-spec#260

Not posted. For the maintainer to review and post.

> A second shape of the same problem, from the Pergamino IDE catalog: a
> *virtual* collection that publishes no data bytes, only a clipped view of an
> upstream Portolan or STAC collection.
>
> Overture publishes per-part STAC items next to its GeoParquet. Our
> `catastro/edificios_overture` collection keeps the two building parts that
> cross the partido. We wrote one local item per part, each with an
> absolute `data` href into Overture's bucket (roles `data`, `external`), the
> clip as `processing:expression`, and a geometry clipped to the partido.
> That passes PTL-COL-005, but only because the local items differ from
> upstream: they carry the clipped geometry and row count. Where they would
> not differ, we would be in exactly the position this issue describes,
> republishing upstream item JSON to satisfy the validator.
>
> Two observations that may help choose between the options:
>
> 1. **Option (b) has a natural carrier already.** portolan-cli marks an
>    asset whose bytes live upstream with the role `external`. A collection
>    whose `canonical` link points at an upstream STAC collection and whose
>    item links, child links, or `external` data assets resolve into that
>    upstream's tree states the relationship explicitly, without a new field.
>    Option (a) alone cannot tell a deliberate metadata-first mirror from a
>    mirror that forgot to publish its items.
> 2. **The upstream tree moves.** Overture deletes releases a few months after
>    each new one, and `canonical` hrefs that embed the release go dead with
>    them. Any rule that traverses the upstream (option c) has to report a
>    vanished upstream differently from a wrong mirror, or every
>    metadata-first mirror of a rolling dataset fails between its
>    upstream's release and its own next sync.
>
> A related gap: PTL-AST-003 warns when an `external` data asset has no
> `file:size` or `file:checksum`. For bytes the publisher does not host, the
> value can only be copied, and copying is how we found an upstream catalog
> whose declared sizes do not match what its server returns. It would help if
> the spec said that integrity fields are optional on `external` assets, the
> way core.md's Validation section already exempts third-party servers from
> the byte-range and CORS rules.
