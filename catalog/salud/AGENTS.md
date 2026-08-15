# Guía para agentes — Salud

Establecimientos y cobertura sanitaria: centros de salud, CAPS, áreas programáticas, desfibriladores de acceso público y guardias.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`salud/areas_programaticas_salud`](./areas_programaticas_salud/AGENTS.md) — Áreas programaticas de salud, 17 registros, Polygon
- [`salud/caps`](./caps/AGENTS.md) — Centros de Atención Primaria de Salud (CAPS), 30 registros, Point
- [`salud/centros_de_salud`](./centros_de_salud/AGENTS.md) — Centros de salud, 23 registros, Multi Point
- [`salud/desfibriladores`](./desfibriladores/AGENTS.md) — Desfibriladores, 10 registros, Point
- [`salud/estaciones_de_salud`](./estaciones_de_salud/AGENTS.md) — Estaciones de salud, 29 registros, Multi Point
- [`salud/guardias_emergencias_servicios`](./guardias_emergencias_servicios/AGENTS.md) — Guardias de servicios, 6 registros, Multi Point
- [`salud/guardias_medicas`](./guardias_medicas/AGENTS.md) — Guardias médicas, 5 registros, Multi Point

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
