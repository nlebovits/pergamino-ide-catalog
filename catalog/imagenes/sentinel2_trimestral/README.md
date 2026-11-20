# Sentinel-2: la fecha más despejada de cada trimestre

Una fecha por trimestre calendario, desde el primero de 2017, de imágenes
Sentinel-2 L2A (reflectancia de superficie) sobre el Partido de Pergamino.
Cada ítem es el día del trimestre cuyas escenas cubren todo el partido con
la menor nubosidad declarada.

Este catálogo no copia ni recalcula ningún píxel. Los ítems apuntan a los
COG que publica Element 84 Earth Search en el Registry of Open Data on AWS,
y enlazan cada escena con todas sus bandas.

## Contenido

Un ítem por trimestre (`2025q3`, por ejemplo), con:

- **`visual-<tesela>-<HHMM>`**, uno por escena del día: el `TCI.tif` de
  Earth Search, color verdadero RGB de 8 bits a 10 m en la proyección UTM
  de su tesela MGRS, nodata 0, con overviews internas. Tres teselas cubren
  el partido: 20HPH y 20HQH (UTM 20S) y 21HTC (UTM 21S). `HHMM` es la hora
  UTC de la toma. Un día con dos pasadas tiene la misma tesela dos veces.
  Los recursos llevan los roles `data`, `visual` y `external`, sin
  `file:size` ni `file:checksum`: el archivo es de Earth Search y puede
  cambiar.
- **`thumbnail`**: JPEG del mosaico del día recortado al partido, generado
  desde las overviews de los COG.
- Un vínculo **`derived_from`** por escena, al ítem de Earth Search. Ese
  ítem tiene todas las bandas (B01 a B12), la clasificación de escena (SCL)
  y los metadatos de la escena.

La geometría de cada ítem es el partido intersecado con las huellas de las
escenas del día. `datetime` es la hora de la primera toma del día.

En la colección:

- **`items.parquet`**: una fila por ítem, en stac-geoparquet.
- **`escenas.parquet`**: todas las escenas Sentinel-2 L2A de Earth Search
  que tocan el rectángulo del partido desde 2017, una fila por escena, en
  orden temporal, en stac-geoparquet. Sirve para elegir otra fecha, armar
  una serie temporal o calcular una mediana sin consultar la API de Earth
  Search.

## Método

`tools/imagery/s2_quarterly.py`, para cada trimestre:

1. Busca en Element 84 Earth Search
   (`https://earth-search.aws.element84.com/v1`) las escenas L2A que tocan
   el rectángulo del partido (longitud -60.944 a -60.139, latitud -34.177 a
   -33.540) en el trimestre. Agrupa las escenas por día.
2. Se queda con los días cuyas huellas cubren el partido entero. De esos
   elige el día cuya escena más nubosa tiene el menor `eo:cloud_cover`. La
   nubosidad es la que declara Earth Search para la tesela MGRS entera, no
   la del partido.
3. Usa la colección `sentinel-2-c1-l2a` (que Earth Search titula
   "Sentinel-2 Collection 1 Level-2A") cuando tiene un día que cubre el
   partido. Si no, usa `sentinel-2-l2a` ("Sentinel-2 Level-2A"). Sobre el
   partido `sentinel-2-c1-l2a` no tiene escenas de 2017 y tiene huecos en
   2022. Cada ítem dice qué colección usó
   (`pergamino:source_collection`).
4. Si ningún día cubre el partido entero, elige el que cubre la mayor
   parte. `pergamino:partido_coverage` guarda la fracción cubierta, de 0 a
   1.

Un trimestre sin ninguna escena no tiene ítem y queda listado en
`pergamino:excluded_quarters` de la colección.

## Actualización

`tools/imagery/refresh.py`, llamado por la actualización semanal, agrega el
trimestre más reciente cuando terminó hace al menos 14 días y todavía no
está. La misma corrida reconstruye `items.parquet` y `escenas.parquet`.

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

Las miniaturas son datos modificados: llevan "Contains modified Copernicus
Sentinel data" con el año en su descripción. Quien recorte, combine o
modifique las escenas debe incluir esa leyenda con el año o los años que
use. Cada ítem trae la leyenda de su año en `pergamino:attribution`.

No hay identificador SPDX para estos términos, así que la colección declara
`license: other` y enlaza el aviso legal.

## Procedencia

- Productor: la Agencia Espacial Europea (ESA), dentro del programa
  Copernicus de la Unión Europea.
- Escenas L2A en COG y catálogo STAC: Element 84, Earth Search, con las
  imágenes en el Registry of Open Data on AWS
  (https://registry.opendata.aws/sentinel-2-l2a-cogs/).
- Selección de fechas, ítems y miniaturas: este catálogo, con
  `tools/imagery/s2_quarterly.py`.

## Limitaciones

- `eo:cloud_cover` mide la tesela MGRS entera, que es mucho más grande que
  el partido. La fecha elegida puede tener nubes sobre el partido aunque
  la tesela declare poca nubosidad, o al revés. Mirar la miniatura.
- Los recursos apuntan a archivos de Earth Search. Si Element 84 los mueve
  o los borra, el recurso deja de responder. El identificador de cada
  escena (`pergamino:scene_ids`) permite buscarla de nuevo en Earth Search.
- Los trimestres que salen de `sentinel-2-l2a` y los de
  `sentinel-2-c1-l2a` tienen líneas base de procesamiento distintas de la
  ESA (cada escena declara la suya en `s2:processing_baseline`).

## Acceso rápido

```sql
SELECT id, datetime, "eo:cloud_cover" AS nubosidad,
       "pergamino:source_collection" AS coleccion
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/imagenes/sentinel2_trimestral/items.parquet')
ORDER BY datetime;
```

La guía para agentes, [AGENTS.md](./AGENTS.md), tiene recetas con DuckDB,
GDAL y lazycogs.
