#!/usr/bin/env python3
"""Extract one collection from the GeoNode WFS into a GeoParquet file.

The steps, for the dataset ``tools/sources.json`` names:

1. ``portolan extract wfs --raw --output-crs EPSG:4326`` for that one
   typename. The CLI pages through the WFS, writes GeoParquet 1.1 with a
   ``bbox`` covering column, and also converts the layer's GeoServer SLD
   into a MapLibre style and fetches its legend image. The CLI converts
   only categorical SLD rules. When it writes no style, the layer's SLD is
   fetched and its range rules become a MapLibre ``step`` style
   (``tools/generate/sld_graduated.py``).
2. Repair invalid geometries with ``shapely.make_valid`` (default
   ``linework`` method), and recompute the ``bbox`` of each repaired row.
3. ``gpio sort hilbert``, so row groups carry spatial locality and DuckDB
   skips them on a bbox filter.
4. Compare the row count with the WFS ``resultType=hits`` count, read before
   and after the extract. A count that moved means the publisher was editing
   the layer, and the extract is refused.

``content_hash`` is an order-independent hash over every row. Two extracts of
unchanged data hash the same even when the WFS returns rows in another order,
which is how the refresh skips a no-op version.

    python3 tools/extract.py ambiente-y-agro/arbolado /tmp/out
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geonode  # noqa: E402

ATTEMPTS = 3
RETRY_PAUSE = 60


@dataclass(frozen=True)
class ExtractResult:
    parquet: Path
    style: Path | None
    legend: Path | None
    rows: int
    repaired: int
    null_geometries: int
    content_hash: str


def tool(name: str) -> str:
    """A console script from this interpreter's environment, else PATH."""
    local = Path(sys.executable).parent / name
    if local.exists():
        return str(local)
    found = shutil.which(name)
    if found is None:
        sys.exit(f"{name} is not installed; see tools/requirements.txt")
    return found


def run(args: list[str]) -> None:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-15:]
        raise RuntimeError(f"{Path(args[0]).name} failed:\n" + "\n".join(tail))


def extract_raw(alternate: str, workdir: Path) -> Path:
    """Run portolan's raw WFS extract and return the layer's directory.

    A long extract can lose one page to a timeout while GeoServer is busy.
    The whole layer is retried, up to ATTEMPTS times.
    """
    for attempt in range(1, ATTEMPTS + 1):
        out = workdir / f"extract-{attempt}"
        try:
            run([
                tool("portolan"), "extract", "wfs", geonode.OWS, str(out),
                "--layers", alternate, "--raw", "--auto",
                "--output-crs", "EPSG:4326", "--wfs-version", "2.0.0",
                "--timeout", "900",
            ])
            break
        except RuntimeError as exc:
            if attempt == ATTEMPTS:
                raise
            print(f"  extract attempt {attempt} failed, retrying in "
                  f"{RETRY_PAUSE}s: {str(exc).splitlines()[-1]}", flush=True)
            time.sleep(RETRY_PAUSE)
    files = [p for p in out.rglob("*.parquet") if ".portolan" not in p.parts]
    if len(files) != 1:
        raise RuntimeError(f"expected one parquet for {alternate}, got {files}")
    return files[0].parent


def repair_geometries(path: Path) -> tuple[int, int]:
    """Make every invalid geometry valid, in place. Returns (repaired, nulls).

    The bbox covering column is recomputed for repaired rows, because
    make_valid can drop a collapsed part and shrink the extent.
    """
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq
    import shapely

    table = pq.read_table(path)
    geoms = shapely.from_wkb(
        table.column("geometry").to_numpy(zero_copy_only=False))
    missing = shapely.is_missing(geoms)
    invalid = ~missing & ~shapely.is_valid(geoms)
    count = int(invalid.sum())
    if count:
        geoms[invalid] = shapely.make_valid(geoms[invalid])
        wkb = shapely.to_wkb(geoms, flavor="iso")
        index = table.schema.get_field_index("geometry")
        table = table.set_column(
            index, table.schema.field(index), pa.array(wkb, pa.binary()))
        if "bbox" in table.column_names:
            bounds = shapely.bounds(geoms)
            old = table.column("bbox").combine_chunks()
            names = ["xmin", "ymin", "xmax", "ymax"]
            columns = []
            for i, name in enumerate(names):
                values = old.field(name).to_numpy(zero_copy_only=False).copy()
                values[invalid] = bounds[invalid, i]
                columns.append(pa.array(values, pa.float64()))
            fixed = pa.StructArray.from_arrays(
                columns, names, mask=pa.array(missing))
            index = table.schema.get_field_index("bbox")
            table = table.set_column(index, table.schema.field(index), fixed)
        pq.write_table(table, path, compression="zstd")
    return count, int(np.asarray(missing).sum())


