# Guía para agentes — Overture Maps

Un solo archivo de vistas DuckDB da acceso a las cuatro capas, ya recortadas al partido.

## Colecciones

- [`externos/overture/edificios`](./edificios/AGENTS.md) — vista `ov.edificios`
- [`externos/overture/lugares`](./lugares/AGENTS.md) — vista `ov.lugares`
- [`externos/overture/segmentos`](./segmentos/AGENTS.md) — vista `ov.segmentos`
- [`externos/overture/uso_del_suelo`](./uso_del_suelo/AGENTS.md) — vista `ov.uso_del_suelo`

## Unir capas

Lugares de interés que caen dentro de un edificio, por categoría:

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://data.source.coop/nlebovits/pergamino-ide/externos/overture/pergamino_overture.ddb' AS ov (READ_ONLY);
SELECT l.basic_category, count(*) AS lugares
FROM ov.lugares AS l
JOIN ov.edificios AS e
  ON ST_Intersects(l.geometry, e.geometry)
GROUP BY l.basic_category
ORDER BY lugares DESC
LIMIT 10;
```

## Notas

- Las vistas leen las partes externas en cada consulta; nada se guarda en este catálogo.
- `id` es el identificador GERS de Overture, estable entre publicaciones para el mismo objeto.
