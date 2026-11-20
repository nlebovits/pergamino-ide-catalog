# Guía para agentes — Pobreza cronica (2010)

`demografia/pobreza_cronica`: polígonos. La capa contiene índices que permiten visualizar, por radio censal, la pobreza crónica para el Partido de Pergamino según Censo INDEC 2010.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/pobreza_cronica/pobreza_cronica.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/demografia/pobreza_cronica/pobreza_cronica.pmtiles`, capa `pobreza_cronica`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/pobreza_cronica/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:pobreza_cronica` de GeoNode.

## Esquema

- `id` (int64)
- `radio_id` (double)
- `varon` (int64)
- `mujer` (int64)
- `habitantes_al_2010` (int64)
- `porcentaje_hogares_hacinamiento_critico` (string)
- `porcentaje_hogares_jefe_primario_completo_o_menos` (string)
- `porcentaje_hogares_jefe_secundario_incompleto_o_menos` (string)
- `porcentaje_hogares_vivienda_deficitaria` (string)
- `porcentaje_hogares_sin_acceso_red_cloacal` (string)
- `porcentaje_población_situación_pobreza_crónica` (string)
- `porcentaje_de_población_urbana` (string)
- `observaciones` (string)
- `nivel_de_incidencia_de_pobreza_cronica` (string)
- `licencia` (string)
- `fuente` (string)
- `actualizacion` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
nivel_de_incidencia_de_pobreza_cronica: Muy bajo (0 - 0,99%) | Bajo (1 - 4,99%) | Moderado (5 - 9,99%) | Alto (10 - 14,99%) | Muy alto (15 - 24,99%) | Crítico (25 - 100%) | Sin datos
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/pobreza_cronica/pobreza_cronica.parquet')
LIMIT 5;
```

### Registros por `nivel_de_incidencia_de_pobreza_cronica`

```sql
SELECT "nivel_de_incidencia_de_pobreza_cronica", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/pobreza_cronica/pobreza_cronica.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/pobreza_cronica/pobreza_cronica.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/pobreza_cronica/pobreza_cronica.parquet')
WHERE bbox.xmin >= -60.6215 AND bbox.xmax <= -60.4606
  AND bbox.ymin >= -33.9218 AND bbox.ymax <= -33.7947;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
