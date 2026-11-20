# Servicios sanitarios

Redes de agua corriente y cloacas (líneas, nodos y cobertura), medidores, pozos y estaciones de bombeo de la Dirección de Obras y Servicios Sanitarios (DOSS), desagües pluviales, sumideros y compuertas, y zonas de facturación.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Red de agua corriente - Líneas](./agua_lineas/) | líneas | Sistema de tuberías y conexiones de la red de agua corriente de la Ciudad de Pergamino. |
| [Red de agua corriente - Nodos](./agua_nodos/) | puntos | Sistema de llaves y nodos de la red de agua corriente de la Ciudad de Pergamino. |
| [Red cloacal - Líneas](./cloacas_lineas/) | líneas | Sistema de tuberías y conexiones de la red cloacal de la Ciudad de Pergamino. |
| [Red cloacal - Nodos](./cloacas_nodos/) | puntos | Sistema de nodos y nodos de la red cloacal de la Ciudad de Pergamino. |
| [Cobertura de red de agua corriente](./cobertura_agua/) | polígonos | Capa de cobertura del servicio sanitario de red de agua corriente para la Ciudad de Pergamino. |
| [Cobertura de red cloacal](./cobertura_cloacas/) | polígonos | Capa de cobertura del servicio sanitario de red cloacal para la Ciudad de Pergamino. |
| [Códigos de reparto de facturación](./codigo_reparto_facturacion/) | líneas | Dataset extraído del callejero con los códigos de reparto de facturación según la Secretaría de Hacienda. |
| [Coeficientes zonales (DOSS)](./coeficientes_zonales_doss/) | polígonos | Coeficientes multiplicadores para el cobro de tasas por Servicios Sanitarios para la Ciudad de Pergamino. |
| [Compuertas antirretorno en desagües pluviales](./compuertas_pluviales/) | puntos | Ubicación de las compuertas antiretorno de desagües pluviales sobre el Arroyo Pergamino, en el área urbana y periurbana de la Ciudad. |
| [Estaciones de bombeo pluvial](./estaciones_de_bombeo/) | puntos | Estaciones de bombeo de agua pluvial que sirven para evitar inundaciones en la Ciudad de Pergamino. |
| [Medidores de agua](./medidores_agua/) | polígonos | Zonas de instalación de medidores domiciliarios de agua corriente en la Ciudad de Pergamino. |
| [Ductos pluviales](./pluviales/) | líneas | Desagües pluviales de la Ciudad de Pergamino. |
| [Pozos de agua DOSS](./pozos_agua_doss/) | puntos | Localización de pozos de extracción de agua de la Dirección de Obras y Servicios Sanitarios de la Ciudad de Pergamino. |
| [Sumideros pluviales](./sumideros/) | puntos | Sumideros pluviales de la Ciudad de Pergamino. |
| [Zonas de facturacion](./zonas_facturacion/) | polígonos | Zonas de coeficientes de facturación determinadas por la Secretaría de Hacienda para el Partido de Pergamino. |

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/agua_lineas.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
