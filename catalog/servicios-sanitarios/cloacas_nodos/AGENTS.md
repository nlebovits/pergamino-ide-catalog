# Guía para agentes — Red cloacal - Nodos

`servicios-sanitarios/cloacas_nodos`: puntos. Sistema de nodos y nodos de la red cloacal de la Ciudad de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_nodos/cloacas_nodos.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_nodos/cloacas_nodos.pmtiles`, capa `cloacas_nodos`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_nodos/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:cloacas_nodos` de GeoNode.

## Esquema

- `id` (int64)
- `ubicacion` (string)
- `clase` (string)
- `cota_tapa` (string)
- `cota_fondo` (string)
- `prof` (double)
- `colectora` (int64)
- `q` (string)
- `mat_tapa` (string)
- `material` (string)
- `tipo_tapa` (string)
- `condicion` (string)
- `inf_napa` (string)
- `sistema` (string)
- `antig` (string)
- `resp_obra` (string)
- `fecha_act` (date32[day])
- `resp_act` (string)
- `obs` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
ubicacion: CENTRO DE CALLE | VEREDA | ESQUINA EN CALLE | ESQUINA VEREDA | CALLE | PREDIO
clase: BOCA DE REGISTRO | CAMARA DE LIMPIEZA | CONEXION | EMPALME
mat_tapa: FUNDICION | CEMENTO
material: MAMPOSTERIA | -
tipo_tapa: CIEGA | VENTILADA
condicion: VISIBLE | TAPA TAPADA
sistema: TERCERA | SEGUNDA | PRIMERA | PARQUE_INDUSTRIAL
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_nodos/cloacas_nodos.parquet')
LIMIT 5;
```

### Registros por `ubicacion`

```sql
SELECT "ubicacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_nodos/cloacas_nodos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `clase`

```sql
SELECT "clase", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_nodos/cloacas_nodos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_nodos/cloacas_nodos.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-sanitarios/cloacas_nodos/cloacas_nodos.parquet')
WHERE bbox.xmin >= -60.5781 AND bbox.xmax <= -60.5641
  AND bbox.ymin >= -33.9091 AND bbox.ymax <= -33.8927;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
