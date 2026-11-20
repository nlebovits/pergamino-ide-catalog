# Centros de Atención Primaria de Salud (CAPS)

Centros de Atención Primaria de Salud del Partido de Pergamino.

| | |
|---|---|
| Identificador | `salud/caps` |
| Geometría | puntos |
| Fuente | [Centros de Atención Primaria de Salud (CAPS) en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/82), capa WFS `geonode:caps` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> El propósito de esta capa es publicar los datos básicos de cada CAPS, entre los que se encuentran los distintos tipos de atención médica que brindan.

## Calidad de los datos

Según el registro de GeoNode:

> La capa se obtuvo a partir de datos aportados por la Secretaría de Salud de la Municipalidad de Pergamino.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `nombre` | string |
| `direccion` | string |
| `telefono` | string |
| `horario` | string |
| `barrio` | string |
| `clinmedica` | string |
| `pediatria` | string |
| `tocogineco` | string |
| `obstetrici` | string |
| `odontologi` | string |
| `trabsocial` | string |
| `nutricion` | string |
| `psicologia` | string |
| `fonoaudio` | string |
| `ecografia` | string |
| `oftalmolog` | string |
| `kinesiolog` | string |
| `cardioinfa` | string |
| `enfermeria` | string |
| `vacunas_calendario` | string |
| `actualizacion` | int64 |
| `tipo` | string |
| `localidad` | string |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/salud/caps/caps.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./caps.pmtiles` (capa `caps`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./caps.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_caps.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/82).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
