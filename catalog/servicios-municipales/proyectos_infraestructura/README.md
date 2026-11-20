# Proyectos de infraestructura vial

Proyectos de nfraestructura urbana sobre las vías de circulación: cordón cuneta y pavimentación para el Partido de Pergamino.

| | |
|---|---|
| Identificador | `servicios-municipales/proyectos_infraestructura` |
| Geometría | líneas |
| Fuente | [Proyectos de infraestructura vial en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/297), capa WFS `geonode:proyectos_infraestructura` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | continua |

## Propósito

Según el registro de GeoNode:

> Los datos que se muestran incluyen proyectos de futuras obras en las calles de la Ciudad y pueblos del Partido, condicionadas a factibilidad técnica.

## Calidad de los datos

Según el registro de GeoNode:

> La capa de datos es un subconjunto de datos espaciales del callejero, donde se resaltan los datos de proyectos de obras informados por la Dirección de Infraestructura Urbana.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `nombre` | string |
| `impar_ini` | int64 |
| `impar_fin` | int64 |
| `par_ini` | int64 |
| `par_fin` | int64 |
| `clase` | string |
| `barrio` | string |
| `etiqueta` | string |
| `localidad` | string |
| `longitud` | int64 |
| `ancho_real` | double |
| `ancho_calzada` | double |
| `material_calzada` | string |
| `cordon_cuneta` | string |
| `pav_etapa` | double |
| `cc_etapa` | double |
| `proyecto_infraestructura` | string |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/proyectos_infraestructura.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./proyectos_infraestructura.pmtiles` (capa `proyectos_infraestructura`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./proyectos_infraestructura.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_proyectos_infraestructura.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/297).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
