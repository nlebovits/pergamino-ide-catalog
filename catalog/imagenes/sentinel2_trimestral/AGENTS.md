# Guía para agentes — Sentinel-2, la fecha más despejada de cada trimestre

Un ítem por trimestre calendario desde 2017. Cada uno es el día del
trimestre cuyas escenas Sentinel-2 L2A cubren todo el Partido de Pergamino
con la menor nubosidad declarada. Los recursos apuntan a los COG de Element
84 Earth Search: este catálogo no copia ni recalcula píxeles. Ver el README
para el método.

## Cómo encontrar el trimestre que hace falta

Leer `items.parquet` (una fila por trimestre) y filtrar por `datetime`. No
recorrer los JSON de los ítems. El `id` es año + `q` + trimestre: `2025q3`.

URL base: `https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/`.
Archivos publicados: `<base>items.parquet`, `<base>escenas.parquet`,
`<base><id>/<id>.json` y `<base><id>/thumbnail.jpg`. Los píxeles están en
Earth Search, no en esta URL base.

Columnas útiles de `items.parquet` (stac-geoparquet; las propiedades del
ítem son columnas de primer nivel):

- `id`, `title`, `datetime` (hora de la primera toma del día), `geometry`
  (el partido intersecado con las huellas de las escenas), `bbox`,
  `assets`, `links`.
- `eo:cloud_cover`: la nubosidad declarada de la escena más nubosa del día,
  sobre la tesela MGRS entera.
- `pergamino:scene_ids`: las escenas del día, ids de Earth Search.
- `pergamino:source_collection`: `sentinel-2-c1-l2a` o `sentinel-2-l2a`.
- `pergamino:partido_coverage`: fracción del partido que cubren las
  huellas, de 0 a 1.
- `pergamino:attribution`: la leyenda Copernicus de ese año.

Los recursos `visual-<tesela>-<HHMM>` son el `TCI.tif` de cada escena: RGB
de 8 bits a 10 m, nodata 0, en UTM 20S (EPSG:32720) para 20HPH y 20HQH, y
UTM 21S (EPSG:32721) para 21HTC.

`escenas.parquet` tiene una fila por escena de Earth Search sobre el
rectángulo del partido desde 2017, con todas las columnas y recursos del
ítem de Earth Search: cada banda por su nombre común (`blue`, `green`,
`red`, `nir`, `swir16`…), `scl`, `visual` y `thumbnail`.

## Recetas probadas

Los trimestres, con su fecha y su nubosidad:

```sql
SELECT id, datetime, "eo:cloud_cover" AS nubosidad,
       "pergamino:source_collection" AS coleccion,
       "pergamino:partido_coverage" AS cobertura
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/items.parquet')
ORDER BY datetime;
```

Las URL de los COG de color verdadero de un trimestre:

```sql
SELECT e.id, e."grid:code" AS tesela, e.assets.visual.href AS tci
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/escenas.parquet') e
JOIN (
  SELECT unnest("pergamino:scene_ids") AS escena
  FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/items.parquet')
  WHERE id = '2025q3'
) s ON e.id = s.escena
ORDER BY e.id;
```

Otras fechas despejadas del mismo trimestre, con las URL de sus bandas roja
e infrarroja y de la SCL:

```sql
SELECT id, datetime, "grid:code" AS tesela, "eo:cloud_cover" AS nubosidad,
       assets.red.href AS rojo, assets.nir.href AS nir, assets.scl.href AS scl
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/escenas.parquet')
WHERE datetime >= TIMESTAMPTZ '2025-07-01 00:00:00+00'
  AND datetime < TIMESTAMPTZ '2025-10-01 00:00:00+00'
  AND "eo:cloud_cover" < 5
ORDER BY datetime, tesela;
```

El mosaico del día recortado al partido, en un GeoTIFF local. Cada ítem
trae su propio comando en `processing:expression`, en el primer recurso
`visual-*`. El recorte lee el límite del partido de su GeoParquet
publicado, así que GDAL necesita el driver Parquet (GDAL 3.5 o posterior,
compilado con Arrow):

