# Vialidad

Red vial del Partido de Pergamino: callejero, tipo de calzada y vereda, cordón cuneta, señalización, semáforos, alumbrado público y caminos rurales.

18 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Alcantarillas en rutas](./alcantarillas_vialidad/) | 74 | Point | Alcantarillas en rutas provinciales y nacionales para todo el Partido de Pergamino. |
| [Altura de calle](./altura_de_calle/) | 11.703 | Multi LineString | Altura (numeración) de calles del Partido de Pergamino. |
| [Callejero](./callejero/) | 11.703 | Multi LineString | No abstract provided |
| [Listado de calles](./callejero_listado/) | 1.098 | - | Nomenclador de calles del Partido de Pergamino: nombre de la calle, localidad e identificador interno. Es una tabla d... |
| [Cámaras y radares de tránsito](./camaras_y_radares/) | 20 | Point | Cámaras, radares y tótems para el control y multas por exceso de velocidad, violación de sendas peatonales y cruce de... |
| [Carteles viales](./carteles_viales/) | 3.002 | Point | Carteles y señales de tránsito en el Partido de Pergamino. |
| [Comisiones caminos rurales](./comisiones_caminos_rurales/) | 29 | Polygon | Comisiones de caminos rurales del Partido de Pergamino determinados para el cobro de tasa vial. |
| [Cordon cuneta](./cordon_cuneta/) | 11.703 | Multi LineString | Describe si la calle posee cordón cuneta ejecutado, tanto en ambas como en alguna de ellas: ambas, par, impar, ningun... |
| [Luminarias en vía pública](./luminarias/) | 25.152 | Multi Point | Luminarias en vía pública del Partido de Pergamino. Permite distinguir las zonas con luminaria LED y de sodio, así co... |
| [Material de calzada](./material_de_calzada/) | 11.703 | Multi LineString | Tipo de material mayoritario que posee la calle, adoquinado, asfalto, hormigón, escoriado, tierra y metálico. |
| [Progresivas y mojones de rutas](./progresivas_rutas/) | 340 | Point | Progresivas en mojones de rutas nacionales y provinciales localizadas en el Partido de Pergamino. |
| [Puntos fijos de nivelación IGN](./puntos_fijos/) | 76 | Point | Puntos fijos de nivelación del IGN para la Ciudad de Pergamino. |
| [Rampas de acceso a veredas](./rampas_acceso_veredas/) | 1.653 | Point | Rampas de acceso a veredas para personas con discapacidad motriz. |
| [Recambio led](./recambio_led/) | 25.152 | Multi Point | Capa de luminarias clasificadas por proyecto y ejecución de recambio LED. |
| [Reductores de velocidad](./reductores_de_velocidad/) | 217 | Multi Point | Reductores de velocidad y bumpers. |
| [Semaforos](./semaforos/) | 294 | Point | Capa de semáforos del Partido de Pergamino. |
| [Tipo de vereda](./tipo_de_vereda/) | 11.703 | Multi LineString | Tipo de vereda de acuerdo al Censo de Arbolado 2013 par ala Ciudad de Pergamino. |
| [Tranqueras Geolocalizadas](./tranqueras_rurales/) | 171 | Point | Tranqueras rurales del Partido de Pergamino pertenecientes al programa de la Secretaría de Seguridad |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **IGN** — Puntos fijos de nivelación IGN

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/publico_alcantarillas_vialidad.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
