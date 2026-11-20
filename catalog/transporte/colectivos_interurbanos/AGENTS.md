# Guía para agentes — Colectivos interurbanos

`transporte/colectivos_interurbanos`: líneas. Lineas de colectivos interurbanos que conectan el Partido de Pergamino con Partidos aledaños.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/colectivos_interurbanos/colectivos_interurbanos.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/transporte/colectivos_interurbanos/colectivos_interurbanos.pmtiles`, capa `colectivos_interurbanos`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/colectivos_interurbanos/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:colectivos_interurbanos` de GeoNode.

## Esquema

- `id` (int64)
- `empresa` (string)
- `ruta` (string)
- `linea` (string)
- `tramo` (string)
- `recorrido` (string)
- `comentario` (string)
- `duracion` (int64)
- `acumulada` (int64)
- `frecuencia` (int64)
- `nombre` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
empresa: EVHSA | 13 de Noviembre | La Nueva Perla | El Acuerdo
ruta: Conesa-Pergamino | Pergamino-Conesa | Ruta 32 | Ruta 188 | Ruta 8 | Acceso Benitez | Bv. Colón
linea: 227 | 345 | Linea 2 | 330 | 368
recorrido: Vuelta | Ida | Ida-alternativa | Vuelta-alternativa
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/colectivos_interurbanos/colectivos_interurbanos.parquet')
LIMIT 5;
```

### Registros por `empresa`

```sql
SELECT "empresa", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/colectivos_interurbanos/colectivos_interurbanos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `ruta`

```sql
SELECT "ruta", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/colectivos_interurbanos/colectivos_interurbanos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/colectivos_interurbanos/colectivos_interurbanos.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/colectivos_interurbanos/colectivos_interurbanos.parquet')
WHERE bbox.xmin >= -60.7048 AND bbox.xmax <= -60.5038
  AND bbox.ymin >= -34.0149 AND bbox.ymax <= -33.8753;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
