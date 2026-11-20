# Partido de Pergamino

Límites del Partido de Pergamino según el Catastro Municipal.

| | |
|---|---|
| Identificador | `limites/partido_pergamino` |
| Geometría | polígonos |
| Fuente | [Partido de Pergamino en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/223), capa WFS `geonode:partido_pergamino` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> Los límites del Partido permiten establecer demarcaciones precisas respecto a las jurisdicciones.

## Calidad de los datos

Según el registro de GeoNode:

> Los límites del partido se tomaron inicialmente del catastro municipal, y posteriormente fueron modificados mediante imágenes aéreas y planos de mensura.

## Esquema

| Columna | Tipo |
|---|---|
| `gid` | int64 |
| `departa` | string |
| `cabecer` | string |
| `provincia` | string |
| `cod_depto` | double |
| `poblacion` | string |
| `gentilicio` | string |
| `pref_tel` | double |
| `patrona` | string |
| `coordenada` | string |
| `web` | string |
| `area_ha` | int64 |
| `area_km2` | int64 |
| `lon_centroide` | double |
| `lat_centroide` | double |
| `perimetro_m` | int64 |
| `perimetro_km` | int64 |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/partido_pergamino/partido_pergamino.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./partido_pergamino.pmtiles` (capa `partido_pergamino`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./partido_pergamino.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_partido_pergamino.parquet`.

## Procedencia

Productor: Agencia de Recaudación de la Provincia de Buenos Aires (ARBA). Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/223).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, CARTOARBA".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
