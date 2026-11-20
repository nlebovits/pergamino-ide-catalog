# Guía para agentes — Límites administrativos

Límites del partido, barrios y pueblos, localidades y sus áreas, delegaciones, aglomerados urbanos, manchas urbanas históricas desde 1773, circuitos electorales y códigos postales.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`limites/aglomerados_urbanos`](./aglomerados_urbanos/AGENTS.md): Aglomerados urbanos, polígonos
- [`limites/areas_localidades`](./areas_localidades/AGENTS.md): Áreas de localidades por método Voronoi, polígonos
- [`limites/barrios_y_pueblos`](./barrios_y_pueblos/AGENTS.md): Barrios y pueblos, polígonos
- [`limites/circuitos_electorales`](./circuitos_electorales/AGENTS.md): Circuitos electorales, polígonos
- [`limites/cpa`](./cpa/AGENTS.md): Códigos Postales Argentinos (CPA), puntos
- [`limites/delegaciones_pueblos`](./delegaciones_pueblos/AGENTS.md): Delegaciones de pueblos, puntos
- [`limites/localidades`](./localidades/AGENTS.md): Localidades, puntos
- [`limites/manchas_urbanas_historicas`](./manchas_urbanas_historicas/AGENTS.md): Manchas urbanas historicas, polígonos
- [`limites/partido_pergamino`](./partido_pergamino/AGENTS.md): Partido de Pergamino, polígonos
- [`limites/zonas_electorales_celp`](./zonas_electorales_celp/AGENTS.md): Zonas electorales celp, polígonos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
