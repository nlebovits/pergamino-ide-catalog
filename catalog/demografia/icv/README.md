# Índice de Calidad de Vida (ICV)

Capa de datos que permite conocer el Índice de Calidad de Vida o ICV desde una perspectiva geográfica, elaborado por el CONICET. Mapa de cobertura sobre el Partido de Pergamino

| | |
|---|---|
| Identificador | `demografia/icv` |
| Geometría | polígonos |
| Fuente | [Índice de Calidad de Vida (ICV) en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/179), capa WFS `geonode:icv` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | desconocida |

## Propósito

Según el registro de GeoNode:

> El índice de calidad de vida resume el dato, por radio censal, que es producto de distintas variables socioeconómicas censadas en 2010 por el INDEC, y suma nuevas variables estudiadas por el CONICET.

## Calidad de los datos

Según el registro de GeoNode:

> El dato fue obtenido a partir de la publicación propia del sitio del CONICET: https://www.conicet.gov.ar/dime-donde-resides-y-te-dire-cuan-bien-o-mal-vives

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `clavera` | double |
| `radio_id` | double |
| `varon` | int64 |
| `mujer` | int64 |
| `habitantes_al_2010` | int64 |
| `indice_calidad_vida_2010` | double |
| `fuente` | string |
| `actualizacion` | string |
| `observaciones` | string |
| `normalized_hab_2010` | int64 |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/icv/icv.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./icv.pmtiles` (capa `icv`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./icv.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_icv.parquet`.

## Procedencia

Productor: Consejo Nacional de Investigaciones Científicas y Técnicas (CONICET). Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/179).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, CONICET".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
