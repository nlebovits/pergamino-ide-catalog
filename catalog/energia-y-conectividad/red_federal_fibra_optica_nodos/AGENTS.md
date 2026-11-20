# Guía para agentes — Nodos de la Red Federal de Fibra Óptica

`energia-y-conectividad/red_federal_fibra_optica_nodos`: puntos. Capa de nodos de la Red Federal de Fibra Óptica de Argentina (REFEFO) en un radio de 50km desde el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/red_federal_fibra_optica_nodos/red_federal_fibra_optica_nodos.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/red_federal_fibra_optica_nodos/red_federal_fibra_optica_nodos.pmtiles`, capa `red_federal_fibra_optica_nodos`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/red_federal_fibra_optica_nodos/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:red_federal_fibra_optica_nodos` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `fid` (int64)
- `cuicom` (int64)
- `nivacc` (string)
- `localidad` (string)
- `departamen` (string)
- `provincia` (string)
- `operat` (string)
- `observ` (string)
- `longitud` (double)
- `latitud` (double)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
departamen: Pergamino | Rosario | Constitución | Ramallo | Salto | San Nicolas | Arrecifes | Capitán Sarmiento | Chacabuco | Colón | Rojas | San Pedro | Junin
provincia: Buenos Aires | Santa Fe
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/red_federal_fibra_optica_nodos/red_federal_fibra_optica_nodos.parquet')
LIMIT 5;
```

### Registros por `departamen`

```sql
SELECT "departamen", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/red_federal_fibra_optica_nodos/red_federal_fibra_optica_nodos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `provincia`

```sql
SELECT "provincia", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/red_federal_fibra_optica_nodos/red_federal_fibra_optica_nodos.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/red_federal_fibra_optica_nodos/red_federal_fibra_optica_nodos.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/energia-y-conectividad/red_federal_fibra_optica_nodos/red_federal_fibra_optica_nodos.parquet')
WHERE bbox.xmin >= -60.5154 AND bbox.xmax <= -60.2233
  AND bbox.ymin >= -34.0011 AND bbox.ymax <= -33.7098;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
