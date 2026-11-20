# Guía para agentes — Predios educativos

`educacion/predios_educativos`: polígonos. Predios educativos del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/educacion/predios_educativos/predios_educativos.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/educacion/predios_educativos/predios_educativos.pmtiles`, capa `predios_educativos`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/educacion/predios_educativos/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:predios_educativos` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `cui` (int64)
- `cue_clave` (string)
- `latitud` (double)
- `longitud` (double)
- `fuente` (string)
- `actualizacion` (string)
- `area` (double)
- `partido` (string)
- `barrio` (string)
- `localidad` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
actualizacion: 2024-09-11Z | 2026-03-11Z | 2026-03-04Z | 2026-03-03Z | 2026-03-06Z | 2026-03-09Z | 2026-03-19Z
localidad: Pergamino | Rural | El Socorro (Villa Angélica) | Acevedo | Mariano Alfonzo | Fontezuela | Guerrico | Juan Andrés de la Peña | Manuel Ocampo | Rancagua | Urquiza (Juan Anchorena) | La Violeta | Mariano Benítez | Pinzón
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/predios_educativos/predios_educativos.parquet')
LIMIT 5;
```

### Registros por `actualizacion`

```sql
SELECT "actualizacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/predios_educativos/predios_educativos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/predios_educativos/predios_educativos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/predios_educativos/predios_educativos.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/predios_educativos/predios_educativos.parquet')
WHERE bbox.xmin >= -60.5770 AND bbox.xmax <= -60.4409
  AND bbox.ymin >= -33.8922 AND bbox.ymax <= -33.7911;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
