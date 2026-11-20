# Guía para agentes — Dependencias de seguridad y acceso a la justicia

`seguridad/dependencias_seguridad`: puntos. Dependencias y destacamentos policiales y judiciales como comisarías, puestos de vigilancia, juzgados, tribunales, defensorías, oficinas administrativas para todo el Partido de Pergamino, tanto de jurisdición provincial, nacional o municipal.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/dependencias_seguridad.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/dependencias_seguridad.pmtiles`, capa `dependencias_seguridad`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:dependencias_seguridad` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `direccion` (string)
- `telefono` (string)
- `localidad` (string)
- `actualizacion` (string)
- `fuente` (string)
- `nombre` (string)
- `etiqueta` (string)
- `ambito` (string)
- `clase` (string)
- `jurisdiccion` (string)
- `especialidad` (string)
- `detalle` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
localidad: Pergamino | Fontezuela | Acevedo | El Socorro | El Socorro (Villa Alicia) | Guerrico | Juan A de la Peña | La Violeta | Manuel Ocampo | Mariano Benitez | Mariano H Alfonzo | Pinzon | Rancagua | Urquiza
actualizacion: 2026-05-13Z | 2026-09-22Z
fuente: Municipalidad de Pergamino | SCBA | Ministerio de Seguridad | Dataset PBA | ordenanza 9423-21
ambito: seguridad | justicia
clase: destacamento | juzgado | oficina administrativa | asesoria | comisaria | delegacion | camara | defensoria | tribunal | departamento
jurisdiccion: provincial | municipal | nacion
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/dependencias_seguridad.parquet')
LIMIT 5;
```

### Registros por `localidad`

```sql
SELECT "localidad", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/dependencias_seguridad.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `actualizacion`

```sql
SELECT "actualizacion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/dependencias_seguridad.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/dependencias_seguridad.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/seguridad/dependencias_seguridad/dependencias_seguridad.parquet')
WHERE bbox.xmin >= -60.5662 AND bbox.xmax <= -60.4334
  AND bbox.ymin >= -33.8794 AND bbox.ymax <= -33.8040;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
