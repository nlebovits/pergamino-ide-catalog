# Guía para agentes — Segmentos de transporte (Overture Maps)

Segmentos de calles, caminos, vías férreas y vías navegables de Overture Maps dentro del partido de Pergamino, referenciados sin copiar los datos.

## Consulta

La vista ya aplica el recorte: prefiltro sobre la columna `bbox` (DuckDB descarta grupos de filas con las estadísticas del footer) y `ST_Intersects` con el límite oficial del partido. Requiere `spatial` y `httpfs`.

### Longitud de la red por clase, en km

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://data.source.coop/nlebovits/pergamino-ide/vialidad/segmentos_overture/segmentos_overture.ddb' AS ov (READ_ONLY);
SELECT subtype, class,
       round(sum(ST_Length_Spheroid(geometry)) / 1000, 1) AS km
FROM ov.segmentos
GROUP BY subtype, class
ORDER BY km DESC;
```

### Sin el archivo de vistas

Cada item lleva en `assets.data["processing:expression"]` la consulta equivalente sobre su parte. Las URLs de las partes cambian con cada publicación de Overture, así que conviene leerlas del STAC o usar la vista.

## Notas

- Columnas en inglés, con la semántica de Overture: ver https://docs.overturemaps.org/schema/reference/transportation/segment/.
- `geometry` está en EPSG:4326. Para medir en metros usar `ST_Length_Spheroid` o `ST_Area_Spheroid`.
- `sources` registra la fuente de cada atributo; la licencia de cada fuente está en https://docs.overturemaps.org/attribution/.
- Overture borra las publicaciones viejas a los pocos meses. Las URLs de las partes se actualizan con `tools/virtual/refresh.py`.

## Colecciones relacionadas

- Las demás capas de Overture Maps en este catálogo: `catastro/edificios_overture`, `comercio-y-cultura/lugares_overture`, `ambiente-y-agro/uso_del_suelo_overture`.
- `limites/partido_pergamino`: el límite que define el recorte.
