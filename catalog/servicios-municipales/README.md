# Servicios municipales

Dependencias y trámites municipales, desarrollo social, higiene urbana, recolección de residuos, puntos de reciclado y sanitarios públicos.

15 colecciones. Forma parte del espejo cloud-native de la [IDE Pergamino](../README.md).

## Colecciones

| Colección | Registros | Geometría | Descripción |
|---|--:|---|---|
| [Agencias gubernamentales](./agencias_gubernamentales/) | 10 | Multi Point | Agencias varias de gobierno con jurisdicción provincial y nacional en el territorio del Partido de Pergamino. |
| [Áreas programaticas de Desarrollo Social](./areas_programaticas_desarrollo_social/) | 7 | Polygon | Áreas programáticas de la Secretaría de Desarrollo Social para la Ciudad de Pergamino. |
| [Barrido y limpieza de calles](./barrido_y_limpieza/) | 21 | Polygon | Zonas de barrido y limpieza de calles en la Ciudad de Pergamino. |
| [Bocas pago tasas municipales](./bocas_pago_tasas/) | 86 | Point | Bocas de pago de tasas municipales para todo el Partido de Pergamino. |
| [Centros de Desarrollo Comunitario (CDC)](./centros_de_desarrollo_comunitario/) | 11 | Point | Centros de Desarrollo Comunitario (CDC) del Partido de Pergamino, dependientes de la Secretaría de Desarrollo Social. |
| [Contenedores de basura y reciclaje](./contenedores_basura_reciclaje/) | 3.228 | Point | Contenedores y campanas del programa Actuá en Verde para todo el Partido de Pergamino, actualmente bajo la gestión de... |
| [Dependencias municipales](./dependencias_municipales/) | 202 | Point | Capa de dependencias y oficinas generales de la Municipalidad, para todo el Partido de Pergamino, con o sin atención ... |
| [Dependencias de la Secretaría de Desarrollo Social](./desarrollo_social/) | 8 | Multi Point | Centros dependientes de la Secretaría de Desarrollo Social para todo el Partido de Pergamino. |
| [Desecho de pilas usadas](./desecho_pilas_usadas/) | 2 | Point | Puntos de desecho de pilas usadas en el Partido de Pergamino. |
| [Ecobotellas](./ecobotellas/) | 4 | Point | Capa de lugares donde se pueden depositar las ecobotellas. |
| [Proyectos de infraestructura vial](./proyectos_infraestructura/) | 11.703 | Multi LineString | Proyectos de nfraestructura urbana sobre las vías de circulación: cordón cuneta y pavimentación para el Partido de Pe... |
| [Puntos clickeados](./puntos_clickeados/) | 4 | Point | Puntos educativos Clickeados del Partido de Pergamino pertenecientes a la Secretaría de Desarrollo Social. |
| [Recoleccion de residuos domiciliarios](./recoleccion_residuos_domiciliarios/) | 34 | Polygon | Rutas de recolección de residuos domiciliarios desde 2025, empresa ENTRE para todo el Partido de Pergamino. |
| [Recoleccionde residuos voluminosos](./recoleccion_residuos_voluminosos/) | 4 | Multi Polygon | Zonas de recolección de residuos voluminosos de la Ciudad de Pergamino. |
| [Baños públicos](./sanitarios_publicos/) | 5 | Point | Capa de baños públicos de la Ciudad de Pergamino. |

## Acceso

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

df = duckdb.sql("""
  SELECT * FROM read_parquet(
    'https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/agencias_gubernamentales/publico_agencias_gubernamentales.parquet')
  LIMIT 10
""").df()
```

## Procedencia y licencia

Fuente original: [IDE Pergamino](https://geonode.pergamino.gob.ar/) — Dirección de Sistemas de Información Georreferenciada, Municipalidad de Pergamino.

Licencia: CC BY-SA 4.0, según la declaración del municipio para su IDE. Las colecciones de terceros conservan la atribución a su organismo de origen.
