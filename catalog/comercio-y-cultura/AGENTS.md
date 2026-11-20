# Guía para agentes — Comercio y cultura

Actividad comercial, gastronomía y hospedaje, cultura, deporte y entretenimiento, medios de comunicación, entidades profesionales y sindicales, parques industriales y puntos de interés.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`comercio-y-cultura/agencias_de_viaje`](./agencias_de_viaje/AGENTS.md): Agencias de viaje, puntos
- [`comercio-y-cultura/asociaciones_sindicales`](./asociaciones_sindicales/AGENTS.md): Asociaciones sindicales, puntos
- [`comercio-y-cultura/colegios_de_profesionales`](./colegios_de_profesionales/AGENTS.md): Colegios profesionales, puntos
- [`comercio-y-cultura/deportivo`](./deportivo/AGENTS.md): Clubes deportivos, puntos
- [`comercio-y-cultura/entretenimiento`](./entretenimiento/AGENTS.md): Entretenimiento, puntos
- [`comercio-y-cultura/estaciones_servicio`](./estaciones_servicio/AGENTS.md): Estaciones de servicio, puntos
- [`comercio-y-cultura/extraccion_dinero`](./extraccion_dinero/AGENTS.md): Extraccion de dinero, puntos
- [`comercio-y-cultura/gastronomia`](./gastronomia/AGENTS.md): Oferta gastronómica, puntos
- [`comercio-y-cultura/gomerias`](./gomerias/AGENTS.md): Gomerias, puntos
- [`comercio-y-cultura/hospedajes`](./hospedajes/AGENTS.md): Hoteles y hospedajes, puntos
- [`comercio-y-cultura/lugares_overture`](./lugares_overture/AGENTS.md): Lugares de interés (Overture Maps), vectores externos
- [`comercio-y-cultura/medios_de_comunicacion`](./medios_de_comunicacion/AGENTS.md): Medios de comunicacion, puntos
- [`comercio-y-cultura/museos_y_espacios_culturales`](./museos_y_espacios_culturales/AGENTS.md): Museos y espacios culturales, puntos
- [`comercio-y-cultura/oferentes_espacios_culturales`](./oferentes_espacios_culturales/AGENTS.md): Oferentes de espacios culturales, puntos
- [`comercio-y-cultura/parques_industriales_y_anexos`](./parques_industriales_y_anexos/AGENTS.md): Parques industriales y anexos, polígonos
- [`comercio-y-cultura/paseos_comerciales`](./paseos_comerciales/AGENTS.md): Paseos comerciales, líneas
- [`comercio-y-cultura/puntos_de_interes`](./puntos_de_interes/AGENTS.md): Puntos de interes cultural, puntos
- [`comercio-y-cultura/puntos_venta_simple`](./puntos_venta_simple/AGENTS.md): Puntos de venta SIMPLE, puntos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
- Las colecciones `comercio-y-cultura/lugares_overture` son virtuales: no tienen un GeoParquet propio. Su `AGENTS.md` dice cómo leer el recorte (un VRT de GDAL o un archivo de vistas DuckDB), y la consulta lee los datos del servidor del productor.
