# Guía para agentes — Imágenes

Imágenes del Partido de Pergamino: ortofotos municipales de 2022 y mosaicos
trimestrales de Sentinel-2. Cada colección tiene su propio `AGENTS.md` con
el esquema de los ítems, recetas de acceso probadas y advertencias. Este
archivo es el índice del grupo.

## Colecciones

- [`imagenes/ortofotos_10cm_2022`](./ortofotos_10cm_2022/AGENTS.md) — Ortofotos 10 cm 2022, RGB de 8 bits en EPSG:4326, un ítem por mosaico de GeoNode, más `overview.tif` en EPSG:3857.
- [`imagenes/sentinel2_trimestral`](./sentinel2_trimestral/AGENTS.md) — Sentinel-2, mediana trimestral sin nubes, cuatro bandas uint16 a 10 m en EPSG:32720, un ítem por trimestre.

## Notas de acceso

- Los píxeles están en el recurso `data` de cada ítem, no en la colección.
  Para encontrar el ítem que hace falta, leer `items.parquet` de la
  colección (una lectura) en lugar de recorrer los JSON de los ítems.
- En `items.parquet` los `href` de los recursos son relativos a la carpeta
  del ítem (`./<id>.tif`, `./data.tif`). La URL pública de un COG es
  `https://data.source.coop/nlebovits/pergamino-ide/imagenes/<colección>/<id>/<archivo>`.
- Leer con la máscara activada (`masked=True` en rasterio y rioxarray). Sin
  ella, el área sin imagen de las ortofotos aparece como píxeles de valor 0.
- Las dos colecciones usan sistemas de referencia distintos. Para cruzarlas
  entre sí o con las capas vectoriales del catálogo (EPSG:4326),
  reproyectar primero.
- Licencias distintas: las ortofotos son CC BY-SA 4.0; Sentinel-2 exige la
  leyenda "Contains modified Copernicus Sentinel data [Year]" al
  redistribuir.