def declared_crs(path: Path) -> dict | str | None:
    """The CRS a GeoParquet file declares, or None for the default (CRS84).

    The GeoServer behind GeoNode ignores ``srsName=EPSG:4326`` for layers
    whose CRS list does not include it, and answers in the layer's native
    CRS, mostly EPSG:22175 (POSGAR 94 / Argentina 5). portolan writes that
    CRS into the file, and this is how the extract notices.
    """
    import json

    import pyarrow.parquet as pq

    meta = pq.ParquetFile(path).schema_arrow.metadata or {}
    geo = json.loads(meta.get(b"geo", b"{}"))
    return geo.get("columns", {}).get("geometry", {}).get("crs")


def check_lonlat(path: Path) -> None:
    """Refuse a file whose bbox is not longitude and latitude."""
    import json

    import pyarrow.parquet as pq

    if declared_crs(path) is not None:
        raise RuntimeError(f"{path.name} still declares a CRS after reprojection")
    meta = pq.ParquetFile(path).schema_arrow.metadata or {}
    bbox = json.loads(meta[b"geo"])["columns"]["geometry"].get("bbox")
    if bbox and not (-180 <= bbox[0] <= bbox[2] <= 180
                     and -90 <= bbox[1] <= bbox[3] <= 90):
        raise RuntimeError(f"{path.name} bbox {bbox} is not lon/lat")


def hilbert_sort(src: Path, dst: Path) -> None:
    run([tool("gpio"), "sort", "hilbert", str(src), str(dst)])


def content_hash(path: Path) -> str:
    """An order-independent hash of every row, as a decimal string.

    The sum of per-row hashes ignores order and, unlike XOR, does not cancel
    a duplicated row. Geometry is hashed after ``ST_Normalize``, so two
    repairs of one invalid shape that differ only in vertex order hash the
    same.
    """
    import duckdb
    import pyarrow.parquet as pq

    con = duckdb.connect()
    source = "read_parquet(?)"
    if "geometry" in pq.ParquetFile(path).schema_arrow.names:
        con.execute("INSTALL spatial; LOAD spatial;")
        source = (f"(SELECT * REPLACE (ST_AsWKB(ST_Normalize(geometry)) "
                  f"AS geometry) FROM {source})")
    return con.execute(
        "SELECT sum(hash(t)::HUGEINT)::VARCHAR || ':' || count(*) "
        f"FROM {source} t",
        [str(path)],
    ).fetchone()[0]


PMTILES_MAX_ZOOM = 15  # as catalog/.portolan/config.yaml
# tippecanoe keeps every point at the maximum zoom and drops 1.5 in 2.5 per
# zoom below it, so a layer of 10 points shows 4 at z12. ``g`` guesses the
# rate that keeps at most 50,000 features in the densest tile instead: a
# municipal point layer keeps every point at every zoom.
DROP_RATE = "--drop-rate=g"
# A dense point layer (43,525 trees) would then put every point in one
# 1.9 MB tile at z8. Point tiles are capped, and tippecanoe drops the
# densest points until a tile fits. Lines and polygons keep no cap.
POINT_TILE_BYTES = 500_000


def is_point_layer(parquet: Path) -> bool:
    """True when the GeoParquet metadata lists only point geometry types."""
    import pyarrow.parquet as pq

    geo = json.loads(pq.read_schema(parquet).metadata[b"geo"])
    column = geo["columns"][geo["primary_column"]]
    types = column.get("geometry_types") or []
    return bool(types) and all("Point" in t for t in types)


def tippecanoe_command(build):
    """gpio's tippecanoe command builder, with ``DROP_RATE`` added.

    gpio (pinned in tools/requirements.txt) has no drop-rate option.
    ``tests/test_refresh.py`` checks that the flag reaches the command.
    """
    def command(*args, **kwargs):
        cmd = build(*args, **kwargs)
        return cmd if DROP_RATE in cmd else cmd + [DROP_RATE]
    return command


def make_pmtiles(parquet: Path, out: Path, layer: str) -> None:
    """Build the collection's PMTiles with tippecanoe, through gpio.

    tippecanoe writes a progress line per tile to the inherited stderr. The
    output goes to a file and is shown only when the build fails.
    """
    import os

    from geoparquet_io.api.ops import create_pmtiles
    from geoparquet_io.core import pmtiles as gpio_pmtiles

    build = gpio_pmtiles._build_tippecanoe_command
    gpio_pmtiles._build_tippecanoe_command = tippecanoe_command(build)
    with tempfile.TemporaryFile() as log:
        saved = os.dup(2), os.dup(1)
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(log.fileno(), 2)
        os.dup2(log.fileno(), 1)
        try:
            cap = POINT_TILE_BYTES if is_point_layer(parquet) else None
            create_pmtiles(str(parquet), str(out), layer=layer, min_zoom=0,
                           max_zoom=PMTILES_MAX_ZOOM, force=True,
                           maximum_tile_bytes=cap)
        except Exception as exc:
            log.seek(0)
            tail = log.read().decode(errors="replace")[-3000:]
            raise RuntimeError(f"PMTiles build failed: {exc}\n{tail}") from exc
        finally:
            gpio_pmtiles._build_tippecanoe_command = build
            os.dup2(saved[0], 2)
            os.dup2(saved[1], 1)
            os.close(saved[0])
            os.close(saved[1])


