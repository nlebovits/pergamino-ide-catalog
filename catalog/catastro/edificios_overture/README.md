# Edificios (Overture Maps)

Huellas de edificios de Overture Maps dentro del partido de Pergamino, referenciadas sin copiar los datos.

Esta colección es **virtual**: describe datos que publica otro catálogo y no copia sus bytes. El recurso `data` apunta al archivo original con una URL absoluta y lleva el rol `external`. El recorte al partido lo hace un archivo pequeño de este catálogo al leer los datos.

## Contenido

Tipo `building` del tema `buildings` de Overture Maps. Los items son los archivos GeoParquet de la publicación vigente cuyo rectángulo toca el partido; cada uno cubre una región mucho mayor. La publicación usada y la ruta por la que se resolvió están en `pergamino:virtual` dentro de `collection.json`.

## Acceso

El archivo `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_overture/edificios_overture.ddb` contiene solo la vista `edificios` de esta colección:

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_overture/edificios_overture.ddb' AS ov (READ_ONLY);
SELECT * FROM ov.edificios LIMIT 10;
```

Para el mapa, las PMTiles de Overture (recurso `visual`) con el estilo `styles/default.json`, que oculta lo que cae fuera del partido.

## Esquema

Nombres y tipos leídos del GeoParquet; descripciones tomadas de overture-portolan, que las copia del esquema de Overture.

| Columna | Tipo | Descripción (Overture) |
|---|---|---|
| `id` | `VARCHAR` | A feature ID. This may be an ID associated with the Global Entity Reference System (GERS) if—and-only-if the feature represents an entity that is part of GERS. |
| `names` | `STRUCT("primary" VARCHAR, common MAP(VARCHAR, VARCHAR), rules STRUCT(variant VARCHAR, "language" VARCHAR, perspectives STRUCT("mode" VARCHAR, countries VARCHAR[]), "value" VARCHAR, "between" DOUBLE[], side VARCHAR)[])` | Properties defining the names of a feature. The struct carries a primary name, optional common names by language, and optional rules. Quoted from the namesContainer definition in the Overture schema. |
| `sources` | `STRUCT(property VARCHAR, dataset VARCHAR, license VARCHAR, record_id VARCHAR, update_time VARCHAR, confidence DOUBLE, "between" DOUBLE[], provider VARCHAR, resource VARCHAR, "version" VARCHAR)[]` | The array of source information for the properties of a given feature, with each entry being a source object which lists the property in JSON Pointer notation. All features must have a root level source which is the default source if a specific property's source is not specified. |
| `level` | `INTEGER` | Z-order of the feature where 0 is visual level |
| `height` | `DOUBLE` | Height of the building or part in meters. The height is the distance from the lowest point to the highest point. |
| `min_height` | `DOUBLE` | The height of the bottom part of building in meters. Used if a building or part of building starts above the ground level. |
| `is_underground` | `BOOLEAN` | Whether the entire building or part is completely below ground. This is useful for rendering which typically omits these buildings or styles them differently because they are not visible above ground. This is different than the level column which is used to indicate z-ordering of elements and negative values may be above ground. |
| `num_floors` | `INTEGER` | Number of above-ground floors of the building or part. |
| `num_floors_underground` | `INTEGER` | Number of below-ground floors of the building or part. |
| `min_floor` | `INTEGER` | The "start" floor of this building or part. Indicates that the building or part is "floating" and its bottom-most floor is above ground level, usually because it is part of a larger building in which some parts do reach down to ground level. An example is a building that has an entry road or driveway at ground level into an interior courtyard, where part of the building bridges above the entry road. This property may sometimes be populated when min_height is missing and in these cases can be used as a proxy for min_height. |
| `subtype` | `VARCHAR` | A broad category of the building type/purpose. When the current use of the building does not match the built purpose, the subtype should be set to represent the current use of the building. |
| `class` | `VARCHAR` | Further delineation of the building's built purpose. |
| `facade_color` | `VARCHAR` | The color (name or color triplet) of the facade of a building or building part in hexadecimal |
| `facade_material` | `VARCHAR` | The outer surface material of building facade. |
| `roof_material` | `VARCHAR` | The outermost material of the roof. |
| `roof_shape` | `VARCHAR` | The shape of the roof |
| `roof_direction` | `DOUBLE` | Bearing of the roof ridge line in degrees. |
| `roof_orientation` | `VARCHAR` | Orientation of the roof shape relative to the footprint shape. Either "along" or "across". |
| `roof_color` | `VARCHAR` | The color (name or color triplet) of the roof of a building or building part in hexadecimal |
| `roof_height` | `DOUBLE` | The height of the building roof in meters. This represents the distance from the base of the roof to the highest point of the roof. |
| `geometry` | `GEOMETRY('OGC:CRS84')` | A regular building's geometry is defined as its footprint or roofprint (if traced from aerial/satellite imagery). It MUST be a Polygon or MultiPolygon as defined by the GeoJSON schema. |
| `has_parts` | `BOOLEAN` | Flag indicating whether the building has parts |
| `version` | `INTEGER` | Version number of the feature, incremented in each Overture release where the geometry or attributes of this feature changed. |
| `bbox` | `STRUCT(xmin DOUBLE, xmax DOUBLE, ymin DOUBLE, ymax DOUBLE)` |  |

## Procedencia

- Productor: Overture Maps Foundation (https://overturemaps.org/).
- Guía: https://docs.overturemaps.org/guides/buildings/
- Esquema: https://docs.overturemaps.org/schema/reference/buildings/building/
- Catálogo del que deriva: overture-portolan (`https://nlebovits.github.io/overture-portolan/buildings/building/collection.json`); si sus URLs no responden, el catálogo STAC de Overture (`https://stac.overturemaps.org/catalog.json`).

## Licencia

**ODbL 1.0**, según el catálogo STAC de Overture (`license: ODbL-1.0`). La página de atribución de Overture dice para este tema: "License for theme: ODbL".

Atribución: https://docs.overturemaps.org/attribution/
