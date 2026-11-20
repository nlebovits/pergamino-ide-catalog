# Guía para agentes — Catastro

Parcelario y jerarquía catastral del Partido de Pergamino, desde la circunscripción hasta la subparcela y la propiedad horizontal, junto con zonificación, edificaciones detectadas sobre imágenes y edificios de interés.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`catastro/areas_fiscalizadas_construcciones`](./areas_fiscalizadas_construcciones/AGENTS.md): Áreas fiscalizadas construcciones no declaradas, polígonos
- [`catastro/chacra`](./chacra/AGENTS.md): Catastro chacra, polígonos
- [`catastro/circunscripcion`](./circunscripcion/AGENTS.md): Catastro circunscripcion, polígonos
- [`catastro/complejos_habitacionales`](./complejos_habitacionales/AGENTS.md): Complejos habitacionales, polígonos
- [`catastro/edificaciones_automaticas`](./edificaciones_automaticas/AGENTS.md): Edificaciones detectadas con IA, polígonos
- [`catastro/edificios_en_altura`](./edificios_en_altura/AGENTS.md): Edificios en altura, puntos
- [`catastro/edificios_historicos`](./edificios_historicos/AGENTS.md): Edificios históricos, puntos
- [`catastro/fraccion`](./fraccion/AGENTS.md): Catastro fraccion, polígonos
- [`catastro/manzana`](./manzana/AGENTS.md): Catastro manzana, polígonos
- [`catastro/medida_lado`](./medida_lado/AGENTS.md): Catastro medida lado de parcela, puntos
- [`catastro/parcela`](./parcela/AGENTS.md): Catastro parcela, polígonos
- [`catastro/ph`](./ph/AGENTS.md): Catastro ph, puntos
- [`catastro/quinta`](./quinta/AGENTS.md): Catastro quinta, polígonos
- [`catastro/seccion`](./seccion/AGENTS.md): Catastro seccion, polígonos
- [`catastro/subparcela`](./subparcela/AGENTS.md): Catastro subparcela, polígonos
- [`catastro/zonificacion`](./zonificacion/AGENTS.md): Zonificacion, polígonos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
