# Catastro medida lado de parcela

Medidas de los macizos (parcelas) del Partido de Pergamino.

| | |
|---|---|
| Identificador | `catastro/medida_lado` |
| Geometría | puntos |
| Fuente | [Catastro medida lado de parcela en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/91), capa WFS `geonode:catastro_medida_lado` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | cuando es necesario |

## Propósito

Según el registro de GeoNode:

> Las medidas visibles en esta capa de datos son referenciales.

## Calidad de los datos

Según el registro de GeoNode:

> Parcelas catastrales obtenidas de ARBA (carto ARBA), modificadas y alineadas por la DSIG mediante imágenes aéreas con un margen de error promedio de 5m.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `lzn` | double |
| `tdl` | string |
| `feo` | decimal128(38, 0) |
| `cca` | string |
| `sag` | string |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/medida_lado/medida_lado.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./medida_lado.pmtiles` (capa `medida_lado`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./medida_lado.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_catastro_medida_lado.parquet`.

## Procedencia

Productor: Agencia de Recaudación de la Provincia de Buenos Aires (ARBA). Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/91).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, CARTOARBA".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
