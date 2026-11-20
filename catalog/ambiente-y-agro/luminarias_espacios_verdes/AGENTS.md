# Guía para agentes — Luminarias en espacios verdes

`ambiente-y-agro/luminarias_espacios_verdes`: puntos. Luminarias en espacios verdes públicos para el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/luminarias_espacios_verdes/luminarias_espacios_verdes.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/luminarias_espacios_verdes/luminarias_espacios_verdes.pmtiles`, capa `luminarias_espacios_verdes`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/luminarias_espacios_verdes/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:luminarias_espacios_verdes` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `latitud` (double)
- `longitud` (double)
- `fuente` (string)
- `actualizacion` (int64)
- `detalle` (string)
- `potencia_lampara` (int64)
- `marca_lampara` (string)
- `modelo_lampara` (string)
- `tipo_poste` (string)
- `altura_poste` (int64)
- `tipo_lampara` (string)
- `cantidad_lamparas` (int64)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
fuente: Imagen aérea | Secretaría de Control de Gestión | Subsecretaría de Control de Gestión | Control de Gestión | Delegación Guerrico
marca_lampara: Philips | Italavia | Strand | Philco
modelo_lampara: 824110110681 | 82301026 | SX200 | Ranger | 82300289
tipo_poste: acero | Acero, brazo simple | columna_acero | madera
tipo_lampara: led | LED | halogena
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/luminarias_espacios_verdes/luminarias_espacios_verdes.parquet')
LIMIT 5;
```

### Registros por `fuente`

```sql
SELECT "fuente", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/luminarias_espacios_verdes/luminarias_espacios_verdes.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `marca_lampara`

```sql
SELECT "marca_lampara", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/luminarias_espacios_verdes/luminarias_espacios_verdes.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/luminarias_espacios_verdes/luminarias_espacios_verdes.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/luminarias_espacios_verdes/luminarias_espacios_verdes.parquet')
WHERE bbox.xmin >= -60.4289 AND bbox.xmax <= -60.3440
  AND bbox.ymin >= -33.8185 AND bbox.ymax <= -33.7694;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
