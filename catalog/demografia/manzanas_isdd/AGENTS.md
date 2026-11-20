# Guía para agentes — Densidad de población por Mapeo Dasimétrico - Censo 2022

`demografia/manzanas_isdd`: polígonos. Este conjunto de datos georreferenciados presenta la estimación espacial desagregada de la población, los hogares y diversos indicadores de vulnerabilidad sociohabitacional a escala de manzana urbana para el Partido de Pergamino (ISDD). El dataset ha sido generado utilizando como fuente primaria los microdatos del Censo Nacional de Población, Hogares y Viviendas 2022 a nivel de radio censal, y como fuentes auxiliares el dataset de OpenBuildingMap (OBM) y el catastro local.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/manzanas_isdd/manzanas_isdd.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/demografia/manzanas_isdd/manzanas_isdd.pmtiles`, capa `manzanas_isdd`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/demografia/manzanas_isdd/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:manzanas_isdd` de GeoNode.

## Esquema

- `fid` (int64)
- `codigo` (double)
- `viviendas_2020` (int64)
- `domicilios_2020` (int64)
- `clasificacion` (string)
- `seccion` (int64)
- `barrio` (string)
- `barrio_tipo` (string)
- `poblacion_radio` (int64)
- `hogares_radio` (int64)
- `area_m2` (double)
- `poblacion_isdd` (double)
- `hogares_isdd` (double)
- `redcode` (double)
- `poblacion_isdd_radio` (double)
- `hogares_isdd_radio` (double)
- `coeficiente_mz_radio_isdd` (double)
- `h_nbi_si` (double)
- `p_nbi_si` (double)
- `h_hacina_crit` (double)
- `p_hacina_crit` (double)
- `h_inmat_def` (double)
- `p_inmat_def` (double)
- `h_nbi_h15_h17_h18` (double)
- `p_nbi_h15_h17_h18` (double)
- `p_sin_cob` (double)
- `p_edad_0_14` (double)
- `p_edad_65_mas` (double)
- `h_viv_def` (double)
- `p_viv_def` (double)
- `h_agua_sin_red` (double)
- `p_agua_sin_red` (double)
- `densidad_isdd_hab_ha` (double)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
clasificacion: urbana | periurbana
barrio_tipo: Abierto | Pueblo | Cerrado
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/manzanas_isdd/manzanas_isdd.parquet')
LIMIT 5;
```

### Registros por `clasificacion`

```sql
SELECT "clasificacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/manzanas_isdd/manzanas_isdd.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `barrio_tipo`

```sql
SELECT "barrio_tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/manzanas_isdd/manzanas_isdd.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/manzanas_isdd/manzanas_isdd.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/demografia/manzanas_isdd/manzanas_isdd.parquet')
WHERE bbox.xmin >= -60.5748 AND bbox.xmax <= -60.4375
  AND bbox.ymin >= -33.9173 AND bbox.ymax <= -33.8294;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
