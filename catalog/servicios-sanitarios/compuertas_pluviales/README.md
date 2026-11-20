# Compuertas antirretorno en desagües pluviales

Ubicación de las compuertas antiretorno de desagües pluviales sobre el Arroyo Pergamino, en el área urbana y periurbana de la Ciudad.

| | |
|---|---|
| Identificador | `servicios-sanitarios/compuertas_pluviales` |
| Geometría | puntos |
| Fuente | [Compuertas antirretorno en desagües pluviales en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/355), capa WFS `geonode:compuertas_pluviales` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> El dato sirve como base para relevamientos de estado y funcionamiento de los componentes del sistema pluvial de la Ciudad de Pergamino.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue obtenido a partir de información aportada por DC.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `fid` | int64 |
| `codigo` | string |
| `ubicacion` | string |
| `estado` | string |
| `observaciones` | string |
| `forma` | string |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/compuertas_pluviales/compuertas_pluviales.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./compuertas_pluviales.pmtiles` (capa `compuertas_pluviales`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./compuertas_pluviales.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/355).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
