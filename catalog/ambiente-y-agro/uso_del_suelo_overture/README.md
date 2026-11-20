# Uso del suelo (Overture Maps)

Polígonos de uso del suelo de Overture Maps dentro del partido de Pergamino, referenciados sin copiar los datos.

Esta colección es **virtual**: describe datos que publica otro catálogo y no copia sus bytes. El recurso `data` apunta al archivo original con una URL absoluta y lleva el rol `external`. El recorte al partido lo hace un archivo pequeño de este catálogo al leer los datos.

## Contenido

Tipo `land_use` del tema `base` de Overture Maps. El recurso `data` de la colección es el archivo GeoParquet de la publicación vigente que contiene el partido; cubre una región mucho mayor. La publicación usada y la ruta por la que se resolvió están en `pergamino:virtual` dentro de `collection.json`.

## Acceso

El archivo `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/uso_del_suelo_overture/uso_del_suelo_overture.ddb` contiene solo la vista `uso_del_suelo` de esta colección:

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/uso_del_suelo_overture/uso_del_suelo_overture.ddb' AS ov (READ_ONLY);
SELECT * FROM ov.uso_del_suelo LIMIT 10;
```

Para el mapa, las PMTiles de Overture (recurso `visual`) con el estilo `styles/default.json`, que oculta lo que cae fuera del partido.

## Esquema

Nombres y tipos leídos del GeoParquet; descripciones tomadas de overture-portolan, que las copia del esquema de Overture.

| Columna | Tipo | Descripción (Overture) |
|---|---|---|
| `id` | `VARCHAR` | A feature ID. This may be an ID associated with the Global Entity Reference System (GERS) if—and-only-if the feature represents an entity that is part of GERS. |
| `geometry` | `GEOMETRY('OGC:CRS84')` | Classifications of the human use of a section of land. Translates `landuse` from OpenStreetMap tag from OpenStreetMap. |
| `sources` | `STRUCT(property VARCHAR, dataset VARCHAR, license VARCHAR, record_id VARCHAR, update_time VARCHAR, confidence DOUBLE, "between" DOUBLE[], provider VARCHAR, resource VARCHAR, "version" VARCHAR)[]` | The array of source information for the properties of a given feature, with each entry being a source object which lists the property in JSON Pointer notation. All features must have a root level source which is the default source if a specific property's source is not specified. |
| `names` | `STRUCT("primary" VARCHAR, common MAP(VARCHAR, VARCHAR), rules STRUCT(variant VARCHAR, "language" VARCHAR, perspectives STRUCT("mode" VARCHAR, countries VARCHAR[]), "value" VARCHAR, "between" DOUBLE[], side VARCHAR)[])` | Properties defining the names of a feature. The struct carries a primary name, optional common names by language, and optional rules. Quoted from the namesContainer definition in the Overture schema. |
| `level` | `INTEGER` | Z-order of the feature where 0 is visual level |
| `wikidata` | `VARCHAR` | A wikidata ID if available, as found on https://www.wikidata.org/. |
| `source_tags` | `MAP(VARCHAR, VARCHAR)` | Any attributes/tags from the original source data that should be passed through. |
| `subtype` | `VARCHAR` | Broad type of land |
| `class` | `VARCHAR` | Further classification of the land use |
| `elevation` | `INTEGER` | Elevation above sea level (in meters) of the feature. |
| `surface` | `VARCHAR` | Surface material, mostly from the OSM tag, with some normalization. |
| `version` | `INTEGER` | Version number of the feature, incremented in each Overture release where the geometry or attributes of this feature changed. |
| `bbox` | `STRUCT(xmin DOUBLE, xmax DOUBLE, ymin DOUBLE, ymax DOUBLE)` |  |

## Procedencia

- Productor: Overture Maps Foundation (https://overturemaps.org/).
- Guía: https://docs.overturemaps.org/guides/base/
- Esquema: https://docs.overturemaps.org/schema/reference/base/land_use/
- Catálogo del que deriva: overture-portolan (`https://nlebovits.github.io/overture-portolan/base/land_use/collection.json`); si sus URLs no responden, el catálogo STAC de Overture (`https://stac.overturemaps.org/catalog.json`).

## Licencia

**ODbL 1.0**, según el catálogo STAC de Overture (`license: ODbL-1.0`). La página de atribución de Overture dice para este tema: "License for theme: ODbL".

Atribución: https://docs.overturemaps.org/attribution/
