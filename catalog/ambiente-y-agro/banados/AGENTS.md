# Guía para agentes — Bañados

`ambiente-y-agro/banados`: polígonos. Capa de bañados de la cuenca del Arroyo Pergamino. La extensión de la capa supera el territorio del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/banados/banados.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/banados/banados.pmtiles`, capa `banados`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/banados/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:banados` de GeoNode.

## Esquema

- `id` (int64)
- `area` (double)
- `perimetro` (double)
- `fuente` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/banados/banados.parquet')
LIMIT 5;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/banados/banados.parquet')
WHERE bbox.xmin >= -60.9012 AND bbox.xmax <= -60.8496
  AND bbox.ymin >= -33.8637 AND bbox.ymax <= -33.8163;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.
