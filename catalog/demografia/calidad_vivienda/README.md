# Calidad de vivienda (INDEC 2010)

Índice de calidad de vivienda según Censo INDEC 2010 para todo el Partido de Pergamino.

| | |
|---|---|
| Identificador | `demografia/calidad_vivienda` |
| Geometría | polígonos |
| Fuente | [Calidad de vivienda (INDEC 2010) en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/76), capa WFS `geonode:calidad_vivienda` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> El índice de calidad de vivienda resume numéricamente distintas variables materiales y constructivas de las construcciones que ofician como viviendas.

## Calidad de los datos

Según el registro de GeoNode:

> Los datos fueron tomados del INDEC sobre la base del Censo 2010 y posteriores actualizaciones estadísticas, agregados por radio censal.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `habitantes_al_2010` | int64 |
| `1_satisfactorio` | int64 |
| `2_basico` | int64 |
| `3_insuficiente` | int64 |
| `total` | int64 |
| `indice_insuficiente` | double |
| `clavera` | int64 |
| `fuente` | string |
| `actualizacion` | int64 |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/calidad_vivienda/calidad_vivienda.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./calidad_vivienda.pmtiles` (capa `calidad_vivienda`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./calidad_vivienda.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_calidad_vivienda.parquet`.

## Procedencia

Productor: Instituto Nacional de Estadística y Censos (INDEC). Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/76).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, INDEC".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
