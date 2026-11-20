# Curvas de nivel cuenca Arroyo Pergamino

Curvas de nivel elaboradas por IATASA-ABS para el proyecto de la Presa del Arroyo Pergamino, nivel de paso a 2.5m. El área de la cuenca excede los límites del Partido de Pergamino.

| | |
|---|---|
| Identificador | `ambiente-y-agro/curvas_nivel_cuenca` |
| Geometría | líneas |
| Fuente | [Curvas de nivel cuenca Arroyo Pergamino en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/128), capa WFS `geonode:curvas_nivel_cuenca` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> Las curvas de nivel sirven para entender el relieve del territorio.

## Calidad de los datos

Según el registro de GeoNode:

> El dato se obtuvo a partir de planos de archivos de la Municipalidad de Pergamino pertenecientes a un estudio realizado por IATASA-ABS.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `fuente` | string |
| `cotas` | double |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/curvas_nivel_cuenca/curvas_nivel_cuenca.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./curvas_nivel_cuenca.pmtiles` (capa `curvas_nivel_cuenca`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./curvas_nivel_cuenca.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_curvas_nivel_cuenca.parquet`.

## Procedencia

Productor: UTE IATASA - ABS S.A.. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/128).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, ABS-IATASA".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
