# Energía y conectividad

Cobertura de gas natural, circuitos energéticos, nodos y tramos de la Red Federal de Fibra Óptica, y puntos de acceso wifi en espacios verdes.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Circuitos energéticos (TEAM-UNNOBA)](./circuitos_energeticos/) | puntos | Circuitos energéticos identificados por el equipo de investigación TEAM UNNOBA para todo el Partido de Pergamino. |
| [Cobertura de gas natural](./cobertura_gas_natural/) | polígonos | Cobertura de gas natural en el territorio de la Ciudad de Pergamino, provista por Litoral Gas S.A. |
| [Nodos de la Red Federal de Fibra Óptica](./red_federal_fibra_optica_nodos/) | puntos | Capa de nodos de la Red Federal de Fibra Óptica de Argentina (REFEFO) en un radio de 50km desde el Partido de Pergamino. |
| [Tramos de la Red Federal de Fibra Óptica](./red_federal_fibra_optica_tramos/) | líneas | Capa de tramos de la Red Federal de Fibra Óptica de Argentina (REFEFO) en un radio de 50km desde el Partido de Pergamino. |
| [WiFi en espacios verdes públicos](./wifi_espacios_verdes/) | puntos | Zonas de Internet gratuito por WiFi en espacios verdes de la Ciudad de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **IDECOM - Ente Nacional de Comunicaciones (ENACOM)**: Nodos de la Red Federal de Fibra Óptica, Tramos de la Red Federal de Fibra Óptica
- **Universidad Nacional del Noroeste de la Provincia de Buenos Aires**: Circuitos energéticos (TEAM-UNNOBA)

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/circuitos_energeticos/circuitos_energeticos.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
