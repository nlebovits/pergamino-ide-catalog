# Recoleccion de residuos domiciliarios

Rutas de recolección de residuos domiciliarios desde 2025, empresa ENTRE para todo el Partido de Pergamino.

| | |
|---|---|
| Identificador | `servicios-municipales/recoleccion_residuos_domiciliarios` |
| Geometría | polígonos |
| Fuente | [Recoleccion de residuos domiciliarios en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/243), capa WFS `geonode:recoleccion_residuos_domiciliarios` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> La capa muestra las zonas o rutas de recolección de residuos domiciliarios para todo Pergamino.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue digitalizado con la colaboración de la empresa ENTRE.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `nombre` | string |
| `turno` | string |
| `lunes` | string |
| `martes` | string |
| `miercoles` | string |
| `jueves` | string |
| `viernes` | string |
| `sabado` | string |
| `domingo` | int64 |
| `observacion` | string |
| `horario` | string |
| `numero_ruta` | int64 |
| `etiqueta` | string |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/recoleccion_residuos_domiciliarios.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./recoleccion_residuos_domiciliarios.pmtiles` (capa `recoleccion_residuos_domiciliarios`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./recoleccion_residuos_domiciliarios.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_recoleccion_residuos_domiciliarios.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/243).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
