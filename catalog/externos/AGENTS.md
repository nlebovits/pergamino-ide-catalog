# Guía para agentes — Datos de otros catálogos

Colecciones virtuales: la parte de conjuntos de datos publicados en otros catálogos Portolan que cae dentro del partido de Pergamino, sin copiar los datos. Peligro de inundación fluvial del JRC (GloFAS) y edificios, lugares, transporte y uso del suelo de Overture Maps.

- [`externos/glofas/`](./glofas/AGENTS.md) — ráster; leer el VRT `recorte` con GDAL.
- [`externos/overture/`](./overture/AGENTS.md) — vectores; `ATTACH` del archivo de vistas DuckDB.

## Antes de consultar

- Los datos no están en este catálogo. Cada consulta los lee del servidor del otro catálogo; si ese servidor falla, la consulta falla.
- El recorte usa el límite oficial del partido publicado en `https://data.source.coop/nlebovits/pergamino-ide/limites/partido_pergamino/partido_pergamino.parquet` (colección `limites/partido_pergamino`).
- Atribuir al productor (JRC, Overture Maps Foundation), no al municipio.
