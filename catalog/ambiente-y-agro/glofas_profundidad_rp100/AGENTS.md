# Guía para agentes — Profundidad de inundación, retorno de 100 años

Profundidad del agua en metros para una crecida fluvial con un período de retorno de 100 años, modelada por el JRC (CEMS-GloFAS) a 3 segundos de arco, recortada al partido de Pergamino sin copiar los datos.

## Qué hay

Cada celda guarda la profundidad del agua en metros, en `float32`. Las celdas sin inundación y las que quedan fuera del partido valen `-9999` (nodata).

## Leer el recorte

El VRT `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp100/glofas_profundidad_rp100.vrt` lee la tesela externa por `/vsicurl/` y devuelve solo la ventana del partido, con nodata fuera del límite.

```bash
gdalinfo -stats /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp100/glofas_profundidad_rp100.vrt
gdal_translate -of COG \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp100/glofas_profundidad_rp100.vrt \
  glofas_profundidad_rp100.tif
```

Con Python:

```python
import rasterio
with rasterio.open("/vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp100/glofas_profundidad_rp100.vrt") as src:
    banda = src.read(1, masked=True)
```

## Rehacer el recorte

El VRT se genera así; el límite se lee de su URL publicada:

```bash
gdalwarp -of VRT \
  -cutline /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/limites/partido_pergamino/partido_pergamino.parquet \
  -crop_to_cutline \
  /vsicurl/https://data.source.coop/nlebovits/jrc-glofas/depth-rp100/ID75_S30_W70/ID75_S30_W70_RP100_depth.tif \
  glofas_profundidad_rp100.vrt
```

## Notas

- Las estadísticas de la banda en `collection.json` (recurso `recorte`) describen la ventana del partido, no la tesela.
- Los `file:size` y `file:checksum` de los items de nlebovits/jrc-glofas no coinciden con los bytes que sirve el servidor (comprobado con HEAD). Esta colección no los copia.
- Los mapas modelan crecidas de ríos de cuencas grandes. No representan anegamientos por lluvia local. Las inundaciones observadas en el partido son `ambiente-y-agro/inundacion_1995` y `ambiente-y-agro/inundacion_2016`, en este mismo grupo.
- NOTE: this dataset is not an official flood hazard map (for details and limitations please refer to related publications).

## Comparar períodos de retorno

Todos los VRT de GloFAS comparten la grilla, así que se pueden apilar sin remuestrear. Las siete profundidades:

```bash
gdalbuildvrt -separate profundidad.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp10/glofas_profundidad_rp10.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp20/glofas_profundidad_rp20.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp50/glofas_profundidad_rp50.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp75/glofas_profundidad_rp75.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp100/glofas_profundidad_rp100.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp200/glofas_profundidad_rp200.vrt \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_profundidad_rp500/glofas_profundidad_rp500.vrt
```

## Colecciones relacionadas

- Las demás colecciones `ambiente-y-agro/glofas_*`: misma tesela, otros períodos de retorno.
- `limites/partido_pergamino`: el límite que define el recorte.
