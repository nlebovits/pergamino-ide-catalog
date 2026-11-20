# Guía para agentes — Pozos de agua DOSS

`servicios-sanitarios/pozos_agua_doss`: puntos. Localización de pozos de extracción de agua de la Dirección de Obras y Servicios Sanitarios de la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pozos_agua_doss/pozos_agua_doss.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pozos_agua_doss/pozos_agua_doss.pmtiles`, capa `pozos_agua_doss`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pozos_agua_doss/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:pozos_doss` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `nombre` (string)
- `ubicacion` (string)
- `estado` (string)
- `anio_pozo` (int64)
- `hp_bomba` (double)
- `actualizacion_estado` (string)
- `longitud` (double)
- `latitud` (double)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
estado: funcionamiento | parado | anulado | cegado | proyecto | construccion
actualizacion_estado: 2020-10-27Z | 2025-05-30Z | 2026-02-09Z | 2023-12-28Z | 2025-01-13Z | 2025-05-29Z
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pozos_agua_doss/pozos_agua_doss.parquet')
LIMIT 5;
```

### Registros por `estado`

```sql
SELECT "estado", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pozos_agua_doss/pozos_agua_doss.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `actualizacion_estado`

```sql
SELECT "actualizacion_estado", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pozos_agua_doss/pozos_agua_doss.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pozos_agua_doss/pozos_agua_doss.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/pozos_agua_doss/pozos_agua_doss.parquet')
WHERE bbox.xmin >= -60.5806 AND bbox.xmax <= -60.5639
  AND bbox.ymin >= -33.8979 AND bbox.ymax <= -33.8814;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
