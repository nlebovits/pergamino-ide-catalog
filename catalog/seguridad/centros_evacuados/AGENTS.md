# Guía para agentes — Centros de evacuados ante riesgo

`seguridad/centros_evacuados`: puntos. Centros de evacuación ante casos de emergencia dentro del marco de la Gestión de Riesgo.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/centros_evacuados/centros_evacuados.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/centros_evacuados/centros_evacuados.pmtiles`, capa `centros_evacuados`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/centros_evacuados/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:centros_evacuados` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `nombre` (string)
- `direccion` (string)
- `zona` (string)
- `capacidad` (string)
- `fuente` (string)
- `observaciones` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/centros_evacuados/centros_evacuados.parquet')
LIMIT 5;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/centros_evacuados/centros_evacuados.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/centros_evacuados/centros_evacuados.parquet')
WHERE bbox.xmin >= -60.5715 AND bbox.xmax <= -60.5610
  AND bbox.ymin >= -33.9006 AND bbox.ymax <= -33.8906;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
