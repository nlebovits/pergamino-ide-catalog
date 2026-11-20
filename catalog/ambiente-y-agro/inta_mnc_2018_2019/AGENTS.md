# Guía para agentes — Mapa nacional de cultivos INTA 2018-2019

`ambiente-y-agro/inta_mnc_2018_2019`: polígonos. Mapa nacional de cultivos INTA 2018-2019 para el Partido de Pergamino, tomado de https://geo-backend.inta.gob.ar/catalogue/#/dataset/479

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inta_mnc_2018_2019/inta_mnc_2018_2019.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inta_mnc_2018_2019/inta_mnc_2018_2019.pmtiles`, capa `inta_mnc_2018_2019`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inta_mnc_2018_2019/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:inta_mnc_2018_2019` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `dn` (int64)
- `categorias` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
categorias: Maz (Cultivo unico) | Ganaderia | Soja (Cultivo unico) | Cultivo de invierno - Soja
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inta_mnc_2018_2019/inta_mnc_2018_2019.parquet')
LIMIT 5;
```

### Registros por `categorias`

```sql
SELECT "categorias", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inta_mnc_2018_2019/inta_mnc_2018_2019.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inta_mnc_2018_2019/inta_mnc_2018_2019.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/inta_mnc_2018_2019/inta_mnc_2018_2019.parquet')
WHERE bbox.xmin >= -60.6219 AND bbox.xmax <= -60.4609
  AND bbox.ymin >= -33.9259 AND bbox.ymax <= -33.8005;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
