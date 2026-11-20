# Arbolado (2013)

Capa de árboles en veredas censados en 2013 para el área urbana de la Ciudad de Pergamino. Se excluyen plazas y parques.

| | |
|---|---|
| Identificador | `ambiente-y-agro/arbolado` |
| Geometría | puntos |
| Fuente | [Arbolado (2013) en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/58), capa WFS `geonode:arbolado` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> El objeto de esta capa es publicar el arbolado como patrimonio vivo de la Ciudad. Sus datos pueden ser utilizados para realizar estadísticas y planeamiento urbano.

## Calidad de los datos

Según el registro de GeoNode:

> Los datos se obtuvieron a partir de un proyecto de Censo de arbolado público realizado en 2012/2013. Para la georreferenciación se utilizaron dispositivos GPS y planillas en formato papel. Algunas georreferenciaciones se corrigieron mediante imágenes aéreas.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `ele` | double |
| `time` | string |
| `name` | int64 |
| `modulo` | string |
| `id_gps` | int64 |
| `id_asociad` | int64 |
| `espacio` | string |
| `altura` | string |
| `estado_gen` | string |
| `observacio` | string |
| `planilla` | int64 |
| `altura_ini` | int64 |
| `altura_fin` | int64 |
| `lado` | string |
| `id_bbdd` | int64 |
| `obs_data` | string |
| `circunsf` | double |
| `diametro` | double |
| `vereda` | string |
| `numeracion_aproximada` | double |
| `especie_arbol` | string |
| `elementos_estranos` | string |
| `tipo_elementos_estranos` | string |
| `descripcion_elementos_estranos` | string |
| `clavel_del_aire` | string |
| `calle` | string |
| `ancho_vereda` | double |
| `dano_en_vereda` | string |
| `vereda_levantada` | string |
| `fuente` | string |
| `actualizacion` | string |
| `barrio` | string |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/arbolado.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./arbolado.pmtiles` (capa `arbolado`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./arbolado.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_arbolado.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/58).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
