# Guía para agentes — Red de nivelación de precisión del IGN

`vialidad/red_nivelacion_ign_precision`: puntos. Red de Nivelación de Precisión del Instituto Geográfico Nacional recortado al Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/red_nivelacion_ign_precision/red_nivelacion_ign_precision.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/red_nivelacion_ign_precision/red_nivelacion_ign_precision.pmtiles`, capa `red_nivelacion_ign_precision`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/red_nivelacion_ign_precision/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:red_nivelacion_ign_precision` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `nomenclatu` (string)
- `latg` (int64)
- `latm` (int64)
- `lats` (double)
- `long` (int64)
- `lonm` (int64)
- `lons` (double)
- `alturaelip` (double)
- `precision` (string)
- `nortegk` (int64)
- `estegk` (int64)
- `faja` (int64)
- `cotasrvn16` (double)
- `marca` (string)
- `estado` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
precision: 500 m | 15 m | 0.05 m
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/red_nivelacion_ign_precision/red_nivelacion_ign_precision.parquet')
LIMIT 5;
```

### Registros por `precision`

```sql
SELECT "precision", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/red_nivelacion_ign_precision/red_nivelacion_ign_precision.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/red_nivelacion_ign_precision/red_nivelacion_ign_precision.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/red_nivelacion_ign_precision/red_nivelacion_ign_precision.parquet')
WHERE bbox.xmin >= -60.6002 AND bbox.xmax <= -60.4609
  AND bbox.ymin >= -33.8966 AND bbox.ymax <= -33.8016;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
