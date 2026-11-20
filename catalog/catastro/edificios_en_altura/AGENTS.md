# Guía para agentes — Edificios en altura

`catastro/edificios_en_altura`: puntos. Edificios de 3 o más pisos en el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/edificios_en_altura.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/edificios_en_altura.pmtiles`, capa `edificios_en_altura`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:edificios_en_altura` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `tipo` (string)
- `pisos` (int64)
- `cocheras` (string)
- `te` (string)
- `calle` (string)
- `numero` (int64)
- `estado` (string)
- `nombre_edificio` (string)
- `codigo_nomenclatura` (string)
- `tipo_predominante` (string)
- `tipo_complementario` (string)
- `azotea` (string)
- `escalera_tipo` (string)
- `departamento_por_piso` (int64)
- `accesibilidad` (string)
- `departamentos_pb` (int64)
- `id_edificio_dc` (int64)
- `ascensores` (int64)
- `categoria` (string)
- `observaciones` (string)
- `altura_aproximada` (int64)
- `ph` (string)
- `cantidad_viviendas` (int64)
- `cantidad_pisos` (int64)
- `cantidad_dormitorios` (string)
- `expediente_obra` (string)
- `final_obra` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
tipo: vivienda | comercio | educacion | hotel | clinica | mixto | municipalidad | sin dato | club | religion | justicia | salud | cultura | otro
cocheras: si | no | 1 | 5 | 8
estado: finalizado | construccion | en construcción
tipo_complementario: comercio | ninguna | oficina | administrativo | ninguno | vivienda
escalera_tipo: interna | interna externa_emergencia
accesibilidad: no | si
categoria: privado | publico | público
ph: si | no_corresponde | no | sin_dato
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/edificios_en_altura.parquet')
LIMIT 5;
```

### Registros por `tipo`

```sql
SELECT "tipo", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/edificios_en_altura.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `cocheras`

```sql
SELECT "cocheras", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/edificios_en_altura.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/edificios_en_altura.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/edificios_en_altura/edificios_en_altura.parquet')
WHERE bbox.xmin >= -60.5176 AND bbox.xmax <= -60.4777
  AND bbox.ymin >= -33.8299 AND bbox.ymax <= -33.7767;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
