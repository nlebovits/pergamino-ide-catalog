# Guía para agentes — Zonificacion

`catastro/zonificacion`: polígonos. Capa de zonificación y uso del suelo para el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/zonificacion.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/zonificacion.pmtiles`, capa `zonificacion`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:zonificacion` de GeoNode.

## Esquema

- `id` (int64)
- `descripcion` (string)
- `designacion` (string)
- `categoria` (int64)
- `fos` (double)
- `fota` (double)
- `fotp` (double)
- `dena` (int64)
- `denp` (int64)
- `um2` (int64)
- `ul` (int64)
- `sm` (double)
- `lm` (double)
- `hmax` (string)
- `ud` (string)
- `uc` (string)
- `observaciones` (string)
- `distrito` (string)
- `fotp_prem` (double)
- `des_cat` (string)
- `actan` (string)
- `tipo_suelo` (string)
- `superficie_ha` (double)
- `zonas` (string)
- `u_c_r` (string)
- `ord_ma` (string)
- `dec_ma` (string)
- `ord_mod` (string)
- `dec_mod` (string)
- `fecha_ac` (string)
- `x` (int64)
- `y` (int64)
- `t_etiqueta` (int64)
- `localidad` (string)
- `ord_observaciones` (string)
- `urbano` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
hmax: 9,5 MTS | 16MTS
tipo_suelo: RESIDENCIAL | PRODUCTIVO - INTENSIVO | PRODUCTIVO INDUSTRIAL | ESPACIO VERDE | CORREDORES | UE - EQUIPAMIENTO | RESERVA | RECUPERACION | PRODUCTIVO - EXTENSIVO | RESIDENCIAL - ESPECIAL
zonas: RESIDENCIAL | AGROPECUARIA | INDUSTRIAL | ESPARCIMIENTO | COMERCIAL | USO ESPECIFICO | RESERVA | RECUPERACION | RESIDENCIAL EXTRAURBANA
u_c_r: URBANA | COMPLEMENTARIA | EV, ESPARCIMIENTO, RECREACION | USO ESPECIFICO | RURAL
ord_mod: 8591-17 EN PROCESO DE CONVALIDACION | 9003-18 | 7890-2013 | 8919-18 EN PROCESO DE CONVALIDACION | 9003-18, 9746/2023 | 9741-23 | 9741-23 EN PROCESO DE CONVALIDACION
dec_mod: EN PROCESO DE CONVALIDACION | Convalidado por Decreto Provincial Nº 183/2019
fecha_ac: 09/2016 | 01/2020 | 05/2017 | 07/2025 | 01/2019 | 08/2018 | 03/2020 | 07/2009 | 08/2024 | 12/2024
localidad: PERGAMINO | FONTEZUELA | GUERRICO | URQUIZA | ACEVEDO | J. A. DE LA PEÑA | MARIANO ALFONSO | RANCAGUA | LA VIOLETA | MANUEL OCAMPO | MARIANO BENITEZ | PINZON | EL SOCORRO | RURAL
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/zonificacion.parquet')
LIMIT 5;
```

### Registros por `hmax`

```sql
SELECT "hmax", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/zonificacion.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `tipo_suelo`

```sql
SELECT "tipo_suelo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/zonificacion.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/zonificacion.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/zonificacion/zonificacion.parquet')
WHERE bbox.xmin >= -60.6210 AND bbox.xmax <= -60.4601
  AND bbox.ymin >= -33.9225 AND bbox.ymax <= -33.7953;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
