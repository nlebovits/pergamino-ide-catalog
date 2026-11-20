# Guía para agentes — Carteles viales

`vialidad/carteles_viales`: puntos. Carteles y señales de tránsito en el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/carteles_viales/carteles_viales.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/carteles_viales/carteles_viales.pmtiles`, capa `carteles_viales`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/carteles_viales/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:carteles_viales` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `tipo` (string)
- `calle_1` (string)
- `calle_2` (string)
- `altura` (int64)
- `fuente` (string)
- `instalado` (string)
- `estado` (string)
- `verificar` (string)
- `categoria` (string)
- `actualizacion` (int64)
- `texto_cartel` (string)
- `forma_cartel` (string)
- `localidad` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
fuente: vista de calle | Imagen aérea 2022 | DSIG
instalado: si | no
estado: incompleto | bueno | malo
verificar: no | si
categoria: informativa | prescriptiva | preventiva
localidad: Pergamino | Urquiza | Fontezuela
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/carteles_viales/carteles_viales.parquet')
LIMIT 5;
```

### Registros por `fuente`

```sql
SELECT "fuente", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/carteles_viales/carteles_viales.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `instalado`

```sql
SELECT "instalado", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/carteles_viales/carteles_viales.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/carteles_viales/carteles_viales.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/carteles_viales/carteles_viales.parquet')
WHERE bbox.xmin >= -60.5317 AND bbox.xmax <= -60.4779
  AND bbox.ymin >= -33.9092 AND bbox.ymax <= -33.8927;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
