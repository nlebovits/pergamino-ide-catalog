# Guía para agentes — Estacionamiento lado izquierdo

`transporte/estacionamiento_nocturno`: líneas. Calles en las cuales se permite el estacionamiento del lado izquierdo en la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_nocturno/estacionamiento_nocturno.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_nocturno/estacionamiento_nocturno.pmtiles`, capa `estacionamiento_nocturno`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_nocturno/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:estacionamiento_nocturno` de GeoNode.

## Esquema

- `id` (int64)
- `nombre` (string)
- `nombre_alt` (string)
- `pre_tipo` (string)
- `pre_dir` (string)
- `impar_ini` (int64)
- `impar_fin` (int64)
- `par_ini` (int64)
- `par_fin` (int64)
- `clase` (string)
- `etiqueta` (string)
- `t_etiq` (int64)
- `long` (int64)
- `est_medido` (string)
- `nombre_corto` (string)
- `ancho_vereda_par` (double)
- `ancho_vereda_impar` (double)
- `ancho_nominal` (int64)
- `ancho_real` (double)
- `ancho_calzada` (double)
- `nombre_completo` (string)
- `material_calzada` (string)
- `observaciones` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
est_medido: centro | micro | macro
material_calzada: hormigon | asfalto
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_nocturno/estacionamiento_nocturno.parquet')
LIMIT 5;
```

### Registros por `est_medido`

```sql
SELECT "est_medido", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_nocturno/estacionamiento_nocturno.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `material_calzada`

```sql
SELECT "material_calzada", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_nocturno/estacionamiento_nocturno.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_nocturno/estacionamiento_nocturno.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_nocturno/estacionamiento_nocturno.parquet')
WHERE bbox.xmin >= -60.5756 AND bbox.xmax <= -60.5656
  AND bbox.ymin >= -33.8984 AND bbox.ymax <= -33.8884;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
