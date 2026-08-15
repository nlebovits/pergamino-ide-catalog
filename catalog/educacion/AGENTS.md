# Guía para agentes — Educación

Establecimientos educativos por nivel y tipo de gestión, predios educativos y bibliotecas del Partido de Pergamino.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`educacion/bibliotecas`](./bibliotecas/AGENTS.md) — Bibliotecas, 11 registros, Point
- [`educacion/gestion`](./gestion/AGENTS.md) — Educacion por gestion, 200 registros, Multi Point
- [`educacion/nivel`](./nivel/AGENTS.md) — Educacion por nivel, 200 registros, Multi Point
- [`educacion/predios_educativos`](./predios_educativos/AGENTS.md) — Predios educativos, 133 registros, Multi Polygon

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
