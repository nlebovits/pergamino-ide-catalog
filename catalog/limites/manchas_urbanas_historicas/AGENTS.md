# Guía para agentes — Manchas urbanas historicas

`limites/manchas_urbanas_historicas`: polígonos. Manchas urbanas históricas de la Ciudad de Pergamino, desde 1773 a 2025, tomadas del Plan Estratégico Pergamino (PEP).

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/manchas_urbanas_historicas.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/manchas_urbanas_historicas.pmtiles`, capa `manchas_urbanas_historicas`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:manchas_urbanas_historicas` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `fuente` (string)
- `denominacion` (string)
- `poblacion` (int64)
- `superficia_ha` (int64)
- `observaciones` (string)
- `periodo` (int64)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
fuente: PEP | IDE
denominacion: Pergamino | La Dormida de Pergamino
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/manchas_urbanas_historicas.parquet')
LIMIT 5;
```

### Registros por `fuente`

```sql
SELECT "fuente", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/manchas_urbanas_historicas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `denominacion`

```sql
SELECT "denominacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/manchas_urbanas_historicas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/manchas_urbanas_historicas.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/manchas_urbanas_historicas/manchas_urbanas_historicas.parquet')
WHERE bbox.xmin >= -60.5856 AND bbox.xmax <= -60.5585
  AND bbox.ymin >= -33.9078 AND bbox.ymax <= -33.8901;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
