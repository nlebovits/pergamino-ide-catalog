# Salud

Establecimientos y cobertura sanitaria: centros de salud, CAPS, áreas programáticas, desfibriladores de acceso público y guardias.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Áreas programaticas de salud](./areas_programaticas_salud/) | polígonos | Áreas o zonas programáticas de la Secretaria de Salud para la Ciudad de Pergamino. |
| [Centros de Atención Primaria de Salud (CAPS)](./caps/) | puntos | Centros de Atención Primaria de Salud del Partido de Pergamino. |
| [Centros de salud](./centros_de_salud/) | puntos | Principales centros de salud del Partido de Pergamino. |
| [Desfibriladores](./desfibriladores/) | puntos | Desfibriladores portátiles gestionados por Defensa Civil para todo el Partido de Pergamino. |
| [Estaciones de salud](./estaciones_de_salud/) | puntos | Estaciones de salud del Partido de Pergamino donde se puede realizar gimnasia al aire libre. |
| [Guardias de servicios](./guardias_emergencias_servicios/) | puntos | Guardias de emergencias de servicios públicos y privados en la Ciudad de Pergamino |
| [Guardias médicas](./guardias_medicas/) | puntos | Guardias médicas de los principales centros de salud de Pergamino, públicos y privados. |

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/salud/areas_programaticas_salud/areas_programaticas_salud.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
