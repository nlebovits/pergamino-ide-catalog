# Educacion por gestion

Capa de establecimientos educativos del Partido de Pergamino organizados por gestión como jardines, escuelas, colegios, institutos, profesorados y universidades

| | |
|---|---|
| Identificador | `educacion/gestion` |
| Geometría | puntos |
| Fuente | [Educacion por gestion en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/300), capa WFS `geonode:educacion_gestion` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> Si bien los establecimientos educativos son publicados por organismos oficiales de PBA, la ubicación de ellos difiere en ciertos casos, por ello los hemos adaptado para mejorar la calidad del dato local.

## Calidad de los datos

Según el registro de GeoNode:

> Los datos fueron obtenidos a partir de datos abiertos de Mapa Escolar PBA. Se reposicionaron algunas escuelas a partir de imágenes aéreas.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `clave` | string |
| `cue_anexo` | double |
| `nombre` | string |
| `nro` | string |
| `direccion` | string |
| `calles_ale` | string |
| `telefono` | string |
| `cp` | string |
| `email` | string |
| `sector` | string |
| `layer` | string |
| `etiqueta` | string |
| `nivel` | string |
| `fuente` | string |
| `latitud` | double |
| `longitud` | double |
| `barrio` | string |
| `localidad` | string |
| `estado` | string |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/gestion/gestion.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./gestion.pmtiles` (capa `gestion`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./gestion.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_educacion_gestion.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/300).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, Mapa Escolar".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
