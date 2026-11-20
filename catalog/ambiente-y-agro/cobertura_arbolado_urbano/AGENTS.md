# Guía para agentes — Cobertura del arbolado urbano

`ambiente-y-agro/cobertura_arbolado_urbano`: polígonos. Dataset que contiene las cobertura verde, o cobertura de follaje arbóreo de las áreas urbanas del Partido de Pergamino. La obtención del dato se basó en detección por IA, con correcciones manuales

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cobertura_arbolado_urbano/cobertura_arbolado_urbano.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cobertura_arbolado_urbano/cobertura_arbolado_urbano.pmtiles`, capa `cobertura_arbolado_urbano`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cobertura_arbolado_urbano/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:cobertura_arbolado_urbano` de GeoNode.

## Esquema

- `id` (int64)
- `localidad` (string)
- `barrio` (string)
- `area` (double)
- `perimetro` (double)
- `espacio_verde` (string)
- `metodo_deteccion` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
localidad: Pergamino | Manuel Ocampo | Acevedo | El Socorro (Villa Angélica) | Rancagua | Urquiza (Juan Anchorena) | Mariano Alfonzo | La Violeta | Pinzón | Guerrico | Fontezuela | Mariano Benítez | Juan Andrés de la Peña
espacio_verde: no | si
metodo_deteccion: automatica | manual | correccion
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cobertura_arbolado_urbano/cobertura_arbolado_urbano.parquet')
LIMIT 5;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cobertura_arbolado_urbano/cobertura_arbolado_urbano.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `espacio_verde`

```sql
SELECT "espacio_verde", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cobertura_arbolado_urbano/cobertura_arbolado_urbano.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cobertura_arbolado_urbano/cobertura_arbolado_urbano.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/cobertura_arbolado_urbano/cobertura_arbolado_urbano.parquet')
WHERE bbox.xmin >= -60.5748 AND bbox.xmax <= -60.4375
  AND bbox.ymin >= -33.8841 AND bbox.ymax <= -33.8077;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
