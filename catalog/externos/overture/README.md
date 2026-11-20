# Overture Maps

Edificios, lugares de interés, segmentos de transporte y uso del suelo de Overture Maps dentro del partido de Pergamino, referenciados sin copiar los datos. Un archivo DuckDB de vistas recorta cada capa al partido al consultarla.

Esta colección es **virtual**: describe datos que publica otro catálogo y no copia sus bytes. El recurso `data` apunta al archivo original con una URL absoluta y lleva el rol `external`. El recorte al partido lo hace un archivo pequeño de este catálogo al leer los datos.

## Colecciones

| Colección | Vista | Tipo de Overture |
|---|---|---|
| [Edificios (Overture Maps)](./edificios/) | `edificios` | `buildings/building` |
| [Lugares de interés (Overture Maps)](./lugares/) | `lugares` | `places/place` |
| [Segmentos de transporte (Overture Maps)](./segmentos/) | `segmentos` | `transportation/segment` |
| [Uso del suelo (Overture Maps)](./uso_del_suelo/) | `uso_del_suelo` | `base/land_use` |

El tema `addresses` no se incluye: la publicación de Overture no trae direcciones de Argentina.

## Acceso

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://data.source.coop/nlebovits/pergamino-ide/externos/overture/pergamino_overture.ddb' AS ov (READ_ONLY);
SHOW TABLES FROM ov;
```

## Licencia

Cada colección declara la licencia que Overture declara para su tema. Atribución: https://docs.overturemaps.org/attribution/
