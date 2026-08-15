# Transporte

Transporte público y movilidad: colectivos urbanos e interurbanos y sus líneas, paradas, ferrocarriles, ciclovías, remises y taxis, aeropuertos y estacionamiento.

19 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Aeropuertos y aeródromos](./aeropuertos/) | 40 | Point | Capa de aeropuertos y aeropistas declaradas en Pergamino y alrededores. |
| [Cicloturismo rural](./cicloturismo_rural/) | 10 | LineString | Capa de recorridos cicloturísticos para la zona rural del Partido de Pergamino. Elaborado sobre la base de los camino... |
| [Ciclovias](./ciclovias/) | 11.703 | Multi LineString | Ciclovías o bicisendas de la Ciudad de Pergamino. |
| [Colectivos interurbanos](./colectivos_interurbanos/) | 57 | Multi LineString | Lineas de colectivos interurbanos que conectan el Partido de Pergamino con Partidos aledaños. |
| [Colectivos urbanos](./colectivos_urbanos/) | 16 | LineString | Líneas de colectivos urbanos de la Ciudad de Pergamino. |
| [Estacionamiento medido](./estacionamiento_medido/) | 380 | Multi LineString | Capa de calles afectadas por el sistema de estacionamiento medido SIMPLE de la Ciudad de Pergamino. |
| [Estacionamiento de motos y bicicletas](./estacionamiento_motos_bicicletas/) | 69 | Point | Capa de estacionamiento de motos y bicicletas en la vía pública para el Partido de Pergamino. |
| [Estacionamiento lado izquierdo](./estacionamiento_nocturno/) | 47 | Multi LineString | Calles en las cuales se permite el estacionamiento del lado izquierdo en la Ciudad de Pergamino. |
| [Estacionamiento privado](./estacionamiento_privado/) | 30 | Point | Capa de playas de estacionamiento privadas para la Ciudad de Pergamino. |
| [Ferrocarriles](./ferrocarriles/) | 109 | LineString | Redes ferroviarias en el Partido de Pergamino. |
| [Linea a](./linea_a/) | 3 | LineString | Linea A de colectivos urbanos |
| [Linea b](./linea_b/) | 2 | LineString | Linea B de colectivos urbanos |
| [Linea c](./linea_c/) | 3 | LineString | Linea C de colectivos urbanos |
| [Linea d](./linea_d/) | 4 | LineString | Linea D de colectivos urbanos |
| [Linea e](./linea_e/) | 2 | LineString | Linea E de colectivos urbanos |
| [Linea parque industrial](./linea_parque_industrial/) | 2 | LineString | Linea especial Parque Industrial de colectivos urbanos |
| [Paradas de colectivo](./paradas_de_colectivo/) | 394 | Point | Paradas de colectivos/bus urbanos e interurbanos en el Partido de Pergamino. |
| [Paradas de remis y taxis](./remis_taxi/) | 24 | Point | Capa de locales de remises y paradas de taxis en la Ciudad de Pergamino. |
| [Puntos de recarga SUBE](./sube/) | 97 | Point | Puntos de recarga de tarjetas SUBE en el Partido de Pergamino. |

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/publico_aeropuertos.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