```bash
export GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR
B=https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com
B=$B/sentinel-2-c1-l2a
P=https://data.source.coop/nlebovits/pergamino-ide
gdalwarp -t_srs EPSG:32720 -tr 10 10 -tap \
  -cutline /vsicurl/$P/limites/partido_pergamino/partido_pergamino.parquet \
  -crop_to_cutline -dstalpha \
  -co COMPRESS=DEFLATE -co TILED=YES \
  /vsicurl/$B/20/H/PH/2025/9/S2C_T20HPH_20250912T140820_L2A/TCI.tif \
  /vsicurl/$B/20/H/QH/2025/9/S2C_T20HQH_20250912T140820_L2A/TCI.tif \
  /vsicurl/$B/21/H/TC/2025/9/S2C_T21HTC_20250912T140820_L2A/TCI.tif \
  sentinel2_2025q3.tif
```

Mediana trimestral del NDVI en un cuadrado de 6 km alrededor del centro de
Pergamino, con lazycogs (probado con lazycogs 0.8.0 y obstore 0.12.1;
lazycogs pide Python 3.12 o posterior). lazycogs lee `escenas.parquet`,
reproyecta y combina las escenas al leer. Los archivos de
`sentinel-2-c1-l2a` están en el bucket público
`e84-earth-search-sentinel-data`, que se lee sin firmar:

```bash
curl -sO https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/escenas.parquet
```

```python
import lazycogs
import numpy as np
from obstore.store import S3Store
from pyproj import Transformer

x, y = Transformer.from_crs("EPSG:4326", "EPSG:32720", always_xy=True) \
    .transform(-60.5746, -33.8957)
store = S3Store("e84-earth-search-sentinel-data", region="us-west-2",
                skip_signature=True)
da = lazycogs.open(
    "escenas.parquet",
    datetime="2025-07-01/2025-09-30",
    bbox=(x - 3000, y - 3000, x + 3000, y + 3000),
    crs="EPSG:32720",
    resolution=10,
    bands=["red", "nir"],
    filter='"eo:cloud_cover" < 20',
    mosaic_method=lazycogs.MedianMethod,
    time_period="P1Y",
    store=store,
)
# Reflectancia de Collection 1: DN × 0.0001 − 0.1 (raster:bands de cada
# recurso).
red, nir = (da.sel(band=b).isel(time=0).astype("float32") * 0.0001 - 0.1
            for b in ("red", "nir"))
ndvi = ((nir - red) / (nir + red)).values
print(float(np.nanmedian(ndvi)))
```

## Advertencias

- `eo:cloud_cover` es la nubosidad de la tesela MGRS entera, no la del
  partido. Mirar `thumbnail.jpg` antes de usar una fecha.
- Las tres teselas usan dos proyecciones (UTM 20S y 21S). Para unirlas,
  reproyectar, como hacen las recetas de gdalwarp y lazycogs. Las capas
  vectoriales del catálogo están en EPSG:4326.
- El `TCI.tif` es la imagen de color verdadero de 8 bits que produce la
  ESA, no reflectancia. Para cualquier cálculo usar las bandas (`red`,
  `nir`…) de `escenas.parquet` o del ítem de Earth Search.
- La receta de lazycogs no enmascara nubes: filtra escenas por
  `eo:cloud_cover` y toma la mediana. Para enmascarar por píxel, leer
  también la banda `scl`.
- `sentinel-2-l2a` está en otro bucket (`sentinel-cogs`, también en
  us-west-2). Para leer esos trimestres con lazycogs hace falta un
  `S3Store` de ese bucket. En `sentinel-2-l2a` la reflectancia de las
  escenas anteriores a la línea base 04.00 es DN × 0.0001, sin el
  desplazamiento de −0.1: leer `raster:bands` de cada recurso.
- Al redistribuir o mostrar datos modificados, incluir "Contains modified
  Copernicus Sentinel data" con el año (`pergamino:attribution`).
