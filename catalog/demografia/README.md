# Demografía e indicadores sociales

Geografía censal y sus indicadores: radios censales INDEC 2010 y 2022, NBI, Índice de Calidad de Vida (CONICET), hacinamiento, razón de sexo, pobreza crónica, calidad de vivienda, población y domicilios por manzana, y barrios populares RENABAP. Varias capas son datos nacionales rehospedados por el municipio.

12 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Calidad de vivienda (INDEC 2010)](./calidad_vivienda/) | 178 | Polygon | Índice de calidad de vivienda según Censo INDEC 2010 para todo el Partido de Pergamino. |
| [Domicilios por manzana](./domicilios_por_manzana/) | 2.197 | LineString | Cantidad de domicilios y viviendas por manzana relevados por la Municipalidad de Pergamino en 2020. Contiene porcenta... |
| [Habitantes por manzana provisorio 2022](./habitantes_por_manzana_provisorio_2022/) | 2.888 | Multi Polygon | Habitantes por manzana calculado a partir de la cantidad de viviendas y datos provisorios publicados para el Censo 20... |
| [Nivel de hacinamiento (2010)](./hacinamiento/) | 178 | Multi Polygon | Índice de hacinamiento según Censo INDEC 2010 para el Partido de Pergamino. |
| [Índice de Calidad de Vida (ICV)](./icv/) | 178 | Polygon | Capa de datos que permite conocer el Índice de Calidad de Vida o ICV desde una perspectiva geográfica, elaborado por ... |
| [Necesidades básicas insatisfechas (NBI)](./nbi/) | 178 | Polygon | Niveles Básicos Insatisfechos según Censo INDEC 2010, para el Partido de Pergamino. Las Necesidades Básicas Insatisfe... |
| [Pobreza cronica (2010)](./pobreza_cronica/) | 178 | Polygon | La capa contiene índices que permiten visualizar, por radio censal, la pobreza crónica para el Partido de Pergamino s... |
| [Proyeccion 2010 a 2030 habitantes por manzana](./proyeccion_habitantes_por_manzana_2010_2030/) | 2.939 | Polygon | Proyección de 2010 a 2030 de habitantes por manzana calculado a partir de la cantidad de viviendas y datos provisorio... |
| [Radios censales indec 2010](./radios_censales_indec_2010/) | 178 | Polygon | Radios censales INDEC 2010 con dato de población para el Partido de Pergamino. |
| [Razón de sexo censo 2010](./razon_de_sexo_2010/) | 178 | Polygon | Coeficientes de razón de sexo, o predominancia entre cantidad de varones y mujeres por radio censal para el Partido d... |
| [REDATAM Censo 2022 por radio](./redatam_censo_2022_radios/) | 212 | Multi Polygon | La capa contiene múltiples datos de población obtenidos en el Censo del 2022 a nivel de radio censal para el Partido ... |
| [Renabap barrios populares](./renabap_barrios_populares/) | 21 | Multi Polygon | Barrios populares relevados por RENABAP, en el Partido de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **CONICET** — Índice de Calidad de Vida (ICV)
- **INDEC** — Necesidades básicas insatisfechas (NBI), Nivel de hacinamiento (2010), Pobreza cronica (2010), Proyeccion 2010 a 2030 habitantes por manzana, Radios censales indec 2010, Razón de sexo censo 2010

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/demografia/calidad_vivienda/publico_calidad_vivienda.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
