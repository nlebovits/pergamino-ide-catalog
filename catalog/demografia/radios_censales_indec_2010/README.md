# Radios censales indec 2010

Radios censales INDEC 2010 con dato de población para el Partido de Pergamino.

| | |
|---|---|
| Identificador | `demografia/radios_censales_indec_2010` |
| Geometría | polígonos |
| Fuente | [Radios censales indec 2010 en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/240), capa WFS `geonode:radios_censales_indec_2010` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> El dato sirve para comparar población en los distintos censos.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue obtenido desde el portal oficial del INDEC.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `clavera` | double |
| `radio-id` | double |
| `varon` | int64 |
| `mujer` | int64 |
| `hab_2010` | int64 |
| `radio_id` | int64 |
| `fuente` | string |
| `actualizacion` | int64 |
| `normalized_v` | double |
| `normalized_m` | double |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/radios_censales_indec_2010/radios_censales_indec_2010.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./radios_censales_indec_2010.pmtiles` (capa `radios_censales_indec_2010`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./radios_censales_indec_2010.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_radios_censales_indec_2010.parquet`.

## Procedencia

Productor: Instituto Nacional de Estadística y Censos (INDEC). Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/240).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, INDEC".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
