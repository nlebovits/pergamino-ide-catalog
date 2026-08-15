# Guía para agentes — Vialidad

Red vial del Partido de Pergamino: callejero, tipo de calzada y vereda, cordón cuneta, señalización, semáforos, alumbrado público y caminos rurales.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`vialidad/alcantarillas_vialidad`](./alcantarillas_vialidad/AGENTS.md) — Alcantarillas en rutas, 74 registros, Point
- [`vialidad/altura_de_calle`](./altura_de_calle/AGENTS.md) — Altura de calle, 11.703 registros, Multi LineString
- [`vialidad/callejero`](./callejero/AGENTS.md) — Callejero, 11.703 registros, Multi LineString
- [`vialidad/callejero_listado`](./callejero_listado/AGENTS.md) — Listado de calles, 1.098 registros, -
- [`vialidad/camaras_y_radares`](./camaras_y_radares/AGENTS.md) — Cámaras y radares de tránsito, 20 registros, Point
- [`vialidad/carteles_viales`](./carteles_viales/AGENTS.md) — Carteles viales, 3.002 registros, Point
- [`vialidad/comisiones_caminos_rurales`](./comisiones_caminos_rurales/AGENTS.md) — Comisiones caminos rurales, 29 registros, Polygon
- [`vialidad/cordon_cuneta`](./cordon_cuneta/AGENTS.md) — Cordon cuneta, 11.703 registros, Multi LineString
- [`vialidad/luminarias`](./luminarias/AGENTS.md) — Luminarias en vía pública, 25.152 registros, Multi Point
- [`vialidad/material_de_calzada`](./material_de_calzada/AGENTS.md) — Material de calzada, 11.703 registros, Multi LineString
- [`vialidad/progresivas_rutas`](./progresivas_rutas/AGENTS.md) — Progresivas y mojones de rutas, 340 registros, Point
- [`vialidad/puntos_fijos`](./puntos_fijos/AGENTS.md) — Puntos fijos de nivelación IGN, 76 registros, Point
- [`vialidad/rampas_acceso_veredas`](./rampas_acceso_veredas/AGENTS.md) — Rampas de acceso a veredas, 1.653 registros, Point
- [`vialidad/recambio_led`](./recambio_led/AGENTS.md) — Recambio led, 25.152 registros, Multi Point
- [`vialidad/reductores_de_velocidad`](./reductores_de_velocidad/AGENTS.md) — Reductores de velocidad, 217 registros, Multi Point
- [`vialidad/semaforos`](./semaforos/AGENTS.md) — Semaforos, 294 registros, Point
- [`vialidad/tipo_de_vereda`](./tipo_de_vereda/AGENTS.md) — Tipo de vereda, 11.703 registros, Multi LineString
- [`vialidad/tranqueras_rurales`](./tranqueras_rurales/AGENTS.md) — Tranqueras Geolocalizadas, 171 registros, Point

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
