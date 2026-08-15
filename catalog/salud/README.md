# Salud

Establecimientos y cobertura sanitaria: centros de salud, CAPS, áreas programáticas, desfibriladores de acceso público y guardias.

7 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Áreas programaticas de salud](./areas_programaticas_salud/) | 17 | Polygon | Áreas o zonas programáticas de la Secretaria de Salud para la Ciudad de Pergamino. |
| [Centros de Atención Primaria de Salud (CAPS)](./caps/) | 30 | Point | Centros de Atención Primaria de Salud del Partido de Pergamino. |
| [Centros de salud](./centros_de_salud/) | 23 | Multi Point | Principales centros de salud del Partido de Pergamino. |
| [Desfibriladores](./desfibriladores/) | 10 | Point | Desfibriladores portátiles gestionados por Defensa Civil para todo el Partido de Pergamino. |
| [Estaciones de salud](./estaciones_de_salud/) | 29 | Multi Point | Estaciones de salud del Partido de Pergamino donde se puede realizar gimnasia al aire libre. |
| [Guardias de servicios](./guardias_emergencias_servicios/) | 6 | Multi Point | Guardias de emergencias de servicios públicos y privados en la Ciudad de Pergamino |
| [Guardias médicas](./guardias_medicas/) | 5 | Multi Point | Guardias médicas de los principales centros de salud de Pergamino, públicos y privados. |

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/salud/areas_programaticas_salud/publico_areas_programaticas_salud.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
