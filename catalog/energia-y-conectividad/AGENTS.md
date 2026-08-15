# Guía para agentes — Energía y conectividad

Cobertura de gas natural, circuitos energéticos, red de fibra óptica municipal y federal, y puntos de acceso wifi en espacios verdes.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`energia-y-conectividad/circuitos_energeticos`](./circuitos_energeticos/AGENTS.md) — Circuitos energéticos (TEAM-UNNOBA), 19 registros, Point
- [`energia-y-conectividad/cobertura_gas_natural`](./cobertura_gas_natural/AGENTS.md) — Cobertura de gas natural, 17 registros, Polygon
- [`energia-y-conectividad/fibra_optica`](./fibra_optica/AGENTS.md) — Red de fibra óptica municipal, 16 registros, Multi LineString
- [`energia-y-conectividad/red_federal_fibra_optica_nodos`](./red_federal_fibra_optica_nodos/AGENTS.md) — Nodos de la Red Federal de Fibra Óptica, 50 registros, Point
- [`energia-y-conectividad/red_federal_fibra_optica_tramos`](./red_federal_fibra_optica_tramos/AGENTS.md) — Tramos de la Red Federal de Fibra Óptica, 53 registros, Multi LineString
- [`energia-y-conectividad/wifi_espacios_verdes`](./wifi_espacios_verdes/AGENTS.md) — WiFi en espacios verdes públicos, 11 registros, Point

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
