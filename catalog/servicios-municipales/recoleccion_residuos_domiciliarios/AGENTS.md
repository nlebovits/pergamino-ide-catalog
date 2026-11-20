# Guía para agentes — Recoleccion de residuos domiciliarios

`servicios-municipales/recoleccion_residuos_domiciliarios`: polígonos. Rutas de recolección de residuos domiciliarios desde 2025, empresa ENTRE para todo el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/recoleccion_residuos_domiciliarios.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/recoleccion_residuos_domiciliarios.pmtiles`, capa `recoleccion_residuos_domiciliarios`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:recoleccion_residuos_domiciliarios` de GeoNode.

## Esquema

- `id` (int64)
- `nombre` (string)
- `turno` (string)
- `lunes` (string)
- `martes` (string)
- `miercoles` (string)
- `jueves` (string)
- `viernes` (string)
- `sabado` (string)
- `domingo` (int64)
- `observacion` (string)
- `horario` (string)
- `numero_ruta` (int64)
- `etiqueta` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
turno: dia | noche
lunes: 1 | 0 | si
martes: 0 | 1 | si
miercoles: 1 | 0 | si
jueves: 0 | 1 | si
viernes: 1 | 0 | si
sabado: 0 | 1 | si
horario: 05 a 13 | 13 a 21 | 21 a 04
etiqueta: Lu, Mi, Vi | Ma, Ju, Sa | Lu, Ju | Ma, Vi | Mi, Sa | Lu, Ma, Mi, Ju, Vi, Sa | Ma, Ju, Do | Lu, Ma, Mi, Ju, Vi, Do
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/recoleccion_residuos_domiciliarios.parquet')
LIMIT 5;
```

### Registros por `turno`

```sql
SELECT "turno", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/recoleccion_residuos_domiciliarios.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `lunes`

```sql
SELECT "lunes", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/recoleccion_residuos_domiciliarios.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/recoleccion_residuos_domiciliarios.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/recoleccion_residuos_domiciliarios/recoleccion_residuos_domiciliarios.parquet')
WHERE bbox.xmin >= -60.5732 AND bbox.xmax <= -60.4364
  AND bbox.ymin >= -33.8852 AND bbox.ymax <= -33.8098;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
