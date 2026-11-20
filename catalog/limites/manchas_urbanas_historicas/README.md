# Manchas urbanas historicas

Manchas urbanas históricas de la Ciudad de Pergamino, desde 1773 a 2025, tomadas del Plan Estratégico Pergamino (PEP).

| | |
|---|---|
| Identificador | `limites/manchas_urbanas_historicas` |
| Geometría | polígonos |
| Fuente | [Manchas urbanas historicas en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/203), capa WFS `geonode:manchas_urbanas_historicas` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> El proósito de este dataset es brindar un aproximado de los contornos de crecimiento de la mancha urbana de la ciudad de Pergamino. Los límites son referenciales.

## Calidad de los datos

Según el registro de GeoNode:

> El dato ha sido digitalizado a partir del Plan Estratégico Pergamino, coordinado oportunamente por la Secretaría de Obras Públicas entre los años 2009 y 2012. Los datos de población fueron estimados por tasa de crecimiento a partir de los censos oficiales. La delimitación de contornos es aproximada y responde a descripciones textuales históricas de cómo fue creciendo la Ciudad a lo largo de los años.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `fuente` | string |
| `denominacion` | string |
| `poblacion` | int64 |
| `superficia_ha` | int64 |
| `observaciones` | string |
| `periodo` | int64 |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/manchas_urbanas_historicas.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./manchas_urbanas_historicas.pmtiles` (capa `manchas_urbanas_historicas`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./manchas_urbanas_historicas.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_manchas_urbanas_historicas.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/203).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
