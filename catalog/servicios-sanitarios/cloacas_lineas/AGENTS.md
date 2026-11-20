# Guía para agentes — Red cloacal - Líneas

`servicios-sanitarios/cloacas_lineas`: líneas. Sistema de tuberías y conexiones de la red cloacal de la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/cloacas_lineas.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/cloacas_lineas.pmtiles`, capa `cloacas_lineas`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:cloacas_lineas` de GeoNode.

## Esquema

- `id` (int64)
- `diametro` (int64)
- `material` (string)
- `ubicacion` (string)
- `dist_lm` (double)
- `clase` (string)
- `ventila` (string)
- `intrados_i` (string)
- `intrados_f` (string)
- `longitud` (int64)
- `pendiente` (string)
- `sistema` (string)
- `q_max` (string)
- `q_actual` (string)
- `conex_exis` (int64)
- `conex_pend` (int64)
- `condicion` (string)
- `antig` (string)
- `resp_obra` (string)
- `fecha_act` (date32[day])
- `resp_act` (string)
- `obs` (string)
- `tapada_i` (double)
- `tapada_f` (double)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
material: PVC | HS | AC
ubicacion: VEREDA | CENTRO CALLE | CALLE | PREDIO
clase: DOMICILIARIO | MAXIMA
ventila: NO | SI
sistema: TERCERA | SEGUNDA | PRIMERA | PARQUE_INDUSTRIAL
condicion: FUERA DE SERVICIO | 0
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/cloacas_lineas.parquet')
LIMIT 5;
```

### Registros por `material`

```sql
SELECT "material", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/cloacas_lineas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `ubicacion`

```sql
SELECT "ubicacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/cloacas_lineas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/cloacas_lineas.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_lineas/cloacas_lineas.parquet')
WHERE bbox.xmin >= -60.5780 AND bbox.xmax <= -60.5640
  AND bbox.ymin >= -33.9091 AND bbox.ymax <= -33.8927;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
