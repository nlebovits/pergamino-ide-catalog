# Energía y conectividad

Cobertura de gas natural, circuitos energéticos, red de fibra óptica municipal y federal, y puntos de acceso wifi en espacios verdes.

6 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Circuitos energéticos (TEAM-UNNOBA)](./circuitos_energeticos/) | 19 | Point | Circuitos energéticos identificados por el equipo de investigación TEAM UNNOBA para todo el Partido de Pergamino. |
| [Cobertura de gas natural](./cobertura_gas_natural/) | 17 | Polygon | Cobertura de gas natural en el territorio de la Ciudad de Pergamino, provista por Litoral Gas S.A. |
| [Red de fibra óptica municipal](./fibra_optica/) | 16 | Multi LineString | Tramos de la red de fibra óptica del Municipio de Pergamino. Cada tramo registra su nombre, longitud en metros, categ... |
| [Nodos de la Red Federal de Fibra Óptica](./red_federal_fibra_optica_nodos/) | 50 | Point | Capa de nodos de la Red Federal de Fibra Óptica de Argentina (REFEFO) en un radio de 50km desde el Partido de Pergamino. |
| [Tramos de la Red Federal de Fibra Óptica](./red_federal_fibra_optica_tramos/) | 53 | Multi LineString | Capa de tramos de la Red Federal de Fibra Óptica de Argentina (REFEFO) en un radio de 50km desde el Partido de Pergam... |
| [WiFi en espacios verdes públicos](./wifi_espacios_verdes/) | 11 | Point | Zonas de Internet gratuito por WiFi en espacios verdes de la Ciudad de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **IDECOM/ENACOM** — Nodos de la Red Federal de Fibra Óptica, Tramos de la Red Federal de Fibra Óptica

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/circuitos_energeticos/publico_circuitos_energeticos.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
