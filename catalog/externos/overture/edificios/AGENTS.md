# Guía para agentes — Edificios (Overture Maps)

Huellas de edificios de Overture Maps dentro del partido de Pergamino, referenciadas sin copiar los datos.

## Consulta

La vista ya aplica el recorte: prefiltro sobre la columna `bbox` (DuckDB descarta grupos de filas con las estadísticas del footer) y `ST_Intersects` con el límite oficial del partido. Requiere `spatial` y `httpfs`.

### Edificios por subtipo

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://data.source.coop/nlebovits/pergamino-ide/externos/overture/pergamino_overture.ddb' AS ov (READ_ONLY);
SELECT subtype, count(*) AS edificios
FROM ov.edificios
GROUP BY subtype
ORDER BY edificios DESC;
```

### Sin el archivo de vistas

Cada item lleva en `assets.data["processing:expression"]` la consulta equivalente sobre su parte. Las URLs de las partes cambian con cada publicación de Overture, así que conviene leerlas del STAC o usar la vista.

## Notas

- Columnas en inglés, con la semántica de Overture: ver https://docs.overturemaps.org/schema/reference/buildings/building/.
- `geometry` está en EPSG:4326. Para medir en metros usar `ST_Length_Spheroid` o `ST_Area_Spheroid`.
- `sources` registra la fuente de cada atributo; la licencia de cada fuente está en https://docs.overturemaps.org/attribution/.
- Overture borra las publicaciones viejas a los pocos meses. Las URLs de las partes se actualizan con `tools/virtual/refresh.py`.

## Colecciones relacionadas

- Las demás colecciones de `externos/overture/`, en el mismo archivo de vistas.
- `limites/partido_pergamino`: el límite que define el recorte.
