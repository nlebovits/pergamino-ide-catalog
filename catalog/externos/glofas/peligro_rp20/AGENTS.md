# Guía para agentes — Clases de profundidad de inundación, retorno de 20 años

Profundidad del agua agrupada en cuatro clases para una crecida fluvial con un período de retorno de 20 años, modelada por el JRC (CEMS-GloFAS), recortada al partido de Pergamino sin copiar los datos.

## Qué hay

Cada celda guarda una clase de profundidad en `uint8`; `255` es nodata. El README del JRC define las clases así:

> Water depth classification: 1: <1 m 2: 1–<3 m 3: 3–<10 m 4: >10 m

| Valor | Clase |
|--:|---|
| 1 | Menos de 1 m |
| 2 | De 1 m a menos de 3 m |
| 3 | De 3 m a menos de 10 m |
| 4 | Más de 10 m |

El README de nlebovits/jrc-glofas describe las clases como 0–4 con nombres de peligro (*No hazard*, *Low*…). Esta colección sigue la definición del JRC.

## Leer el recorte

El VRT `https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/peligro_rp20/peligro_rp20.vrt` lee la tesela externa por `/vsicurl/` y devuelve solo la ventana del partido, con nodata fuera del límite.

```bash
gdalinfo -stats /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/peligro_rp20/peligro_rp20.vrt
gdal_translate -of COG \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/peligro_rp20/peligro_rp20.vrt \
  peligro_rp20.tif
```

Con Python:

```python
import rasterio
with rasterio.open("/vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/peligro_rp20/peligro_rp20.vrt") as src:
    banda = src.read(1, masked=True)
```

## Rehacer el recorte

El VRT se genera así; el límite se lee de su URL publicada:

```bash
gdalwarp -of VRT \
  -cutline /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/limites/partido_pergamino/partido_pergamino.parquet \
  -crop_to_cutline \
  /vsicurl/https://data.source.coop/nlebovits/jrc-glofas/hazard-rp20/ID75_S30_W70/ID75_S30_W70_RP20_depth_reclass.tif \
  peligro_rp20.vrt
```

## Notas

- Las estadísticas de la banda en `collection.json` (recurso `recorte`) describen la ventana del partido, no la tesela.
- Los `file:size` y `file:checksum` de los items de nlebovits/jrc-glofas no coinciden con los bytes que sirve el servidor (comprobado con HEAD). Esta colección no los copia.
- Los mapas modelan crecidas de ríos de cuencas grandes. No representan anegamientos por lluvia local. Las inundaciones observadas en el partido están en el grupo `ambiente-y-agro/`.
- NOTE: this dataset is not an official flood hazard map (for details and limitations please refer to related publications).

## Colecciones relacionadas

- Las demás colecciones de `externos/glofas/`: misma tesela, otros períodos de retorno.
- `limites/partido_pergamino`: el límite que define el recorte.
