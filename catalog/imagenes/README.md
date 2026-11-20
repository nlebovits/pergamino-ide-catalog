# Imágenes

Imágenes del Partido de Pergamino en Cloud Optimized GeoTIFF (COG), una
fecha o un mosaico por ítem STAC, con una copia de los ítems en
stac-geoparquet (`items.parquet`) para buscarlas sin leer cada JSON.

| Colección | Fuente | Contenido |
|---|---|---|
| [Ortofotos 10 cm 2022](./ortofotos_10cm_2022/README.md) | GeoNode de la Municipalidad de Pergamino | Mosaicos RGB de vuelos con VANT de 2022, uno por ítem, y una vista general de todos en Web Mercator |
| [Sentinel-2: la fecha más despejada de cada trimestre](./sentinel2_trimestral/README.md) | Copernicus Sentinel-2 L2A, vía Element 84 Earth Search | Una fecha por trimestre calendario desde 2017: el día que cubre todo el partido con la menor nubosidad, como referencias a los COG de color verdadero de Earth Search |

## Procedencia

- **Ortofotos.** Las publica la Dirección de Sistemas de Información
  Georreferenciada (DSIG) de la Municipalidad de Pergamino en
  https://geonode.pergamino.gob.ar/. Este catálogo republica los mosaicos
  sin alterarlos cuando ya cumplen el perfil Portolan, y los recodifica una
  sola vez cuando no. Cada colección explica cuál es cuál.
- **Sentinel-2.** Este catálogo elige una fecha por trimestre entre las
  escenas L2A que Element 84 publica en
  https://earth-search.aws.element84.com/v1, y apunta a sus COG sin
  copiarlos. Solo las miniaturas se generan aquí.

## Licencias

Las dos colecciones tienen licencias distintas.

- Ortofotos: **CC BY-SA 4.0**, por la declaración de la Municipalidad para su
  IDE (citada en la colección).
- Sentinel-2: el aviso legal de Copernicus sobre el uso de datos Sentinel.
  Quien recorte, combine o modifique estas escenas y publique el resultado
  debe incluir la leyenda "Contains modified Copernicus Sentinel data
  [Year]".

## Formato

- Ortofotos: COG con teselas de 512 px, overviews internas y
  estadísticas por banda embebidas en la cabecera. Las áreas sin imagen
  están enmascaradas (máscara interna), de modo que un cliente no las
  dibuja en negro. La geometría de cada ítem es la huella de los píxeles
  válidos, no el rectángulo de la grilla.
- Sentinel-2: los COG de Earth Search, con overviews internas y nodata 0.
  La geometría de cada ítem es el partido intersecado con las huellas de
  las escenas.
- `items.parquet` en cada colección: una fila por ítem, stac-geoparquet con
  columna de cobertura `bbox`.
