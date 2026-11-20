# Límites administrativos

Límites del partido, barrios y pueblos, localidades y sus áreas, delegaciones, aglomerados urbanos, manchas urbanas históricas desde 1773, circuitos electorales y códigos postales.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Aglomerados urbanos](./aglomerados_urbanos/) | polígonos | Mancha de aglomerados urbanos del Partido de Pergamino donde se observan edificaciones e instalaciones urbanas en las cuales se desarroll... |
| [Áreas de localidades por método Voronoi](./areas_localidades/) | polígonos | Áreas de Voronoi aplicadas a los centroides de las localidades del Partido de Pergamino. |
| [Barrios y pueblos](./barrios_y_pueblos/) | polígonos | Barrios y pueblos del Partido de Pergamino con dato de cantidad de habitantes y hogares estimada al 2023. |
| [Circuitos electorales](./circuitos_electorales/) | polígonos | Circuitos electorales del Partido de Pergamino |
| [Códigos Postales Argentinos (CPA)](./cpa/) | puntos | Código Postal Argentino tomado de la página Oficial del Correo Argentino para la Ciudad de Pergamino. |
| [Delegaciones de pueblos](./delegaciones_pueblos/) | puntos | Capa de delegaciones de Pueblos del Partido de Pergamino. |
| [Localidades](./localidades/) | puntos | Localidades del Partido de Pergamino y alrededores. |
| [Manchas urbanas historicas](./manchas_urbanas_historicas/) | polígonos | Manchas urbanas históricas de la Ciudad de Pergamino, desde 1773 a 2025, tomadas del Plan Estratégico Pergamino (PEP). |
| [Partido de Pergamino](./partido_pergamino/) | polígonos | Límites del Partido de Pergamino según el Catastro Municipal. |
| [Zonas electorales celp](./zonas_electorales_celp/) | polígonos | Capa de zonas electorales de la Cooperativa Eléctrica Limitada de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **Agencia de Recaudación de la Provincia de Buenos Aires (ARBA)**: Partido de Pergamino
- **Base de Asentamientos Humanos de la República Argentina (BAHRA)**: Localidades
- **Correo Oficial de la República Argentina**: Códigos Postales Argentinos (CPA)

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/aglomerados_urbanos/aglomerados_urbanos.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
