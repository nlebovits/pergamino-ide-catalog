# Guía para agentes — Índice de Calidad de Vida (ICV)

`demografia/icv`: polígonos. Capa de datos que permite conocer el Índice de Calidad de Vida o ICV desde una perspectiva geográfica, elaborado por el CONICET. Mapa de cobertura sobre el Partido de Pergamino

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/icv/icv.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/demografia/icv/icv.pmtiles`, capa `icv`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/icv/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:icv` de GeoNode.

## Esquema

- `id` (int64)
- `clavera` (double)
- `radio_id` (double)
- `varon` (int64)
- `mujer` (int64)
- `habitantes_al_2010` (int64)
- `indice_calidad_vida_2010` (double)
- `fuente` (string)
- `actualizacion` (string)
- `observaciones` (string)
- `normalized_hab_2010` (int64)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/icv/icv.parquet')
LIMIT 5;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/icv/icv.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/icv/icv.parquet')
WHERE bbox.xmin >= -60.6215 AND bbox.xmax <= -60.4606
  AND bbox.ymin >= -33.9218 AND bbox.ymax <= -33.7947;
```

### Unión con `demografia/radios_censales_indec_2010` por `clavera`

```sql
SELECT t."clavera", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/icv/icv.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/radios_censales_indec_2010/radios_censales_indec_2010.parquet') AS r
  ON CAST(t."clavera" AS VARCHAR) = CAST(r."clavera" AS VARCHAR)
GROUP BY ALL
ORDER BY registros DESC
LIMIT 10;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `demografia/radios_censales_indec_2010`, por `clavera`. Hay valores de `clavera` que coinciden en las dos colecciones.
- `limites/barrios_y_pueblos`, por intersección espacial.
