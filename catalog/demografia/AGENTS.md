# Guía para agentes — Demografía e indicadores sociales

Geografía censal y sus indicadores: radios censales INDEC 2010 y 2022, NBI, Índice de Calidad de Vida (CONICET), hacinamiento, razón de sexo, pobreza crónica, calidad de vivienda, población y domicilios por manzana, y barrios populares RENABAP. Varias capas son datos nacionales rehospedados por el municipio.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`demografia/calidad_vivienda`](./calidad_vivienda/AGENTS.md) — Calidad de vivienda (INDEC 2010), 178 registros, Polygon
- [`demografia/domicilios_por_manzana`](./domicilios_por_manzana/AGENTS.md) — Domicilios por manzana, 2.197 registros, LineString
- [`demografia/habitantes_por_manzana_provisorio_2022`](./habitantes_por_manzana_provisorio_2022/AGENTS.md) — Habitantes por manzana provisorio 2022, 2.888 registros, Multi Polygon
- [`demografia/hacinamiento`](./hacinamiento/AGENTS.md) — Nivel de hacinamiento (2010), 178 registros, Multi Polygon
- [`demografia/icv`](./icv/AGENTS.md) — Índice de Calidad de Vida (ICV), 178 registros, Polygon
- [`demografia/nbi`](./nbi/AGENTS.md) — Necesidades básicas insatisfechas (NBI), 178 registros, Polygon
- [`demografia/pobreza_cronica`](./pobreza_cronica/AGENTS.md) — Pobreza cronica (2010), 178 registros, Polygon
- [`demografia/proyeccion_habitantes_por_manzana_2010_2030`](./proyeccion_habitantes_por_manzana_2010_2030/AGENTS.md) — Proyeccion 2010 a 2030 habitantes por manzana, 2.939 registros, Polygon
- [`demografia/radios_censales_indec_2010`](./radios_censales_indec_2010/AGENTS.md) — Radios censales indec 2010, 178 registros, Polygon
- [`demografia/razon_de_sexo_2010`](./razon_de_sexo_2010/AGENTS.md) — Razón de sexo censo 2010, 178 registros, Polygon
- [`demografia/redatam_censo_2022_radios`](./redatam_censo_2022_radios/AGENTS.md) — REDATAM Censo 2022 por radio, 212 registros, Multi Polygon
- [`demografia/renabap_barrios_populares`](./renabap_barrios_populares/AGENTS.md) — Renabap barrios populares, 21 registros, Multi Polygon

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
