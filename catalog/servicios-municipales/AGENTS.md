# Guía para agentes — Servicios municipales

Dependencias y trámites municipales, desarrollo social, higiene urbana, recolección de residuos, puntos de reciclado y sanitarios públicos.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`servicios-municipales/agencias_gubernamentales`](./agencias_gubernamentales/AGENTS.md): Agencias gubernamentales, puntos
- [`servicios-municipales/areas_programaticas_desarrollo_social`](./areas_programaticas_desarrollo_social/AGENTS.md): Áreas programaticas de Desarrollo Social, polígonos
- [`servicios-municipales/barrido_y_limpieza`](./barrido_y_limpieza/AGENTS.md): Barrido y limpieza de calles, polígonos
- [`servicios-municipales/bocas_pago_tasas`](./bocas_pago_tasas/AGENTS.md): Bocas pago tasas municipales, puntos
- [`servicios-municipales/centros_de_desarrollo_comunitario`](./centros_de_desarrollo_comunitario/AGENTS.md): Centros de Desarrollo Comunitario (CDC), puntos
- [`servicios-municipales/contenedores_basura_reciclaje`](./contenedores_basura_reciclaje/AGENTS.md): Contenedores de basura y reciclaje, puntos
- [`servicios-municipales/dependencias_municipales`](./dependencias_municipales/AGENTS.md): Dependencias municipales, puntos
- [`servicios-municipales/desarrollo_social`](./desarrollo_social/AGENTS.md): Dependencias de la Secretaría de Desarrollo Social, puntos
- [`servicios-municipales/desecho_pilas_usadas`](./desecho_pilas_usadas/AGENTS.md): Desecho de pilas usadas, puntos
- [`servicios-municipales/proyectos_infraestructura`](./proyectos_infraestructura/AGENTS.md): Proyectos de infraestructura vial, líneas
- [`servicios-municipales/puntos_clickeados`](./puntos_clickeados/AGENTS.md): Puntos clickeados, puntos
- [`servicios-municipales/recoleccion_residuos_domiciliarios`](./recoleccion_residuos_domiciliarios/AGENTS.md): Recoleccion de residuos domiciliarios, polígonos
- [`servicios-municipales/recoleccion_residuos_voluminosos`](./recoleccion_residuos_voluminosos/AGENTS.md): Recoleccionde residuos voluminosos, polígonos
- [`servicios-municipales/sanitarios_publicos`](./sanitarios_publicos/AGENTS.md): Baños públicos, puntos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
