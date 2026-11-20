# Guía para agentes — Cobertura de red de agua corriente

`servicios-sanitarios/cobertura_agua`: polígonos. Capa de cobertura del servicio sanitario de red de agua corriente para la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua/cobertura_agua.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua/cobertura_agua.pmtiles`, capa `cobertura_agua`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:cobertura_agua` de GeoNode.

## Esquema

- `id` (int64)
- `zona` (string)
- `sistema` (string)
- `area` (double)
- `fecha_actualizacion` (string)
- `observaciones` (string)
- `gestion` (string)
- `fuente` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
zona: Norte | Sur | Kennedy | Villa Alicia | Quinta Mastrangelo
sistema: Distribución con bombas de impulsión | Central con tanque elevado
gestion: entre 2015 y 2019 | entre 2023 y 2027 | entre 2019 y 2023 | Anterior a 2015
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua/cobertura_agua.parquet')
LIMIT 5;
```

### Registros por `zona`

```sql
SELECT "zona", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua/cobertura_agua.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `sistema`

```sql
SELECT "sistema", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua/cobertura_agua.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua/cobertura_agua.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_agua/cobertura_agua.parquet')
WHERE bbox.xmin >= -60.5834 AND bbox.xmax <= -60.5676
  AND bbox.ymin >= -33.9046 AND bbox.ymax <= -33.8897;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
