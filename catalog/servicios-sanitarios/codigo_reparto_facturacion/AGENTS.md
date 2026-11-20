# Guía para agentes — Códigos de reparto de facturación

`servicios-sanitarios/codigo_reparto_facturacion`: líneas. Dataset extraído del callejero con los códigos de reparto de facturación según la Secretaría de Hacienda.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/codigo_reparto_facturacion.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/codigo_reparto_facturacion.pmtiles`, capa `codigo_reparto_facturacion`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:codigo_reparto_facturacion` de GeoNode.

## Esquema

- `id` (int64)
- `nombre` (string)
- `nombre_alt` (string)
- `numero_reparto_facturacion` (int64)
- `pre_tipo` (string)
- `pre_dir` (string)
- `impar_ini` (int64)
- `par_fin` (int64)
- `clase` (string)
- `sentido` (int64)
- `barrio` (string)
- `localidad` (string)
- `long` (int64)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
pre_tipo: AV | BV | AU | PJE | PASEO
pre_dir: BIS | AV
clase: CALLE | RESTRINGIDO | CAMINO | AVENIDA | RUTA | PUENTE | ENLACE | ACCESO | PEATONAL | COLECTORA | AU | FFCC-PEATONAL | PUENTE-PEATONAL
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/codigo_reparto_facturacion.parquet')
LIMIT 5;
```

### Registros por `pre_tipo`

```sql
SELECT "pre_tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/codigo_reparto_facturacion.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `pre_dir`

```sql
SELECT "pre_dir", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/codigo_reparto_facturacion.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/codigo_reparto_facturacion.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/codigo_reparto_facturacion/codigo_reparto_facturacion.parquet')
WHERE bbox.xmin >= -60.6220 AND bbox.xmax <= -60.4609
  AND bbox.ymin >= -33.9274 AND bbox.ymax <= -33.8026;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
