# Seguridad

Cuarteles de bomberos, cuadrículas y jurisdicciones policiales, cámaras de seguridad, dependencias, zonas de emergencia y riesgo, y centros de evacuados.

8 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Bomberos](./bomberos/) | 2 | Multi Point | Estaciones de bombero del Partido de Pergamino. |
| [Camaras seguridad](./camaras_seguridad/) | 523 | Multi Point | Cámaras de seguridad en la vía pública de la Ciudad de Pergamino. |
| [Centros de evacuados ante riesgo](./centros_evacuados/) | 5 | Point | Centros de evacuación ante casos de emergencia dentro del marco de la Gestión de Riesgo. |
| [Cuadriculas policiales](./cuadriculas_policiales/) | 14 | Polygon | Capa de 14 cuadrículas policiales comprendidas dentro de las 6 zonas de seguridad de la Ciudad de Pergamino |
| [Dependencias de seguridad y acceso a la justicia](./dependencias_seguridad/) | 52 | Multi Point | Dependencias y destacamentos policiales y judiciales como comisarías, puestos de vigilancia, juzgados, tribunales, de... |
| [Jurisdicciones policiales](./jurisdicciones_policiales/) | 3 | Polygon | Jurisdicciones de las tres comisarías existentes en la Ciudad, Cada jurisdicción contiene 2 zonas. |
| [Zonas de gestión ante emergencias y riesgos](./zonas_emergencias_y_riesgo/) | 9 | Polygon | Zonas de división de tareas en la Gestión de Emergencias y Riesgo para la Ciudad de Pergamino. |
| [Zonas de seguridad](./zonas_seguridad/) | 14 | Polygon | Zonas de seguridad de la Ciudad de Pergamino propuestas por la Secretaría de Seguridad. |

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/seguridad/bomberos/publico_bomberos.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
