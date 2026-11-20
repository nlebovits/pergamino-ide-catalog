# Segmentos de transporte (Overture Maps)

Segmentos de calles, caminos, vías férreas y vías navegables de Overture Maps dentro del partido de Pergamino, referenciados sin copiar los datos.

Esta colección es **virtual**: describe datos que publica otro catálogo y no copia sus bytes. El recurso `data` apunta al archivo original con una URL absoluta y lleva el rol `external`. El recorte al partido lo hace un archivo pequeño de este catálogo al leer los datos.

## Contenido

Tipo `segment` del tema `transportation` de Overture Maps. Los items son los archivos GeoParquet de la publicación vigente cuyo rectángulo toca el partido; cada uno cubre una región mucho mayor. La publicación usada y la ruta por la que se resolvió están en `pergamino:virtual` dentro de `collection.json`.

## Acceso

El archivo `https://data.source.coop/nlebovits/pergamino-ide/externos/overture/pergamino_overture.ddb` contiene solo vistas, una por colección de `externos/overture/`. La vista de esta colección es `segmentos`:

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://data.source.coop/nlebovits/pergamino-ide/externos/overture/pergamino_overture.ddb' AS ov (READ_ONLY);
SELECT * FROM ov.segmentos LIMIT 10;
```

Para el mapa, las PMTiles de Overture (recurso `visual`) con el estilo `styles/default.json`, que oculta lo que cae fuera del partido.

## Esquema

Nombres y tipos leídos del GeoParquet; descripciones tomadas de overture-portolan, que las copia del esquema de Overture.

| Columna | Tipo | Descripción (Overture) |
|---|---|---|
| `id` | `VARCHAR` | A feature ID. This may be an ID associated with the Global Entity Reference System (GERS) if—and-only-if the feature represents an entity that is part of GERS. |
| `names` | `STRUCT("primary" VARCHAR, common MAP(VARCHAR, VARCHAR), rules STRUCT(variant VARCHAR, "language" VARCHAR, perspectives STRUCT("mode" VARCHAR, countries VARCHAR[]), "value" VARCHAR, "between" DOUBLE[], side VARCHAR)[])` | Properties defining the names of a feature. The struct carries a primary name, optional common names by language, and optional rules. Quoted from the namesContainer definition in the Overture schema. |
| `subtype` | `VARCHAR` | Broad category of transportation segment. |
| `class` | `VARCHAR` | Captures the kind of rail segment. |
| `subclass` | `VARCHAR` | Refines expected usage of the segment, must not overlap. |
| `subclass_rules` | `STRUCT("value" VARCHAR, "between" DOUBLE[])[]` | Set of subclasses scoped along segment |
| `connectors` | `STRUCT(connector_id VARCHAR, "at" DOUBLE)[]` | List of connectors which this segment is physically connected to and their relative location. Each connector is a possible routing decision point, meaning it defines a place along the segment in which there is possibility to transition to other segments which share the same connector. |
| `road_surface` | `STRUCT("value" VARCHAR, "between" DOUBLE[])[]` | Physical surface of the road. May either be specified as a single global value for the segment, or as an array of surface rules. |
| `road_flags` | `STRUCT("values" VARCHAR[], "between" DOUBLE[])[]` | Set of boolean attributes applicable to roads. May be specified either as a single flag array of flag values, or as an array of flag rules. |
| `rail_flags` | `STRUCT("values" VARCHAR[], "between" DOUBLE[])[]` | Set of boolean attributes applicable to railways. May be specified either as a single flag array of flag values, or as an array of flag rules. |
| `width_rules` | `STRUCT("value" DOUBLE, "between" DOUBLE[])[]` | Edge-to-edge width of the road modeled by this segment, in meters. Examples: (1) If this segment models a carriageway without sidewalk, this value represents the edge-to-edge width of the carriageway, inclusive of any shoulder. (2) If this segment models a sidewalk by itself, this value represents the edge-to-edge width of the sidewalk. (3) If this segment models a combined sidewalk and carriageway, this value represents the edge-to-edge width inclusive of sidewalk. |
| `level_rules` | `STRUCT("value" INTEGER, "between" DOUBLE[])[]` | Defines the Z-order, i.e. stacking order, of the road segment. |
| `access_restrictions` | `STRUCT(access_type VARCHAR, "when" STRUCT(during VARCHAR, heading VARCHAR, "using" VARCHAR[], recognized VARCHAR[], "mode" VARCHAR[], vehicle STRUCT(dimension VARCHAR, comparison VARCHAR, "value" DOUBLE, unit VARCHAR)[]), "between" DOUBLE[])[]` | Rules governing access to this road segment |
| `speed_limits` | `STRUCT(min_speed STRUCT("value" INTEGER, unit VARCHAR), max_speed STRUCT("value" INTEGER, unit VARCHAR), is_max_speed_variable BOOLEAN, "when" STRUCT(during VARCHAR, heading VARCHAR, "using" VARCHAR[], recognized VARCHAR[], "mode" VARCHAR[], vehicle STRUCT(dimension VARCHAR, comparison VARCHAR, "value" DOUBLE, unit VARCHAR)[]), "between" DOUBLE[])[]` | Rules governing speed on this road segment |
| `prohibited_transitions` | `STRUCT("sequence" STRUCT(connector_id VARCHAR, segment_id VARCHAR)[], final_heading VARCHAR, "when" STRUCT(heading VARCHAR, during VARCHAR, "using" VARCHAR[], recognized VARCHAR[], "mode" VARCHAR[], vehicle STRUCT(dimension VARCHAR, comparison VARCHAR, "value" DOUBLE, unit VARCHAR)[]), "between" DOUBLE[])[]` | Rules preventing transitions from this segment to another segment. |
| `routes` | `STRUCT("name" VARCHAR, network VARCHAR, "ref" VARCHAR, symbol VARCHAR, wikidata VARCHAR, "between" DOUBLE[])[]` | Routes this segment belongs to |
| `destinations` | `STRUCT(labels STRUCT("value" VARCHAR, "type" VARCHAR)[], symbols VARCHAR[], from_connector_id VARCHAR, to_segment_id VARCHAR, to_connector_id VARCHAR, "when" STRUCT(heading VARCHAR), final_heading VARCHAR)[]` | Describes objects that can be reached by following a transportation segment in the same way those objects are described on signposts or ground writing that a traveller following the segment would observe in the real world. This allows navigation systems to refer to signs and observable writing that a traveller actually sees. |
| `sources` | `STRUCT(property VARCHAR, dataset VARCHAR, license VARCHAR, record_id VARCHAR, update_time VARCHAR, confidence DOUBLE, "between" DOUBLE[], provider VARCHAR, "resource" VARCHAR, "version" VARCHAR)[]` | The array of source information for the properties of a given feature, with each entry being a source object which lists the property in JSON Pointer notation. All features must have a root level source which is the default source if a specific property's source is not specified. |
| `geometry` | `GEOMETRY('OGC:CRS84')` | Segment's geometry which MUST be a LineSting as defined by GeoJSON schema. |
| `version` | `INTEGER` | Version number of the feature, incremented in each Overture release where the geometry or attributes of this feature changed. |
| `bbox` | `STRUCT(xmin DOUBLE, xmax DOUBLE, ymin DOUBLE, ymax DOUBLE)` |  |

## Procedencia

- Productor: Overture Maps Foundation (https://overturemaps.org/).
- Guía: https://docs.overturemaps.org/guides/transportation/
- Esquema: https://docs.overturemaps.org/schema/reference/transportation/segment/
- Catálogo del que deriva: overture-portolan (`https://nlebovits.github.io/overture-portolan/transportation/segment/collection.json`); si sus URLs no responden, el catálogo STAC de Overture (`https://stac.overturemaps.org/catalog.json`).

## Licencia

**ODbL 1.0**, según el catálogo STAC de Overture (`license: ODbL-1.0`). La página de atribución de Overture dice para este tema: "License for theme: ODbL".

Atribución: https://docs.overturemaps.org/attribution/
