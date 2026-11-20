# Lugares de interés (Overture Maps)

Lugares de interés (comercios, servicios, instituciones) de Overture Maps dentro del partido de Pergamino, referenciados sin copiar los datos.

Esta colección es **virtual**: describe datos que publica otro catálogo y no copia sus bytes. El recurso `data` apunta al archivo original con una URL absoluta y lleva el rol `external`. El recorte al partido lo hace un archivo pequeño de este catálogo al leer los datos.

## Contenido

Tipo `place` del tema `places` de Overture Maps. El recurso `data` de la colección es el archivo GeoParquet de la publicación vigente que contiene el partido; cubre una región mucho mayor. La publicación usada y la ruta por la que se resolvió están en `pergamino:virtual` dentro de `collection.json`.

## Acceso

El archivo `https://data.source.coop/nlebovits/pergamino-ide/externos/overture/pergamino_overture.ddb` contiene solo vistas, una por colección de `externos/overture/`. La vista de esta colección es `lugares`:

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://data.source.coop/nlebovits/pergamino-ide/externos/overture/pergamino_overture.ddb' AS ov (READ_ONLY);
SELECT * FROM ov.lugares LIMIT 10;
```

Para el mapa, las PMTiles de Overture (recurso `visual`) con el estilo `styles/default.json`, que oculta lo que cae fuera del partido.

## Esquema

Nombres y tipos leídos del GeoParquet; descripciones tomadas de overture-portolan, que las copia del esquema de Overture.

| Columna | Tipo | Descripción (Overture) |
|---|---|---|
| `id` | `VARCHAR` | A feature ID. This may be an ID associated with the Global Entity Reference System (GERS) if—and-only-if the feature represents an entity that is part of GERS. |
| `geometry` | `GEOMETRY('OGC:CRS84')` | Place's geometry which MUST be a Point as defined by GeoJSON schema. |
| `confidence` | `DOUBLE` | The confidence of the existence of the place. It's a number between 0 and 1. 0 means that we're sure that the place doesn't exist (anymore). 1 means that we're sure that the place exists. If there's no value for the confidence, it means that we don't have any confidence information. Places with operating_status set to 'closed' will have a confidence score of 0 |
| `websites` | `VARCHAR[]` | The websites of the place. |
| `emails` | `VARCHAR[]` | The email addresses of the place. |
| `socials` | `VARCHAR[]` | The social media URLs of the place. |
| `phones` | `VARCHAR[]` | The phone numbers of the place. |
| `brand` | `STRUCT(wikidata VARCHAR, "names" STRUCT("primary" VARCHAR, common MAP(VARCHAR, VARCHAR), rules STRUCT(variant VARCHAR, "language" VARCHAR, perspectives STRUCT("mode" VARCHAR, countries VARCHAR[]), "value" VARCHAR, "between" DOUBLE[], side VARCHAR)[]))` | The brand of the place. A location with multiple brands is modeled as multiple separate places, each with its own brand. |
| `addresses` | `STRUCT(freeform VARCHAR, locality VARCHAR, postcode VARCHAR, region VARCHAR, country VARCHAR)[]` | The addresses of the place. |
| `names` | `STRUCT("primary" VARCHAR, common MAP(VARCHAR, VARCHAR), rules STRUCT(variant VARCHAR, "language" VARCHAR, perspectives STRUCT("mode" VARCHAR, countries VARCHAR[]), "value" VARCHAR, "between" DOUBLE[], side VARCHAR)[])` | Properties defining the names of a feature. The struct carries a primary name, optional common names by language, and optional rules. Quoted from the namesContainer definition in the Overture schema. |
| `sources` | `STRUCT(property VARCHAR, dataset VARCHAR, license VARCHAR, record_id VARCHAR, update_time VARCHAR, confidence DOUBLE, "between" DOUBLE[], provider VARCHAR, "resource" VARCHAR, "version" VARCHAR)[]` | The array of source information for the properties of a given feature, with each entry being a source object which lists the property in JSON Pointer notation. All features must have a root level source which is the default source if a specific property's source is not specified. |
| `operating_status` | `VARCHAR` | Indicates the operating status of a place, can be one of ["open", "permanently_closed", "temporarily_closed"]. This is not an indication of 'opening hours' or that the place is open/closed at the current time-of-day or day-of-week. |
| `basic_category` | `VARCHAR` | The basic level category of a place. At present this is a mapping of the categories.primary entry to a new, simplified name. This mapping can be 1:1 or M:1 from the existing categories.primary entry. If the entry is currently empty in categories.primary, this entry will be empty. This type of categorization is a cognitive science model that is relevant for taxonomy and ontology development that shows the most broadest and general category name that is most often found in the middle of a general-to-specific hierarchy, with generalization proceeding upward and specialization proceeding downward. The full list of basic level categories is available at https://docs.overturemaps.org/guides/places/ |
| `taxonomy` | `STRUCT("primary" VARCHAR, hierarchy VARCHAR[], alternates VARCHAR[])` | A new representation of the place's category within the Overture taxonomy. Provides the primary classification, full hierarchy path, and alternate categories. |
| `version` | `INTEGER` | Version number of the feature, incremented in each Overture release where the geometry or attributes of this feature changed. |
| `bbox` | `STRUCT(xmin DOUBLE, xmax DOUBLE, ymin DOUBLE, ymax DOUBLE)` |  |

## Procedencia

- Productor: Overture Maps Foundation (https://overturemaps.org/).
- Guía: https://docs.overturemaps.org/guides/places/
- Esquema: https://docs.overturemaps.org/schema/reference/places/place/
- Catálogo del que deriva: overture-portolan (`https://nlebovits.github.io/overture-portolan/places/place/collection.json`); si sus URLs no responden, el catálogo STAC de Overture (`https://stac.overturemaps.org/catalog.json`).

## Licencia

Overture no declara una licencia única para este tema: su catálogo STAC usa `license: other` y enlaza la página de atribución, donde cada fuente tiene la suya. Esta colección copia esa declaración.

Atribución: https://docs.overturemaps.org/attribution/
