# Guía para agentes — Puntos de interes cultural

`comercio-y-cultura/puntos_de_interes`: puntos. Puntos de interés (POI) cultural del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/puntos_de_interes/puntos_de_interes.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/puntos_de_interes/puntos_de_interes.pmtiles`, capa `puntos_de_interes`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/puntos_de_interes/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:puntos_de_interes` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `nombre` (string)
- `ubicacion` (string)
- `lat` (double)
- `lon` (double)
- `observaciones` (string)
- `link` (string)
- `localidad` (string)
- `tipo_interes` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
localidad: Pergamino | Mariano Benítez | Rural
tipo_interes: cultural | aire libre | arquitectonico | historico | monumento | religioso | deportivo
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/puntos_de_interes/puntos_de_interes.parquet')
LIMIT 5;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/puntos_de_interes/puntos_de_interes.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `tipo_interes`

```sql
SELECT "tipo_interes", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/puntos_de_interes/puntos_de_interes.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/puntos_de_interes/puntos_de_interes.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/comercio-y-cultura/puntos_de_interes/puntos_de_interes.parquet')
WHERE bbox.xmin >= -60.5465 AND bbox.xmax <= -60.5267
  AND bbox.ymin >= -33.8408 AND bbox.ymax <= -33.7925;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
