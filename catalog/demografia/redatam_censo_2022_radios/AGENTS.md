# Guía para agentes — REDATAM Censo 2022 por radio

`demografia/redatam_censo_2022_radios`: polígonos. La capa contiene múltiples datos de población obtenidos en el Censo del 2022 a nivel de radio censal para el Partido de Pergamino, como cantidad de habitantes, mujeres, varones, rangos etáreos, etc.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/redatam_censo_2022_radios/redatam_censo_2022_radios.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/demografia/redatam_censo_2022_radios/redatam_censo_2022_radios.pmtiles`, capa `redatam_censo_2022_radios`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/redatam_censo_2022_radios/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:redatam_censo_2022_radios` de GeoNode.

## Esquema

- `id` (int64)
- `fid` (int64)
- `clavera` (double)
- `codigo_partido` (int64)
- `codigo_localidad` (double)
- `nombre_localidad` (string)
- `fraccion` (double)
- `radio` (double)
- `tipo` (string)
- `radio_id` (double)
- `mujeres_total` (int64)
- `varones_total` (int64)
- `poblacion_total` (int64)
- `indice_normalizado_sexo` (double)
- `mujeres_porcentaje` (double)
- `varones_porcentaje` (double)
- `poblacion_porcentaje_sobre_total` (double)
- `edad_hasta_14` (int64)
- `edad_entre_14_y_64` (int64)
- `edad_64_o_mas` (int64)
- `edad_hasta_14_porcentaje` (double)
- `edad_entre_14_y_64_porcentaje` (double)
- `edad_64_o_mas_porcentaje` (double)
- `viviendas` (int64)
- `hogares` (int64)
- `indice_normalizado_vivienda_hogar` (double)
- `viviendas_ocupadas` (int64)
- `viviendas_desocupadas` (int64)
- `indice_normalizado_ocupacion_vivienda` (double)
- `densidad` (double)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tipo: URBANO | RURAL
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/redatam_censo_2022_radios/redatam_censo_2022_radios.parquet')
LIMIT 5;
```

### Registros por `tipo`

```sql
SELECT "tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/redatam_censo_2022_radios/redatam_censo_2022_radios.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/redatam_censo_2022_radios/redatam_censo_2022_radios.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/redatam_censo_2022_radios/redatam_censo_2022_radios.parquet')
WHERE bbox.xmin >= -60.6220 AND bbox.xmax <= -60.4609
  AND bbox.ymin >= -33.9220 AND bbox.ymax <= -33.7948;
```

### Unión con `demografia/radios_censales_indec_2010` por `clavera`

```sql
SELECT t."clavera", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/redatam_censo_2022_radios/redatam_censo_2022_radios.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/radios_censales_indec_2010/radios_censales_indec_2010.parquet') AS r
  ON CAST(t."clavera" AS VARCHAR) = CAST(r."clavera" AS VARCHAR)
GROUP BY ALL
ORDER BY registros DESC
LIMIT 10;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `demografia/radios_censales_indec_2010`, por `clavera`. Hay valores de `clavera` que coinciden en las dos colecciones.
- `limites/barrios_y_pueblos`, por intersección espacial.
