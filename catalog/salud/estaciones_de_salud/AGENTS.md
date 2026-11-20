# Guía para agentes — Estaciones de salud

`salud/estaciones_de_salud`: puntos. Estaciones de salud del Partido de Pergamino donde se puede realizar gimnasia al aire libre.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/salud/estaciones_de_salud/estaciones_de_salud.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/salud/estaciones_de_salud/estaciones_de_salud.pmtiles`, capa `estaciones_de_salud`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/salud/estaciones_de_salud/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:estaciones_de_salud` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `nombre` (string)
- `localidad` (string)
- `barrio` (string)
- `ubicacion` (string)
- `actualizacion` (string)
- `fuente` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
localidad: Pergamino | Manuel Ocampo | Acevedo | El Socorro | Fontezuela | Guerrico | J A de la Peña | La Violeta | Mariano H Alfonzo | Pinzon | Rancagua | Urquiza
actualizacion: 2020-10-22Z | 2020-12-11Z | 2020-12-21Z | 2021-01-22Z | 2023-01-24Z
fuente: Municipalidad de Pergamino | Imagen aérea 2020 | Imagenes aéreas 2020
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/salud/estaciones_de_salud/estaciones_de_salud.parquet')
LIMIT 5;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/salud/estaciones_de_salud/estaciones_de_salud.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `actualizacion`

```sql
SELECT "actualizacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/salud/estaciones_de_salud/estaciones_de_salud.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/salud/estaciones_de_salud/estaciones_de_salud.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/salud/estaciones_de_salud/estaciones_de_salud.parquet')
WHERE bbox.xmin >= -60.5686 AND bbox.xmax <= -60.4354
  AND bbox.ymin >= -33.8810 AND bbox.ymax <= -33.8078;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
