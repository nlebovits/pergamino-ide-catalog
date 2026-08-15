# Guía para agentes — Servicios municipales

Dependencias y trámites municipales, desarrollo social, higiene urbana, recolección de residuos, puntos de reciclado y sanitarios públicos.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`servicios-municipales/agencias_gubernamentales`](./agencias_gubernamentales/AGENTS.md) — Agencias gubernamentales, 10 registros, Multi Point
- [`servicios-municipales/areas_programaticas_desarrollo_social`](./areas_programaticas_desarrollo_social/AGENTS.md) — Áreas programaticas de Desarrollo Social, 7 registros, Polygon
- [`servicios-municipales/barrido_y_limpieza`](./barrido_y_limpieza/AGENTS.md) — Barrido y limpieza de calles, 21 registros, Polygon
- [`servicios-municipales/bocas_pago_tasas`](./bocas_pago_tasas/AGENTS.md) — Bocas pago tasas municipales, 86 registros, Point
- [`servicios-municipales/centros_de_desarrollo_comunitario`](./centros_de_desarrollo_comunitario/AGENTS.md) — Centros de Desarrollo Comunitario (CDC), 11 registros, Point
- [`servicios-municipales/contenedores_basura_reciclaje`](./contenedores_basura_reciclaje/AGENTS.md) — Contenedores de basura y reciclaje, 3.228 registros, Point
- [`servicios-municipales/dependencias_municipales`](./dependencias_municipales/AGENTS.md) — Dependencias municipales, 202 registros, Point
- [`servicios-municipales/desarrollo_social`](./desarrollo_social/AGENTS.md) — Dependencias de la Secretaría de Desarrollo Social, 8 registros, Multi Point
- [`servicios-municipales/desecho_pilas_usadas`](./desecho_pilas_usadas/AGENTS.md) — Desecho de pilas usadas, 2 registros, Point
- [`servicios-municipales/ecobotellas`](./ecobotellas/AGENTS.md) — Ecobotellas, 4 registros, Point
- [`servicios-municipales/proyectos_infraestructura`](./proyectos_infraestructura/AGENTS.md) — Proyectos de infraestructura vial, 11.703 registros, Multi LineString
- [`servicios-municipales/puntos_clickeados`](./puntos_clickeados/AGENTS.md) — Puntos clickeados, 4 registros, Point
- [`servicios-municipales/recoleccion_residuos_domiciliarios`](./recoleccion_residuos_domiciliarios/AGENTS.md) — Recoleccion de residuos domiciliarios, 34 registros, Polygon
- [`servicios-municipales/recoleccion_residuos_voluminosos`](./recoleccion_residuos_voluminosos/AGENTS.md) — Recoleccionde residuos voluminosos, 4 registros, Multi Polygon
- [`servicios-municipales/sanitarios_publicos`](./sanitarios_publicos/AGENTS.md) — Baños públicos, 5 registros, Point

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
