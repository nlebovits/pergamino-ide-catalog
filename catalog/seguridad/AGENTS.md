# Guía para agentes — Seguridad

Cuarteles de bomberos, cuadrículas y jurisdicciones policiales, cámaras de seguridad, dependencias, zonas de emergencia y riesgo, y centros de evacuados.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`seguridad/bomberos`](./bomberos/AGENTS.md) — Bomberos, 2 registros, Multi Point
- [`seguridad/camaras_seguridad`](./camaras_seguridad/AGENTS.md) — Camaras seguridad, 523 registros, Multi Point
- [`seguridad/centros_evacuados`](./centros_evacuados/AGENTS.md) — Centros de evacuados ante riesgo, 5 registros, Point
- [`seguridad/cuadriculas_policiales`](./cuadriculas_policiales/AGENTS.md) — Cuadriculas policiales, 14 registros, Polygon
- [`seguridad/dependencias_seguridad`](./dependencias_seguridad/AGENTS.md) — Dependencias de seguridad y acceso a la justicia, 52 registros, Multi Point
- [`seguridad/jurisdicciones_policiales`](./jurisdicciones_policiales/AGENTS.md) — Jurisdicciones policiales, 3 registros, Polygon
- [`seguridad/zonas_emergencias_y_riesgo`](./zonas_emergencias_y_riesgo/AGENTS.md) — Zonas de gestión ante emergencias y riesgos, 9 registros, Polygon
- [`seguridad/zonas_seguridad`](./zonas_seguridad/AGENTS.md) — Zonas de seguridad, 14 registros, Polygon

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
