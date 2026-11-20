# Guía para agentes — Imágenes

Imágenes del Partido de Pergamino: ortofotos municipales de 2022 y la fecha
más despejada de cada trimestre de Sentinel-2. Cada colección tiene su propio `AGENTS.md` con
el esquema de los ítems, recetas de acceso probadas y advertencias. Este
archivo es el índice del grupo.

## Colecciones

- [`imagenes/ortofotos_10cm_2022`](./ortofotos_10cm_2022/AGENTS.md) — Ortofotos 10 cm 2022, RGB de 8 bits en EPSG:4326, un ítem por mosaico de GeoNode, más `overview.tif` en EPSG:3857.
- [`imagenes/sentinel2_trimestral`](./sentinel2_trimestral/AGENTS.md) — Sentinel-2, la fecha más despejada de cada trimestre, un ítem por trimestre con referencias a los `TCI.tif` de Earth Search (RGB de 8 bits a 10 m, UTM 20S y 21S), más `escenas.parquet` con todas las escenas desde 2017.

## Notas de acceso

- Los píxeles están en los recursos de cada ítem, no en la colección.
  Para encontrar el ítem que hace falta, leer `items.parquet` de la
  colección (una lectura) en lugar de recorrer los JSON de los ítems.
- En las ortofotos, los `href` de `items.parquet` son relativos a la
  carpeta del ítem (`./<id>.tif`). La URL pública de un COG es
  `https://data.source.coop/nlebovits/pergamino-ide/imagenes/<colección>/<id>/<archivo>`.
  En Sentinel-2 los `href` son URL absolutas de Earth Search.
- Leer con la máscara activada (`masked=True` en rasterio y rioxarray). Sin
  ella, el área sin imagen de las ortofotos aparece como píxeles de valor 0.
- Las dos colecciones usan sistemas de referencia distintos. Para cruzarlas
  entre sí o con las capas vectoriales del catálogo (EPSG:4326),
  reproyectar primero.
- Licencias distintas: las ortofotos son CC BY-SA 4.0; Sentinel-2 exige la
  leyenda "Contains modified Copernicus Sentinel data [Year]" al
  publicar datos modificados.
