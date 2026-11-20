# Guía para agentes — Nivel de hacinamiento (2010)

`demografia/hacinamiento`: polígonos. Índice de hacinamiento según Censo INDEC 2010 para el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/hacinamiento/hacinamiento.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/demografia/hacinamiento/hacinamiento.pmtiles`, capa `hacinamiento`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/hacinamiento/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:hacinamiento` de GeoNode.

## Esquema

- `id` (int64)
- `habitantes_al_2010` (int64)
- `0-0.50ppc` (int64)
- `0.51-0.99` (int64)
- `1.00-1.49` (int64)
- `1.50-1.99` (int64)
- `2.00-3.00` (int64)
- `mas3.00ppc` (int64)
- `total` (int64)
- `indice_mas3ppc` (double)
- `clavera` (int64)
- `observaciones` (string)
- `fuente` (string)
- `actualizacion` (int64)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/hacinamiento/hacinamiento.parquet')
LIMIT 5;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/hacinamiento/hacinamiento.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/hacinamiento/hacinamiento.parquet')
WHERE bbox.xmin >= -60.6215 AND bbox.xmax <= -60.4606
  AND bbox.ymin >= -33.9218 AND bbox.ymax <= -33.7947;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
