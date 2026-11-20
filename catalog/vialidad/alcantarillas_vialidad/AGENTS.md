# Guía para agentes — Alcantarillas en rutas

`vialidad/alcantarillas_vialidad`: puntos. Alcantarillas en rutas provinciales y nacionales para todo el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/alcantarillas_vialidad.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/alcantarillas_vialidad.pmtiles`, capa `alcantarillas_vialidad`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:alcantarillas_vialidad` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `cod_ruta` (double)
- `progresiva` (double)
- `progresiv0` (double)
- `ano_ruta` (int64)
- `clase_estr` (string)
- `material_e` (string)
- `descripcio` (string)
- `angulo` (double)
- `fuente` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
clase_estr: alc. losa separada | losa | alc. caño circular
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/alcantarillas_vialidad.parquet')
LIMIT 5;
```

### Registros por `clase_estr`

```sql
SELECT "clase_estr", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/alcantarillas_vialidad.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/alcantarillas_vialidad.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/alcantarillas_vialidad/alcantarillas_vialidad.parquet')
WHERE bbox.xmin >= -60.6223 AND bbox.xmax <= -60.5040
  AND bbox.ymin >= -33.9010 AND bbox.ymax <= -33.8210;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
