# Guía para agentes — Edificaciones detectadas con IA

`catastro/edificaciones_automaticas`: polígonos. Edificaciones detectadas automáticamente para el Partido de Pergamino por google research mediante entrenamiento IA: Open Buildings 2023. Cada edificio posee un coeficiente de certeza, mientras más cercano a 1 se encuentre, mayor será su probabilidad de que efectivamente se trate de una edificación.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificaciones_automaticas/edificaciones_automaticas.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificaciones_automaticas/edificaciones_automaticas.pmtiles`, capa `edificaciones_automaticas`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificaciones_automaticas/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:edificaciones_automaticas` de GeoNode.

## Esquema

- `id` (int64)
- `latitude` (double)
- `longitude` (double)
- `area_in_meters` (double)
- `confidence` (double)
- `full_plus_code` (string)
- `nombre` (string)
- `tipo` (string)
- `localidad` (string)
- `nomencla` (string)
- `partida` (double)
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
- `tipo_objeto_siser` (int64)
- `numero_objeto_siser` (decimal128(38, 0))
- `subpar_uf` (int64)
- `zonificacion` (string)
- `matricula` (string)
- `n` (int64)
- `distance` (double)
- `altura_minima` (int64)
- `altura_promedio` (int64)
- `altura_maxima` (int64)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tipo: Abierto | Pueblo | Mixto | Restringido
localidad: Pergamino | Rural | Acevedo | El Socorro (Villa Angélica) | Urquiza (Juan Anchorena) | Mariano Alfonzo | Manuel Ocampo | La Violeta | Rancagua | Pinzón | Guerrico | Fontezuela | Mariano Benítez | Juan Andrés de la Peña | Villa San José de Rancagua
chacra_letra: D | 0 | B
fraccion_letra: B | 0 | A
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificaciones_automaticas/edificaciones_automaticas.parquet')
LIMIT 5;
```

### Registros por `tipo`

```sql
SELECT "tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificaciones_automaticas/edificaciones_automaticas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificaciones_automaticas/edificaciones_automaticas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificaciones_automaticas/edificaciones_automaticas.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificaciones_automaticas/edificaciones_automaticas.parquet')
WHERE bbox.xmin >= -60.6182 AND bbox.xmax <= -60.4593
  AND bbox.ymin >= -33.9121 AND bbox.ymax <= -33.7918;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
