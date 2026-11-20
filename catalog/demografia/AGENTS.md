# Guía para agentes — Demografía e indicadores sociales

Geografía censal y sus indicadores: radios censales INDEC 2010 y 2022, NBI, Índice de Calidad de Vida (CONICET), hacinamiento, razón de sexo, pobreza crónica, calidad de vivienda, densidad de población por censo, población por manzana por mapeo dasimétrico, y barrios populares RENABAP. Varias capas son datos nacionales rehospedados por el municipio.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`demografia/calidad_vivienda`](./calidad_vivienda/AGENTS.md): Calidad de vivienda (INDEC 2010), polígonos
- [`demografia/hacinamiento`](./hacinamiento/AGENTS.md): Nivel de hacinamiento (2010), polígonos
- [`demografia/icv`](./icv/AGENTS.md): Índice de Calidad de Vida (ICV), polígonos
- [`demografia/manzanas_isdd`](./manzanas_isdd/AGENTS.md): Densidad de población por Mapeo Dasimétrico - Censo 2022, polígonos
- [`demografia/nbi`](./nbi/AGENTS.md): Necesidades básicas insatisfechas (NBI), polígonos
- [`demografia/poblacion_1991`](./poblacion_1991/AGENTS.md): Densidad de población 1991, polígonos
- [`demografia/poblacion_2001`](./poblacion_2001/AGENTS.md): Densidad de población 2001, polígonos
- [`demografia/poblacion_2010`](./poblacion_2010/AGENTS.md): Densidad de población 2010, polígonos
- [`demografia/poblacion_2022`](./poblacion_2022/AGENTS.md): Densidad de población 2022, polígonos
- [`demografia/pobreza_cronica`](./pobreza_cronica/AGENTS.md): Pobreza cronica (2010), polígonos
- [`demografia/radios_censales_indec_2010`](./radios_censales_indec_2010/AGENTS.md): Radios censales indec 2010, polígonos
- [`demografia/razon_de_sexo_2010`](./razon_de_sexo_2010/AGENTS.md): Razón de sexo censo 2010, polígonos
- [`demografia/redatam_censo_2022_radios`](./redatam_censo_2022_radios/AGENTS.md): REDATAM Censo 2022 por radio, polígonos
- [`demografia/renabap_barrios_populares`](./renabap_barrios_populares/AGENTS.md): Renabap barrios populares, polígonos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
