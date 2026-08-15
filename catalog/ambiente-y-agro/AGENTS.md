# Guía para agentes — Ambiente y agro

Arbolado urbano, espacios verdes, suelos y cultivos INTA, hidrografía y cuencas, curvas de nivel, isohietas, modelo digital de elevaciones, inundaciones históricas y el proyecto de presa. Incluye datos de INTA, IGN e INA rehospedados por el municipio.

Cada colección tiene su propio `AGENTS.md` con esquema, claves de unión y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`ambiente-y-agro/arbolado`](./arbolado/AGENTS.md) — Arbolado (2013), 43.525 registros, Multi Point
- [`ambiente-y-agro/banados`](./banados/AGENTS.md) — Bañados, 10 registros, Point
- [`ambiente-y-agro/cobertura_arbolado_urbano`](./cobertura_arbolado_urbano/AGENTS.md) — Cobertura del arbolado urbano, 45.825 registros, LineString
- [`ambiente-y-agro/cuencas_arroyo_pergamino`](./cuencas_arroyo_pergamino/AGENTS.md) — Cuenca del Arroyo Pergamino, 32 registros, Polygon
- [`ambiente-y-agro/cuencas_hidricas_norte_ba`](./cuencas_hidricas_norte_ba/AGENTS.md) — Cuencas hídricas del Norte de la Provincia de Buenos Aires, 10 registros, Multi Polygon
- [`ambiente-y-agro/cursos_de_agua`](./cursos_de_agua/AGENTS.md) — Cursos de agua, 437 registros, Multi LineString
- [`ambiente-y-agro/curvas_de_nivel_iatasa_abs`](./curvas_de_nivel_iatasa_abs/AGENTS.md) — Curvas de nivel (IATASA-ABS), 349 registros, LineString
- [`ambiente-y-agro/curvas_nivel_cuenca`](./curvas_nivel_cuenca/AGENTS.md) — Curvas de nivel cuenca Arroyo Pergamino, 848 registros, LineString
- [`ambiente-y-agro/curvas_nivel_ign`](./curvas_nivel_ign/AGENTS.md) — Curvas de nivel (IGN), 202 registros, LineString
- [`ambiente-y-agro/espacios_verdes`](./espacios_verdes/AGENTS.md) — Espacios verdes públicos, 492 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2018_2019`](./inta_mnc_2018_2019/AGENTS.md) — Mapa nacional de cultivos INTA 2018-2019, 47.114 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2019_invierno`](./inta_mnc_2019_invierno/AGENTS.md) — Mapa nacional de cultivos INTA invierno 2019, 19.729 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2020_invierno`](./inta_mnc_2020_invierno/AGENTS.md) — Mapa nacional de cultivos INTA invierno 2020, 20.897 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2020_verano`](./inta_mnc_2020_verano/AGENTS.md) — Mapa nacional de cultivos INTA verano 2020, 28.724 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2021_invierno`](./inta_mnc_2021_invierno/AGENTS.md) — Mapa nacional de cultivos INTA invierno 2021, 26.177 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2021_verano`](./inta_mnc_2021_verano/AGENTS.md) — Mapa nacional de cultivos INTA verano 2021, 19.896 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2022_invierno`](./inta_mnc_2022_invierno/AGENTS.md) — Mapa nacional de cultivos INTA invierno 2022, 28.132 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2022_verano`](./inta_mnc_2022_verano/AGENTS.md) — Mapa nacional de cultivos INTA verano 2022, 33.194 registros, Polygon
- [`ambiente-y-agro/inta_mnc_2023_verano`](./inta_mnc_2023_verano/AGENTS.md) — Mapa nacional de cultivos INTA verano 2023, 38.025 registros, Polygon
- [`ambiente-y-agro/inundacion_1995`](./inundacion_1995/AGENTS.md) — Inundacion de 1995, 26 registros, Polygon
- [`ambiente-y-agro/inundacion_2016`](./inundacion_2016/AGENTS.md) — Inundacion de 2016, 7 registros, Multi Polygon
- [`ambiente-y-agro/isohietas_precipitaciones_medias_anuales_pergamino_geointa`](./isohietas_precipitaciones_medias_anuales_pergamino_geointa/AGENTS.md) — Isohietas de precipitaciones medias anuales (inta), 88 registros, LineString
- [`ambiente-y-agro/limpieza_mantenimiento_espacios_verdes`](./limpieza_mantenimiento_espacios_verdes/AGENTS.md) — Limpieza y mantenimiento de espacios verdes, 94 registros, Multi Polygon
- [`ambiente-y-agro/luminarias_espacios_verdes`](./luminarias_espacios_verdes/AGENTS.md) — Luminarias en espacios verdes, 1.346 registros, Multi Point
- [`ambiente-y-agro/proyecto_presa`](./proyecto_presa/AGENTS.md) — Proyecto presa Pergamino, 1 registros, LineString
- [`ambiente-y-agro/proyecto_presa_area_inundable`](./proyecto_presa_area_inundable/AGENTS.md) — Proyecto presa Pergamino - Área inundable, 1 registros, Polygon
- [`ambiente-y-agro/puntos_de_nivel_iatasa_abs`](./puntos_de_nivel_iatasa_abs/AGENTS.md) — Puntos de nivel (IATASA-ABS), 6.003 registros, Multi Point
- [`ambiente-y-agro/riego_por_pivote_central`](./riego_por_pivote_central/AGENTS.md) — Riego por pivote central, 87 registros, Multi Polygon
- [`ambiente-y-agro/suelos_pergamino_50mil`](./suelos_pergamino_50mil/AGENTS.md) — Carta de suelos Pergamino 1:50.000, 95 registros, Multi Polygon

## Notas de acceso

- Todos los datos están en GeoParquet 1.1.0, WKB, EPSG:4326, con columna de cobertura `bbox` y ordenamiento espacial Hilbert. Los filtros espaciales aprovechan las estadísticas por grupo de filas.
- Las capas tienen además PMTiles para visualización web y un estilo MapLibre en `styles/default.json` derivado del SLD oficial del GeoServer municipal.
- Los nombres de columna están en español y varias capas traen `fuente` y `actualizacion` a nivel de registro, que es la señal de vigencia más confiable.
