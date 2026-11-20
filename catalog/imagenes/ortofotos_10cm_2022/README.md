# Ortofotos 10 cm 2022

Mosaicos de ortofotos RGB del Partido de Pergamino que la Municipalidad
publica en su GeoNode, un ítem STAC por mosaico, en Cloud Optimized GeoTIFF.
Incluye una vista general de todos los mosaicos (`overview.tif`) y una copia
de los ítems en stac-geoparquet (`items.parquet`).

GeoNode describe cada mosaico con el mismo resumen y la misma declaración de
calidad:

> Vuelos fotogramétricos del año 2022 realizados con VANT a pedido de la
> Municipalidad de Pergamino.

> Las imágenes fueron capturadas y elaboradas por la empresa TECSO a pedido
> de la Municipalidad de Pergamino, poseen entre 8 y 10 cm/px de resolución
> espacial.

El campo "información complementaria" de cada registro nombra el área que
cubre el mosaico ("Área cubierta: Barrio Centro", "Área cubierta: Pueblo
Acevedo"). El título de cada ítem lo cita. Cuando un registro no trae esa
información ("No information provided"), el ítem toma el título del nombre
del mosaico en GeoNode.

## Contenido

- **Un ítem por mosaico.** El recurso `data` de cada ítem es el COG: RGB de
  8 bits en EPSG:4326, JPEG YCbCr, teselas de 512 px, overviews internas,
  máscara interna para el área sin imagen y estadísticas por banda
  embebidas en la cabecera. La geometría del ítem es la huella de los
  píxeles válidos, no el rectángulo de la grilla.
- **`overview.tif`**, recurso de la colección con los roles `visual` y
  `overview`: todos los mosaicos en una imagen RGB de 8 bits en Web Mercator
  (EPSG:3857) a 1 m, comprimida en WebP sin pérdida. El área sin imagen
  vale 0 y está declarada como nodata; ningún píxel con imagen vale 0. Sirve para ver qué cubre la
  colección sin abrir cada mosaico. Para medir o analizar, usar los COG de
  los ítems.
- **`items.parquet`**: una fila por ítem, en stac-geoparquet, ordenadas por
  la curva de Hilbert del centro de su bbox.
- **Vistas previas**: `thumbnail.jpg` en la colección (los mosaicos de la
  ciudad de Pergamino, recortados de la vista general) y en cada ítem.

## Qué se seleccionó

Se toman los datasets de GeoNode de subtipo `raster` cuyo nombre contiene
`10cm` y cuyo resumen dice 2022. Queda afuera `open_buildings_height_8m`,
también de subtipo `raster`, porque no es una ortofoto. GeoNode lo describe
así:

> Raster de alturas de edificios del Open Buildings 2.5D Temporal Dataset
> (Google Research). Estimaciones anuales (2016-2023) de altura de
> construcciones derivadas de Sentinel-2 mediante IA. Resolución efectiva
> ~8 m.

## Cómo se obtuvo cada mosaico

1. Se descarga el original de
   `https://geonode.pergamino.gob.ar/datasets/<alternate>/dataset_download`.
   GeoServer rechaza esa descarga para los mosaicos más grandes ("Download
   Limits Exceeded"). Esos se piden al WCS 2.0.1 de GeoServer
   (`https://geonode.pergamino.gob.ar/geoserver/ows`) en piezas cuadradas
   alineadas a la grilla nativa, sin remuestreo, y se arman en un solo
   raster. El WCS no entrega la máscara del original: escribe 0 donde no hay
   imagen, y la máscara se reconstruye como los píxeles con las tres bandas
   en 0.
2. Si la descarga ya cumple todos los requisitos de raster de Portolan v0.3.0
   (COG válido, teselas de 512 px, pirámide completa de overviews,
   estadísticas embebidas en la cabecera, máscara), se publica **byte a
   byte**, sin tocarla.
3. Si no, se recodifica **una vez** como COG JPEG con la misma calidad JPEG
   que declara el original, para no agregar más pérdida de la necesaria ni
   inflar el archivo. Las piezas del WCS, cuya calidad original no se
   conoce, usan calidad 75. Las estadísticas embebidas de un mosaico
   recodificado son exactas, calculadas sobre todos los píxeles
   enmascarados como válidos.

Cada ítem dice qué camino siguió: `pergamino:source_method`
(`dataset_download` o `wcs`), `pergamino:reencoded_because` (qué le faltaba
a la descarga, cuando se recodificó) y `pergamino:jpeg_quality`. La
descripción del recurso `data` lo repite en texto. Los ítems descargados
directamente tienen además un recurso `source` con la URL de descarga de
GeoNode.

## Fecha

GeoNode no registra la fecha de los vuelos: `temporal_extent_start` y
`temporal_extent_end` están vacíos y la fecha del registro es la de
publicación en GeoNode. El resumen dice "del año 2022". Por eso cada ítem
tiene `datetime` nulo y el intervalo `start_datetime` / `end_datetime` que
abarca 2022 entero.

## Actualización

Cada ítem guarda el `pk` y el `uuid` del registro de GeoNode
(`pergamino:geonode_pk`, `pergamino:geonode_uuid`) y el `last_updated` del
registro al momento de la descarga (`pergamino:source_updated`). La
actualización semanal (`tools/imagery/refresh.py`) compara ese valor con
GeoNode y vuelve a descargar solo los mosaicos que cambiaron, más los que
aparezcan nuevos. Un mosaico que desaparece de GeoNode no se borra solo: se
informa para que lo decida una persona.

## Licencia

**CC BY-SA 4.0.** El campo de licencia de cada registro de GeoNode está
vacío. La licencia sale de la declaración de la Municipalidad de Pergamino
para su Infraestructura de Datos Espaciales, publicada en
https://pergamino.ar/servicios/ide-pergamino/:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan
> licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar,
> compartir y adaptar este material siempre que reconozca atribución y
> permita la misma licencia en sus derivados.

Los mosaicos se publican en el GeoNode de esa IDE. La atribución que declara
cada registro es "Municipalidad de Pergamino". Las restricciones que
declara cada registro (`constraints_other`) son "Ninguna".

La colección declara `license: CC-BY-SA-4.0` (identificador SPDX) y enlaza
el texto de la licencia en Creative Commons como vínculo `license`.

## Procedencia

- Productor: TECSO, según la declaración de calidad citada arriba.
- Licenciante y publicador: Municipalidad de Pergamino, Dirección de
  Sistemas de Información Georreferenciada (DSIG).
- Fuente: https://geonode.pergamino.gob.ar/. Cada ítem enlaza su registro
  con un vínculo `via`, de la forma
  `https://geonode.pergamino.gob.ar/catalogue/#/dataset/<pk>`.
- Este catálogo es un espejo. Para el dato autoritativo, consultar el
  GeoNode de la Municipalidad.

## Limitaciones

- La resolución nominal es la que declara GeoNode, entre 8 y 10 cm/px. La
  grilla de los COG es la del original, en grados.
- Los mosaicos se superponen en los bordes. En la vista general, donde dos
  se superponen, se ve el que se dibujó último.
- Los mosaicos armados desde el WCS pueden enmascarar como "sin imagen"
  algún píxel real negro puro (las tres bandas en 0).

## Acceso rápido

```sql
INSTALL spatial; LOAD spatial;
SELECT id, title, "pergamino:geonode_pk" AS pk
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/ortofotos_10cm_2022/items.parquet')
ORDER BY id;
```

La guía para agentes, [AGENTS.md](./AGENTS.md), tiene recetas con GDAL,
rasterio y DuckDB.
