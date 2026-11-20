# Guía para agentes — Carta de suelos Pergamino 1:50.000

`ambiente-y-agro/suelos_pergamino_50mil`: polígonos. Recorte de Cartas de Suelos República Argentina (INTA) para el Partido de Pergamino. El Plan Mapa de Suelos de la Región Pampeana en el año 1964 marca la etapa de mayor trascendencia del inventario de los suelos de nuestro país a escala de semidetalle y de reconocimiento (1:50.000 - 1:100.000). Las Cartas de Suelos de la Provincia de Buenos Aires son el resultado de este plan y la continuación de las tareas de relevamiento y cartografía de suelos hasta la actualidad.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/suelos_pergamino_50mil.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/suelos_pergamino_50mil.pmtiles`, capa `suelos_pergamino_50mil`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:suelos_pergamino_50mil` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `objectid_1` (int64)
- `objectid` (int64)
- `simbc` (string)
- `nombre_uc` (string)
- `tipo` (string)
- `serie1` (string)
- `porc1` (int64)
- `serie2` (string)
- `porc2` (int64)
- `serie3` (string)
- `porc3` (int64)
- `serie4` (string)
- `porc4` (int64)
- `serie5` (string)
- `porc5` (int64)
- `serie6` (string)
- `porc6` (int64)
- `fase1` (string)
- `fase2` (string)
- `fase3` (string)
- `fase4` (string)
- `fase5` (string)
- `fase6` (string)
- `paisaje` (string)
- `posic1` (string)
- `posic2` (string)
- `posic3` (string)
- `posic4` (string)
- `posic5` (string)
- `posic6` (int64)
- `cap_uso` (string)
- `taxo_ppal` (string)
- `taxo_2rio` (string)
- `taxo_3rio` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tipo: Consociacion | Comp Indif. | Complejo | Asociacion | GND
serie3: Las Gamas | Faustina | Santa Lucia | El Recuerdo | Gelly | Manantiales | Ramallo | Wheelwright
posic3: bajo | Bajo | pendiente | plano medio | Hoya y tendido
taxo_ppal: Argiudol tipico | Argiudol vertico | Complejo indiferenciado | Argiudol abruptico | Argiudol acuico | Natracualf molico | Natracualf tipico | Natracuol tipico | Paleudol tipico | Argiacuol vertico | Argialbol argiacuico | Lagunas | Miscelaneas
taxo_2rio: Argiudol tipico | Argiudol vertico | Natracualf tipico | Natralbol tipico | Argiudol abruptico | Natracualf molico | Argialbol argiacuico | Natracuol tipico | Paleudol tipico
taxo_3rio: Argiudol abruptico | Natracualf molico | Natracuol tipico | Natralbol tipico | Natracualf tipico | Argiudol vertico
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/suelos_pergamino_50mil.parquet')
LIMIT 5;
```

### Registros por `tipo`

```sql
SELECT "tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/suelos_pergamino_50mil.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `serie3`

```sql
SELECT "serie3", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/suelos_pergamino_50mil.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/suelos_pergamino_50mil.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/suelos_pergamino_50mil/suelos_pergamino_50mil.parquet')
WHERE bbox.xmin >= -60.6219 AND bbox.xmax <= -60.4609
  AND bbox.ymin >= -33.9226 AND bbox.ymax <= -33.7956;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
