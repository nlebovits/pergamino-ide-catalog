# Servicios sanitarios

Cobertura de agua corriente y red cloacal por período de gestión, medidores, pozos y estaciones de bombeo de la Dirección de Obras y Servicios Sanitarios (DOSS), desagües pluviales y zonas de facturación.

17 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Cobertura agua antes de 2015](./cobertura_agua_antes_de_2015/) | 8 | Polygon | Capa de cobertura del servicio sanitario de red de agua corriente para Pergamino, anterior a la gestión 2015. La cobe... |
| [Cobertura agua de 2015 a 2019](./cobertura_agua_de_2015_a_2019/) | 39 | Polygon | Capa de cobertura del servicio sanitario de red de agua corriente para Pergamino, entre 2015 y 2019. La cobertura del... |
| [Cobertura agua de 2019 a 2023](./cobertura_agua_de_2019_a_2023/) | 23 | Polygon | Capa de cobertura del servicio sanitario de red de agua corriente para Pergamino, entre 2019 y 2023. La cobertura del... |
| [Cobertura agua de 2023 a 2027](./cobertura_agua_de_2023_a_2027/) | 37 | Multi Polygon | Capa de cobertura del servicio sanitario de red de agua corriente para Pergamino, entre 2023 y 2027. La cobertura del... |
| [Cobertura cloacas antes de 2015](./cobertura_cloacas_antes_de_2015/) | 78 | Multi Polygon | Capa de cobertura del servicio sanitario de red cloacal para Pergamino, anterior a la gestión 2015. La cobertura del ... |
| [Cobertura cloacas de 2015 a 2019](./cobertura_cloacas_de_2015_a_2019/) | 127 | Multi Polygon | Capa de cobertura del servicio sanitario de red cloacal para Pergamino, posterior a la gestión 2015. La cobertura del... |
| [Cobertura cloacas de 2019 a 2023](./cobertura_cloacas_de_2019_a_2023/) | 62 | Multi Polygon | Capa de cobertura del servicio sanitario de red cloacal para Pergamino, posterior a la gestión 2019. La cobertura del... |
| [Cobertura cloacas de 2023 a 2027](./cobertura_cloacas_de_2023_a_2027/) | 29 | Multi Polygon | Capa de cobertura del servicio sanitario de red cloacal para Pergamino, posterior a la gestión 2023. La cobertura del... |
| [Códigos de reparto de facturación](./codigo_reparto_facturacion/) | 11.703 | Multi LineString | Dataset extraído del callejero con los códigos de reparto de facturación según la Secretaría de Hacienda. |
| [Coeficientes zonales (DOSS)](./coeficientes_zonales_doss/) | 58 | Multi Polygon | Coeficientes multiplicadores para el cobro de tasas por Servicios Sanitarios para la Ciudad de Pergamino. |
| [Colectoras cloacales maximas](./colectoras_cloacales_maximas/) | 42 | LineString | Colectoras cloacales máximas divididas en los diversos sistemas que posee la red de servicios sanitarios de la Ciudad... |
| [Estaciones de bombeo pluvial](./estaciones_de_bombeo/) | 4 | Point | Estaciones de bombeo de agua pluvial que sirven para evitar inundaciones en la Ciudad de Pergamino. |
| [Medidores de agua](./medidores_agua/) | 17 | Multi Polygon | Zonas de instalación de medidores domiciliarios de agua corriente en la Ciudad de Pergamino. |
| [Ductos pluviales](./pluviales/) | 1.739 | Multi LineString | Desagües pluviales de la Ciudad de Pergamino. |
| [Pozos agua doss](./pozos_agua_doss/) | 95 | Multi Point | Localización de pozos de extracción de agua de Pergamino. |
| [Sumideros pluviales](./sumideros/) | 955 | Point | Sumideros pluviales de la Ciudad de Pergamino. |
| [Zonas de facturacion](./zonas_facturacion/) | 54 | Multi Polygon | Zonas de coeficientes de facturación determinadas por la Secretaría de Hacienda para el Partido de Pergamino. |

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua_antes_de_2015/publico_cobertura_agua_antes_de_2015.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
