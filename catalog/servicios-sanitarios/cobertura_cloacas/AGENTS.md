# Guía para agentes — Cobertura de red cloacal

`servicios-sanitarios/cobertura_cloacas`: polígonos. Capa de cobertura del servicio sanitario de red cloacal para la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_cloacas/cobertura_cloacas.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_cloacas/cobertura_cloacas.pmtiles`, capa `cobertura_cloacas`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_cloacas/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:cobertura_cloacas` de GeoNode.

## Esquema

- `id` (int64)
- `fid` (int64)
- `colectora` (string)
- `ramal` (string)
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
colectora: 3ra | 2da | 1ra | Industrial
ramal: Principal | Norte | Sur | Oeste | Kennedy | Nexo Sur | Nexo Norte | Centenario | Villa Gral San Martín | del Lago
gestion: entre 2015 y 2019 | Anterior a 2015 | entre 2019 y 2023 | entre 2023 y 2027
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_cloacas/cobertura_cloacas.parquet')
LIMIT 5;
```

### Registros por `colectora`

```sql
SELECT "colectora", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_cloacas/cobertura_cloacas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `ramal`

```sql
SELECT "ramal", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_cloacas/cobertura_cloacas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_cloacas/cobertura_cloacas.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cobertura_cloacas/cobertura_cloacas.parquet')
WHERE bbox.xmin >= -60.5778 AND bbox.xmax <= -60.5637
  AND bbox.ymin >= -33.9097 AND bbox.ymax <= -33.8930;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
