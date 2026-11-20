# Zonificacion

Capa de zonificación y uso del suelo para el Partido de Pergamino.

| | |
|---|---|
| Identificador | `catastro/zonificacion` |
| Geometría | polígonos |
| Fuente | [Zonificacion en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/269), capa WFS `geonode:zonificacion` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> La capa de zonificación se publica para la consulta de uso de suelo tanto para habilitaciones de comercios e industria como para la presentación de planos de construcción.

## Calidad de los datos

Según el registro de GeoNode:

> La capa de zonificación se adecúa al código de zonificación del Partido de Pergamino de acuerdo a la Secretaría de Desarrollo Urbano.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `descripcion` | string |
| `designacion` | string |
| `categoria` | int64 |
| `fos` | double |
| `fota` | double |
| `fotp` | double |
| `dena` | int64 |
| `denp` | int64 |
| `um2` | int64 |
| `ul` | int64 |
| `sm` | double |
| `lm` | double |
| `hmax` | string |
| `ud` | string |
| `uc` | string |
| `observaciones` | string |
| `distrito` | string |
| `fotp_prem` | double |
| `des_cat` | string |
| `actan` | string |
| `tipo_suelo` | string |
| `superficie_ha` | double |
| `zonas` | string |
| `u_c_r` | string |
| `ord_ma` | string |
| `dec_ma` | string |
| `ord_mod` | string |
| `dec_mod` | string |
| `fecha_ac` | string |
| `x` | int64 |
| `y` | int64 |
| `t_etiqueta` | int64 |
| `localidad` | string |
| `ord_observaciones` | string |
| `urbano` | string |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/zonificacion.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./zonificacion.pmtiles` (capa `zonificacion`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./zonificacion.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_zonificacion.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/269).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
