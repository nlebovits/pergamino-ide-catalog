# Guía para agentes — Ferrocarriles

`transporte/ferrocarriles`: líneas. Redes ferroviarias en el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/ferrocarriles/ferrocarriles.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/transporte/ferrocarriles/ferrocarriles.pmtiles`, capa `ferrocarriles`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/ferrocarriles/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:ferrocarriles` de GeoNode.

## Esquema

- `gid` (int64)
- `nombre` (string)
- `trocha` (string)
- `provincia` (string)
- `observaciones` (string)
- `actualizacion` (string)
- `fuente` (string)
- `etiqueta` (string)
- `estado` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
trocha: Ancha  (1676 Mm) | Angosta (1000 Mm)
provincia: Buenos Aires | Santa Fe
etiqueta: General Bartolome Mitre | General Belgrano | General San Martin
estado: desuso | activa
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/ferrocarriles/ferrocarriles.parquet')
LIMIT 5;
```

### Registros por `trocha`

```sql
SELECT "trocha", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/ferrocarriles/ferrocarriles.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `provincia`

```sql
SELECT "provincia", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/ferrocarriles/ferrocarriles.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/ferrocarriles/ferrocarriles.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/ferrocarriles/ferrocarriles.parquet')
WHERE bbox.xmin >= -60.8003 AND bbox.xmax <= -60.5336
  AND bbox.ymin >= -33.9284 AND bbox.ymax <= -33.7442;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
