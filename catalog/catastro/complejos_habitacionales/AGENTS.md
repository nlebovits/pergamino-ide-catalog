# Guía para agentes — Complejos habitacionales

`catastro/complejos_habitacionales`: polígonos. Capa de complejos habitacionales existentes, en construcción y proyectados en el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/complejos_habitacionales/complejos_habitacionales.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/catastro/complejos_habitacionales/complejos_habitacionales.pmtiles`, capa `complejos_habitacionales`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/complejos_habitacionales/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:complejos_habitacionales` de GeoNode.

## Esquema

- `id` (int64)
- `complejo` (string)
- `barrio` (string)
- `tipo` (string)
- `plan` (string)
- `obs` (string)
- `nombre_alternativo` (string)
- `viviendas` (int64)
- `distrito` (string)
- `estado` (string)
- `habilitacion` (int64)
- `zonificacion` (string)
- `nomenclatura` (string)
- `a_prefactibilidad` (string)
- `b_visacion` (string)
- `c_proyecto_infraestructura` (string)
- `d_administrativa_y_obras` (string)
- `e_finalizacion` (string)
- `peso_color` (decimal128(38, 0))
- `area_planos_m2` (int64)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tipo: abierto | cerrado | mixto
plan: privado | Municipal, Secretaría de Tierra y Vivienda | Municipal | municipal | Instituto de la Vivienda | ProCreAr | Solares Urquiza I | Solares Urquiza II
distrito: Norte | Sur | Este | Pueblo | Oeste | Rural | Centro
estado: finalizado | en construccion | parcialmente construido | En trámite
zonificacion: R4 | R5c | R6 | AR (en proceso a CC) | AR (en proceso a R6) | CC | R5d | AR | AR (en proceso a R5c) | I1c | R5b
a_prefactibilidad: sin datos | en proceso | completado | avanzado | presentado
b_visacion: sin datos | en proceso | completado | no iniciado | avanzado | presentado
c_proyecto_infraestructura: sin datos | en proceso | no iniciado | avanzado | completado | presentado
d_administrativa_y_obras: sin datos | en proceso | no iniciado | completado | presentado
e_finalizacion: sin datos | no iniciado | en proceso | completado | presentado | avanzado
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/complejos_habitacionales/complejos_habitacionales.parquet')
LIMIT 5;
```

### Registros por `tipo`

```sql
SELECT "tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/complejos_habitacionales/complejos_habitacionales.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `plan`

```sql
SELECT "plan", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/complejos_habitacionales/complejos_habitacionales.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/complejos_habitacionales/complejos_habitacionales.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/complejos_habitacionales/complejos_habitacionales.parquet')
WHERE bbox.xmin >= -60.5784 AND bbox.xmax <= -60.5112
  AND bbox.ymin >= -33.8771 AND bbox.ymax <= -33.8062;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
