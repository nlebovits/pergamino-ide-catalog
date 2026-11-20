# Vialidad

Red vial del Partido de Pergamino: callejero, material de calzada, cordón cuneta, rampas de acceso, señalización, semáforos, reductores de velocidad, alumbrado público, puntos fijos y red de nivelación del IGN, y caminos rurales.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Alcantarillas en rutas](./alcantarillas_vialidad/) | puntos | Alcantarillas en rutas provinciales y nacionales para todo el Partido de Pergamino. |
| [Callejero](./callejero/) | líneas | No abstract provided |
| [Cámaras y radares de tránsito](./camaras_y_radares/) | puntos | Cámaras, radares y tótems para el control y multas por exceso de velocidad, violación de sendas peatonales y cruce de semáforos en rojo p... |
| [Carteles viales](./carteles_viales/) | puntos | Carteles y señales de tránsito en el Partido de Pergamino. |
| [Comisiones caminos rurales](./comisiones_caminos_rurales/) | polígonos | Comisiones de caminos rurales del Partido de Pergamino determinados para el cobro de tasa vial. |
| [Cordon cuneta](./cordon_cuneta/) | líneas | Describe tipo de cordón cuneta para las calles del Partido de Pergamino en ambas márgenes: ambas, par, impar, ninguno y no_corresponde. |
| [Luminarias en vía pública](./luminarias/) | puntos | Luminarias en vía pública del Partido de Pergamino. |
| [Material de calzada](./material_de_calzada/) | líneas | Describe el tipo de material mayoritario para las calles del Partido de Pergamino: adoquinado, asfalto, hormigón, escoriado, tierra y met... |
| [Progresivas y mojones de rutas](./progresivas_rutas/) | puntos | Progresivas en mojones de rutas nacionales y provinciales localizadas en el Partido de Pergamino. |
| [Puntos fijos de nivelación IGN](./puntos_fijos/) | puntos | Puntos fijos de nivelación del IGN para la Ciudad de Pergamino. |
| [Rampas de acceso discapacidad motriz](./rampas_acceso_veredas/) | puntos | Rampas de acceso a veredas para personas con dificultades motrices o carritos de bebés/infantes para todo el Partido de Pergamino. |
| [Red de nivelación de precisión del IGN](./red_nivelacion_ign_precision/) | puntos | Red de Nivelación de Precisión del Instituto Geográfico Nacional recortado al Partido de Pergamino. |
| [Reductores de velocidad](./reductores_de_velocidad/) | puntos | Reductores de velocidad y bumpers, también conocidos como lomas o lomos de burro localizados dentro del Partido de Pergamino. |
| [Segmentos de transporte (Overture Maps)](./segmentos_overture/) | vectores externos | Segmentos de calles, caminos, vías férreas y vías navegables de Overture Maps dentro del partido de Pergamino, referenciados sin copiar l... |
| [Semaforos](./semaforos/) | puntos | Capa de semáforos del Partido de Pergamino. |

## Datos de otros catálogos

Estas colecciones no vienen de GeoNode. Describen la parte de un conjunto de datos publicado en otro catálogo que cae dentro del partido, sin copiar sus bytes: el recurso `data` apunta al archivo original y un recurso `recorte` lo recorta al leer. Cada una conserva la licencia de su productor; ver su README.

- **Overture Maps Foundation**: `segmentos_overture`

## Datos de terceros

Estas colecciones son datos producidos por otros organismos y rehospedados por la Municipalidad de Pergamino. La atribución corresponde al organismo de origen.

- **Instituto Geográfico Nacional (IGN)**: Puntos fijos de nivelación IGN, Red de nivelación de precisión del IGN

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/alcantarillas_vialidad.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.

Las colecciones de *Datos de otros catálogos* no vienen de GeoNode ni llevan la licencia del municipio: cada una declara la de su productor.
