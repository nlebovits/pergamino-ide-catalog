# Códigos de reparto de facturación

Dataset extraído del callejero con los códigos de reparto de facturación según la Secretaría de Hacienda.

| | |
|---|---|
| Identificador | `servicios-sanitarios/codigo_reparto_facturacion` |
| Geometría | líneas |
| Fuente | [Códigos de reparto de facturación en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/296), capa WFS `geonode:codigo_reparto_facturacion` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> El proósito de este dataset es poder visualizar a qué repartidor le pertenece cada domicilio postal.

## Calidad de los datos

Según el registro de GeoNode:

> Los datos fueron aportados por el área de Facturación de la Dirección de Hacienda, Secretaría de Hacienda.

## Restricciones de uso declaradas

Según el registro de GeoNode:

> Ninguno

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `nombre` | string |
| `nombre_alt` | string |
| `numero_reparto_facturacion` | int64 |
| `pre_tipo` | string |
| `pre_dir` | string |
| `impar_ini` | int64 |
| `par_fin` | int64 |
| `clase` | string |
| `sentido` | int64 |
| `barrio` | string |
| `localidad` | string |
| `long` | int64 |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/codigo_reparto_facturacion.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./codigo_reparto_facturacion.pmtiles` (capa `codigo_reparto_facturacion`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./codigo_reparto_facturacion.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_codigo_reparto_facturacion.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/296).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
