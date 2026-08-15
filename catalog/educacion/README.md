# Educación

Establecimientos educativos por nivel y tipo de gestión, predios educativos y bibliotecas del Partido de Pergamino.

4 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Bibliotecas](./bibliotecas/) | 11 | Point | Bibliotecas del Partido de Pergamino. |
| [Educacion por gestion](./gestion/) | 200 | Multi Point | Capa de establecimientos educativos del Partido de Pergamino organizados por gestión como jardines, escuelas, colegio... |
| [Educacion por nivel](./nivel/) | 200 | Multi Point | Capa de establecimientos educativos del Partido de Pergamino organizados por nivel como jardines, escuelas, colegios,... |
| [Predios educativos](./predios_educativos/) | 133 | Multi Polygon | Predios educativos del Partido de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **Mapa Escolar** — Educacion por nivel
- **Prov. Buenos Aires** — Predios educativos

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/educacion/bibliotecas/publico_bibliotecas.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
