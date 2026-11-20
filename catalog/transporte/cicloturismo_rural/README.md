# Cicloturismo rural

Capa de recorridos turísticos para recorrer en bicicleta las distintas zonas rurales y Pueblos del Partido de Pergamino.

| | |
|---|---|
| Identificador | `transporte/cicloturismo_rural` |
| Geometría | líneas |
| Fuente | [Cicloturismo rural en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/102), capa WFS `geonode:cicloturismo` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | no planificada |

## Propósito

Según el registro de GeoNode:

> Los recorridos rurales de cicloturismo pretenden ser guias para aquellos ciclistas que deseen realizar este deporte por caminos de tierra, visitando pueblos y parajes del Partido con fines turísticos.

## Calidad de los datos

Según el registro de GeoNode:

> Elaborado sobre la base de los caminos habituales que recorren las distintas asociaciones de cicloturismo del Partido en conjunto con la Dirección de Turismo Municipal.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `circuito` | string |
| `tramo` | string |
| `dificultad` | string |
| `longitud` | int64 |
| `duracion_tramo` | int64 |
| `observaciones` | string |
| `color` | string |
| `tipo_linea` | string |
| `atlas` | int64 |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/cicloturismo_rural.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./cicloturismo_rural.pmtiles` (capa `cicloturismo_rural`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./cicloturismo_rural.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_cicloturismo_rural.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/102).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
