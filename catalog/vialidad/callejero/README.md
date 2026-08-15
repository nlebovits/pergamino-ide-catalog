# IDE Pergamino - Infraestructura de Datos Espaciales

Catálogo de datos geoespaciales abiertos del Municipio de Pergamino,
Provincia de Buenos Aires, Argentina. Incluye capas de catastro,
infraestructura, transporte, servicios de emergencia, demografía,
agricultura, medio ambiente, planificación urbana e indicadores sociales.

Este catálogo es un espejo cloud-native de la IDE de Pergamino. Los datos
originales son publicados por la Dirección de Sistemas de Información
Georreferenciada (DSIG) de la Municipalidad de Pergamino a través de su
GeoServer y su portal GeoNode. Aquí se republican en formatos optimizados
para consulta directa desde la nube (GeoParquet, PMTiles) sin alterar su
contenido.

![Argentina](https://img.shields.io/badge/Argentina-blue) ![Buenos Aires](https://img.shields.io/badge/Buenos_Aires-blue) ![Pergamino](https://img.shields.io/badge/Pergamino-blue) ![catastro](https://img.shields.io/badge/catastro-blue) ![infraestructura](https://img.shields.io/badge/infraestructura-blue) ![transporte](https://img.shields.io/badge/transporte-blue) ![censo](https://img.shields.io/badge/censo-blue) ![agricultura](https://img.shields.io/badge/agricultura-blue) ![medio ambiente](https://img.shields.io/badge/medio_ambiente-blue) ![planificación urbana](https://img.shields.io/badge/planificaci%C3%B3n_urbana-blue) ![datos abiertos](https://img.shields.io/badge/datos_abiertos-blue) ![GeoParquet](https://img.shields.io/badge/GeoParquet-blue)

## Spatial Coverage

- **Bounding Box**: [-60.94418595, -34.17681178, -60.13879236, -33.55320865]

## Temporal Coverage

- **Start**: open
- **End**: ongoing

## Schema

| Column | Type | Description |
|--------|------|-------------|
| id | int64 |  |
| codigo | int64 |  |
| ancho | int64 |  |
| nombre | string |  |
| nombre_alt | string |  |
| pre_tipo | string |  |
| pre_dir | string |  |
| impar_ini | int64 |  |
| impar_fin | int64 |  |
| par_ini | int64 |  |
| par_fin | int64 |  |
| ruta | string |  |
| clase | string |  |
| sentido | int64 |  |
| barrio | string |  |
| barrido | decimal128(38, 0) |  |
| zona_barri | string |  |
| etiqueta | string |  |
| buffer | int64 |  |
| t_etiq | int64 |  |
| e_num_imp | string |  |
| e_num_par | string |  |
| localidad | string |  |
| long | int64 |  |
| long_km | double |  |
| buff | int64 |  |
| ordenanza | string |  |
| prog_ini | double |  |
| prog_fin | double |  |
| est_medido | string |  |
| cc_empresa | string |  |
| cc_fecha_inicio_obra | string |  |
| cc_fecha_fin_obra | string |  |
| cc_expediente | string |  |
| cc_etapa | double |  |
| pav_empresa | string |  |
| pav_fecha_inicio_obra | string |  |
| pav_fecha_fin_obra | string |  |
| pav_expediente | string |  |
| pav_etapa | double |  |
| velocidad_maxima | int64 |  |
| cpa_impar | string |  |
| cpa_par | string |  |
| restriccion_estacionamiento | string |  |
| observaciones | string |  |
| nombre_corto | string |  |
| ancho_vereda_par | double |  |
| ancho_vereda_impar | double |  |
| tipo_vereda_par | string |  |
| tipo_vereda_impar | string |  |
| cob_cloacas_par | string |  |
| cob_cloacas_impar | string |  |
| cob_agua_par | string |  |
| cob_agua_impar | string |  |
| ancho_nominal | int64 |  |
| ancho_real | double |  |
| ancho_calzada | double |  |
| id_calle | int64 |  |
| lado_ciclovia | string |  |
| transitable | string |  |
| numero_reparto_facturacion | int64 |  |
| nombre_completo | string |  |
| material_calzada | string |  |
| cordon_cuneta | string |  |
| proyecto_infraestructura | string |  |
| arbolado | string |  |
| geometry | binary |  |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> |  |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./publico_callejero.parquet | 921.9 KB | 1220efea0d2a... |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./publico_callejero.parquet")
print(gdf.head())
```

## STAC Metadata

- **root**: `../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://ide.pergamino.gob.ar:8443/geoserver/wfs](https://ide.pergamino.gob.ar:8443/geoserver/wfs)

## Processing Notes

Extraído del servicio WFS de IDE Pergamino
(https://ide.pergamino.gob.ar:8443/geoserver/wfs) y enriquecido con los
metadatos ISO publicados por GeoNode (https://geonode.pergamino.gob.ar).
Convertido a GeoParquet 1.1.0 (WKB, EPSG:4326, columna de cobertura bbox)
y a PMTiles para visualización web. Las simbologías proceden de los SLD
oficiales del GeoServer municipal.


## Citation

Municipalidad de Pergamino (2026). IDE Pergamino - Infraestructura de
Datos Espaciales. Espejo cloud-native publicado por Nissim Lebovits.
Disponible en: https://source.coop/nlebovits/pergamino-ide


## Attribution

Municipalidad de Pergamino - Dirección de Sistemas de Información Georreferenciada (IDE Pergamino), Provincia de Buenos Aires, Argentina

## License

[CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/)

## Contact

Nissim Lebovits <nlebovits@pm.me>

## Known Issues

- La licencia CC BY-SA 4.0 corresponde a la declaración de la Municipalidad
  de Pergamino para su IDE. Varias capas son datos de terceros rehospedados
  por el municipio (INTA, IGN, INDEC, RENABAP, CONICET, INA, BAHRA, Correo
  Argentino, CARTOARBA). Esas capas conservan la atribución a su organismo
  de origen y no se relicencian.
- El municipio advierte que la información "se encuentra en constante
  actualización por parte de las distintas áreas responsables de su
  generación, por lo tanto, podria contener diferencias e inconsistencias
  en relación al objeto o fenómeno representado, tanto espacial como
  temporalmente."
- GeoNode declara `maintenance_frequency: notPlanned` para 111 de 218
  conjuntos de datos. La mayor parte del catálogo no tiene una
  actualización programada.
- La vigencia del contenido no coincide con la fecha de publicación de los
  metadatos. Consultar las columnas `fuente` y `actualizacion` de cada capa.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
