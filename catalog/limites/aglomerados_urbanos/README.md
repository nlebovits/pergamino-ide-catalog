# Aglomerados urbanos

Mancha de aglomerados urbanos del Partido de Pergamino donde se observan edificaciones e instalaciones urbanas en las cuales se desarrollan actividades humanas.

| | |
|---|---|
| Identificador | `limites/aglomerados_urbanos` |
| Geometría | polígonos |
| Fuente | [Aglomerados urbanos en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/46), capa WFS `geonode:aglomerados_urbanos` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> El dataset no debe ser tomado como un límite formal de la urbanidad/ruralidad, ya que es continuamente cambiante y no siempre responde a la planificación urbana, sino a las actividades humanas en el entorno social.

## Calidad de los datos

Según el registro de GeoNode:

> Los límites de las áreas se obtuvieron mediante imágenes aéreas, tomando como referencia los aglomerados de viviendas o industrias adyacentes a la Ciudad y Pueblos del Partido de Pergamino.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `area` | double |
| `metodologia` | string |
| `clasificacion` | string |
| `distrito` | string |
| `fecha_actualizacion` | double |
| `fuente` | string |
| `definicion` | string |
| `descargo_responsabilidad` | string |
| `observaciones` | string |
| `seccion` | int64 |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/aglomerados_urbanos/aglomerados_urbanos.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./aglomerados_urbanos.pmtiles` (capa `aglomerados_urbanos`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./aglomerados_urbanos.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_aglomerados_urbanos.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/46).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
