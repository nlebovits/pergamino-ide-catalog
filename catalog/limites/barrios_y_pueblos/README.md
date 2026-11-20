# Barrios y pueblos

Barrios y pueblos del Partido de Pergamino con dato de cantidad de habitantes y hogares estimada al 2023.

| | |
|---|---|
| Identificador | `limites/barrios_y_pueblos` |
| Geometría | polígonos |
| Fuente | [Barrios y pueblos en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/68), capa WFS `geonode:barrios_y_pueblos` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> Los límites de los barrios de la Ciudad de Pergamino se utilizan para referenciar zonas del territorio.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue digitalizado a partir de la ordenanza 8850-18.

## Información complementaria

Según el registro de GeoNode:

> El dato de población y cantidad de hogares por barrio es una estimación (ISDD) basada en datos oficiales del INDEC y algoritmos de distribución basados en las edificaciones de open buildings (google). El algoritmo utilizado es el de distribución dasimétrica.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `nombre` | string |
| `tipo` | string |
| `area` | double |
| `ordenanza` | string |
| `delimitacion` | string |
| `distrito` | string |
| `color_id` | int64 |
| `localidad` | string |
| `manzanas` | int64 |
| `seccion` | string |
| `primera_letra` | string |
| `habitantes_2023_ISDD` | double |
| `hogares_2023_ISDD` | double |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./barrios_y_pueblos.pmtiles` (capa `barrios_y_pueblos`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./barrios_y_pueblos.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/68).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
