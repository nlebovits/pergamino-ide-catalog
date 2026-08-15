# Guía para agentes — Servicios sanitarios

Cobertura de agua corriente y red cloacal por período de gestión, medidores, pozos y estaciones de bombeo de la Dirección de Obras y Servicios Sanitarios (DOSS), desagües pluviales y zonas de facturación.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`servicios-sanitarios/cobertura_agua_antes_de_2015`](./cobertura_agua_antes_de_2015/AGENTS.md) — Cobertura agua antes de 2015, 8 registros, Polygon
- [`servicios-sanitarios/cobertura_agua_de_2015_a_2019`](./cobertura_agua_de_2015_a_2019/AGENTS.md) — Cobertura agua de 2015 a 2019, 39 registros, Polygon
- [`servicios-sanitarios/cobertura_agua_de_2019_a_2023`](./cobertura_agua_de_2019_a_2023/AGENTS.md) — Cobertura agua de 2019 a 2023, 23 registros, Polygon
- [`servicios-sanitarios/cobertura_agua_de_2023_a_2027`](./cobertura_agua_de_2023_a_2027/AGENTS.md) — Cobertura agua de 2023 a 2027, 37 registros, Multi Polygon
- [`servicios-sanitarios/cobertura_cloacas_antes_de_2015`](./cobertura_cloacas_antes_de_2015/AGENTS.md) — Cobertura cloacas antes de 2015, 78 registros, Multi Polygon
- [`servicios-sanitarios/cobertura_cloacas_de_2015_a_2019`](./cobertura_cloacas_de_2015_a_2019/AGENTS.md) — Cobertura cloacas de 2015 a 2019, 127 registros, Multi Polygon
- [`servicios-sanitarios/cobertura_cloacas_de_2019_a_2023`](./cobertura_cloacas_de_2019_a_2023/AGENTS.md) — Cobertura cloacas de 2019 a 2023, 62 registros, Multi Polygon
- [`servicios-sanitarios/cobertura_cloacas_de_2023_a_2027`](./cobertura_cloacas_de_2023_a_2027/AGENTS.md) — Cobertura cloacas de 2023 a 2027, 29 registros, Multi Polygon
- [`servicios-sanitarios/codigo_reparto_facturacion`](./codigo_reparto_facturacion/AGENTS.md) — Códigos de reparto de facturación, 11.703 registros, Multi LineString
- [`servicios-sanitarios/coeficientes_zonales_doss`](./coeficientes_zonales_doss/AGENTS.md) — Coeficientes zonales (DOSS), 58 registros, Multi Polygon
- [`servicios-sanitarios/colectoras_cloacales_maximas`](./colectoras_cloacales_maximas/AGENTS.md) — Colectoras cloacales maximas, 42 registros, LineString
- [`servicios-sanitarios/estaciones_de_bombeo`](./estaciones_de_bombeo/AGENTS.md) — Estaciones de bombeo pluvial, 4 registros, Point
- [`servicios-sanitarios/medidores_agua`](./medidores_agua/AGENTS.md) — Medidores de agua, 17 registros, Multi Polygon
- [`servicios-sanitarios/pluviales`](./pluviales/AGENTS.md) — Ductos pluviales, 1.739 registros, Multi LineString
- [`servicios-sanitarios/pozos_agua_doss`](./pozos_agua_doss/AGENTS.md) — Pozos agua doss, 95 registros, Multi Point
- [`servicios-sanitarios/sumideros`](./sumideros/AGENTS.md) — Sumideros pluviales, 955 registros, Point
- [`servicios-sanitarios/zonas_facturacion`](./zonas_facturacion/AGENTS.md) — Zonas de facturacion, 54 registros, Multi Polygon

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
