# Guía para agentes — Zonas de seguridad

`seguridad/zonas_seguridad`: polígonos. Zonas de seguridad de la Ciudad de Pergamino propuestas por la Secretaría de Seguridad.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/zonas_seguridad/zonas_seguridad.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/zonas_seguridad/zonas_seguridad.pmtiles`, capa `zonas_seguridad`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/zonas_seguridad/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:zonas_seguridad` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `comisaria` (string)
- `zona` (string)
- `localidad` (string)
- `cuadricula` (int64)
- `jurisdiccion` (int64)
- `observaciones` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
comisaria: 1ra | 2da | 3ra
zona: 1A | 1B | 2A | 2B | 3A | 3B
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/zonas_seguridad/zonas_seguridad.parquet')
LIMIT 5;
```

### Registros por `comisaria`

```sql
SELECT "comisaria", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/zonas_seguridad/zonas_seguridad.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `zona`

```sql
SELECT "zona", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/zonas_seguridad/zonas_seguridad.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/zonas_seguridad/zonas_seguridad.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/zonas_seguridad/zonas_seguridad.parquet')
WHERE bbox.xmin >= -60.5761 AND bbox.xmax <= -60.5506
  AND bbox.ymin >= -33.9048 AND bbox.ymax <= -33.8833;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
