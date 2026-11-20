# Seguridad

Cuarteles de bomberos, dependencias de seguridad, zonas de seguridad, zonas de emergencia y riesgo, y centros de evacuados.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Bomberos](./bomberos/) | puntos | Estaciones de bombero del Partido de Pergamino. |
| [Centros de evacuados ante riesgo](./centros_evacuados/) | puntos | Centros de evacuación ante casos de emergencia dentro del marco de la Gestión de Riesgo. |
| [Dependencias de seguridad y acceso a la justicia](./dependencias_seguridad/) | puntos | Dependencias y destacamentos policiales y judiciales como comisarías, puestos de vigilancia, juzgados, tribunales, defensorías, oficinas... |
| [Zonas de gestión ante emergencias y riesgos](./zonas_emergencias_y_riesgo/) | polígonos | Zonas de división de tareas en la Gestión de Emergencias y Riesgo para la Ciudad de Pergamino. |
| [Zonas de seguridad](./zonas_seguridad/) | polígonos | Zonas de seguridad de la Ciudad de Pergamino propuestas por la Secretaría de Seguridad. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **Provincia de Buenos Aires**: Dependencias de seguridad y acceso a la justicia

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/bomberos/bomberos.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
