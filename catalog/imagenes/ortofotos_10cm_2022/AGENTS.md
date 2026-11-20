# Guía para agentes — Ortofotos 10 cm 2022

Mosaicos RGB de vuelos con VANT de 2022 que la Municipalidad de Pergamino
publica en su GeoNode, un ítem STAC por mosaico. GeoNode: "Vuelos
fotogramétricos del año 2022 realizados con VANT a pedido de la
Municipalidad de Pergamino." y "poseen entre 8 y 10 cm/px de resolución
espacial".

## Cómo encontrar el mosaico que hace falta

Leer `items.parquet` (una fila por ítem) y filtrar por geometría. No
recorrer los JSON de los ítems uno por uno. La geometría de cada fila es la
huella de los píxeles válidos del mosaico, en EPSG:4326.

URL base: `https://data.source.coop/nlebovits/pergamino-ide/imagenes/ortofotos_10cm_2022/`.
El COG de un ítem está en `<base><id>/<id>.tif`. En `items.parquet` el
`href` del recurso `data` es relativo a la carpeta del ítem (`./<id>.tif`),
así que la URL se arma con el `id`.

Columnas de `items.parquet` (stac-geoparquet; las propiedades del ítem son
columnas de primer nivel):

- `id`, `title`, `description` (resumen y declaración de calidad citados de
  GeoNode), `geometry`, `bbox`, `start_datetime`, `end_datetime`, `assets`.
- `proj:code`, `proj:shape`, `proj:transform`, `proj:bbox`: la grilla del
  COG.
- `pergamino:geonode_pk`, `pergamino:geonode_uuid`,
  `pergamino:geonode_alternate`, `pergamino:geonode_title`: el registro de
  GeoNode. Su página es
  `https://geonode.pergamino.gob.ar/catalogue/#/dataset/<pk>`.
- `pergamino:source_updated`: `last_updated` del registro de GeoNode cuando
  se descargó.
- `pergamino:source_method` (`dataset_download` o `wcs`),
  `pergamino:reencoded_because`, `pergamino:jpeg_quality`: cómo se obtuvo
  el COG. Ver el README.
- `pergamino:attribution`: la atribución que declara GeoNode.

## Recetas probadas

Qué mosaico cubre un punto (aquí, un punto del Barrio Centro):

```sql
SELECT id, title,
       'https://data.source.coop/nlebovits/pergamino-ide/imagenes/ortofotos_10cm_2022/'
         || id || '/' || id || '.tif' AS cog
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/ortofotos_10cm_2022/items.parquet')
WHERE ST_Intersects(geometry, ST_Point(-60.5746, -33.8957));
```

Cada mosaico con su registro de GeoNode y cómo se obtuvo:

```sql
SELECT id,
       "pergamino:geonode_title" AS titulo_geonode,
       'https://geonode.pergamino.gob.ar/catalogue/#/dataset/'
         || "pergamino:geonode_pk" AS registro,
       "pergamino:source_method" AS metodo,
       "pergamino:source_updated" AS actualizado_en_geonode
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/ortofotos_10cm_2022/items.parquet')
ORDER BY id;
```

Mosaicos que tocan un barrio del catálogo (`limites/barrios_y_pueblos`):

```sql
SELECT b.nombre AS barrio, o.id AS mosaico
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') b
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/ortofotos_10cm_2022/items.parquet') o
  ON ST_Intersects(b.geometry, ST_SetCRS(o.geometry, 'OGC:CRS84'))
WHERE b.nombre ILIKE '%centro%'
ORDER BY mosaico;
```

Leer la estructura de un COG sin descargarlo:

```bash
gdalinfo \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/imagenes/ortofotos_10cm_2022/centro_10cm/centro_10cm.tif
```

Recortar un rectángulo a un GeoTIFF local (lee solo las teselas que tocan):

```bash
gdal_translate -projwin -60.578 -33.893 -60.571 -33.898 \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/imagenes/ortofotos_10cm_2022/centro_10cm/centro_10cm.tif \
  recorte_centro.tif
```

Leer una ventana con rasterio, con la máscara activa:

```python
import rasterio
from rasterio.windows import from_bounds

url = ("https://data.source.coop/nlebovits/pergamino-ide/imagenes/"
       "ortofotos_10cm_2022/centro_10cm/centro_10cm.tif")
with rasterio.open(url) as src:
    win = from_bounds(-60.578, -33.898, -60.571, -33.893, src.transform)
    rgb = src.read(window=win, masked=True)
print(rgb.shape, rgb.mask.mean())
```

Ver toda la colección de una vez, desde la vista general (lee una overview
interna, no la imagen a 1 m):

```python
import rasterio

url = ("https://data.source.coop/nlebovits/pergamino-ide/imagenes/"
       "ortofotos_10cm_2022/overview.tif")
with rasterio.open(url) as src:
    small = src.read([1, 2, 3],
                     out_shape=(3, src.height // 64, src.width // 64),
                     masked=True)
print(src.crs, small.shape)
```

## Advertencias

- Leer siempre con la máscara (`masked=True`). Fuera de la huella los
  píxeles valen 0 y no son imagen.
- El sistema de referencia de los ítems es EPSG:4326 (grados), el que
  entrega GeoNode. La vista general está en EPSG:3857. Para medir
  distancias o áreas, reproyectar a una proyección métrica, por ejemplo
  UTM 20S (EPSG:32720).
- GeoNode no registra la fecha de vuelo. Los ítems tienen `datetime` nulo y
  un intervalo que abarca 2022. No inferir una fecha más precisa.
- Las estadísticas por banda de los ítems que se publicaron byte a byte son
  las que trae el archivo de GeoNode, marcadas como aproximadas
  (`STATISTICS_APPROXIMATE=YES`). Las de los recodificados son exactas.
- Licencia CC BY-SA 4.0 por la declaración de la IDE municipal (ver el
  README). Atribuir a la Municipalidad de Pergamino.
