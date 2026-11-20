# Servicios municipales

Dependencias y trámites municipales, desarrollo social, higiene urbana, recolección de residuos, puntos de reciclado y sanitarios públicos.

Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Geometría | Descripción |
|---|---|---|
| [Agencias gubernamentales](./agencias_gubernamentales/) | puntos | Agencias varias de gobierno con jurisdicción provincial y nacional en el territorio del Partido de Pergamino. |
| [Áreas programaticas de Desarrollo Social](./areas_programaticas_desarrollo_social/) | polígonos | Áreas programáticas de la Secretaría de Desarrollo Social para la Ciudad de Pergamino. |
| [Barrido y limpieza de calles](./barrido_y_limpieza/) | polígonos | Zonas de barrido y limpieza de calles en la Ciudad de Pergamino. |
| [Bocas pago tasas municipales](./bocas_pago_tasas/) | puntos | Bocas de pago de tasas municipales para todo el Partido de Pergamino. |
| [Centros de Desarrollo Comunitario (CDC)](./centros_de_desarrollo_comunitario/) | puntos | Centros de Desarrollo Comunitario (CDC) del Partido de Pergamino, dependientes de la Secretaría de Desarrollo Social. |
| [Contenedores de basura y reciclaje](./contenedores_basura_reciclaje/) | puntos | Contenedores y campanas del programa Actuá en Verde para todo el Partido de Pergamino, actualmente bajo la gestión de la empresa ENTRE. |
| [Dependencias municipales](./dependencias_municipales/) | puntos | Capa de dependencias y oficinas generales de la Municipalidad, para todo el Partido de Pergamino, con o sin atención al público. |
| [Dependencias de la Secretaría de Desarrollo Social](./desarrollo_social/) | puntos | Centros dependientes de la Secretaría de Desarrollo Social para todo el Partido de Pergamino. |
| [Desecho de pilas usadas](./desecho_pilas_usadas/) | puntos | Puntos de desecho de pilas usadas en el Partido de Pergamino. |
| [Proyectos de infraestructura vial](./proyectos_infraestructura/) | líneas | Proyectos de nfraestructura urbana sobre las vías de circulación: cordón cuneta y pavimentación para el Partido de Pergamino. |
| [Puntos clickeados](./puntos_clickeados/) | puntos | Puntos educativos Clickeados del Partido de Pergamino pertenecientes a la Secretaría de Desarrollo Social. |
| [Recoleccion de residuos domiciliarios](./recoleccion_residuos_domiciliarios/) | polígonos | Rutas de recolección de residuos domiciliarios desde 2025, empresa ENTRE para todo el Partido de Pergamino. |
| [Recoleccionde residuos voluminosos](./recoleccion_residuos_voluminosos/) | polígonos | Zonas de recolección de residuos voluminosos de la Ciudad de Pergamino. |
| [Baños públicos](./sanitarios_publicos/) | puntos | Capa de baños públicos de la Ciudad de Pergamino. |

## Acceso

Cada colección tiene su README con el esquema, y su AGENTS.md con consultas probadas. Por ejemplo:

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/agencias_gubernamentales/agencias_gubernamentales.parquet') LIMIT 10").show()
```

## Procedencia y licencia

Fuente: [GeoNode de la IDE Pergamino](https://geonode.pergamino.gob.ar/), Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
