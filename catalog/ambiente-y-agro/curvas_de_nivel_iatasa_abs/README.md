# Curvas de nivel (IATASA-ABS)

Curvas de nivel elaboradas por IATASA-ABS para la Ciudad de Pergamino, año 2007.

| | |
|---|---|
| Identificador | `ambiente-y-agro/curvas_de_nivel_iatasa_abs` |
| Geometría | líneas |
| Fuente | [Curvas de nivel (IATASA-ABS) en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/127), capa WFS `geonode:curvas_de_nivel_iatasa_abs` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> Las curvas de nivel son lineas imaginarias que permiten entender los pendientes del terreno.

## Calidad de los datos

Según el registro de GeoNode:

> El dato se obtuvo a partir de los planos de relevamientos generados por IATASA-ABS para la Ciudad de Pergamino. El dato fue relevado entre 2005 y 2010.

## Esquema

| Columna | Tipo |
|---|---|
| `gid` | int64 |
| `cota` | double |
| `fuente` | string |
| `actualizacion` | string |
| `observaciones` | string |
| `grosor_marca` | double |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/curvas_de_nivel_iatasa_abs/curvas_de_nivel_iatasa_abs.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./curvas_de_nivel_iatasa_abs.pmtiles` (capa `curvas_de_nivel_iatasa_abs`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./curvas_de_nivel_iatasa_abs.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_curvas_de_nivel_iatasa_abs.parquet`.

## Procedencia

Productor: UTE IATASA - ABS S.A.. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/127).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, ABS-IATASA".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
