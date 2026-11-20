# Guía para agentes — Seguridad

Cuarteles de bomberos, dependencias de seguridad, zonas de seguridad, zonas de emergencia y riesgo, y centros de evacuados.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`seguridad/bomberos`](./bomberos/AGENTS.md): Bomberos, puntos
- [`seguridad/centros_evacuados`](./centros_evacuados/AGENTS.md): Centros de evacuados ante riesgo, puntos
- [`seguridad/dependencias_seguridad`](./dependencias_seguridad/AGENTS.md): Dependencias de seguridad y acceso a la justicia, puntos
- [`seguridad/zonas_emergencias_y_riesgo`](./zonas_emergencias_y_riesgo/AGENTS.md): Zonas de gestión ante emergencias y riesgos, polígonos
- [`seguridad/zonas_seguridad`](./zonas_seguridad/AGENTS.md): Zonas de seguridad, polígonos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
