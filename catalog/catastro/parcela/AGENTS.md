# Guía para agentes — Catastro parcela

`catastro/parcela`: polígonos. Capa de parcelas catastrales del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.pmtiles`, capa `parcela`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:catastro_parcela` de GeoNode.

## Esquema

- `id` (int64)
- `nomencla` (string)
- `tpa` (string)
- `partida` (decimal128(38, 0))
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
- `lon` (double)
- `lat` (double)
- `calle_frente` (string)
- `altura_frente` (string)
- `codigo_postal` (int64)
- `barrio` (string)
- `localidad` (string)
- `fuente` (string)
- `actualizacion` (string)
- `zonificacion` (string)
- `pluscode` (string)
- `situacion_administrativa` (string)
- `matricula` (string)
- `factor_ocupacion_parcela` (int64)
- `area_m2` (int64)
- `area_ha` (double)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tpa: Urbano | Rural
chacra_letra: 0 | B | D
fraccion_letra: B | A | 0
localidad: Pergamino | Rural | Acevedo | Manuel Ocampo | El Socorro (Villa Angélica) | Mariano Alfonzo | Urquiza (Juan Anchorena) | Rancagua | La Violeta | Pinzón | Guerrico | Mariano Benítez | Fontezuela | Villa San José de Rancagua
situacion_administrativa: Aprobada y publicada por ARBA | En proceso de subdivisión | Subdividida pero no publicada | Subdivisión de UF en trámite | NO FIGURA EN ARBA | Figura como macizo en ARBA
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet')
LIMIT 5;
```

### Registros por `tpa`

```sql
SELECT "tpa", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `chacra_letra`

```sql
SELECT "chacra_letra", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet')
WHERE bbox.xmin >= -60.6220 AND bbox.xmax <= -60.4610
  AND bbox.ymin >= -33.9220 AND bbox.ymax <= -33.7947;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
