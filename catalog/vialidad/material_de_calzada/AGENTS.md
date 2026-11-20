# Guía para agentes — Material de calzada

`vialidad/material_de_calzada`: líneas. Describe el tipo de material mayoritario para las calles del Partido de Pergamino: adoquinado, asfalto, hormigón, escoriado, tierra y metálico.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/material_de_calzada.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/material_de_calzada.pmtiles`, capa `material_de_calzada`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:vista_callejero_1` de GeoNode.

## Esquema

- `id` (int64)
- `codigo` (int64)
- `ancho` (int64)
- `nombre` (string)
- `nombre_alt` (string)
- `pre_tipo` (string)
- `pre_dir` (string)
- `impar_ini` (int64)
- `impar_fin` (int64)
- `par_ini` (int64)
- `par_fin` (int64)
- `ruta` (string)
- `clase` (string)
- `sentido` (int64)
- `barrio` (string)
- `barrido` (decimal128(38, 0))
- `zona_barri` (string)
- `etiqueta` (string)
- `buffer` (int64)
- `t_etiq` (int64)
- `e_num_imp` (string)
- `e_num_par` (string)
- `localidad` (string)
- `long` (int64)
- `long_km` (double)
- `buff` (int64)
- `ordenanza` (string)
- `prog_ini` (double)
- `prog_fin` (double)
- `est_medido` (string)
- `cc_empresa` (string)
- `cc_fecha_inicio_obra` (string)
- `cc_fecha_fin_obra` (string)
- `cc_expediente` (string)
- `cc_etapa` (double)
- `pav_empresa` (string)
- `pav_fecha_inicio_obra` (string)
- `pav_fecha_fin_obra` (string)
- `pav_expediente` (string)
- `pav_etapa` (double)
- `velocidad_maxima` (int64)
- `cpa_impar` (string)
- `cpa_par` (string)
- `restriccion_estacionamiento` (string)
- `observaciones` (string)
- `nombre_corto` (string)
- `ancho_vereda_par` (double)
- `ancho_vereda_impar` (double)
- `tipo_vereda_par` (string)
- `tipo_vereda_impar` (string)
- `cob_cloacas_par` (string)
- `cob_cloacas_impar` (string)
- `cob_agua_par` (string)
- `cob_agua_impar` (string)
- `ancho_nominal` (int64)
- `ancho_real` (double)
- `ancho_calzada` (double)
- `id_calle` (int64)
- `lado_ciclovia` (string)
- `transitable` (string)
- `numero_reparto_facturacion` (int64)
- `nombre_completo` (string)
- `material_calzada` (string)
- `cordon_cuneta` (string)
- `proyecto_infraestructura` (string)
- `arbolado` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
pre_tipo: AV | BV | AU | PJE | PASEO
pre_dir: BIS | AV
clase: CALLE | RESTRINGIDO | CAMINO | AVENIDA | RUTA | PUENTE | ENLACE | ACCESO | PEATONAL | COLECTORA | AU | FFCC-PEATONAL | PUENTE-PEATONAL
zona_barri: SUR | CENTRO | ESTE | OESTE | NORTE | P PERGAMINENSES
est_medido: centro | micro | macro | macro_proyecto
cc_empresa: Argentina Hace | SANTA CELIA CONSTRUCCIONES S.R.L. | FIM | CELP | SANTA CELIA CONSTRUCCIONES S.R.L | AMOREBLA S.A. | COOP. DE TRABAJO SAN FRANCISCO SOLANO LIMITADA | Amorebla S.A. | COOP. DE TRABAJO SAN FRANCISCO SOLANO | D-1740/2018 | SANTA CELIA CONSUTRCCIONES S.R.L.
cc_expediente: D-1208/2018 | D-822/2018 | Licitación Provincia | D-1740/2018 | Licitación provincia | D/10211/2017
pav_empresa: CELP DIVISION VIAL | CELP Division Vial | 3_2024
pav_expediente: 8525-16 | 9892-17 | D-5101/2018
restriccion_estacionamiento: solo impar - 00:00 a 24:00 | total - 00:00 a 24:00 | total - 08:00 a 20:00 | impar - 00:00 a 24:00 | solo par - 00:00 a 24:00
tipo_vereda_par: Verde | Mixta | sin_dato | Embaldosada | no_corresponde
tipo_vereda_impar: Verde | Mixta | sin_dato | Embaldosada | no_corresponde
cob_cloacas_par: no_corresponde | total | duda | sin_cobertura | limite | sin_dato | parcial
cob_cloacas_impar: no_corresponde | total | duda | sin_cobertura | limite | sin_dato | parcial
cob_agua_par: no_corresponde | total | duda | sin_cobertura | limite | sin_dato | parcial
cob_agua_impar: no_corresponde | total | duda | sin_cobertura | limite | sin_dato | parcial
lado_ciclovia: no | par | impar
transitable: si | no
material_calzada: tierra | asfalto | hormigon | escoriado | adoquinado | metal
cordon_cuneta: ambos | ninguno | no_corresponde | par | impar
proyecto_infraestructura: asfalto | cordon | cordon_y_asfalto
arbolado: ambos | ninguno | impar | par | no_corresponde
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/material_de_calzada.parquet')
LIMIT 5;
```

### Registros por `pre_tipo`

```sql
SELECT "pre_tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/material_de_calzada.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `pre_dir`

```sql
SELECT "pre_dir", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/material_de_calzada.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/material_de_calzada.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/material_de_calzada.parquet')
WHERE bbox.xmin >= -60.6220 AND bbox.xmax <= -60.4609
  AND bbox.ymin >= -33.9274 AND bbox.ymax <= -33.8026;
```

### Unión con `vialidad/callejero` por `id_calle`

```sql
SELECT t."id_calle", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/material_de_calzada/material_de_calzada.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/callejero/callejero.parquet') AS r
  ON CAST(t."id_calle" AS VARCHAR) = CAST(r."id_calle" AS VARCHAR)
GROUP BY ALL
ORDER BY registros DESC
LIMIT 10;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `vialidad/callejero`, por `id_calle`. Hay valores de `id_calle` que coinciden en las dos colecciones.
- `limites/barrios_y_pueblos`, por intersección espacial.
