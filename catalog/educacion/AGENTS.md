# Guía para agentes — Educación

Establecimientos educativos, por nivel y por tipo de gestión, predios educativos y bibliotecas del Partido de Pergamino.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`educacion/bibliotecas`](./bibliotecas/AGENTS.md): Bibliotecas, puntos
- [`educacion/educacion`](./educacion/AGENTS.md): Educacion, puntos
- [`educacion/gestion`](./gestion/AGENTS.md): Educacion por gestion, puntos
- [`educacion/nivel`](./nivel/AGENTS.md): Educacion por nivel, puntos
- [`educacion/predios_educativos`](./predios_educativos/AGENTS.md): Predios educativos, polígonos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
