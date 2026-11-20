# Guía para agentes — Aeropuertos y aeródromos

`transporte/aeropuertos`: puntos. Capa de aeropuertos y aeropistas declaradas en Pergamino y alrededores.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/aeropuertos.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/aeropuertos.pmtiles`, capa `aeropuertos`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:aeropuertos` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `local` (string)
- `oaci` (string)
- `iata` (string)
- `tipo` (string)
- `denominacion` (string)
- `coordenadas` (string)
- `latitud` (double)
- `longitud` (double)
- `elev` (double)
- `uom_elev` (string)
- `ref` (string)
- `distancia_ref` (double)
- `direccion_ref` (string)
- `condicion` (string)
- `control` (string)
- `region` (string)
- `fir` (string)
- `uso` (string)
- `trafico` (string)
- `sna` (string)
- `concesionado` (string)
- `provincia` (string)
- `inhab` (string)
- `fuente` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tipo: Aeródromo | Helipuerto
condicion: PRIVADO | PUBLICO
control: NOCONTROL | AERADIO
uso: CIVIL | AEROAPP | ULM
sna: NO | SI
provincia: BUENOS AIRES | SANTA FÉ
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/aeropuertos.parquet')
LIMIT 5;
```

### Registros por `tipo`

```sql
SELECT "tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/aeropuertos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `condicion`

```sql
SELECT "condicion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/aeropuertos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/aeropuertos.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/transporte/aeropuertos/aeropuertos.parquet')
WHERE bbox.xmin >= -60.6944 AND bbox.xmax <= -60.2860
  AND bbox.ymin >= -34.0116 AND bbox.ymax <= -33.6900;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
