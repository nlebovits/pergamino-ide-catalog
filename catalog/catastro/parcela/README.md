# Catastro parcela

Capa de parcelas catastrales del Partido de Pergamino.

| | |
|---|---|
| Identificador | `catastro/parcela` |
| Geometría | polígonos |
| Fuente | [Catastro parcela en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/92), capa WFS `geonode:catastro_parcela` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | continua |

## Propósito

Según el registro de GeoNode:

> El propósito de esta capa es poder localizar los inmuebles en el territorio.

## Calidad de los datos

Según el registro de GeoNode:

> Parcelas catastrales obtenidas de ARBA (carto ARBA), modificadas y alineadas por la DSIG mediante imágenes aéreas con un margen de error promedio de 5m.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `nomencla` | string |
| `tpa` | string |
| `partida` | decimal128(38, 0) |
| `etiqueta` | string |
| `circunscripcion` | int64 |
| `seccion` | string |
| `chacra_numero` | int64 |
| `chacra_letra` | string |
| `quinta_numero` | int64 |
| `quinta_letra` | string |
| `fraccion_numero` | int64 |
| `fraccion_letra` | string |
| `manzana_numero` | int64 |
| `manzana_letra` | string |
| `parcela_numero` | int64 |
| `parcela_letra` | string |
| `tipo_objeto_siser` | int64 |
| `numero_objeto_siser` | decimal128(38, 0) |
| `subpar_uf` | int64 |
| `lon` | double |
| `lat` | double |
| `calle_frente` | string |
| `altura_frente` | string |
| `codigo_postal` | int64 |
| `barrio` | string |
| `localidad` | string |
| `fuente` | string |
| `actualizacion` | string |
| `zonificacion` | string |
| `pluscode` | string |
| `situacion_administrativa` | string |
| `matricula` | string |
| `factor_ocupacion_parcela` | int64 |
| `area_m2` | int64 |
| `area_ha` | double |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./parcela.pmtiles` (capa `parcela`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./parcela.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_catastro_parcela.parquet`.

## Procedencia

Productor: Agencia de Recaudación de la Provincia de Buenos Aires (ARBA). Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/92).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, CARTOARBA".

Es un dato de otro organismo, rehospedado por el municipio. La atribución corresponde al organismo de origen.

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
