# Guía para agentes — Transporte

Transporte público y movilidad: colectivos urbanos e interurbanos y sus líneas, paradas, ferrocarriles, ciclovías, remises y taxis, aeropuertos y estacionamiento.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`transporte/aeropuertos`](./aeropuertos/AGENTS.md) — Aeropuertos y aeródromos, 40 registros, Point
- [`transporte/cicloturismo_rural`](./cicloturismo_rural/AGENTS.md) — Cicloturismo rural, 10 registros, LineString
- [`transporte/ciclovias`](./ciclovias/AGENTS.md) — Ciclovias, 11.703 registros, Multi LineString
- [`transporte/colectivos_interurbanos`](./colectivos_interurbanos/AGENTS.md) — Colectivos interurbanos, 57 registros, Multi LineString
- [`transporte/colectivos_urbanos`](./colectivos_urbanos/AGENTS.md) — Colectivos urbanos, 16 registros, LineString
- [`transporte/estacionamiento_medido`](./estacionamiento_medido/AGENTS.md) — Estacionamiento medido, 380 registros, Multi LineString
- [`transporte/estacionamiento_motos_bicicletas`](./estacionamiento_motos_bicicletas/AGENTS.md) — Estacionamiento de motos y bicicletas, 69 registros, Point
- [`transporte/estacionamiento_nocturno`](./estacionamiento_nocturno/AGENTS.md) — Estacionamiento lado izquierdo, 47 registros, Multi LineString
- [`transporte/estacionamiento_privado`](./estacionamiento_privado/AGENTS.md) — Estacionamiento privado, 30 registros, Point
- [`transporte/ferrocarriles`](./ferrocarriles/AGENTS.md) — Ferrocarriles, 109 registros, LineString
- [`transporte/linea_a`](./linea_a/AGENTS.md) — Linea a, 3 registros, LineString
- [`transporte/linea_b`](./linea_b/AGENTS.md) — Linea b, 2 registros, LineString
- [`transporte/linea_c`](./linea_c/AGENTS.md) — Linea c, 3 registros, LineString
- [`transporte/linea_d`](./linea_d/AGENTS.md) — Linea d, 4 registros, LineString
- [`transporte/linea_e`](./linea_e/AGENTS.md) — Linea e, 2 registros, LineString
- [`transporte/linea_parque_industrial`](./linea_parque_industrial/AGENTS.md) — Linea parque industrial, 2 registros, LineString
- [`transporte/paradas_de_colectivo`](./paradas_de_colectivo/AGENTS.md) — Paradas de colectivo, 394 registros, Point
- [`transporte/remis_taxi`](./remis_taxi/AGENTS.md) — Paradas de remis y taxis, 24 registros, Point
- [`transporte/sube`](./sube/AGENTS.md) — Puntos de recarga SUBE, 97 registros, Point

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
