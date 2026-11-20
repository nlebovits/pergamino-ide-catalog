# Guía para agentes — Rampas de acceso discapacidad motriz

`vialidad/rampas_acceso_veredas`: puntos. Rampas de acceso a veredas para personas con dificultades motrices o carritos de bebés/infantes para todo el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/rampas_acceso_veredas/rampas_acceso_veredas.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/rampas_acceso_veredas/rampas_acceso_veredas.pmtiles`, capa `rampas_acceso_veredas`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/rampas_acceso_veredas/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:rampas_acceso_discapacidad` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `direccion` (string)
- `estado` (string)
- `organismo` (string)
- `año` (int64)
- `baranda` (string)
- `tipo` (string)
- `observaciones` (string)
- `barrio` (string)
- `localidad` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
estado: bueno | regular | malo
organismo: Consejo Municipal del Discapacitado | dirección de Infraestructura | particular
baranda: no | si
tipo: premoldeado | verde | pavimento | baldosa
localidad: Pergamino | Acevedo | Mariano ALfonzo | El Socorro | Manuel Ocampo | La Violeta | Guerrico | Rancagua | Urquiza (Juan Anchorena)
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/rampas_acceso_veredas/rampas_acceso_veredas.parquet')
LIMIT 5;
```

### Registros por `estado`

```sql
SELECT "estado", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/rampas_acceso_veredas/rampas_acceso_veredas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `organismo`

```sql
SELECT "organismo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/rampas_acceso_veredas/rampas_acceso_veredas.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/rampas_acceso_veredas/rampas_acceso_veredas.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/rampas_acceso_veredas/rampas_acceso_veredas.parquet')
WHERE bbox.xmin >= -60.5704 AND bbox.xmax <= -60.4362
  AND bbox.ymin >= -33.8820 AND bbox.ymax <= -33.8090;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
