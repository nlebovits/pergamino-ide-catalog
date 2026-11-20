# Guía para agentes — Barrios y pueblos

`limites/barrios_y_pueblos`: polígonos. Barrios y pueblos del Partido de Pergamino con dato de cantidad de habitantes y hogares estimada al 2023.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.pmtiles`, capa `barrios_y_pueblos`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:barrios_y_pueblos` de GeoNode.

## Esquema

- `id` (int64)
- `nombre` (string)
- `tipo` (string)
- `area` (double)
- `ordenanza` (string)
- `delimitacion` (string)
- `distrito` (string)
- `color_id` (int64)
- `localidad` (string)
- `manzanas` (int64)
- `seccion` (string)
- `primera_letra` (string)
- `habitantes_2023_ISDD` (double)
- `hogares_2023_ISDD` (double)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tipo: Abierto | Pueblo | Mixto | Restringido
ordenanza: 8850-18 | 9159-19
distrito: norte | rural | sur | este | oeste | centro
localidad: Pergamino | Acevedo | El Socorro (Villa Angélica) | Fontezuela | Guerrico | Juan Andrés de la Peña | La Violeta | Manuel Ocampo | Mariano Alfonzo | Mariano Benítez | Pinzón | Rancagua | Urquiza (Juan Anchorena) | Villa San José de Rancagua
seccion: 1 | 4 | 2 | 3 | 3 y 4 | 2 y 3
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet')
LIMIT 5;
```

### Registros por `tipo`

```sql
SELECT "tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `ordenanza`

```sql
SELECT "ordenanza", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet')
WHERE bbox.xmin >= -60.5748 AND bbox.xmax <= -60.4375
  AND bbox.ymin >= -33.9182 AND bbox.ymax <= -33.8307;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.
