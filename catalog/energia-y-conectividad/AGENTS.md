# Guía para agentes — Energía y conectividad

Cobertura de gas natural, circuitos energéticos, nodos y tramos de la Red Federal de Fibra Óptica, y puntos de acceso wifi en espacios verdes.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`energia-y-conectividad/circuitos_energeticos`](./circuitos_energeticos/AGENTS.md): Circuitos energéticos (TEAM-UNNOBA), puntos
- [`energia-y-conectividad/cobertura_gas_natural`](./cobertura_gas_natural/AGENTS.md): Cobertura de gas natural, polígonos
- [`energia-y-conectividad/red_federal_fibra_optica_nodos`](./red_federal_fibra_optica_nodos/AGENTS.md): Nodos de la Red Federal de Fibra Óptica, puntos
- [`energia-y-conectividad/red_federal_fibra_optica_tramos`](./red_federal_fibra_optica_tramos/AGENTS.md): Tramos de la Red Federal de Fibra Óptica, líneas
- [`energia-y-conectividad/wifi_espacios_verdes`](./wifi_espacios_verdes/AGENTS.md): WiFi en espacios verdes públicos, puntos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
