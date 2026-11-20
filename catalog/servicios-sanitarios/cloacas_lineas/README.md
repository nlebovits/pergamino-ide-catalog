# Red cloacal - Líneas

Sistema de tuberías y conexiones de la red cloacal de la Ciudad de Pergamino.

| | |
|---|---|
| Identificador | `servicios-sanitarios/cloacas_lineas` |
| Geometría | líneas |
| Fuente | [Red cloacal - Líneas en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/106), capa WFS `geonode:cloacas_lineas` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> Gestión de obras y servicios sanitarios, planeamiento y determinación referencial de interferencias.

## Calidad de los datos

Según el registro de GeoNode:

> Dato aportado por la Dirección de Obras y Servicios Sanitarios de la Municipalidad de Pergamino.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `diametro` | int64 |
| `material` | string |
| `ubicacion` | string |
| `dist_lm` | double |
| `clase` | string |
| `ventila` | string |
| `intrados_i` | string |
| `intrados_f` | string |
| `longitud` | int64 |
| `pendiente` | string |
| `sistema` | string |
| `q_max` | string |
| `q_actual` | string |
| `conex_exis` | int64 |
| `conex_pend` | int64 |
| `condicion` | string |
| `antig` | string |
| `resp_obra` | string |
| `fecha_act` | date32[day] |
| `resp_act` | string |
| `obs` | string |
| `tapada_i` | double |
| `tapada_f` | double |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/cloacas_lineas.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./cloacas_lineas.pmtiles` (capa `cloacas_lineas`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./cloacas_lineas.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/106).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
