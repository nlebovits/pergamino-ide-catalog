# Guía para agentes — Inundacion de 2016

`ambiente-y-agro/inundacion_2016`: polígonos. Mancha de máxima de inundación y anegamiento del evento climatológico ocurrido el 26-12-2016 en el Partido de Pergamino, que afectó zonas bajas cercanas a cursos de agua.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inundacion_2016/inundacion_2016.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inundacion_2016/inundacion_2016.pmtiles`, capa `inundacion_2016`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inundacion_2016/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:inundacion_2016` de GeoNode.

## Esquema

- `id` (int64)
- `relevo` (string)
- `localidad` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
relevo: Contralor Urbano | Delegado Claudio A López | Delegado Cornejo Fernando
localidad: Pergamino | Manuel Ocampo | Pinzon
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inundacion_2016/inundacion_2016.parquet')
LIMIT 5;
```

### Registros por `relevo`

```sql
SELECT "relevo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inundacion_2016/inundacion_2016.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inundacion_2016/inundacion_2016.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inundacion_2016/inundacion_2016.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inundacion_2016/inundacion_2016.parquet')
WHERE bbox.xmin >= -60.6569 AND bbox.xmax <= -60.6189
  AND bbox.ymin >= -33.9023 AND bbox.ymax <= -33.8539;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
