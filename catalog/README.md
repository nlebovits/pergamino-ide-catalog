# IDE Pergamino — Infraestructura de Datos Espaciales

Espejo cloud-native de la IDE del Municipio de Pergamino, Provincia de Buenos Aires, Argentina. Las capas vectoriales que publica el municipio en GeoNode están aquí en GeoParquet y PMTiles, consultables directamente desde la nube.

## Grupos

| Grupo | Contenido |
|---|---|
| [Catastro](./catastro/) | Parcelario y jerarquía catastral del Partido de Pergamino, desde la circunscripción hasta la subparcela y la propiedad horizontal, junto con zonificación, edificaciones detectadas sobre imágenes y edificios de interés |
| [Vialidad](./vialidad/) | Red vial del Partido de Pergamino: callejero, material de calzada, cordón cuneta, rampas de acceso, señalización, semáforos, reductores de velocidad, alumbrado público, puntos fijos y red de nivelación del IGN, y caminos rurales |
| [Transporte](./transporte/) | Transporte público y movilidad: colectivos urbanos e interurbanos, paradas, puntos de carga SUBE, ferrocarriles, circuitos de cicloturismo y la Vuelta al Partido, remises y taxis, aeropuertos y estacionamiento |
| [Servicios sanitarios](./servicios-sanitarios/) | Redes de agua corriente y cloacas (líneas, nodos y cobertura), medidores, pozos y estaciones de bombeo de la Dirección de Obras y Servicios Sanitarios (DOSS), desagües pluviales, sumideros y compuertas, y zonas de facturación |
| [Energía y conectividad](./energia-y-conectividad/) | Cobertura de gas natural, circuitos energéticos, nodos y tramos de la Red Federal de Fibra Óptica, y puntos de acceso wifi en espacios verdes |
| [Salud](./salud/) | Establecimientos y cobertura sanitaria: centros de salud, CAPS, áreas programáticas, desfibriladores de acceso público y guardias |
| [Educación](./educacion/) | Establecimientos educativos, por nivel y por tipo de gestión, predios educativos y bibliotecas del Partido de Pergamino |
| [Seguridad](./seguridad/) | Cuarteles de bomberos, dependencias de seguridad, zonas de seguridad, zonas de emergencia y riesgo, y centros de evacuados |
| [Demografía e indicadores sociales](./demografia/) | Geografía censal y sus indicadores: radios censales INDEC 2010 y 2022, NBI, Índice de Calidad de Vida (CONICET), hacinamiento, razón de sexo, pobreza crónica, calidad de vivienda, densidad de población por censo, población por manzana por mapeo dasimétrico, y barrios populares RENABAP |
| [Ambiente y agro](./ambiente-y-agro/) | Arbolado urbano, espacios verdes, suelos y cultivos INTA, hidrografía y cuencas, curvas de nivel, isohietas, carbono en el suelo, inundaciones históricas y el proyecto de presa |
| [Límites administrativos](./limites/) | Límites del partido, barrios y pueblos, localidades y sus áreas, delegaciones, aglomerados urbanos, manchas urbanas históricas desde 1773, circuitos electorales y códigos postales |
| [Servicios municipales](./servicios-municipales/) | Dependencias y trámites municipales, desarrollo social, higiene urbana, recolección de residuos, puntos de reciclado y sanitarios públicos |
| [Comercio y cultura](./comercio-y-cultura/) | Actividad comercial, gastronomía y hospedaje, cultura, deporte y entretenimiento, medios de comunicación, entidades profesionales y sindicales, parques industriales y puntos de interés |
| [Imágenes](./imagenes/) | Imágenes del Partido de Pergamino: las ortofotos de 10 cm de 2022 que publica la Municipalidad en su GeoNode y la fecha más despejada de cada trimestre de Sentinel-2 desde 2017, como referencias a los COG de Earth Search |
| [Datos de otros catálogos](./externos/) | Colecciones virtuales: la parte de conjuntos de datos publicados en otros catálogos Portolan que cae dentro del partido de Pergamino, sin copiar los datos |

## Acceso rápido

```python
import duckdb

con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
con.sql("SELECT nombre FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet')").show()
```

## Procedencia

Los datos vectoriales son producidos y publicados por la **Dirección de Sistemas de Información Georreferenciada (DSIG)** de la Municipalidad de Pergamino, en su portal GeoNode:

- Geoportal: https://geonode.pergamino.gob.ar/
- Geoservicios: https://geonode.pergamino.gob.ar/geoserver/ows
- Página institucional: https://pergamino.ar/servicios/ide-pergamino/

Este catálogo **no es la fuente original**. Es un espejo optimizado para consulta en la nube. Para el dato autoritativo y actualizado, consultar la IDE de Pergamino. Un proceso semanal compara cada capa con GeoNode y publica una versión nueva cuando los datos cambian.

Varias capas son datos de organismos nacionales y provinciales rehospedados por el municipio. Cada colección atribuye a su organismo de origen.

## Licencia

**CC BY-SA 4.0**, según la declaración de la Municipalidad de Pergamino para su IDE:

> Los datos dispuestos en nuestra Infraestructura de Datos Espaciales estan licenciados mediante Creative Commons 4.0 BY-SA, lo cual permite utilizar, compartir y adaptar este material siempre que reconozca atribución y permita la misma licencia en sus derivados.

La licencia cubre los datos, no la marca institucional del municipio. Las capas de terceros conservan los términos de su organismo de origen.

## Advertencia del publicador

> La información contenida en la IDE se encuentra en constante actualización por parte de las distintas áreas responsables de su generación, por lo tanto, podria contener diferencias e inconsistencias en relación al objeto o fenómeno representado, tanto espacial como temporalmente.

## Cobertura

Este espejo replica la mayor parte de las capas vectoriales que GeoNode publica. Un pequeño número no se replica. Para consultas sobre la cobertura, escribir a nlebovits@pm.me.
