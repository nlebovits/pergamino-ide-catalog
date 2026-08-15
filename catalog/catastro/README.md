# Catastro

Parcelario y jerarquía catastral del Partido de Pergamino, desde la circunscripción hasta la subparcela y la propiedad horizontal, junto con zonificación, edificaciones y edificios de interés.

20 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Áreas fiscalizadas construcciones no declaradas](./areas_fiscalizadas_construcciones/) | 33 | Polygon | Áreas de las fiscalizaciones en el marco del Proyecto de Detección de Construcciones No Declaradas de la Secretaría d... |
| [Catastro chacra](./chacra/) | 285 | Multi Polygon | Chacras catastrales del Partido de Pergamino. |
| [Catastro circunscripcion](./circunscripcion/) | 23 | Multi Polygon | Capa de Circunscripciones catastrales o Cuarteles del Partido de Pergamino. |
| [Catastro fraccion](./fraccion/) | 181 | Multi Polygon | Fracciones catastrales del Partido de Pergamino. |
| [Catastro manzana](./manzana/) | 2.564 | Multi Polygon | Manzanas catastrales del Partido de Pergamino. |
| [Catastro medida lado de parcela](./medida_lado/) | 196.722 | Point | Medidas de los macizos (parcelas) del Partido de Pergamino. |
| [Catastro parcela](./parcela/) | 55.134 | Polygon | Capa de parcelas catastrales del Partido de Pergamino. |
| [Catastro ph](./ph/) | 9.864 | Point | Capa de PH, propiedad horizontal o subparcelas, del Partido de Pergamino. |
| [Catastro quinta](./quinta/) | 136 | Multi Polygon | Quintas catastrales del Partido de Pergamino. |
| [Catastro seccion](./seccion/) | 71 | Multi Polygon | Capa de secciones catastrales del Partido de Pergamino. |
| [Catastro subparcela](./subparcela/) | 487 | Polygon | Subparcelas catastrales del Partido de Pergamino. |
| [Complejos habitacionales](./complejos_habitacionales/) | 108 | Polygon | Capa de complejos habitacionales existentes, en construcción y proyectados en el Partido de Pergamino. |
| [Edificaciones detectadas PA](./edificaciones_pa/) | 4.921 | Polygon | Edificaciones en planta alta detectadas mediante imágenes de alta resolución. |
| [Edificaciones detectadas PB](./edificaciones_pb/) | 48.168 | Polygon | Edificaciones en planta baja detectadas mediante imágenes de alta resolución. |
| [Edificios en altura](./edificios_en_altura/) | 457 | Multi Point | Edificios de 3 o más pisos en el Partido de Pergamino. |
| [Edificios históricos](./edificios_historicos/) | 73 | Multi Point | Edificios históricos del Partido de Pergamino. |
| [Estado parcela](./estado_parcela/) | 55.134 | Polygon | Estado de edificación de parcela. 0 es baldío, 1 es edificado. |
| [Parcelario](./parcelario/) | 55.134 | Polygon | Capa parcelaria general del Partido de Pergamino, con la mayor cantidad de atributos disponibles por parcela. Es la c... |
| [Parcelario contralor](./parcelario_contralor/) | 55.134 | Polygon | Capa parcelario utilizada por el área de Contralor Urbano. Para obtener más datos de las parcelas recurrir a la capa ... |
| [Zonificacion](./zonificacion/) | 230 | Multi Polygon | Capa de zonificación y uso del suelo para el Partido de Pergamino. |

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/catastro/areas_fiscalizadas_construcciones/publico_areas_fiscalizadas_construcciones.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
