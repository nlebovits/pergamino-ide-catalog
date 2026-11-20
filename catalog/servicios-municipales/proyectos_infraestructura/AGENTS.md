# Guía para agentes — Proyectos de infraestructura vial

`servicios-municipales/proyectos_infraestructura`: líneas. Proyectos de nfraestructura urbana sobre las vías de circulación: cordón cuneta y pavimentación para el Partido de Pergamino.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/proyectos_infraestructura.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/proyectos_infraestructura.pmtiles`, capa `proyectos_infraestructura`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:proyectos_infraestructura` de GeoNode.

## Esquema

- `id` (int64)
- `nombre` (string)
- `impar_ini` (int64)
- `impar_fin` (int64)
- `par_ini` (int64)
- `par_fin` (int64)
- `clase` (string)
- `barrio` (string)
- `etiqueta` (string)
- `localidad` (string)
- `longitud` (int64)
- `ancho_real` (double)
- `ancho_calzada` (double)
- `material_calzada` (string)
- `cordon_cuneta` (string)
- `pav_etapa` (double)
- `cc_etapa` (double)
- `proyecto_infraestructura` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
clase: CALLE | RESTRINGIDO | CAMINO | AVENIDA | RUTA | PUENTE | ENLACE | ACCESO | PEATONAL | COLECTORA | AU | FFCC-PEATONAL | PUENTE-PEATONAL
material_calzada: tierra | asfalto | hormigon | escoriado | adoquinado | metal
cordon_cuneta: ambos | ninguno | no_corresponde | par | impar
proyecto_infraestructura: asfalto | cordon | cordon_y_asfalto
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/proyectos_infraestructura.parquet')
LIMIT 5;
```

### Registros por `clase`

```sql
SELECT "clase", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/proyectos_infraestructura.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `material_calzada`

```sql
SELECT "material_calzada", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/proyectos_infraestructura.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/proyectos_infraestructura.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/proyectos_infraestructura/proyectos_infraestructura.parquet')
WHERE bbox.xmin >= -60.6220 AND bbox.xmax <= -60.4609
  AND bbox.ymin >= -33.9274 AND bbox.ymax <= -33.8026;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
