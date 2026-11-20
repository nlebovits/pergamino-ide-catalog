# Guía para agentes — Ambiente y agro

Arbolado urbano, espacios verdes, suelos y cultivos INTA, hidrografía y cuencas, curvas de nivel, isohietas, carbono en el suelo, inundaciones históricas y el proyecto de presa. Incluye datos de INTA, IGN e INA rehospedados por el municipio.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`ambiente-y-agro/arbolado`](./arbolado/AGENTS.md): Arbolado (2013), puntos
- [`ambiente-y-agro/banados`](./banados/AGENTS.md): Bañados, polígonos
- [`ambiente-y-agro/cobertura_arbolado_urbano`](./cobertura_arbolado_urbano/AGENTS.md): Cobertura del arbolado urbano, polígonos
- [`ambiente-y-agro/cuencas_arroyo_pergamino`](./cuencas_arroyo_pergamino/AGENTS.md): Cuenca del Arroyo Pergamino, polígonos
- [`ambiente-y-agro/cuencas_hidricas_norte_ba`](./cuencas_hidricas_norte_ba/AGENTS.md): Cuencas hídricas del Norte de la Provincia de Buenos Aires, polígonos
- [`ambiente-y-agro/cursos_de_agua`](./cursos_de_agua/AGENTS.md): Cursos de agua, líneas
- [`ambiente-y-agro/curvas_de_nivel_iatasa_abs`](./curvas_de_nivel_iatasa_abs/AGENTS.md): Curvas de nivel (IATASA-ABS), líneas
- [`ambiente-y-agro/curvas_nivel_cuenca`](./curvas_nivel_cuenca/AGENTS.md): Curvas de nivel cuenca Arroyo Pergamino, líneas
- [`ambiente-y-agro/curvas_nivel_ign`](./curvas_nivel_ign/AGENTS.md): Curvas de nivel (IGN), líneas
- [`ambiente-y-agro/espacios_verdes`](./espacios_verdes/AGENTS.md): Espacios verdes públicos, polígonos
- [`ambiente-y-agro/inta_carbono_suelo_2015_2022`](./inta_carbono_suelo_2015_2022/AGENTS.md): Almacenamiento de Carbono en los suelos 2015-2022, polígonos
- [`ambiente-y-agro/inta_mnc_2018_2019`](./inta_mnc_2018_2019/AGENTS.md): Mapa nacional de cultivos INTA 2018-2019, polígonos
- [`ambiente-y-agro/inta_mnc_2019_invierno`](./inta_mnc_2019_invierno/AGENTS.md): Mapa nacional de cultivos INTA invierno 2019, polígonos
- [`ambiente-y-agro/inta_mnc_2020_invierno`](./inta_mnc_2020_invierno/AGENTS.md): Mapa nacional de cultivos INTA invierno 2020, polígonos
- [`ambiente-y-agro/inta_mnc_2020_verano`](./inta_mnc_2020_verano/AGENTS.md): Mapa nacional de cultivos INTA verano 2020, polígonos
- [`ambiente-y-agro/inta_mnc_2021_invierno`](./inta_mnc_2021_invierno/AGENTS.md): Mapa nacional de cultivos INTA invierno 2021, polígonos
- [`ambiente-y-agro/inta_mnc_2021_verano`](./inta_mnc_2021_verano/AGENTS.md): Mapa nacional de cultivos INTA verano 2021, polígonos
- [`ambiente-y-agro/inta_mnc_2022_invierno`](./inta_mnc_2022_invierno/AGENTS.md): Mapa nacional de cultivos INTA invierno 2022, polígonos
- [`ambiente-y-agro/inta_mnc_2022_verano`](./inta_mnc_2022_verano/AGENTS.md): Mapa nacional de cultivos INTA verano 2022, polígonos
- [`ambiente-y-agro/inta_mnc_2023_verano`](./inta_mnc_2023_verano/AGENTS.md): Mapa nacional de cultivos INTA verano 2023, polígonos
- [`ambiente-y-agro/inundacion_1995`](./inundacion_1995/AGENTS.md): Inundacion de 1995, polígonos
- [`ambiente-y-agro/inundacion_2016`](./inundacion_2016/AGENTS.md): Inundacion de 2016, polígonos
- [`ambiente-y-agro/isohietas_precipitaciones_medias_anuales_pergamino_geointa`](./isohietas_precipitaciones_medias_anuales_pergamino_geointa/AGENTS.md): Isohietas de precipitaciones medias anuales (inta), líneas
- [`ambiente-y-agro/limpieza_mantenimiento_espacios_verdes`](./limpieza_mantenimiento_espacios_verdes/AGENTS.md): Limpieza y mantenimiento de espacios verdes, polígonos
- [`ambiente-y-agro/luminarias_espacios_verdes`](./luminarias_espacios_verdes/AGENTS.md): Luminarias en espacios verdes, puntos
- [`ambiente-y-agro/proyecto_presa`](./proyecto_presa/AGENTS.md): Proyecto presa Pergamino, líneas
- [`ambiente-y-agro/proyecto_presa_area_inundable`](./proyecto_presa_area_inundable/AGENTS.md): Proyecto presa Pergamino - Área inundable, polígonos
- [`ambiente-y-agro/puntos_de_nivel_iatasa_abs`](./puntos_de_nivel_iatasa_abs/AGENTS.md): Puntos de nivel (IATASA-ABS), puntos
- [`ambiente-y-agro/riego_por_pivote_central`](./riego_por_pivote_central/AGENTS.md): Riego por pivote central, polígonos
- [`ambiente-y-agro/suelos_pergamino_50mil`](./suelos_pergamino_50mil/AGENTS.md): Carta de suelos Pergamino 1:50.000, polígonos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
