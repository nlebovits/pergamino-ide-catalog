# Guía para agentes — Ductos pluviales

`servicios-sanitarios/pluviales`: líneas. Desagües pluviales de la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pluviales/pluviales.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pluviales/pluviales.pmtiles`, capa `pluviales`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pluviales/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:pluviales` de GeoNode.

## Esquema

- `id` (int64)
- `tipo` (string)
- `forma` (string)
- `ancho` (double)
- `alto` (double)
- `diametro` (double)
- `material` (string)
- `calle` (string)
- `altura_inicial` (int64)
- `altura_final` (int64)
- `observaciones` (string)
- `conducto_cerrado` (string)
- `funcion` (string)
- `longitud` (double)
- `sistema` (string)
- `fuente` (string)
- `descargo_responsabilidad` (string)
- `nombre_pliego` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tipo: ducto | canal | natural
forma: irregular | circular | rectangular | trapecio | bobeda
material: natural | cemento | hormigon | PVC
conducto_cerrado: si | no
funcion: conducto | conducto_sumidero | egreso | bombeo
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pluviales/pluviales.parquet')
LIMIT 5;
```

### Registros por `tipo`

```sql
SELECT "tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pluviales/pluviales.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `forma`

```sql
SELECT "forma", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pluviales/pluviales.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pluviales/pluviales.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pluviales/pluviales.parquet')
WHERE bbox.xmin >= -60.5954 AND bbox.xmax <= -60.5731
  AND bbox.ymin >= -33.9061 AND bbox.ymax <= -33.8921;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
