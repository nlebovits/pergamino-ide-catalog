# Pobreza cronica (2010)

La capa contiene índices que permiten visualizar, por radio censal, la pobreza crónica para el Partido de Pergamino según Censo INDEC 2010.

| | |
|---|---|
| Identificador | `demografia/pobreza_cronica` |
| Geometría | polígonos |
| Fuente | [Pobreza cronica (2010) en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/227), capa WFS `geonode:pobreza_cronica` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> Dentro de la población argentina, hay un grupo de personas que tiene la menor probabilidad de salir de la pobreza. Esto es lo que se denomina “pobreza crónica”. CIPPEC, PNUD y CEDLAS caracterizan a quienes viven en situación de pobreza crónica como el 10% de la población con menor probabilidad de salir de la pobreza, aun en períodos de crecimiento económico.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue obtenido a partir de datos proporcionados por el INDEC.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `radio_id` | double |
| `varon` | int64 |
| `mujer` | int64 |
| `habitantes_al_2010` | int64 |
| `porcentaje_hogares_hacinamiento_critico` | string |
| `porcentaje_hogares_jefe_primario_completo_o_menos` | string |
| `porcentaje_hogares_jefe_secundario_incompleto_o_menos` | string |
| `porcentaje_hogares_vivienda_deficitaria` | string |
| `porcentaje_hogares_sin_acceso_red_cloacal` | string |
| `porcentaje_población_situación_pobreza_crónica` | string |
| `porcentaje_de_población_urbana` | string |
| `observaciones` | string |
| `nivel_de_incidencia_de_pobreza_cronica` | string |
| `licencia` | string |
| `fuente` | string |
| `actualizacion` | string |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/pobreza_cronica/pobreza_cronica.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./pobreza_cronica.pmtiles` (capa `pobreza_cronica`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./pobreza_cronica.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_pobreza_cronica.parquet`.

## Procedencia

Productor: Instituto Nacional de Estadística y Censos (INDEC). Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/227).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, INDEC".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
