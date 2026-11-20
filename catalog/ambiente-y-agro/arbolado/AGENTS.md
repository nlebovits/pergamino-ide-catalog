# Guía para agentes — Arbolado (2013)

`ambiente-y-agro/arbolado`: puntos. Capa de árboles en veredas censados en 2013 para el área urbana de la Ciudad de Pergamino. Se excluyen plazas y parques.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/arbolado.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/arbolado.pmtiles`, capa `arbolado`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:arbolado` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `ele` (double)
- `time` (string)
- `name` (int64)
- `modulo` (string)
- `id_gps` (int64)
- `id_asociad` (int64)
- `espacio` (string)
- `altura` (string)
- `estado_gen` (string)
- `observacio` (string)
- `planilla` (int64)
- `altura_ini` (int64)
- `altura_fin` (int64)
- `lado` (string)
- `id_bbdd` (int64)
- `obs_data` (string)
- `circunsf` (double)
- `diametro` (double)
- `vereda` (string)
- `numeracion_aproximada` (double)
- `especie_arbol` (string)
- `elementos_estranos` (string)
- `tipo_elementos_estranos` (string)
- `descripcion_elementos_estranos` (string)
- `clavel_del_aire` (string)
- `calle` (string)
- `ancho_vereda` (double)
- `dano_en_vereda` (string)
- `vereda_levantada` (string)
- `fuente` (string)
- `actualizacion` (string)
- `barrio` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
espacio: ajardinada | sin_cazuela | con_cazuela | sin_datos
altura: hasta 6 metros | de 6 a 15 metros | más de 15 metros | sin_datos
estado_gen: bueno | regular | muerto | malo
lado: par | impar | sin_dato
vereda: Mixta | Verde | Embaldosada | sin_dato
elementos_estranos: no | si
tipo_elementos_estranos: Residuos | Metálicos | Otros | Luminarias y publicidad
clavel_del_aire: si | no
dano_en_vereda: no | medio | bajo | alto | sin_dato
vereda_levantada: no | si | sin_dato
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/arbolado.parquet')
LIMIT 5;
```

### Registros por `espacio`

```sql
SELECT "espacio", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/arbolado.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `altura`

```sql
SELECT "altura", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/arbolado.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/arbolado.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/arbolado/arbolado.parquet')
WHERE bbox.xmin >= -60.5879 AND bbox.xmax <= -60.5627
  AND bbox.ymin >= -33.8982 AND bbox.ymax <= -33.8857;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
