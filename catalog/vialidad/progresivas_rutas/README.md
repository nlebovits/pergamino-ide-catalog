# Progresivas y mojones de rutas

Progresivas en mojones de rutas nacionales y provinciales localizadas en el Partido de Pergamino.

| | |
|---|---|
| Identificador | `vialidad/progresivas_rutas` |
| Geometría | puntos |
| Fuente | [Progresivas y mojones de rutas en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/230), capa WFS `geonode:progresivas_rutas` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> Las progresivas son mojones en ambos lados de la ruta que indican el kilometraje o distancia de recorrido desde el inicio de la misma. El dataset puede utilizarse como sistema de referencia lineal para geocodificación.

## Calidad de los datos

Según el registro de GeoNode:

> Los datos fueron tomados inicialmente de IDERA y mejorados en precisión geográfica mediante relevamientos propios. Los mojones no observados fueron calculados por interpolación lineal.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `ruta` | string |
| `progresiva` | int64 |
| `tipo` | string |
| `observaciones` | string |
| `fuente` | string |
| `localidad_cercana` | string |
| `limite_localidad` | int64 |
| `limite_partido` | int64 |
| `visible` | int64 |
| `dañado` | int64 |
| `lat` | double |
| `lon` | double |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/progresivas_rutas/progresivas_rutas.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./progresivas_rutas.pmtiles` (capa `progresivas_rutas`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./progresivas_rutas.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_progresivas_rutas.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/230).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
