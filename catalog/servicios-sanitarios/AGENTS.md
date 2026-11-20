# Guía para agentes — Servicios sanitarios

Redes de agua corriente y cloacas (líneas, nodos y cobertura), medidores, pozos y estaciones de bombeo de la Dirección de Obras y Servicios Sanitarios (DOSS), desagües pluviales, sumideros y compuertas, y zonas de facturación.

Cada colección tiene su propio `AGENTS.md` con el esquema, los valores medidos y consultas probadas. Este archivo es el índice del grupo.

## Colecciones

- [`servicios-sanitarios/agua_lineas`](./agua_lineas/AGENTS.md): Red de agua corriente - Líneas, líneas
- [`servicios-sanitarios/agua_nodos`](./agua_nodos/AGENTS.md): Red de agua corriente - Nodos, puntos
- [`servicios-sanitarios/cloacas_lineas`](./cloacas_lineas/AGENTS.md): Red cloacal - Líneas, líneas
- [`servicios-sanitarios/cloacas_nodos`](./cloacas_nodos/AGENTS.md): Red cloacal - Nodos, puntos
- [`servicios-sanitarios/cobertura_agua`](./cobertura_agua/AGENTS.md): Cobertura de red de agua corriente, polígonos
- [`servicios-sanitarios/cobertura_cloacas`](./cobertura_cloacas/AGENTS.md): Cobertura de red cloacal, polígonos
- [`servicios-sanitarios/codigo_reparto_facturacion`](./codigo_reparto_facturacion/AGENTS.md): Códigos de reparto de facturación, líneas
- [`servicios-sanitarios/coeficientes_zonales_doss`](./coeficientes_zonales_doss/AGENTS.md): Coeficientes zonales (DOSS), polígonos
- [`servicios-sanitarios/compuertas_pluviales`](./compuertas_pluviales/AGENTS.md): Compuertas antirretorno en desagües pluviales, puntos
- [`servicios-sanitarios/estaciones_de_bombeo`](./estaciones_de_bombeo/AGENTS.md): Estaciones de bombeo pluvial, puntos
- [`servicios-sanitarios/medidores_agua`](./medidores_agua/AGENTS.md): Medidores de agua, polígonos
- [`servicios-sanitarios/pluviales`](./pluviales/AGENTS.md): Ductos pluviales, líneas
- [`servicios-sanitarios/pozos_agua_doss`](./pozos_agua_doss/AGENTS.md): Pozos de agua DOSS, puntos
- [`servicios-sanitarios/sumideros`](./sumideros/AGENTS.md): Sumideros pluviales, puntos
- [`servicios-sanitarios/zonas_facturacion`](./zonas_facturacion/AGENTS.md): Zonas de facturacion, polígonos

## Notas de acceso

- Los datos están en GeoParquet 1.1, geometría WKB en EPSG:4326, con columna de cobertura `bbox` y orden espacial Hilbert. Un filtro sobre `bbox` lee sólo los grupos de filas que lo cumplen.
- Las capas tienen además PMTiles y un estilo MapLibre en `styles/default.json`, derivado del estilo SLD que publica GeoNode.
- Los nombres de columna están en español, tal como los publica la fuente.
