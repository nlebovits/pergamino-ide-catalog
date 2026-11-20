# Guía para agentes — Red de agua corriente - Líneas

`servicios-sanitarios/agua_lineas`: líneas. Sistema de tuberías y conexiones de la red de agua corriente de la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/agua_lineas.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/agua_lineas.pmtiles`, capa `agua_lineas`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:agua_lineas` de GeoNode.

## Esquema

- `id` (int64)
- `diametro` (int64)
- `material` (string)
- `ubicacion` (string)
- `dist_lm1` (string)
- `dist_lm2` (double)
- `prof` (double)
- `longitud` (double)
- `fin_tapon` (string)
- `clase` (string)
- `clase_tubo` (int64)
- `conex_exis` (int64)
- `conex_pend` (int64)
- `sistema` (string)
- `condicion` (string)
- `antig` (string)
- `fecha_act` (string)
- `resp_act` (string)
- `obs` (string)
- `resp_obra` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
material: PVC | FF | AC
ubicacion: CALLE | VEREDA | PREDIO
fin_tapon: SI | NO
clase: DOMICILIARIA | CABECERA | IMPULSION | DISTRIBUCION
sistema: NORTE | SUR | KENNEDY | VILLA ALICIA | QUINTA MASTRANGELO | CENTRO | CENTENARIO | LA GUARIDA
antig: 2017 | 2022 | 2018 | 2023 | 2024 | 1994 | 2025 | 2021 | 2016 | 2015 | 2026 | 2019 | 2020
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/agua_lineas.parquet')
LIMIT 5;
```

### Registros por `material`

```sql
SELECT "material", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/agua_lineas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `ubicacion`

```sql
SELECT "ubicacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/agua_lineas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/agua_lineas.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/agua_lineas/agua_lineas.parquet')
WHERE bbox.xmin >= -60.5812 AND bbox.xmax <= -60.5643
  AND bbox.ymin >= -33.8998 AND bbox.ymax <= -33.8826;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
