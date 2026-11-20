# Edificios en altura

Edificios de 3 o más pisos en el Partido de Pergamino.

| | |
|---|---|
| Identificador | `catastro/edificios_en_altura` |
| Geometría | puntos |
| Fuente | [Edificios en altura en GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/143), capa WFS `geonode:edificios_en_altura` |
| Licencia | [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Actualización declarada por la fuente | continua |

## Propósito

Según el registro de GeoNode:

> Se considera edificio en altura a cualquier edificación destinada a vivienda o comercio que posea más de planta baja y un piso superior.

## Calidad de los datos

Según el registro de GeoNode:

> El dato se relevó en parte con datos aportados por la Dirección de Obras Particulares y completados con imágenes aéreas.

## Esquema

| Columna | Tipo |
|---|---|
| `geometry` | binary |
| `id` | int64 |
| `tipo` | string |
| `pisos` | int64 |
| `cocheras` | string |
| `te` | string |
| `calle` | string |
| `numero` | int64 |
| `estado` | string |
| `nombre_edificio` | string |
| `codigo_nomenclatura` | string |
| `tipo_predominante` | string |
| `tipo_complementario` | string |
| `azotea` | string |
| `escalera_tipo` | string |
| `departamento_por_piso` | int64 |
| `accesibilidad` | string |
| `departamentos_pb` | int64 |
| `id_edificio_dc` | int64 |
| `ascensores` | int64 |
| `categoria` | string |
| `observaciones` | string |
| `altura_aproximada` | int64 |
| `ph` | string |
| `cantidad_viviendas` | int64 |
| `cantidad_pisos` | int64 |
| `cantidad_dormitorios` | string |
| `expediente_obra` | string |
| `final_obra` | string |
| `bbox` | struct<xmin: double, ymin: double, xmax: double, ymax: double> |

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Acceso

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/edificios_en_altura.parquet') LIMIT 10").show()
```

Hay más consultas, todas probadas, en [AGENTS.md](./AGENTS.md).

## Visualización

Las teselas vectoriales están en `./edificios_en_altura.pmtiles` (capa `edificios_en_altura`). El estilo por defecto, `styles/default.json`, deriva del estilo SLD que publica GeoNode para esta capa.

Leyenda tal como la publica la fuente:

![Leyenda](./legends/source.png)

## Versiones

Cada extracción que cambia los datos es una versión nueva. La versión actual está en `./edificios_en_altura.parquet`. Las anteriores son los activos `version-*` de `collection.json`, con el número de registros y la suma de verificación de cada una. Sus archivos no cambian.

La primera versión proviene del GeoServer anterior de la IDE Pergamino y sigue publicada en `./publico_edificios_en_altura.parquet`.

## Procedencia

Productor: Municipalidad de Pergamino. Publicado por la Dirección de Sistemas de Información Georreferenciada (DSIG) de la Municipalidad de Pergamino en [GeoNode](https://geonode.pergamino.gob.ar/catalogue/#/dataset/143).

Atribución declarada en GeoNode: "Municipalidad de Pergamino".

Este catálogo es un espejo. Para el dato autoritativo, consultar la IDE de Pergamino.

## Licencia

CC-BY-SA-4.0. Es la licencia que declara la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.
