# Guía para agentes — Cicloturismo rural

`transporte/cicloturismo_rural`: líneas. Capa de recorridos turísticos para recorrer en bicicleta las distintas zonas rurales y Pueblos del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/cicloturismo_rural.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/cicloturismo_rural.pmtiles`, capa `cicloturismo_rural`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:cicloturismo` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `circuito` (string)
- `tramo` (string)
- `dificultad` (string)
- `longitud` (int64)
- `duracion_tramo` (int64)
- `observaciones` (string)
- `color` (string)
- `tipo_linea` (string)
- `atlas` (int64)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tramo: ida y vuelta | alternativo | ida | vuelta
dificultad: alta | baja | media
tipo_linea: solid | dot
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/cicloturismo_rural.parquet')
LIMIT 5;
```

### Registros por `tramo`

```sql
SELECT "tramo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/cicloturismo_rural.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `dificultad`

```sql
SELECT "dificultad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/cicloturismo_rural.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/cicloturismo_rural.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/cicloturismo_rural/cicloturismo_rural.parquet')
WHERE bbox.xmin >= -60.4985 AND bbox.xmax <= -60.3826
  AND bbox.ymin >= -33.8945 AND bbox.ymax <= -33.8148;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
