# Guía para agentes — Espacios verdes públicos

`ambiente-y-agro/espacios_verdes`: polígonos. Contiene todos los espacios verdes públicos del Partido de Pergamino, como plazas, plazoletas y parques.

## Acceso

- Datos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/espacios_verdes.parquet`. GeoParquet 1.1, geometría WKB en EPSG:4326, columna de cobertura `bbox`, orden espacial Hilbert.
- Teselas: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/espacios_verdes.pmtiles`, capa `espacios_verdes`, zoom 0 a 15.
- Metadatos: `https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/collection.json`. El número de registros está en `table:row_count`, y cada versión anterior en un activo `version-*`.
- Fuente: capa WFS `geonode:espacios_verdes` de GeoNode.

## Esquema

- `id` (int64)
- `codigo` (string)
- `poligono` (string)
- `nombre` (string)
- `titular` (string)
- `circ` (string)
- `seccion` (string)
- `chacra` (string)
- `quinta` (int64)
- `fraccion` (int64)
- `manzana` (string)
- `parcela` (string)
- `partida` (string)
- `localidad` (string)
- `ordenanza` (string)
- `obs` (string)
- `area` (int64)
- `etiqueta` (string)
- `barrio` (string)
- `juegos` (string)
- `est_salud` (string)
- `monumento` (string)
- `luminaria` (string)
- `asientos` (string)
- `senda_peat` (string)
- `arbolado` (string)
- `edificado` (string)
- `mastil` (string)
- `sector` (string)
- `plan_led` (string)
- `nombre_alternativo` (string)
- `mantenimiento_electrico` (string)
- `mejoras` (string)
- `origen` (string)
- `nomenclaturas` (string)
- `alcance_uso` (string)
- `tipo_cobertura_mayoritaria` (string)
- `usos_predominantes` (string)
- `funcion` (string)
- `forma` (string)
- `denominacion` (string)
- `delimitacion` (string)
- `parcelas` (string)
- `uso_transito` (string)
- `disponibilidad` (string)
- `actualizacion` (string)
- `geometry` (binary)
- `bbox` (struct<xmin: double, ymin: double, xmax: double, ymax: double>)

La fuente no publica descripciones de columnas: GeoNode devuelve una descripción vacía para cada atributo. Por eso las columnas no tienen descripción en `table:columns`, salvo `geometry` y `bbox`, que agrega este catálogo.

Valores medidos en los datos, de más a menos frecuente, de las columnas de texto con pocas categorías:

```text
circ: 1 | 2 | 14 | 15 | 16 | 12 | 19 | 17 | 5 | 22 | 11 | 23 | 4 | 9 | I
seccion: D | B | 0 | A | K | C | E | H | M | F | G | Z | N | J | L
localidad: Pergamino | J. A. de la Peña | Guerrico | Urquiza | Manuel Ocampo | Mariano Alfonzo | Acevedo | La Violeta | El Socorro | Fontezuela | Mariano Benitez | Rancagua | Pinzon
juegos: no | si | sin dato
est_salud: no | si
monumento: no | si | sin dato
luminaria: no | si
asientos: no | si | sin dato
senda_peat: no | si | sin dato
arbolado: no | si | sin dato
edificado: no | si | sin dato
mastil: no | si | sin dato
sector: sur | norte | pueblos | este | oeste | centro | no
plan_led: 2017-MINEM | 2017-licitacion
mejoras: no | si
origen: vial | catastro | ffcc | fluvial | electroducto
alcance_uso: adyacente | ninguno | vecinal | barrial | ciudad | metropolitano
tipo_cobertura_mayoritaria: verde | jardin | dura
funcion: conector_urbano | nodo_verde | sin_funcion | especifico
forma: lineal | cuadrangular | irregular | triangular | circular
denominacion: delimitador_vial | reserva | plazoleta | plaza | ribera | paseo | circuito_deportivo | parque
delimitacion: abierta | cerrada | mixta
uso_transito: ninguno | peatonal | vehicular | peatonal, patin_patineta | peatonal, vehicular | peatonal, ciclismo | peatonal, patin_patineta, vehicular, ciclismo
disponibilidad: funcional | sin_proyecto | en_construccion | proyecto
```

## Consultas de ejemplo

Cada bloque corre tal cual en el CLI de DuckDB después de `INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;`.

### Primeros registros

```sql
SELECT * EXCLUDE (geometry, bbox)
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/espacios_verdes.parquet')
LIMIT 5;
```

### Registros por `circ`

```sql
SELECT "circ", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/espacios_verdes.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por `seccion`

```sql
SELECT "seccion", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/espacios_verdes.parquet')
GROUP BY ALL
ORDER BY registros DESC;
```

### Registros por barrio

```sql
SELECT b.nombre AS barrio, count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/espacios_verdes.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet') AS b
  ON ST_Intersects(ST_PointOnSurface(t.geometry), b.geometry)
GROUP BY b.nombre
ORDER BY registros DESC
LIMIT 10;
```

### Filtro por ventana, con la columna `bbox`

```sql
SELECT count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/espacios_verdes.parquet')
WHERE bbox.xmin >= -60.5731 AND bbox.xmax <= -60.4380
  AND bbox.ymin >= -33.9189 AND bbox.ymax <= -33.8329;
```

### Unión con `catastro/parcela` por `partida`

```sql
SELECT t."partida", count(*) AS registros
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/ambiente-y-agro/espacios_verdes/espacios_verdes.parquet') AS t
JOIN read_parquet('https://data.source.coop/nlebovits/pergamino-ide/catastro/parcela/parcela.parquet') AS r
  ON CAST(t."partida" AS VARCHAR) = CAST(r."partida" AS VARCHAR)
GROUP BY ALL
ORDER BY registros DESC
LIMIT 10;
```

## Notas de calidad

- Las geometrías inválidas de la fuente se reparan con `shapely.make_valid`. `pergamino:repaired_geometries` en el activo de datos dice cuántas se repararon en cada versión.
- La fecha de los metadatos es de publicación en GeoNode, no del contenido. Si la capa tiene columnas como `fuente` o `actualizacion`, son la mejor señal de vigencia.

## Colecciones relacionadas

- `catastro/parcela`, por `partida`. Hay valores de `partida` que coinciden en las dos colecciones.
- `limites/barrios_y_pueblos`, por intersección espacial.
