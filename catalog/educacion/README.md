# Educación

Establecimientos educativos, por nivel y por tipo de gestión, predios educativos y bibliotecas del Partido de Pergamino.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Bibliotecas](./bibliotecas/) | puntos | Bibliotecas del Partido de Pergamino. |
| [Educacion](./educacion/) | puntos | Capa de establecimientos educativos del Partido de Pergamino organizados por nivel y gestión como jardines, escuelas, colegios, instituto... |
| [Educacion por gestion](./gestion/) | puntos | Capa de establecimientos educativos del Partido de Pergamino organizados por gestión como jardines, escuelas, colegios, institutos, profe... |
| [Educacion por nivel](./nivel/) | puntos | Capa de establecimientos educativos del Partido de Pergamino organizados por nivel como jardines, escuelas, colegios, institutos, profeso... |
| [Predios educativos](./predios_educativos/) | polígonos | Predios educativos del Partido de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **Provincia de Buenos Aires**: Predios educativos

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/bibliotecas/bibliotecas.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
