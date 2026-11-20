# Guía para agentes — Cobertura de gas natural

`energia-y-conectividad/cobertura_gas_natural`: polígonos. Cobertura de gas natural en el territorio de la Ciudad de Pergamino, provista por Litoral Gas S.A.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/cobertura_gas_natural/cobertura_gas_natural.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/cobertura_gas_natural/cobertura_gas_natural.pmtiles`, capa `cobertura_gas_natural`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/cobertura_gas_natural/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:cobertura_gas_natural` de GeoNode.

## Esquema

- `id` (int64)
- `numero_plano` (string)
- `actualizacion` (string)
- `fuente` (string)
- `localidad` (string)
- `observaciones` (string)
- `descargo_responsabilidad` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
numero_plano: 89-06 Rev.117 | 89-03 Rev.97 | 89-07 Rev.59 | 89-04 rev.85 | 89.2 Rev.179 | 89-01 Rev.188 | 89-05 Rev.124 | 89-08 Rev.61
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/cobertura_gas_natural/cobertura_gas_natural.parquet')
LIMIT 5;
```

### Registros por `numero_plano`

```sql
SELECT "numero_plano", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/cobertura_gas_natural/cobertura_gas_natural.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/cobertura_gas_natural/cobertura_gas_natural.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/cobertura_gas_natural/cobertura_gas_natural.parquet')
WHERE bbox.xmin >= -60.5684 AND bbox.xmax <= -60.5498
  AND bbox.ymin >= -33.9104 AND bbox.ymax <= -33.8941;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
