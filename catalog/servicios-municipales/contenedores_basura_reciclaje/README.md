# Contenedores de basura y reciclaje

Contenedores y campanas del programa Actuá en Verde para todo el Partido de Pergamino, actualmente bajo la gestión de la empresa ENTRE.

| | |
|---|---|
| Identificador | `servicios-municipales/contenedores_basura_reciclaje` |
| Geometría | puntos |
| Fuente | [Contenedores de basura y reciclaje en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/121), capa WFS `geonode:contenedores_basura_reciclaje` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> El dataset muestra las campanas y contenedores de basura disponibles en la Ciudad y Pueblos del Partido de Pergamino

## Calidad de los datos

Según el registro de GeoNode:

> Los datos originales fueron relevados por la Dirección de Higiene Urbana, Servicios Públicos. Actualmente el servicio lo brinda la empresa ENTRE.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `fid` | int64 |
| `tipo` | string |
| `descripcion` | string |
| `color` | string |
| `programa` | string |
| `actualizacion` | int64 |
| `barrio` | string |
| `fuente` | string |
| `observaciones` | string |
| `localidad` | string |
| `latitud` | double |
| `longitud` | double |
| `codigo_barrio` | int64 |
| `numero_contenedor` | int64 |
| `codigo_contenedor` | string |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/contenedores_basura_reciclaje/contenedores_basura_reciclaje.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./contenedores_basura_reciclaje.pmtiles` (capa `contenedores_basura_reciclaje`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./contenedores_basura_reciclaje.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_contenedores_basura_reciclaje.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/121).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, ENTRE".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
