# Guía para agentes — Catastro

Parcelario y jerarquía catastral del Partido de Pergamino, desde la circunscripción hasta la subparcela y la propiedad horizontal, junto con zonificación, edificaciones y edificios de interés.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`catastro/areas_fiscalizadas_construcciones`](./areas_fiscalizadas_construcciones/AGENTS.md) — Áreas fiscalizadas construcciones no declaradas, 33 registros, Polygon
- [`catastro/chacra`](./chacra/AGENTS.md) — Catastro chacra, 285 registros, Multi Polygon
- [`catastro/circunscripcion`](./circunscripcion/AGENTS.md) — Catastro circunscripcion, 23 registros, Multi Polygon
- [`catastro/fraccion`](./fraccion/AGENTS.md) — Catastro fraccion, 181 registros, Multi Polygon
- [`catastro/manzana`](./manzana/AGENTS.md) — Catastro manzana, 2.564 registros, Multi Polygon
- [`catastro/medida_lado`](./medida_lado/AGENTS.md) — Catastro medida lado de parcela, 196.722 registros, Point
- [`catastro/parcela`](./parcela/AGENTS.md) — Catastro parcela, 55.134 registros, Polygon
- [`catastro/ph`](./ph/AGENTS.md) — Catastro ph, 9.864 registros, Point
- [`catastro/quinta`](./quinta/AGENTS.md) — Catastro quinta, 136 registros, Multi Polygon
- [`catastro/seccion`](./seccion/AGENTS.md) — Catastro seccion, 71 registros, Multi Polygon
- [`catastro/subparcela`](./subparcela/AGENTS.md) — Catastro subparcela, 487 registros, Polygon
- [`catastro/complejos_habitacionales`](./complejos_habitacionales/AGENTS.md) — Complejos habitacionales, 108 registros, Polygon
- [`catastro/edificaciones_pa`](./edificaciones_pa/AGENTS.md) — Edificaciones detectadas PA, 4.921 registros, Polygon
- [`catastro/edificaciones_pb`](./edificaciones_pb/AGENTS.md) — Edificaciones detectadas PB, 48.168 registros, Polygon
- [`catastro/edificios_en_altura`](./edificios_en_altura/AGENTS.md) — Edificios en altura, 457 registros, Multi Point
- [`catastro/edificios_historicos`](./edificios_historicos/AGENTS.md) — Edificios históricos, 73 registros, Multi Point
- [`catastro/estado_parcela`](./estado_parcela/AGENTS.md) — Estado parcela, 55.134 registros, Polygon
- [`catastro/parcelario`](./parcelario/AGENTS.md) — Parcelario, 55.134 registros, Polygon
- [`catastro/parcelario_contralor`](./parcelario_contralor/AGENTS.md) — Parcelario contralor, 55.134 registros, Polygon
- [`catastro/zonificacion`](./zonificacion/AGENTS.md) — Zonificacion, 230 registros, Multi Polygon

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
