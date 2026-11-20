# Guía para agentes — Luminarias en vía pública

`vialidad/luminarias`: puntos. Luminarias en vía pública del Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/luminarias/luminarias.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/luminarias/luminarias.pmtiles`, capa `luminarias`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/vialidad/luminarias/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:luminarias` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `id_gps` (int64)
- `id_bbdd` (int64)
- `id_asociado` (int64)
- `ele_gps` (double)
- `time_gps` (string)
- `name_gps` (int64)
- `modulo_gps` (string)
- `planilla_gps` (int64)
- `longitud` (double)
- `latitud` (double)
- `calle` (string)
- `altura_domicilio` (string)
- `altura_inicial` (int64)
- `altura_final` (int64)
- `barrio` (string)
- `observaciones` (string)
- `lado` (string)
- `tipo_vereda` (string)
- `arboles` (string)
- `observaciones_bbdd` (string)
- `soporte_luminaria` (string)
- `ancho_vereda` (double)
- `tipo_lampara` (string)
- `cantidad_lamparas` (decimal128(38, 0))
- `potencia_lampara` (int64)
- `detalle` (string)
- `fecha_actualizacion` (string)
- `actualizador` (string)
- `fuente` (string)
- `recambio_led` (string)
- `localidad` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
lado: Impar | Par | Centro
tipo_vereda: Verde | Mixta o ajardinada | Embaldosada
arboles: Si | No
soporte_luminaria: Columna de caño BAJA | Columna de caño MEDIA | Columna de madera con brazo | Columna de caño ALTA | Paleta BAJA adosada a caño | Colgante | Columna de caño extra BAJA
tipo_lampara: LED | SODIO | ninguna | sin datos
fuente: Control de Gestión | Imagen aerea 2022 | Imagen aerea 2020 | Delegación Pinzon | Delegación Alfonso | Delegación Guerrico | CELP | Delegación Acevedo | Desarrollo Urbano | Delegación La Violeta
recambio_led: ejecutado_2016-2020 | licitado_2022 | licitado_2024 | ejecutado_2022 | ejecutado_2021 | licitado_2025
localidad: Pergamino | Manuel Ocampo | El Socorro (Villa Angélica) | Alfonzo | Urquiza | Acevedo | Guerrico | La Violeta | Fontezuela | Rancagua | Juan Andrés de la Peña | Pinzon | Mariano Benítez | Villa San José de rancagua | Ayerza
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/luminarias/luminarias.parquet')
LIMIT 5;
```

### Registros por `lado`

```sql
SELECT "lado", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/luminarias/luminarias.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `tipo_vereda`

```sql
SELECT "tipo_vereda", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/luminarias/luminarias.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/luminarias/luminarias.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/vialidad/luminarias/luminarias.parquet')
WHERE bbox.xmin >= -60.5741 AND bbox.xmax <= -60.4371
  AND bbox.ymin >= -33.9193 AND bbox.ymax <= -33.8303;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
