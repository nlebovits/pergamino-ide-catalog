# Guía para agentes — Transporte

Transporte público y movilidad: colectivos urbanos e interurbanos, paradas, puntos de carga SUBE, ferrocarriles, circuitos de cicloturismo y la Vuelta al Partido, remises y taxis, aeropuertos y estacionamiento.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`transporte/aeropuertos`](./aeropuertos/AGENTS.md): Aeropuertos y aeródromos, puntos
- [`transporte/cicloturismo_rural`](./cicloturismo_rural/AGENTS.md): Cicloturismo rural, líneas
- [`transporte/colectivos_interurbanos`](./colectivos_interurbanos/AGENTS.md): Colectivos interurbanos, líneas
- [`transporte/colectivos_urbanos`](./colectivos_urbanos/AGENTS.md): Colectivos urbanos, líneas
- [`transporte/estacionamiento_motos_bicicletas`](./estacionamiento_motos_bicicletas/AGENTS.md): Estacionamiento de motos y bicicletas, puntos
- [`transporte/estacionamiento_nocturno`](./estacionamiento_nocturno/AGENTS.md): Estacionamiento lado izquierdo, líneas
- [`transporte/estacionamiento_privado`](./estacionamiento_privado/AGENTS.md): Estacionamiento privado, puntos
- [`transporte/ferrocarriles`](./ferrocarriles/AGENTS.md): Ferrocarriles, líneas
- [`transporte/paradas_de_colectivo`](./paradas_de_colectivo/AGENTS.md): Paradas de colectivo, puntos
- [`transporte/remis_taxi`](./remis_taxi/AGENTS.md): Paradas de remis y taxis, puntos
- [`transporte/sube`](./sube/AGENTS.md): Puntos de recarga SUBE, puntos
- [`transporte/vuelta_partido`](./vuelta_partido/AGENTS.md): Vuelta al Partido, líneas

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
