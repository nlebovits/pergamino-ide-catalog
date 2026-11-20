# Comercio y cultura

Actividad comercial, gastronomía y hospedaje, cultura, deporte y entretenimiento, medios de comunicación, entidades profesionales y sindicales, parques industriales y puntos de interés.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Agencias de viaje](./agencias_de_viaje/) | puntos | Agencias de viaje y turismo del Partido de Pergamino. |
| [Asociaciones sindicales](./asociaciones_sindicales/) | puntos | Sedes de gremios o asociaciones sindicales presentes en Pergamino. |
| [Colegios profesionales](./colegios_de_profesionales/) | puntos | Colegios de profesionales en el Partido de Pergamino. |
| [Clubes deportivos](./deportivo/) | puntos | Datos y ubicación de clubes y gimnasios del Partido de Pergamino. |
| [Entretenimiento](./entretenimiento/) | puntos | Capa de locales de entretenimiento como teatros, cines, etc., del Partido de Pergamino. |
| [Estaciones de servicio](./estaciones_servicio/) | puntos | Capa de estaciones de servicio del Partido de Pergamino. |
| [Extraccion de dinero](./extraccion_dinero/) | puntos | Puntos de extracción de dinero en efectivo. |
| [Oferta gastronómica](./gastronomia/) | puntos | Oferta gastronómica del Partido de Pergamino. |
| [Gomerias](./gomerias/) | puntos | Gomerías y tiendas de venta de neumáticos en Pergamino. |
| [Hoteles y hospedajes](./hospedajes/) | puntos | Hoteles y hospedajes del Partido de Pergamino. |
| [Lugares de interés (Overture Maps)](./lugares_overture/) | vectores externos | Lugares de interés (comercios, servicios, instituciones) de Overture Maps dentro del partido de Pergamino, referenciados sin copiar los d... |
| [Medios de comunicacion](./medios_de_comunicacion/) | puntos | Medios gráficos y audiovisuales del Partido de Pergamino. |
| [Museos y espacios culturales](./museos_y_espacios_culturales/) | puntos | Museos y espacios culturales del Partido de Pergamino. |
| [Oferentes de espacios culturales](./oferentes_espacios_culturales/) | puntos | Oferentes de espacios culturales públicos y privados en la Ciudad de Pergamino. |
| [Parques industriales y anexos](./parques_industriales_y_anexos/) | polígonos | Parques Industriales y Anexos del Partido de Pergamino. |
| [Paseos comerciales](./paseos_comerciales/) | líneas | Paseos comerciales primarios, secundarios y terciarios de Pergamino. |
| [Puntos de interes cultural](./puntos_de_interes/) | puntos | Puntos de interés (POI) cultural del Partido de Pergamino. |
| [Puntos de venta SIMPLE](./puntos_venta_simple/) | puntos | Capa de puntos de venta y recarga de créditos para el sistema Simple de Estacionamiento Medido para la Ciudad de Pergamino. |

## Datos de otros catálogos

Estas colecciones no vienen de GeoNode. Describen la parte de un conjunto de datos publicado en otro catálogo que cae dentro del partido, sin copiar sus bytes: el recurso `data` apunta al archivo original y un recurso `recorte` lo recorta al leer. Cada una conserva la licencia de su productor; ver su README.

- **Overture Maps Foundation**: `lugares_overture`

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/agencias_de_viaje/agencias_de_viaje.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.

Las colecciones de *Datos de otros catálogos* no vienen de GeoNode ni llevan la licencia del municipio: cada una declara la de su productor.
