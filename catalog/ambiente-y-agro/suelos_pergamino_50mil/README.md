# Carta de suelos Pergamino 1:50.000

Recorte de Cartas de Suelos República Argentina (INTA) para el Partido de Pergamino. El Plan Mapa de Suelos de la Región Pampeana en el año 1964 marca la etapa de mayor trascendencia del inventario de los suelos de nuestro país a escala de semidetalle y de reconocimiento (1:50.000 - 1:100.000). Las Cartas de Suelos de la Provincia de Buenos Aires son el resultado de este plan y la continuación de las tareas de relevamiento y cartografía de suelos hasta la actualidad.

| | |
|---|---|
| Identificador | `ambiente-y-agro/suelos_pergamino_50mil` |
| Geometría | polígonos |
| Fuente | [Carta de suelos Pergamino 1:50.000 en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/259), capa WFS `geonode:suelos_pergamino_50mil` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> El proposito de publicar esta capa es poner a disposición de profesionales de distintas áreas el dato de composición del suelo, dado que el portal GeoINTA (fuente del dato original) no está dispoible por el momento.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue obtenido desde un repositorio externo al portal INTA (https://zenodo.org/record/7837681)

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `objectid_1` | int64 |
| `objectid` | int64 |
| `simbc` | string |
| `nombre_uc` | string |
| `tipo` | string |
| `serie1` | string |
| `porc1` | int64 |
| `serie2` | string |
| `porc2` | int64 |
| `serie3` | string |
| `porc3` | int64 |
| `serie4` | string |
| `porc4` | int64 |
| `serie5` | string |
| `porc5` | int64 |
| `serie6` | string |
| `porc6` | int64 |
| `fase1` | string |
| `fase2` | string |
| `fase3` | string |
| `fase4` | string |
| `fase5` | string |
| `fase6` | string |
| `paisaje` | string |
| `posic1` | string |
| `posic2` | string |
| `posic3` | string |
| `posic4` | string |
| `posic5` | string |
| `posic6` | int64 |
| `cap_uso` | string |
| `taxo_ppal` | string |
| `taxo_2rio` | string |
| `taxo_3rio` | string |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/suelos_pergamino_50mil.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./suelos_pergamino_50mil.pmtiles` (capa `suelos_pergamino_50mil`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./suelos_pergamino_50mil.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_suelos_pergamino_50mil.parquet`.

## Procedencia

Productor: Instituto Nacional de Tecnología Agropecuaria (INTA). Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/259).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, INTA".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
