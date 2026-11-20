# Sentinel-2: mosaicos trimestrales sin nubes

Un mosaico por trimestre calendario, desde el primero de 2017, de imágenes
Sentinel-2 L2A (reflectancia de superficie) sobre el rectángulo del Partido
de Pergamino (longitud -60.944 a -60.139, latitud -34.177 a -33.540). Cada
mosaico es la mediana por píxel de las observaciones del trimestre que la
clasificación de escena de Sentinel-2 no marca como nube, sombra de nube,
cirro, saturación o sin dato.

Contains modified Copernicus Sentinel data. El año de cada mosaico va en su
ítem (`pergamino:attribution`).

## Contenido

Un ítem por trimestre (`2024q3`, por ejemplo), con:

- **`data`**: COG de 4 bandas uint16 a 10 m en UTM 20S (EPSG:32720): B02
  (azul), B03 (verde), B04 (rojo) y B08 (infrarrojo cercano), en ese orden.
  Nodata 0. DEFLATE con predictor 2, teselas de 512 px, overviews internas
  y estadísticas exactas por banda embebidas en la cabecera. Cada banda
  declara en `bands` su `eo:common_name`, su longitud de onda central y su
  escala: reflectancia = DN × 0.0001 − 0.1.
- **`visual`**: COG RGB de 8 bits (B04, B03, B02) en JPEG, con máscara
  interna, para ver el mosaico en un navegador.
- **`thumbnail`**: JPEG reducido del recurso `visual`.

La geometría de cada ítem es la huella de los píxeles con al menos una
observación sin nubes en el trimestre. `items.parquet`, en la colección,
tiene una fila por ítem.

## Método

`tools/imagery/s2_quarterly.py`, para cada trimestre:

