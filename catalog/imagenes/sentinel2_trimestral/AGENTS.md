# Guía para agentes — Sentinel-2, mosaicos trimestrales

Un ítem por trimestre calendario desde 2017. Cada uno es la mediana por
píxel de las observaciones Sentinel-2 L2A sin nubes del trimestre, sobre el
rectángulo del Partido de Pergamino. Derivado de Copernicus Sentinel-2 vía
Element 84 Earth Search. Ver el README para el método.

## Cómo encontrar el trimestre que hace falta

Leer `items.parquet` (una fila por trimestre) y filtrar por
`start_datetime`. No recorrer los JSON de los ítems.

URL base: `https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/`.
Archivos de un ítem: `<base><id>/data.tif`, `<base><id>/visual.tif`,
`<base><id>/thumbnail.jpg`. El `id` es año + `q` + trimestre: `2024q3`.

Columnas útiles de `items.parquet` (stac-geoparquet; las propiedades del
ítem son columnas de primer nivel):

- `id`, `title`, `start_datetime`, `end_datetime` (`datetime` es nulo),
  `geometry` (huella de los píxeles con datos), `bbox`, `assets`.
- `proj:code` (`EPSG:32720`), `proj:shape`, `proj:transform`, `gsd`.
- `pergamino:source_collection`: colección de Earth Search de la que salen
  las escenas.
- `pergamino:scene_count`, `pergamino:scene_ids`,
  `pergamino:acquisition_days`: cuántas escenas y días entraron.
- `pergamino:valid_percent`: porcentaje del rectángulo con al menos una
  observación despejada.
- `pergamino:max_scene_cloud_cover`, `pergamino:dn_shift`: parámetros del
  método.
- `pergamino:attribution`: la leyenda Copernicus de ese año.

## Bandas de `data.tif`

| Banda del archivo | Sentinel-2 | `eo:common_name` |
|---|---|---|
| 1 | B02 | blue |
| 2 | B03 | green |
| 3 | B04 | red |
| 4 | B08 | nir |

uint16, nodata 0. Reflectancia de superficie = DN × 0.0001 − 0.1, en todos
los trimestres (también los de 2017, ya llevados a esa convención). Lo
declara cada banda en `raster:scale` y `raster:offset`.

## Recetas probadas

Los trimestres y cuánto respaldo tiene cada uno:

```sql
SELECT id, start_datetime, end_datetime,
       "pergamino:source_collection" AS coleccion,
       "pergamino:scene_count" AS escenas,
       "pergamino:valid_percent" AS pct_con_datos
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/items.parquet')
ORDER BY start_datetime;
```

Las escenas de Earth Search que entraron en un trimestre:

```sql
SELECT id, unnest("pergamino:scene_ids") AS escena
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/items.parquet')
WHERE id = '2024q3';
```

Valores de las cuatro bandas en un punto (lon, lat en grados):

```bash
gdallocationinfo -wgs84 -valonly \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/2024q3/data.tif \
  -60.5746 -33.8957
```

NDVI de un rectángulo, en reflectancia:

```python
import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

url = ("https://data.source.coop/nlebovits/pergamino-ide/imagenes/"
       "sentinel2_trimestral/2024q3/data.tif")
with rasterio.open(url) as src:
    box = transform_bounds("EPSG:4326", src.crs,
                           -60.62, -33.92, -60.54, -33.86)
    win = from_bounds(*box, transform=src.transform)
    red, nir = src.read([3, 4], window=win, masked=True)
red = red.astype("float32") * 0.0001 - 0.1
nir = nir.astype("float32") * 0.0001 - 0.1
ndvi = (nir - red) / (nir + red)
print(float(np.ma.median(ndvi)))
```

Recortar el color verdadero a un GeoTIFF local:

```bash
gdalwarp -t_srs EPSG:4326 -te -60.62 -33.92 -60.54 -33.86 \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/2024q3/visual.tif \
  pergamino_2024q3.tif
```

## Advertencias

- `visual.tif` tiene un estiramiento fijo para mirar, no reflectancia. Para
  cualquier cálculo usar `data.tif` y la escala de arriba.
- El sistema de referencia es UTM 20S (EPSG:32720), en metros. Las capas
  vectoriales del catálogo están en EPSG:4326: transformar las coordenadas
  antes de cruzarlas, como en la receta del NDVI.
- La mediana mezcla fechas dentro del trimestre. No usar un mosaico para
  fechar un evento.
- Un `pergamino:valid_percent` bajo o un `pergamino:scene_count` chico
  indican un trimestre con pocas observaciones despejadas, donde pueden
  quedar restos de nubes que la SCL no detectó.
- Los trimestres de 2017 salen de `sentinel-2-l2a` y los siguientes de
  `sentinel-2-c1-l2a`, con líneas base de procesamiento distintas. Las
  series largas que crucen ese límite deben tenerlo en cuenta.
- Al redistribuir o mostrar estos datos, incluir "Contains modified
  Copernicus Sentinel data" con el año (`pergamino:attribution`).
