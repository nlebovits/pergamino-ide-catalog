# Guía para agentes — Educacion

`educacion/educacion`: puntos. Capa de establecimientos educativos del Partido de Pergamino organizados por nivel y gestión como jardines, escuelas, colegios, institutos, profesorados y universidades.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/educacion/educacion/educacion.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/educacion/educacion/educacion.pmtiles`, capa `educacion`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/educacion/educacion/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:educacion` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `clave` (string)
- `cue_anexo` (double)
- `nombre` (string)
- `nro` (string)
- `direccion` (string)
- `calles_ale` (string)
- `telefono` (string)
- `cp` (string)
- `email` (string)
- `sector` (string)
- `layer` (string)
- `etiqueta` (string)
- `nivel` (string)
- `fuente` (string)
- `latitud` (double)
- `longitud` (double)
- `barrio` (string)
- `localidad` (string)
- `estado` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
cp: 2700 | 2717 | 2718 | 2701 | 2715 | 2751 | 2703 | 2713 | 2711 | B2700KIZ
sector: Estatal | Privada
nivel: primaria | inicial | secundaria | superior | especial | formacion | primario
localidad: Pergamino | Rural | El Socorro (Villa Angélica) | Mariano Alfonzo | Acevedo | Guerrico | La Violeta | Manuel Ocampo | Rancagua | Urquiza (Juan Anchorena) | Fontezuela | Juan Andrés de la Peña | Mariano Benítez | Pinzón | Villa San José de Rancagua
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/educacion/educacion.parquet')
LIMIT 5;
```

### Registros por `cp`

```sql
SELECT "cp", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/educacion/educacion.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `sector`

```sql
SELECT "sector", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/educacion/educacion.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/educacion/educacion.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/educacion/educacion/educacion.parquet')
WHERE bbox.xmin >= -60.5767 AND bbox.xmax <= -60.4406
  AND bbox.ymin >= -33.8920 AND bbox.ymax <= -33.7911;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