1. Busca en Element 84 Earth Search
   (`https://earth-search.aws.element84.com/v1`) las escenas L2A que tocan
   el rectángulo del partido en el trimestre. Usa la colección
   `sentinel-2-c1-l2a` (que Earth Search titula "Sentinel-2 Collection 1
   Level-2A") cuando tiene escenas para el trimestre, y si no,
   `sentinel-2-l2a` ("Sentinel-2 Level-2A"). Sobre este rectángulo `sentinel-2-c1-l2a` no tiene
   escenas de 2017, así que los trimestres de 2017 salen de
   `sentinel-2-l2a`. Cada ítem dice cuál usó
   (`pergamino:source_collection`).
2. Descarta las escenas cuya nubosidad declarada (`eo:cloud_cover`, sobre
   la tesela MGRS entera) supera el 90 %: cuestan una lectura completa y no
   aportan casi ningún píxel despejado. Si eso dejara el trimestre sin
   escenas, las usa todas. El umbral queda en cada ítem
   (`pergamino:max_scene_cloud_cover`).
3. Carga B02, B03, B04, B08 y la clasificación de escena (SCL) con
   odc-stac, a 10 m en EPSG:32720, agrupando por día solar, en bloques dask
   de 2048 px. La SCL, de 20 m, se lleva a 10 m por vecino más cercano.
4. Enmascara los píxeles con SCL 0 (sin dato), 1 (saturado o defectuoso),
   3 (sombra de nube), 8 (nube, probabilidad media), 9 (nube, probabilidad
   alta) y 10 (cirro), y los valores 0.
5. Toma la mediana por píxel de lo que queda.

Los trimestres sin escenas, o sin ningún píxel despejado, no tienen ítem:
un mosaico enteramente sin datos no describe nada. Quedan listados en
`pergamino:excluded_quarters` de la colección.

### Una sola convención de valores

En Collection 1 la reflectancia es DN × 0.0001 − 0.1. Las escenas de
`sentinel-2-l2a` anteriores a la línea base 04.00 declaran desplazamiento
0 (reflectancia = DN × 0.0001). Antes de la mediana, a los DN distintos de
0 de esas escenas se les suma la diferencia, calculada del `offset` que
declara cada escena (1000 en ese caso), para que todos los mosaicos
compartan la convención de Collection 1. Cada ítem guarda lo que se sumó
en `pergamino:dn_shift`. Las escenas de las dos colecciones además salen
de líneas base de procesamiento distintas de la ESA (cada escena declara
la suya en `s2:processing_baseline`), así que los trimestres de 2017 no son
estrictamente comparables con los siguientes.

### Estiramiento del recurso `visual`

El mismo para todos los trimestres, para poder compararlos a simple vista:
reflectancia de 0 a 0.20 llevada linealmente a 1–255 y luego una gamma de
1/1.4. El valor 0 queda para la máscara. Para analizar, usar `data`, no
`visual`.

## Cuántas observaciones tiene cada trimestre

Cada ítem registra cuántas escenas entraron (`pergamino:scene_count`), sus
identificadores (`pergamino:scene_ids` y un vínculo `derived_from` a cada
una), cuántos días solares distintos (`pergamino:acquisition_days`) y qué
porcentaje del rectángulo tiene al menos una observación despejada
(`pergamino:valid_percent`, igual al `valid_percent` de las estadísticas de
cada banda). Un trimestre con pocas observaciones despejadas se publica
igual; esos campos dicen cuánto confiar en él.

## Actualización

`tools/imagery/refresh.py`, llamado por la actualización semanal, agrega el
trimestre más reciente cuando terminó hace al menos 14 días y todavía no
está. Los trimestres ya publicados no se recalculan.

## Licencia

Los datos de Sentinel-2 se rigen por el aviso legal de la Comisión Europea
sobre el uso de datos Copernicus Sentinel
(https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice):

> The access and use of Copernicus Sentinel Data and Service Information is
> regulated under EU law. In particular, the law provides that users shall
> have a free, full and open access to Copernicus Sentinel Data and Service
> Information without any express or implied warranty, including as
> regards quality and suitability for any purpose.

> EU law grants free access to Copernicus Sentinel Data and Service
> Information for the purpose of the following use in so far as it is
> lawful: (a) reproduction; (b) distribution; (c) communication to the
> public; (d) adaptation, modification and combination with other data and
> information; (e) any combination of points (a) to (d).

> Where the Copernicus Sentinel Data and Service Information have been
> adapted or modified, the user shall provide the following notice:
> (1) 'Contains modified Copernicus Sentinel data [Year]' for Sentinel data

Estos mosaicos son datos modificados. Quien los redistribuya o los muestre
debe incluir "Contains modified Copernicus Sentinel data" con el año o los
años que use.

No hay identificador SPDX para estos términos, así que la colección declara
`license: other` y enlaza el aviso legal.

## Procedencia

- Productor: la Agencia Espacial Europea (ESA), dentro del programa
  Copernicus de la Unión Europea.
- Escenas L2A en COG y catálogo STAC: Element 84, Earth Search
  (https://earth-search.aws.element84.com/v1), con las imágenes en el
  Registry of Open Data on AWS
  (https://registry.opendata.aws/sentinel-2-l2a-cogs/).
- Mosaicos: calculados para este catálogo con
  `tools/imagery/s2_quarterly.py`.

## Limitaciones

- La mediana mezcla fechas: un píxel puede venir de una escena y su vecino
  de otra. No sirve para fechar un evento dentro del trimestre.
- La SCL de Sentinel-2 no detecta todas las nubes ni todas las sombras. Con
  pocas observaciones despejadas pueden quedar restos.
- El rectángulo cubre más que el partido. Para recortar al límite, usar
  `limites/partido_pergamino` del catálogo.

## Acceso rápido

```sql
INSTALL spatial; LOAD spatial;
SELECT id, start_datetime, "pergamino:scene_count" AS escenas
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/items.parquet')
ORDER BY start_datetime;
```

La guía para agentes, [AGENTS.md](./AGENTS.md), tiene recetas con GDAL,
rasterio y DuckDB.
