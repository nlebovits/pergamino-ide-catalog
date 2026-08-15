# Guía para agentes — Comercio y cultura

Actividad comercial, gastronomía y hospedaje, cultura, deporte y entretenimiento, medios de comunicación, entidades profesionales y sindicales, parques industriales y puntos de interés.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`comercio-y-cultura/agencias_de_viaje`](./agencias_de_viaje/AGENTS.md) — Agencias de viaje, 15 registros, Point
- [`comercio-y-cultura/asociaciones_sindicales`](./asociaciones_sindicales/AGENTS.md) — Asociaciones sindicales, 29 registros, Point
- [`comercio-y-cultura/beata_crescencia_perez`](./beata_crescencia_perez/AGENTS.md) — Beata crescencia perez, 3 registros, Point
- [`comercio-y-cultura/colegios_de_profesionales`](./colegios_de_profesionales/AGENTS.md) — Colegios profesionales, 19 registros, Multi Point
- [`comercio-y-cultura/deportivo`](./deportivo/AGENTS.md) — Clubes deportivos, 108 registros, Multi Point
- [`comercio-y-cultura/entretenimiento`](./entretenimiento/AGENTS.md) — Entretenimiento, 14 registros, Point
- [`comercio-y-cultura/estaciones_servicio`](./estaciones_servicio/AGENTS.md) — Estaciones de servicio, 19 registros, Point
- [`comercio-y-cultura/extraccion_dinero`](./extraccion_dinero/AGENTS.md) — Extraccion de dinero, 24 registros, Point
- [`comercio-y-cultura/gastronomia`](./gastronomia/AGENTS.md) — Oferta gastronómica, 159 registros, Point
- [`comercio-y-cultura/gomerias`](./gomerias/AGENTS.md) — Gomerias, 25 registros, Point
- [`comercio-y-cultura/hospedajes`](./hospedajes/AGENTS.md) — Hoteles y hospedajes, 26 registros, Point
- [`comercio-y-cultura/medios_de_comunicacion`](./medios_de_comunicacion/AGENTS.md) — Medios de comunicacion, 36 registros, Point
- [`comercio-y-cultura/museos_y_espacios_culturales`](./museos_y_espacios_culturales/AGENTS.md) — Museos y espacios culturales, 14 registros, Point
- [`comercio-y-cultura/oferentes_espacios_culturales`](./oferentes_espacios_culturales/AGENTS.md) — Oferentes de espacios culturales, 20 registros, Multi Point
- [`comercio-y-cultura/parques_industriales_y_anexos`](./parques_industriales_y_anexos/AGENTS.md) — Parques industriales y anexos, 5 registros, Polygon
- [`comercio-y-cultura/paseos_comerciales`](./paseos_comerciales/AGENTS.md) — Paseos comerciales, 20 registros, Multi LineString
- [`comercio-y-cultura/puntos_de_interes`](./puntos_de_interes/AGENTS.md) — Puntos de interes cultural, 31 registros, Point
- [`comercio-y-cultura/puntos_venta_simple`](./puntos_venta_simple/AGENTS.md) — Puntos de venta SIMPLE, 21 registros, Point

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
