# Guía para agentes — Dependencias municipales

`servicios-municipales/dependencias_municipales`: puntos. Capa de dependencias y oficinas generales de la Municipalidad, para todo el Partido de Pergamino, con o sin atención al público.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/dependencias_municipales/dependencias_municipales.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/dependencias_municipales/dependencias_municipales.pmtiles`, capa `dependencias_municipales`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/dependencias_municipales/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:dependencias_municipales` de GeoNode.

## Esquema

- `geometry` (binary)
- `id` (int64)
- `telefono` (string)
- `dependencia` (string)
- `domicilio` (string)
- `internos` (string)
- `area` (string)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
area: Secretaria de Desarrollo Social | Secretaria Privada | Secretaria de Hacienda y Finanzas | Secretaria de Gobierno | Secretaria de Servicios Publicos | Secretaria de Modernizacion, Innovacion y Tecnologia | Honorable Concejo Deliberante | Secretaria de Seguridad | Secretaria de Desarrollo Urbano | Secretaria de Produccion y Desarrollo | Conmutador | Secretaria de Salud | Secretaria de Tierras, Vivienda y Obra Publica Social | Secretaria de Educacion
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/dependencias_municipales/dependencias_municipales.parquet')
LIMIT 5;
```

### Registros por `area`

```sql
SELECT "area", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/dependencias_municipales/dependencias_municipales.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/dependencias_municipales/dependencias_municipales.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/servicios-municipales/dependencias_municipales/dependencias_municipales.parquet')
WHERE bbox.xmin >= -60.6554 AND bbox.xmax <= -60.5644
  AND bbox.ymin >= -33.8238 AND bbox.ymax <= -33.7738;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `limites/barrios_y_pueblos`, por intersección espacial.
