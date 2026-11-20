# Guía para agentes — Curvas de nivel cuenca Arroyo Pergamino

`ambiente-y-agro/curvas_nivel_cuenca`: líneas. Curvas de nivel elaboradas por IATASA-ABS para el proyecto de la Presa del Arroyo Pergamino, nivel de paso a 2.5m. El área de la cuenca excede los límites del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/curvas_nivel_cuenca/curvas_nivel_cuenca.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/curvas_nivel_cuenca/curvas_nivel_cuenca.pmtiles`, capa `curvas_nivel_cuenca`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/curvas_nivel_cuenca/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:curvas_nivel_cuenca` de GeoNode.

## Esquema

- `id` (int64)
- `fuente` (string)
- `cotas` (double)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/curvas_nivel_cuenca/curvas_nivel_cuenca.parquet')
LIMIT 5;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/curvas_nivel_cuenca/curvas_nivel_cuenca.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/curvas_nivel_cuenca/curvas_nivel_cuenca.parquet')
WHERE bbox.xmin >= -60.8625 AND bbox.xmax <= -60.7427
  AND bbox.ymin >= -33.9064 AND bbox.ymax <= -33.8279;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
