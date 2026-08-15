# Comercio y cultura

Actividad comercial, gastronomía y hospedaje, cultura, deporte y entretenimiento, medios de comunicación, entidades profesionales y sindicales, parques industriales y puntos de interés.

18 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Agencias de viaje](./agencias_de_viaje/) | 15 | Point | Agencias de viaje y turismo del Partido de Pergamino. |
| [Asociaciones sindicales](./asociaciones_sindicales/) | 29 | Point | Sedes de gremios o asociaciones sindicales presentes en Pergamino. |
| [Beata crescencia perez](./beata_crescencia_perez/) | 3 | Point | Capa dedicada a la Beata Crescencia Pérez |
| [Colegios profesionales](./colegios_de_profesionales/) | 19 | Multi Point | Colegios de profesionales en el Partido de Pergamino. |
| [Clubes deportivos](./deportivo/) | 108 | Multi Point | Datos y ubicación de clubes y gimnasios del Partido de Pergamino. |
| [Entretenimiento](./entretenimiento/) | 14 | Point | Capa de locales de entretenimiento como teatros, cines, etc., del Partido de Pergamino. |
| [Estaciones de servicio](./estaciones_servicio/) | 19 | Point | Capa de estaciones de servicio del Partido de Pergamino. |
| [Extraccion de dinero](./extraccion_dinero/) | 24 | Point | Puntos de extracción de dinero en efectivo. |
| [Oferta gastronómica](./gastronomia/) | 159 | Point | Oferta gastronómica del Partido de Pergamino. |
| [Gomerias](./gomerias/) | 25 | Point | Gomerías y tiendas de venta de neumáticos en Pergamino. |
| [Hoteles y hospedajes](./hospedajes/) | 26 | Point | Hoteles y hospedajes del Partido de Pergamino. |
| [Medios de comunicacion](./medios_de_comunicacion/) | 36 | Point | Medios gráficos y audiovisuales del Partido de Pergamino. |
| [Museos y espacios culturales](./museos_y_espacios_culturales/) | 14 | Point | Museos y espacios culturales del Partido de Pergamino. |
| [Oferentes de espacios culturales](./oferentes_espacios_culturales/) | 20 | Multi Point | Oferentes de espacios culturales públicos y privados en la Ciudad de Pergamino. |
| [Parques industriales y anexos](./parques_industriales_y_anexos/) | 5 | Polygon | Parques Industriales y Anexos del Partido de Pergamino. |
| [Paseos comerciales](./paseos_comerciales/) | 20 | Multi LineString | Paseos comerciales primarios, secundarios y terciarios de Pergamino. |
| [Puntos de interes cultural](./puntos_de_interes/) | 31 | Point | Puntos de interés (POI) cultural del Partido de Pergamino. |
| [Puntos de venta SIMPLE](./puntos_venta_simple/) | 21 | Point | Capa de puntos de venta y recarga de créditos para el sistema Simple de Estacionamiento Medido para la Ciudad de Perg... |

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/agencias_de_viaje/publico_agencias_de_viaje.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
