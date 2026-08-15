# Límites administrativos

Límites del partido, barrios, localidades y pueblos, delegaciones, aglomerados urbanos, manchas urbanas históricas desde 1773, circuitos electorales y códigos postales.

10 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Aglomerados urbanos](./aglomerados_urbanos/) | 166 | Polygon | Mancha de aglomerados urbanos del Partido de Pergamino donde se observan edificaciones e instalaciones urbanas en las... |
| [Barrios](./barrios/) | 45 | Multi Polygon | Límites administrativos oficiales de la Ciudad de Pergamino |
| [Circuitos electorales](./circuitos_electorales/) | 122 | Multi Polygon | Circuitos electorales del Partido de Pergamino. |
| [Códigos Postales Argentinos (CPA)](./cpa/) | 6.869 | Point | Código Postal Argentino tomado de la página Oficial del Correo Argentino para la Ciudad de Pergamino. |
| [Delegaciones de pueblos](./delegaciones_pueblos/) | 12 | Point | Capa de delegaciones de Pueblos del Partido de Pergamino. |
| [Localidades](./localidades/) | 59 | Point | Localidades del Partido de Pergamino y alrededores. |
| [Manchas urbanas historicas](./manchas_urbanas_historicas/) | 8 | Multi Polygon | Manchas urbanas históricas de la Ciudad de Pergamino, desde 1773 a 2025, tomadas del Plan Estratégico Pergamino (PEP). |
| [Partido de Pergamino](./partido_pergamino/) | 1 | Polygon | Límites del Partido de Pergamino según el Catastro Municipal. |
| [Pueblos](./pueblos/) | 13 | Multi Polygon | Polígonos de los Pueblos del Partido de Pergamino. |
| [Zonas electorales celp](./zonas_electorales_celp/) | 8 | Polygon | Capa de zonas electorales de la Cooperativa Eléctrica Limitada de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **ARBA** — Partido de Pergamino
- **BAHRA** — Localidades

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/limites/aglomerados_urbanos/publico_aglomerados_urbanos.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
