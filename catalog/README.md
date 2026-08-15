# IDE Pergamino — Infraestructura de Datos Espaciales

Espejo cloud-native de la IDE del Municipio de Pergamino, Provincia de Buenos Aires, Argentina.

183 colecciones en 13 grupos temáticos, en GeoParquet y PMTiles, consultables directamente desde la nube.

## Grupos

| Grupo | Colecciones | Contenido |
|---|--:|---|
| [Catastro](./catastro/) | 20 | Parcelario y jerarquía catastral del Partido de Pergamino, desde la circunscripción hasta la subparcela y la propiedad horizontal, junto con zonificación, edificaciones y edificios de interés |
| [Vialidad](./vialidad/) | 18 | Red vial del Partido de Pergamino: callejero, tipo de calzada y vereda, cordón cuneta, señalización, semáforos, alumbrado público y caminos rurales |
| [Transporte](./transporte/) | 19 | Transporte público y movilidad: colectivos urbanos e interurbanos y sus líneas, paradas, ferrocarriles, ciclovías, remises y taxis, aeropuertos y estacionamiento |
| [Servicios sanitarios](./servicios-sanitarios/) | 17 | Cobertura de agua corriente y red cloacal por período de gestión, medidores, pozos y estaciones de bombeo de la Dirección de Obras y Servicios Sanitarios (DOSS), desagües pluviales y zonas de facturación |
| [Energía y conectividad](./energia-y-conectividad/) | 6 | Cobertura de gas natural, circuitos energéticos, red de fibra óptica municipal y federal, y puntos de acceso wifi en espacios verdes |
| [Salud](./salud/) | 7 | Establecimientos y cobertura sanitaria: centros de salud, CAPS, áreas programáticas, desfibriladores de acceso público y guardias |
| [Educación](./educacion/) | 4 | Establecimientos educativos por nivel y tipo de gestión, predios educativos y bibliotecas del Partido de Pergamino |
| [Seguridad](./seguridad/) | 8 | Cuarteles de bomberos, cuadrículas y jurisdicciones policiales, cámaras de seguridad, dependencias, zonas de emergencia y riesgo, y centros de evacuados |
| [Demografía e indicadores sociales](./demografia/) | 12 | Geografía censal y sus indicadores: radios censales INDEC 2010 y 2022, NBI, Índice de Calidad de Vida (CONICET), hacinamiento, razón de sexo, pobreza crónica, calidad de vivienda, población y domicilios por manzana, y barrios populares RENABAP |
| [Ambiente y agro](./ambiente-y-agro/) | 29 | Arbolado urbano, espacios verdes, suelos y cultivos INTA, hidrografía y cuencas, curvas de nivel, isohietas, modelo digital de elevaciones, inundaciones históricas y el proyecto de presa |
| [Límites administrativos](./limites/) | 10 | Límites del partido, barrios, localidades y pueblos, delegaciones, aglomerados urbanos, manchas urbanas históricas desde 1773, circuitos electorales y códigos postales |
| [Servicios municipales](./servicios-municipales/) | 15 | Dependencias y trámites municipales, desarrollo social, higiene urbana, recolección de residuos, puntos de reciclado y sanitarios públicos |
| [Comercio y cultura](./comercio-y-cultura/) | 18 | Actividad comercial, gastronomía y hospedaje, cultura, deporte y entretenimiento, medios de comunicación, entidades profesionales y sindicales, parques industriales y puntos de interés |

## Acceso rápido

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")

# Los barrios de Pergamino
duckdb.sql("""
  SELECT * FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios/publico_barrios.parquet')
""").df()
```

## Procedencia

Los datos son producidos y publicados por la **Dirección de Sistemas de Información Georreferenciada (DSIG)** de la Municipalidad de Pergamino, a través de su GeoServer y su portal GeoNode:

- Geoportal: https://geonode.pergamino.gob.ar/
- Geoservicios: https://ide.pergamino.gob.ar:8443/geoserver/
- Página institucional: https://pergamino.ar/servicios/ide-pergamino/

Este catálogo **no es la fuente original**. Es un espejo optimizado para consulta en la nube. Para el dato autoritativo y actualizado, consultar la IDE de Pergamino.

Varias capas son datos de organismos nacionales y provinciales (INTA, IGN, INDEC, RENABAP, CONICET, INA, ARBA, BAHRA, Correo Argentino) rehospedados por el municipio. Cada colección atribuye a su organismo de origen.

## Licencia

**CC BY-SA 4.0**, según la declaración de la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

La licencia cubre los datos, no la marca institucional del municipio. Las capas de terceros conservan los términos de su organismo de origen.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.

GeoNode declara `maintenance_frequency: notPlanned` para más de la mitad del catálogo. La mayor parte de los datos no tiene una actualización programada.


## Cobertura

Este espejo replica la mayor parte de las capas vectoriales publicadas por la IDE de Pergamino. Un pequeño número no se replica. Para consultas sobre la cobertura, escribir a nlebovits@pm.me.
