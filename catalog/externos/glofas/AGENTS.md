# Guía para agentes — Peligro de inundación fluvial (JRC GloFAS)

Cada colección es una capa del JRC recortada al partido por un VRT de GDAL. El VRT es la forma de leerla; el COG externo es la tesela de 10° × 10° completa.

## Colecciones

- [`externos/glofas/profundidad_rp10`](./profundidad_rp10/AGENTS.md) — Profundidad de inundación, retorno de 10 años
- [`externos/glofas/profundidad_rp20`](./profundidad_rp20/AGENTS.md) — Profundidad de inundación, retorno de 20 años
- [`externos/glofas/profundidad_rp50`](./profundidad_rp50/AGENTS.md) — Profundidad de inundación, retorno de 50 años
- [`externos/glofas/profundidad_rp75`](./profundidad_rp75/AGENTS.md) — Profundidad de inundación, retorno de 75 años
- [`externos/glofas/profundidad_rp100`](./profundidad_rp100/AGENTS.md) — Profundidad de inundación, retorno de 100 años
- [`externos/glofas/profundidad_rp200`](./profundidad_rp200/AGENTS.md) — Profundidad de inundación, retorno de 200 años
- [`externos/glofas/profundidad_rp500`](./profundidad_rp500/AGENTS.md) — Profundidad de inundación, retorno de 500 años
- [`externos/glofas/peligro_rp10`](./peligro_rp10/AGENTS.md) — Clases de profundidad de inundación, retorno de 10 años
- [`externos/glofas/peligro_rp20`](./peligro_rp20/AGENTS.md) — Clases de profundidad de inundación, retorno de 20 años
- [`externos/glofas/peligro_rp50`](./peligro_rp50/AGENTS.md) — Clases de profundidad de inundación, retorno de 50 años
- [`externos/glofas/peligro_rp75`](./peligro_rp75/AGENTS.md) — Clases de profundidad de inundación, retorno de 75 años
- [`externos/glofas/peligro_rp100`](./peligro_rp100/AGENTS.md) — Clases de profundidad de inundación, retorno de 100 años
- [`externos/glofas/peligro_rp200`](./peligro_rp200/AGENTS.md) — Clases de profundidad de inundación, retorno de 200 años
- [`externos/glofas/peligro_rp500`](./peligro_rp500/AGENTS.md) — Clases de profundidad de inundación, retorno de 500 años
- [`externos/glofas/agua_permanente`](./agua_permanente/AGENTS.md) — Cuerpos de agua permanentes (GloFAS)

## Comparar períodos de retorno

Todos los VRT comparten la grilla, así que se pueden apilar sin remuestrear:

```bash
gdalbuildvrt -separate profundidad.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp10/profundidad_rp10.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp20/profundidad_rp20.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp50/profundidad_rp50.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp75/profundidad_rp75.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp100/profundidad_rp100.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp200/profundidad_rp200.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp500/profundidad_rp500.vrt
```
