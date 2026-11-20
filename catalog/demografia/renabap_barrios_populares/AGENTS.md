# Guía para agentes — Renabap barrios populares

`demografia/renabap_barrios_populares`: polígonos. Barrios populares relevados por RENABAP, en el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/renabap_barrios_populares/renabap_barrios_populares.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/demografia/renabap_barrios_populares/renabap_barrios_populares.pmtiles`, capa `renabap_barrios_populares`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/renabap_barrios_populares/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:renabap_barrios_populares` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `fid` (int64)
- `renabap_id` (int64)
- `nombre_barrio` (string)
- `provincia` (string)
- `departamento` (string)
- `localidad` (string)
- `cantidad_familias_aproximada` (int64)
- `cantidad_viviendas_aproximadas` (int64)
- `decada_de_creacion` (string)
- `anio_de_creacion` (int64)
- `energia_electrica` (string)
- `efluentes_cloacales` (string)
- `agua_corriente` (string)
- `cocina` (string)
- `calefaccion` (string)
- `situacion_dominial` (string)
- `clasificacion_barrio` (string)
- `superficie_m2` (int64)
- `actualizacion` (string)
- `observaciones` (string)
- `revision` (int64)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
localidad: Pergamino | Rancagua
decada_de_creacion: Década 2000 | Década 1990 | Década 2010 | Década 1980 | Década 1920 | Década 1930 | Década 1950
efluentes_cloacales: Desagüe sólo a pozo negro/ciego u hoyo | Desagüe a cámara séptica y pozo ciego
agua_corriente: Conexión irregular a la red de agua | Bomba de agua de pozo domiciliaria | Bomba de agua de pozo comunitaria | Conexión formal a la red de agua con factura | Conexión regular a la red de agua pero sin factura
calefaccion: Sin Datos | Leña o carbón | Energía eléctrica | Gas en garrafa
clasificacion_barrio: Asentamiento | Villa
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/renabap_barrios_populares/renabap_barrios_populares.parquet')
LIMIT 5;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/renabap_barrios_populares/renabap_barrios_populares.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `decada_de_creacion`

```sql
SELECT "decada_de_creacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/renabap_barrios_populares/renabap_barrios_populares.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/renabap_barrios_populares/renabap_barrios_populares.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/renabap_barrios_populares/renabap_barrios_populares.parquet')
WHERE bbox.xmin >= -60.5334 AND bbox.xmax <= -60.4926
  AND bbox.ymin >= -33.9998 AND bbox.ymax <= -33.9531;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
