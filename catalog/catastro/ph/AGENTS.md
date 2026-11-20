# Guía para agentes — Catastro ph

`catastro/ph`: puntos. Capa de PH, propiedad horizontal o subparcelas, del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/ph.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/ph.pmtiles`, capa `ph`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:catastro_ph` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `partido` (int64)
- `partida` (int64)
- `codigo_nomenclatura` (string)
- `superficie_terreno` (int64)
- `superficie_edificado` (int64)
- `nomencla_parcela` (string)
- `etiqueta` (string)
- `circunscripcion` (int64)
- `seccion` (string)
- `chacra_numero` (int64)
- `chacra_letra` (string)
- `quinta_numero` (int64)
- `quinta_letra` (string)
- `fraccion_numero` (int64)
- `fraccion_letra` (string)
- `manzana_numero` (int64)
- `manzana_letra` (string)
- `parcela_numero` (int64)
- `parcela_letra` (string)
- `longitud` (double)
- `latitud` (double)
- `calle_frente` (string)
- `altura_frente` (string)
- `barrio` (string)
- `localidad` (string)
- `fuente` (string)
- `actualizacion` (string)
- `zonificacion` (string)
- `pluscode` (string)
- `situacion_administrativa` (string)
- `observaciones` (string)
- `numero_inmueble` (int64)
- `partida_origen` (int64)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
seccion: B | C | A | D | G | 0 | H | E | F | K | J | L | M | Z | N
localidad: Pergamino | El Socorro (Villa Angélica) | Manuel Ocampo | Urquiza (Juan Anchorena) | Guerrico | La Violeta | Rural | Acevedo | Mariano Alfonzo | Fontezuela | Rancagua
actualizacion: 2025-05-26Z | 2025-07-07Z | 2025-07-08Z | 2025-08-21Z | 2025-06-26Z
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/ph.parquet')
LIMIT 5;
```

### Registros por `seccion`

```sql
SELECT "seccion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/ph.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/ph.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/ph.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/ph.parquet')
WHERE bbox.xmin >= -60.5746 AND bbox.xmax <= -60.4397
  AND bbox.ymin >= -33.8831 AND bbox.ymax <= -33.8091;
```

### Unión con `catastro/parcela` por `partida`

```sql
SELECT t."partida", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/ph/ph.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet') AS r
  ON CAST(t."partida" AS VARCHAR) = CAST(r."partida" AS VARCHAR)
GROUP BY ALL
ORDER BY registros DESC
LIMIT 10;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `catastro/parcela`, por `partida`. Hay valores de `partida` que coinciden en las dos colecciones.
- `limites/barrios_y_pueblos`, por intersección espacial.
