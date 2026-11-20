# Catastro

Parcelario y jerarquía catastral del Partido de Pergamino, desde la circunscripción hasta la subparcela y la propiedad horizontal, junto con zonificación, edificaciones detectadas sobre imágenes y edificios de interés.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Áreas fiscalizadas construcciones no declaradas](./areas_fiscalizadas_construcciones/) | polígonos | Áreas de las fiscalizaciones en el marco del Proyecto de Detección de Construcciones No Declaradas de la Secretaría de Hacienda para el P... |
| [Catastro chacra](./chacra/) | polígonos | Chacras catastrales del Partido de Pergamino. |
| [Catastro circunscripcion](./circunscripcion/) | polígonos | Capa de Circunscripciones catastrales o Cuarteles del Partido de Pergamino. |
| [Complejos habitacionales](./complejos_habitacionales/) | polígonos | Capa de complejos habitacionales existentes, en construcción y proyectados en el Partido de Pergamino. |
| [Edificaciones detectadas con IA](./edificaciones_automaticas/) | polígonos | Edificaciones detectadas automáticamente para el Partido de Pergamino por google research mediante entrenamiento IA: Open Buildings 2023.... |
| [Edificios en altura](./edificios_en_altura/) | puntos | Edificios de 3 o más pisos en el Partido de Pergamino. |
| [Edificios históricos](./edificios_historicos/) | puntos | Edificios históricos del Partido de Pergamino. |
| [Catastro fraccion](./fraccion/) | polígonos | Fracciones catastrales del Partido de Pergamino. |
| [Catastro manzana](./manzana/) | polígonos | Manzanas catastrales del Partido de Pergamino. |
| [Catastro medida lado de parcela](./medida_lado/) | puntos | Medidas de los macizos (parcelas) del Partido de Pergamino. |
| [Catastro parcela](./parcela/) | polígonos | Capa de parcelas catastrales del Partido de Pergamino. |
| [Catastro ph](./ph/) | puntos | Capa de PH, propiedad horizontal o subparcelas, del Partido de Pergamino. |
| [Catastro quinta](./quinta/) | polígonos | Quintas catastrales del Partido de Pergamino. |
| [Catastro seccion](./seccion/) | polígonos | Capa de secciones catastrales del Partido de Pergamino. |
| [Catastro subparcela](./subparcela/) | polígonos | Subparcelas catastrales del Partido de Pergamino. |
| [Zonificacion](./zonificacion/) | polígonos | Capa de zonificación y uso del suelo para el Partido de Pergamino. |

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **Agencia de Recaudación de la Provincia de Buenos Aires (ARBA)**: Catastro chacra, Catastro circunscripcion, Catastro fraccion, Catastro manzana, Catastro medida lado de parcela, Catastro parcela, Catastro ph, Catastro quinta, Catastro seccion, Catastro subparcela

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/areas_fiscalizadas_construcciones/areas_fiscalizadas_construcciones.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
