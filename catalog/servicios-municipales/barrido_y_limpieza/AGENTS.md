# Guía para agentes — Barrido y limpieza de calles

`servicios-municipales/barrido_y_limpieza`: polígonos. Zonas de barrido y limpieza de calles en la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/barrido_y_limpieza.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/barrido_y_limpieza.pmtiles`, capa `barrido_y_limpieza`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:barrido_y_limpieza` de GeoNode.

## Esquema

- `id` (int64)
- `numero_zona` (int64)
- `zona` (string)
- `empresa` (string)
- `frecuencia` (string)
- `fuente` (string)
- `actualizacion` (string)
- `expediente_electronico` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
zona: sur | centro | este | norte | oeste | Sur
empresa: La Esperanza | Santísima trinidad | ENTRE SRL | San Cayetano | Cooperativa Centenario
frecuencia: Lunes y jueves | Martes y viernes | Miercoles y viernes | Lunes a sabados
expediente_electronico: 2026 107260 SSP | 2026 107871 SSP | 2026 107383 SSP | 2026 108782 SSP
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/barrido_y_limpieza.parquet')
LIMIT 5;
```

### Registros por `zona`

```sql
SELECT "zona", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/barrido_y_limpieza.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `empresa`

```sql
SELECT "empresa", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/barrido_y_limpieza.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/barrido_y_limpieza.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/barrido_y_limpieza/barrido_y_limpieza.parquet')
WHERE bbox.xmin >= -60.5771 AND bbox.xmax <= -60.5643
  AND bbox.ymin >= -33.8979 AND bbox.ymax <= -33.8851;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
