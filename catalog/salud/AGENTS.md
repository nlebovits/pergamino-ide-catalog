# Guía para agentes — Salud

Establecimientos y cobertura sanitaria: centros de salud, CAPS, áreas programáticas, desfibriladores de acceso público y guardias.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`salud/areas_programaticas_salud`](./areas_programaticas_salud/AGENTS.md): Áreas programaticas de salud, polígonos
- [`salud/caps`](./caps/AGENTS.md): Centros de Atención Primaria de Salud (CAPS), puntos
- [`salud/centros_de_salud`](./centros_de_salud/AGENTS.md): Centros de salud, puntos
- [`salud/desfibriladores`](./desfibriladores/AGENTS.md): Desfibriladores, puntos
- [`salud/estaciones_de_salud`](./estaciones_de_salud/AGENTS.md): Estaciones de salud, puntos
- [`salud/guardias_emergencias_servicios`](./guardias_emergencias_servicios/AGENTS.md): Guardias de servicios, puntos
- [`salud/guardias_medicas`](./guardias_medicas/AGENTS.md): Guardias médicas, puntos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
