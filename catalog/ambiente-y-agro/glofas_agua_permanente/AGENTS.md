# Guía para agentes — Cuerpos de agua permanentes (GloFAS)

Máscara de los cuerpos de agua permanentes que el JRC usa para completar los mapas de peligro de GloFAS, recortada al partido de Pergamino sin copiar los datos.

## Qué hay

Cada celda vale `1` donde hay agua permanente; `255` es nodata. El JRC usa esta máscara para completar los mapas de peligro, de modo que esas celdas no cuentan como inundación.

## Leer el recorte

El VRT `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_agua_permanente/glofas_agua_permanente.vrt` lee la tesela externa por `/vsicurl/` y devuelve solo la ventana del partido, con nodata fuera del límite.

```bash
gdalinfo -stats /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_agua_permanente/glofas_agua_permanente.vrt
gdal_translate -of COG \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_agua_permanente/glofas_agua_permanente.vrt \
  glofas_agua_permanente.tif
```

Con Python:

```python
import rasterio
with rasterio.open("/vsicurl/https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/glofas_agua_permanente/glofas_agua_permanente.vrt") as src:
    banda = src.read(1, masked=True)
```

## Rehacer el recorte

El VRT se genera así; el límite se lee de su URL publicada:

```bash
gdalwarp -of VRT \
  -cutline /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/limites/partido_pergamino/partido_pergamino.parquet \
  -crop_to_cutline \
  /vsicurl/https://data.source.coop/nlebovits/jrc-glofas/permanent-water/ID75_S30_W70/ID75_S30_W70_permanent_water.tif \
  glofas_agua_permanente.vrt
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
