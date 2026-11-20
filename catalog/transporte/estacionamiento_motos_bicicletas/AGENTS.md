# Guía para agentes — Estacionamiento de motos y bicicletas

`transporte/estacionamiento_motos_bicicletas`: puntos. Capa de estacionamiento de motos y bicicletas en la vía pública para el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_motos_bicicletas/estacionamiento_motos_bicicletas.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_motos_bicicletas/estacionamiento_motos_bicicletas.pmtiles`, capa `estacionamiento_motos_bicicletas`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_motos_bicicletas/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:estacionamiento_motos_bicicletas` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `ubicacion` (string)
- `delimitador` (string)
- `longitud_aproximada` (int64)
- `plaza_bicicletas` (int64)
- `plazas_motos` (int64)
- `plazas_totales` (int64)
- `atador` (string)
- `actualizacion` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
delimitador: bolardos plasticos | pintura en pavimento | cartel con base de cemento | no
atador: no | si
actualizacion: 2025-07-04Z | 2025-02-19Z | 2025-02-18Z | 2025-02-20Z | 2025-03-05Z | 2023-04-13Z | 2023-09-20Z | 2025-01-20Z | 2025-02-21Z | 2025-09-03Z | 2025-11-20Z | 2025-12-22Z | 2025-12-23Z | 2026-03-11Z
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_motos_bicicletas/estacionamiento_motos_bicicletas.parquet')
LIMIT 5;
```

### Registros por `delimitador`

```sql
SELECT "delimitador", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_motos_bicicletas/estacionamiento_motos_bicicletas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `atador`

```sql
SELECT "atador", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_motos_bicicletas/estacionamiento_motos_bicicletas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_motos_bicicletas/estacionamiento_motos_bicicletas.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/estacionamiento_motos_bicicletas/estacionamiento_motos_bicicletas.parquet')
WHERE bbox.xmin >= -60.5822 AND bbox.xmax <= -60.5722
  AND bbox.ymin >= -33.9061 AND bbox.ymax <= -33.8961;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
