# Guía para agentes — Profundidad de inundación, retorno de 20 años

Profundidad del agua en metros para una crecida fluvial con un período de retorno de 20 años, modelada por el JRC (CEMS-GloFAS) a 3 segundos de arco, recortada al partido de Pergamino sin copiar los datos.

## Qué hay

Cada celda guarda la profundidad del agua en metros, en `float32`. Las celdas sin inundación y las que quedan fuera del partido valen `-9999` (nodata).

## Leer el recorte

El VRT `https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp20/profundidad_rp20.vrt` lee la tesela externa por `/vsicurl/` y devuelve solo la ventana del partido, con nodata fuera del límite.

```bash
gdalinfo -stats /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp20/profundidad_rp20.vrt
gdal_translate -of COG \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp20/profundidad_rp20.vrt \
  profundidad_rp20.tif
```

Con Python:

```python
import rasterio
with rasterio.open("/vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/profundidad_rp20/profundidad_rp20.vrt") as src:
    banda = src.read(1, masked=True)
```

## Rehacer el recorte

El VRT se genera así; el límite se lee de su URL publicada:

```bash
gdalwarp -of VRT \
  -cutline /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/limites/partido_pergamino/partido_pergamino.parquet \
  -crop_to_cutline \
  /vsicurl/https://data.source.coop/nlebovits/jrc-glofas/depth-rp20/ID75_S30_W70/ID75_S30_W70_RP20_depth.tif \
  profundidad_rp20.vrt
```

## Notas

- Las estadísticas de la banda en `collection.json` (recurso `recorte`) describen la ventana del partido, no la tesela.
- Los `file:size` y `file:checksum` de los items de nlebovits/jrc-glofas no coinciden con los bytes que sirve el servidor (comprobado con HEAD). Esta colección no los copia.
- Los mapas modelan crecidas de ríos de cuencas grandes. No representan anegamientos por lluvia local. Las inundaciones observadas en el partido están en el grupo `ambiente-y-agro/`.
- NOTE: this dataset is not an official flood hazard map (for details and limitations please refer to related publications).

## Colecciones relacionadas

- Las demás colecciones de `externos/glofas/`: misma tesela, otros períodos de retorno.
- `limites/partido_pergamino`: el límite que define el recorte.
