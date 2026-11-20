# Cobertura de gas natural

Cobertura de gas natural en el territorio de la Ciudad de Pergamino, provista por Litoral Gas S.A.

| | |
|---|---|
| Identificador | `energia-y-conectividad/cobertura_gas_natural` |
| Geometría | polígonos |
| Fuente | [Cobertura de gas natural en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/111), capa WFS `geonode:cobertura_gas_natural` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | desconocida |

## Propósito

Según el registro de GeoNode:

> El dato es referencial.

## Calidad de los datos

Según el registro de GeoNode:

> Los datos fueron aportados por la Empresa Litoral Gas, que a su vez indica expresamente que los mismos son orientativos y deben ser utilizados bajo responsabilidad propia. Toda consulta técnica deberá realizarse en las oficinas de dicha empresa.

## Esquema

| Columna | Tipo |
|---|---|
| `id` | int64 |
| `numero_plano` | string |
| `actualizacion` | string |
| `fuente` | string |
| `localidad` | string |
| `observaciones` | string |
| `descargo_responsabilidad` | string |
| `geometry` | binary |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/cobertura_gas_natural/cobertura_gas_natural.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./cobertura_gas_natural.pmtiles` (capa `cobertura_gas_natural`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./cobertura_gas_natural.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_cobertura_gas_natural.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/111).

Atribución declarada en GeoNode: "Municipalidad de Pergamino, Litoral Gas".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
