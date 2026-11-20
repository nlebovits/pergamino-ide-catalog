# Demografía e indicadores sociales

Geografía censal y sus indicadores: radios censales INDEC 2010 y 2022, NBI, Índice de Calidad de Vida (CONICET), hacinamiento, razón de sexo, pobreza crónica, calidad de vivienda, densidad de población por censo, población por manzana por mapeo dasimétrico, y barrios populares RENABAP. Varias capas son datos nacionales rehospedados por el municipio.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Calidad de vivienda (INDEC 2010)](./calidad_vivienda/) | polígonos | Índice de calidad de vivienda según Censo INDEC 2010 para todo el Partido de Pergamino. |
| [Nivel de hacinamiento (2010)](./hacinamiento/) | polígonos | Índice de hacinamiento según Censo INDEC 2010 para el Partido de Pergamino. |
| [Índice de Calidad de Vida (ICV)](./icv/) | polígonos | Capa de datos que permite conocer el Índice de Calidad de Vida o ICV desde una perspectiva geográfica, elaborado por el CONICET. Mapa de... |
| [Densidad de población por Mapeo Dasimétrico - Censo 2022](./manzanas_isdd/) | polígonos | Este conjunto de datos georreferenciados presenta la estimación espacial desagregada de la población, los hogares y diversos indicadores... |
| [Necesidades básicas insatisfechas (NBI)](./nbi/) | polígonos | Niveles Básicos Insatisfechos según Censo INDEC 2010, para el Partido de Pergamino. Las Necesidades Básicas Insatisfechas (NBI) del INDEC... |
| [Densidad de población 1991](./poblacion_1991/) | polígonos | Datos georreferenciados del Censo 1991 donde se puede observar la densidad poblacional por radio censal. |
| [Densidad de población 2001](./poblacion_2001/) | polígonos | Datos georreferenciados del Censo 2001 donde se puede observar la densidad poblacional por radio censal. |
| [Densidad de población 2010](./poblacion_2010/) | polígonos | Datos georreferenciados del Censo 2010 donde se puede observar la densidad poblacional por radio censal. |
| [Densidad de población 2022](./poblacion_2022/) | polígonos | Datos georreferenciados del Censo 2022 donde se puede observar la densidad poblacional por radio censal. |
| [Pobreza cronica (2010)](./pobreza_cronica/) | polígonos | La capa contiene índices que permiten visualizar, por radio censal, la pobreza crónica para el Partido de Pergamino según Censo INDEC 2010. |
| [Radios censales indec 2010](./radios_censales_indec_2010/) | polígonos | Radios censales INDEC 2010 con dato de población para el Partido de Pergamino. |
| [Razón de sexo censo 2010](./razon_de_sexo_2010/) | polígonos | Coeficientes de razón de sexo, o predominancia entre cantidad de varones y mujeres por radio censal para el Partido de Pergamino. |
| [REDATAM Censo 2022 por radio](./redatam_censo_2022_radios/) | polígonos | La capa contiene múltiples datos de población obtenidos en el Censo del 2022 a nivel de radio censal para el Partido de Pergamino, como c... |
| [Renabap barrios populares](./renabap_barrios_populares/) | polígonos | Barrios populares relevados por RENABAP, en el Partido de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **Consejo Nacional de Investigaciones Científicas y Técnicas (CONICET)**: Índice de Calidad de Vida (ICV)
- **Instituto Nacional de Estadística y Censos (INDEC)**: Calidad de vivienda (INDEC 2010), Densidad de población por Mapeo Dasimétrico - Censo 2022, Necesidades básicas insatisfechas (NBI), Nivel de hacinamiento (2010), Pobreza cronica (2010), Radios censales indec 2010, Razón de sexo censo 2010

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/calidad_vivienda/calidad_vivienda.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
