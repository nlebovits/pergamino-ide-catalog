# Barrido y limpieza de calles

Zonas de barrido y limpieza de calles en la Ciudad de Pergamino.

| | |
|---|---|
| Identificador | `servicios-municipales/barrido_y_limpieza` |
| Geometría | polígonos |
| Fuente | [Barrido y limpieza de calles en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/67), capa WFS `geonode:barrido_y_limpieza` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> El dataset brinda la información de las zonas donde se realiza barrido y limpieza de calle, en particular sobre calles con cordón cuneta y asfaltadas.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue provisto por la Secretaría de Servicios Públicos.

## Restricciones de uso declaradas

Según el registro de GeoNode:

> Ninguno

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `numero_zona` | int64 |
| `zona` | string |
| `empresa` | string |
| `frecuencia` | string |
| `fuente` | string |
| `actualizacion` | string |
| `expediente_electronico` | string |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/barrido_y_limpieza.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./barrido_y_limpieza.pmtiles` (capa `barrido_y_limpieza`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./barrido_y_limpieza.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_barrido_y_limpieza.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/67).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
