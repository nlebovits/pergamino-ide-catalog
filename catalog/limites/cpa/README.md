# Códigos Postales Argentinos (CPA)

Código Postal Argentino tomado de la página Oficial del Correo Argentino para la Ciudad de Pergamino.

| | |
|---|---|
| Identificador | `limites/cpa` |
| Geometría | puntos |
| Fuente | [Códigos Postales Argentinos (CPA) en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/122), capa WFS `geonode:cpa` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> Los códigos postales se utilizan para codificar los lados de una manzana o macizo, de forma que sean únicos en todo el país.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue puntualmente obtenido a partir de datos libres disponibles en internet.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `fid` | int64 |
| `nombre` | string |
| `nombre_alt` | string |
| `pre_tipo` | string |
| `pre_dir` | string |
| `impar_ini` | int64 |
| `impar_fin` | int64 |
| `par_ini` | int64 |
| `par_fin` | int64 |
| `clase` | string |
| `barrio` | string |
| `localidad` | string |
| `cpa` | string |
| `fuente` | string |
| `actualizacion` | int64 |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/cpa/cpa.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./cpa.pmtiles` (capa `cpa`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./cpa.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_cpa.parquet`.

## Procedencia

Productor: Correo Oficial de la República Argentina. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/122).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, Correo Argentino".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
