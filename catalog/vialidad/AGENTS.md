# Guía para agentes — Vialidad

Red vial del Partido de Pergamino: callejero, material de calzada, cordón cuneta, rampas de acceso, señalización, semáforos, reductores de velocidad, alumbrado público, puntos fijos y red de nivelación del IGN, y caminos rurales.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`vialidad/alcantarillas_vialidad`](./alcantarillas_vialidad/AGENTS.md): Alcantarillas en rutas, puntos
- [`vialidad/callejero`](./callejero/AGENTS.md): Callejero, líneas
- [`vialidad/camaras_y_radares`](./camaras_y_radares/AGENTS.md): Cámaras y radares de tránsito, puntos
- [`vialidad/carteles_viales`](./carteles_viales/AGENTS.md): Carteles viales, puntos
- [`vialidad/comisiones_caminos_rurales`](./comisiones_caminos_rurales/AGENTS.md): Comisiones caminos rurales, polígonos
- [`vialidad/cordon_cuneta`](./cordon_cuneta/AGENTS.md): Cordon cuneta, líneas
- [`vialidad/luminarias`](./luminarias/AGENTS.md): Luminarias en vía pública, puntos
- [`vialidad/material_de_calzada`](./material_de_calzada/AGENTS.md): Material de calzada, líneas
- [`vialidad/progresivas_rutas`](./progresivas_rutas/AGENTS.md): Progresivas y mojones de rutas, puntos
- [`vialidad/puntos_fijos`](./puntos_fijos/AGENTS.md): Puntos fijos de nivelación IGN, puntos
- [`vialidad/rampas_acceso_veredas`](./rampas_acceso_veredas/AGENTS.md): Rampas de acceso discapacidad motriz, puntos
- [`vialidad/red_nivelacion_ign_precision`](./red_nivelacion_ign_precision/AGENTS.md): Red de nivelación de precisión del IGN, puntos
- [`vialidad/reductores_de_velocidad`](./reductores_de_velocidad/AGENTS.md): Reductores de velocidad, puntos
- [`vialidad/semaforos`](./semaforos/AGENTS.md): Semaforos, puntos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
