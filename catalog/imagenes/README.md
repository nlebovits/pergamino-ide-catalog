# Imágenes

Imágenes del Partido de Pergamino en Cloud Optimized GeoTIFF (COG), una por
ítem STAC, con una copia de los ítems en stac-geoparquet (`items.parquet`)
para buscarlas sin leer cada JSON.

| Colección | Fuente | Contenido |
|---|---|---|
| [Ortofotos 10 cm 2022](./ortofotos_10cm_2022/README.md) | GeoNode de la Municipalidad de Pergamino | Mosaicos RGB de vuelos con VANT de 2022, uno por ítem, y una vista general de todos en Web Mercator |
| [Sentinel-2: mosaicos trimestrales sin nubes](./sentinel2_trimestral/README.md) | Copernicus Sentinel-2 L2A, vía Element 84 Earth Search | Un mosaico por trimestre calendario desde 2017: la mediana de las observaciones sin nubes, en cuatro bandas a 10 m |

## Procedencia

- **Ortofotos.** Las publica la Dirección de Sistemas de Información
  Georreferenciada (DSIG) de la Municipalidad de Pergamino en
  https://geonode.pergamino.gob.ar/. Este catálogo republica los mosaicos
  sin alterarlos cuando ya cumplen el perfil Portolan, y los recodifica una
  sola vez cuando no. Cada colección explica cuál es cuál.
- **Sentinel-2.** Son productos derivados: este catálogo calcula los
  mosaicos a partir de las escenas L2A que Element 84 publica en
  https://earth-search.aws.element84.com/v1. No son una copia de un producto
  de la ESA.

## Licencias

Las dos colecciones tienen licencias distintas.

- Ortofotos: **CC BY-SA 4.0**, por la declaración de la Municipalidad para su
  IDE (citada en la colección).
- Sentinel-2: el aviso legal de Copernicus sobre el uso de datos Sentinel.
  Quien redistribuya o publique estos mosaicos debe incluir la leyenda
  "Contains modified Copernicus Sentinel data [Year]".

## Formato

- COG con teselas de 512 px, overviews internas y estadísticas por banda
  embebidas en la cabecera. Las áreas sin imagen están enmascaradas (máscara
  interna o nodata), de modo que un cliente no las dibuja en negro.
- La geometría de cada ítem es la huella de los píxeles válidos, no el
  rectángulo de la grilla.
- `items.parquet` en cada colección: una fila por ítem, stac-geoparquet con
  columna de cobertura `bbox`.
