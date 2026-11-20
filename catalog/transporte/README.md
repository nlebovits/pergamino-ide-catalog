# Transporte

Transporte público y movilidad: colectivos urbanos e interurbanos, paradas, puntos de carga SUBE, ferrocarriles, circuitos de cicloturismo y la Vuelta al Partido, remises y taxis, aeropuertos y estacionamiento.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Aeropuertos y aeródromos](./aeropuertos/) | puntos | Capa de aeropuertos y aeropistas declaradas en Pergamino y alrededores. |
| [Cicloturismo rural](./cicloturismo_rural/) | líneas | Capa de recorridos turísticos para recorrer en bicicleta las distintas zonas rurales y Pueblos del Partido de Pergamino. |
| [Colectivos interurbanos](./colectivos_interurbanos/) | líneas | Lineas de colectivos interurbanos que conectan el Partido de Pergamino con Partidos aledaños. |
| [Colectivos urbanos](./colectivos_urbanos/) | líneas | Líneas de colectivos urbanos de la Ciudad de Pergamino. |
| [Estacionamiento de motos y bicicletas](./estacionamiento_motos_bicicletas/) | puntos | Capa de estacionamiento de motos y bicicletas en la vía pública para el Partido de Pergamino. |
| [Estacionamiento lado izquierdo](./estacionamiento_nocturno/) | líneas | Calles en las cuales se permite el estacionamiento del lado izquierdo en la Ciudad de Pergamino. |
| [Estacionamiento privado](./estacionamiento_privado/) | puntos | Capa de playas de estacionamiento privadas para la Ciudad de Pergamino. |
| [Ferrocarriles](./ferrocarriles/) | líneas | Redes ferroviarias en el Partido de Pergamino. |
| [Paradas de colectivo](./paradas_de_colectivo/) | puntos | Paradas de colectivos/bus urbanos e interurbanos en el Partido de Pergamino. |
| [Paradas de remis y taxis](./remis_taxi/) | puntos | Capa de locales de remises y paradas de taxis en la Ciudad de Pergamino. |
| [Puntos de recarga SUBE](./sube/) | puntos | Puntos de recarga de tarjetas SUBE en el Partido de Pergamino. |
| [Vuelta al Partido](./vuelta_partido/) | líneas | Trazas kml de ciclismo rural para 120km y 240km en el Partido de Pergamino. |

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/aeropuertos.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
