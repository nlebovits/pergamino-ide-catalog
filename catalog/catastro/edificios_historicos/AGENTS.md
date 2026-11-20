# Guía para agentes — Edificios históricos

`catastro/edificios_historicos`: puntos. Edificios históricos del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/edificios_historicos.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/edificios_historicos.pmtiles`, capa `edificios_historicos`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:edificios_historicos` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `descrip` (string)
- `calle` (string)
- `numero` (string)
- `circunsc` (string)
- `seccion` (string)
- `manzana` (string)
- `parcela` (string)
- `privado` (string)
- `municipio` (string)
- `provincia` (string)
- `nacion` (string)
- `instituto` (string)
- `estado` (string)
- `expediente` (string)
- `observ` (string)
- `partida` (int64)
- `anio_construccion` (string)
- `uso_actual` (string)
- `uso_anterior` (string)
- `inventario` (int64)
- `ordenanza` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
circunsc: I | 1 | II | XV
seccion: B | A | C | D | E | H
instituto: X | 35
estado: BUENO | REGULAR | MALO | MUY BUENO | NHD
ordenanza: 8261-15 | 8948-18
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/edificios_historicos.parquet')
LIMIT 5;
```

### Registros por `circunsc`

```sql
SELECT "circunsc", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/edificios_historicos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `seccion`

```sql
SELECT "seccion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/edificios_historicos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/edificios_historicos.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/edificios_historicos.parquet')
WHERE bbox.xmin >= -60.5736 AND bbox.xmax <= -60.5636
  AND bbox.ymin >= -33.9078 AND bbox.ymax <= -33.8931;
```

### Unión con `catastro/parcela` por `partida`

```sql
SELECT t."partida", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_historicos/edificios_historicos.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet') AS r
  ON CAST(t."partida" AS VARCHAR) = CAST(r."partida" AS VARCHAR)
GROUP BY ALL
ORDER BY registros DESC
LIMIT 10;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `catastro/parcela`, por `partida`. Hay valores de `partida` que coinciden en las dos colecciones.
- `limites/barrios_y_pueblos`, por intersección espacial.
