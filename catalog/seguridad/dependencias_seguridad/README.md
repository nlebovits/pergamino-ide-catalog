# Dependencias de seguridad y acceso a la justicia

Dependencias y destacamentos policiales y judiciales como comisarías, puestos de vigilancia, juzgados, tribunales, defensorías, oficinas administrativas para todo el Partido de Pergamino, tanto de jurisdición provincial, nacional o municipal.

| | |
|---|---|
| Identificador | `seguridad/dependencias_seguridad` |
| Geometría | puntos |
| Fuente | [Dependencias de seguridad y acceso a la justicia en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/134), capa WFS `geonode:dependencias_seguridad` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> La capa concentra dependencias de acceso a la seguridad y justicia.

## Calidad de los datos

Según el registro de GeoNode:

> El dato se obtuvo de las Comisaría Departamental de Pergamino, registros de la Secretaría de Seguridad y datos públicos del Ministerio de Seguridad de PBA.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `direccion` | string |
| `telefono` | string |
| `localidad` | string |
| `actualizacion` | string |
| `fuente` | string |
| `nombre` | string |
| `etiqueta` | string |
| `ambito` | string |
| `clase` | string |
| `jurisdiccion` | string |
| `especialidad` | string |
| `detalle` | string |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/dependencias_seguridad.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./dependencias_seguridad.pmtiles` (capa `dependencias_seguridad`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./dependencias_seguridad.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_dependencias_seguridad.parquet`.

## Procedencia

Productor: Provincia de Buenos Aires. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/134).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, PBA".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
