# Guía para agentes — Límites administrativos

Límites del partido, barrios, localidades y pueblos, delegaciones, aglomerados urbanos, manchas urbanas históricas desde 1773, circuitos electorales y códigos postales.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`limites/aglomerados_urbanos`](./aglomerados_urbanos/AGENTS.md) — Aglomerados urbanos, 166 registros, Polygon
- [`limites/barrios`](./barrios/AGENTS.md) — Barrios, 45 registros, Multi Polygon
- [`limites/circuitos_electorales`](./circuitos_electorales/AGENTS.md) — Circuitos electorales, 122 registros, Multi Polygon
- [`limites/cpa`](./cpa/AGENTS.md) — Códigos Postales Argentinos (CPA), 6.869 registros, Point
- [`limites/delegaciones_pueblos`](./delegaciones_pueblos/AGENTS.md) — Delegaciones de pueblos, 12 registros, Point
- [`limites/localidades`](./localidades/AGENTS.md) — Localidades, 59 registros, Point
- [`limites/manchas_urbanas_historicas`](./manchas_urbanas_historicas/AGENTS.md) — Manchas urbanas historicas, 8 registros, Multi Polygon
- [`limites/partido_pergamino`](./partido_pergamino/AGENTS.md) — Partido de Pergamino, 1 registros, Polygon
- [`limites/pueblos`](./pueblos/AGENTS.md) — Pueblos, 13 registros, Multi Polygon
- [`limites/zonas_electorales_celp`](./zonas_electorales_celp/AGENTS.md) — Zonas electorales celp, 8 registros, Polygon

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
