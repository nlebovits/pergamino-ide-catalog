# Clases de profundidad de inundación, retorno de 20 años

Profundidad del agua agrupada en cuatro clases para una crecida fluvial con un período de retorno de 20 años, modelada por el JRC (CEMS-GloFAS), recortada al partido de Pergamino sin copiar los datos.

Esta colección es **virtual**: describe datos que publica otro catálogo y no copia sus bytes. El recurso `data` apunta al archivo original con una URL absoluta y lleva el rol `external`. El recorte al partido lo hace un archivo pequeño de este catálogo al leer los datos.

## Contenido

Cada celda guarda una clase de profundidad en `uint8`; `255` es nodata. El README del JRC define las clases así:

> Water depth classification: 1: <1 m 2: 1–<3 m 3: 3–<10 m 4: >10 m

| Valor | Clase |
|--:|---|
| 1 | Menos de 1 m |
| 2 | De 1 m a menos de 3 m |
| 3 | De 3 m a menos de 10 m |
| 4 | Más de 10 m |

El README de nlebovits/jrc-glofas describe las clases como 0–4 con nombres de peligro (*No hazard*, *Low*…). Esta colección sigue la definición del JRC.

Resolución de 3 segundos de arco (unos 90 m), EPSG:4326. La tesela `ID75_S30_W70` del JRC cubre 10° × 10°; el partido entero cae dentro de ella.

## Acceso

- Recorte (VRT de GDAL): `https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/peligro_rp20/peligro_rp20.vrt`
- Tesela completa (COG externo): `https://data.source.coop/nlebovits/jrc-glofas/hazard-rp20/ID75_S30_W70/ID75_S30_W70_RP20_depth_reclass.tif`

El VRT es texto: indica a GDAL qué ventana de la tesela leer y con qué límite recortarla. Abrirlo descarga solo esa ventana. Para guardar una copia local:

```bash
gdal_translate -of COG \
  /vsicurl/https://data.source.coop/nlebovits/pergamino-ide/externos/glofas/peligro_rp20/peligro_rp20.vrt \
  peligro_rp20.tif
```

En QGIS: *Capa → Añadir capa ráster*, origen *Protocolo HTTP(S)*, con la URL del VRT.

## Procedencia

- Productor: European Commission, Joint Research Centre (JRC), Copernicus Emergency Management Service, *Global river flood hazard maps* (https://doi.org/10.2905/JRC.VD32YWG).
- Descarga original: https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/
- Conversión a COG: catálogo Portolan nlebovits/jrc-glofas en Source Cooperative (https://source.coop/nlebovits/jrc-glofas), colección `hazard-rp20`.
- Este catálogo: solo el VRT del recorte, el estilo y la vista previa.

## Advertencias del productor

> NOTE: this dataset is not an official flood hazard map (for details and limitations please refer to related publications).

> Very high water depths may result from limitations in the hydraulic modelling approach, in combination with the spatial resolution, or from artificial sinks in the DEM.

## Licencia

El JRC da dos declaraciones distintas para este conjunto de datos, y esta colección no elige entre ellas (`license: other`, con un enlace a cada texto). El archivo `copyright.txt` de la descarga dice:

> Any copyright and/or sui generis right on the dataset is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence [2]. Reuse is allowed provided appropriate credit is given and any changes are indicated.

El `README.txt` de la misma descarga, y el registro del Catálogo de Datos del JRC, dicen:

> A02. License information, restrictions on use: Open Data Commons Open Database License v1.0

La colección de nlebovits/jrc-glofas declara `proprietary`, un valor que STAC 1.1 desaconseja y que Portolan no admite; no se copia aquí.

Cita recomendada por el JRC (README.txt, A01):

> Baugh, Calum; Colonese, Juan; D'Angelo, Claudia; Francesco, Dottori; Neal, Jeffrey; Prudhomme; Christe; Salamon, Peter (2024): Modelled flood inundation for different return period scenarios at the global scale. European Commission, Joint Research Centre (JRC)
