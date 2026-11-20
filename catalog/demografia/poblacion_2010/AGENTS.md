# Guía para agentes — Densidad de población 2010

`demografia/poblacion_2010`: polígonos. Datos georreferenciados del Censo 2010 donde se puede observar la densidad poblacional por radio censal.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/poblacion_2010/poblacion_2010.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/demografia/poblacion_2010/poblacion_2010.pmtiles`, capa `poblacion_2010`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/poblacion_2010/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:2010_poblacion` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `redcode` (double)
- `p_total` (int64)
- `p_a17` (int64)
- `p_0a3` (int64)
- `p_4a5` (int64)
- `p_6a12` (int64)
- `p_13a17` (int64)
- `p_18a` (int64)
- `p_18a29` (int64)
- `p_30a54` (int64)
- `p_55a69` (int64)
- `p_70a` (int64)
- `m_total` (int64)
- `m_a17` (int64)
- `m_0a3` (int64)
- `m_4a5` (int64)
- `m_6a12` (int64)
- `m_13a17` (int64)
- `m_18a` (int64)
- `m_18a29` (int64)
- `m_30a54` (int64)
- `m_55a69` (int64)
- `m_70a` (int64)
- `v_total` (int64)
- `v_a17` (int64)
- `v_0a3` (int64)
- `v_4a5` (int64)
- `v_6a12` (int64)
- `v_13a17` (int64)
- `v_18a` (int64)
- `v_18a29` (int64)
- `v_30a54` (int64)
- `v_55a69` (int64)
- `v_70a` (int64)
- `p18a_sin_instruccion` (int64)
- `p18a_primaria` (int64)
- `p18a_secundaria` (int64)
- `p18a_soloprimaria` (int64)
- `p18a_solosecundaria` (int64)
- `p18a_terciaria` (int64)
- `p18a_universitaria` (int64)
- `p4a5_asiste` (int64)
- `p6a12_asiste` (int64)
- `p1317_asiste` (int64)
- `p1317_sin_secundaria` (int64)
- `p1829_asiste` (int64)
- `p1829_sin_secundaria` (int64)
- `p1425_asiste` (int64)
- `p1425_sin_secundaria` (int64)
- `p1425` (int64)
- `idprov` (double)
- `prov` (string)
- `iddpto` (double)
- `dpto` (string)
- `redcode_1` (double)
- `radios_poblacion_total` (int64)
- `radios_hogares_total` (int64)
- `radios_latitud_centroide` (double)
- `radios_longitud_centroide` (double)
- `radios_superficie_km2` (double)
- `densidad_hab_km2` (double)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/poblacion_2010/poblacion_2010.parquet')
LIMIT 5;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/poblacion_2010/poblacion_2010.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/poblacion_2010/poblacion_2010.parquet')
WHERE bbox.xmin >= -60.6211 AND bbox.xmax <= -60.4602
  AND bbox.ymin >= -33.9223 AND bbox.ymax <= -33.7950;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