def row_count(path: Path) -> int:
    import pyarrow.parquet as pq

    return pq.ParquetFile(path).metadata.num_rows


def extract(collection: str, outdir: Path,
            sources: dict | None = None) -> ExtractResult:
    """Extract, repair, sort and check one collection into ``outdir``.

    ``outdir`` receives ``<leaf>.parquet``, and ``style.json`` and
    ``legend.png`` when the WFS layer has them.
    """
    sources = sources or geonode.load_sources()
    entry = sources["collections"][collection]
    leaf = collection.split("/")[-1]
    before = geonode.hits(entry["alternate"])
    with tempfile.TemporaryDirectory(prefix=f"extract-{leaf}-") as tmp:
        layer = extract_raw(entry["alternate"], Path(tmp))
        result = process(layer, outdir, leaf)
    if result.style is None:
        style = graduated_style(entry["alternate"], leaf, outdir)
        if style is not None:
            result = replace(result, style=style)
    if result.style is not None:
        repair_style(entry["alternate"], result.style, result.parquet)
    after = geonode.hits(entry["alternate"])
    if not (before == after == result.rows):
        raise RuntimeError(
            f"{collection}: wrote {result.rows} rows, the WFS reported "
            f"{before} before and {after} after; the source changed "
            "mid-extract")
    return result


def graduated_style(alternate: str, leaf: str, outdir: Path) -> Path | None:
    """The layer's graduated SLD as a MapLibre style file, or None."""
    from generate.sld_graduated import convert_graduated

    sld = layer_sld(alternate)
    converted = convert_graduated(sld, leaf)
    if converted is None:
        return None
    out = outdir / "style.json"
    out.write_text(json.dumps(converted[0], indent=2) + "\n")
    return out


def layer_sld(alternate: str) -> bytes:
    return geonode.get(geonode.OWS, {
        "service": "WMS", "version": "1.1.1", "request": "GetStyles",
        "layers": alternate}, raw=True)


def repair_style(alternate: str, style_path: Path, parquet: Path) -> list[str]:
    """Fix the defects of the CLI's SLD conversion.

    A style whose SLD stacks symbolizers is converted again from the SLD
    (``generate/sld_stacked.py``). Every style then gets ``styles.repair``.
    """
    import styles

    from generate import sld_stacked

    style = json.loads(style_path.read_text())
    sld = layer_sld(alternate)
    notes = []
    if sld_stacked.is_stacked(sld):
        leaf = parquet.stem
        converted = sld_stacked.convert(sld, leaf, style)
        if converted is not None:
            style = converted
            notes.append("stacked symbolizers converted from the SLD")
            sld = None
    notes += styles.repair(style, styles.column_types(parquet), sld)
    if notes:
        style_path.write_text(json.dumps(style, indent=2,
                                         ensure_ascii=False) + "\n")
    return notes


def process(layer: Path, outdir: Path, leaf: str) -> ExtractResult:
    """Repair, sort and hash one raw extract directory into ``outdir``.

    ``layer`` is the directory ``portolan extract wfs --raw`` wrote for one
    typename. The raw Parquet in it is modified in place by the repair.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{leaf}.parquet"
    raw = next(p for p in layer.glob("*.parquet"))
    repaired, nulls = repair_geometries(raw)
    if declared_crs(raw) is not None:
        lonlat = raw.with_name(raw.stem + "-4326.parquet")
        run([tool("gpio"), "convert", "reproject", str(raw), str(lonlat),
             "-d", "EPSG:4326"])
        raw = lonlat
    hilbert_sort(raw, out)
    check_lonlat(out)
    style = legend = None
    found = layer / "styles" / "default.json"
    if found.exists():
        style = outdir / "style.json"
        shutil.copyfile(found, style)
    found = layer / "legends" / "source.png"
    if found.exists():
        legend = outdir / "legend.png"
        shutil.copyfile(found, legend)
    return ExtractResult(out, style, legend, row_count(out), repaired, nulls,
                         content_hash(out))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("collection")
    parser.add_argument("outdir", type=Path)
    args = parser.parse_args()
    r = extract(args.collection, args.outdir)
    print(f"{args.collection}: {r.rows} rows, {r.repaired} repaired, "
          f"{r.null_geometries} null geometries, hash {r.content_hash}")
