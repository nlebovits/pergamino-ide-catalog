# Cuencas hídricas del Norte de la Provincia de Buenos Aires

Cuencas hídricas del norte de la Provincia de Buenos Aires que solapan al Partido de Pergamino.

| | |
|---|---|
| Identificador | `ambiente-y-agro/cuencas_hidricas_norte_ba` |
| Geometría | polígonos |
| Fuente | [Cuencas hídricas del Norte de la Provincia de Buenos Aires en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/125), capa WFS `geonode:cuencas_hidricas_norte_ba` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> Las cuencas hídricas son áreas de influencias para las llamadas de agua que conforman el sistema hídrico de mayor categoría.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue obtenido del portal GeoInfra, sus límites fueron adaptados mediante imágenes aéreas.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `fid` | int64 |
| `nombre` | string |
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
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cuencas_hidricas_norte_ba/cuencas_hidricas_norte_ba.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./cuencas_hidricas_norte_ba.pmtiles` (capa `cuencas_hidricas_norte_ba`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./cuencas_hidricas_norte_ba.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_cuencas_hidricas_norte_ba.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/125).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
