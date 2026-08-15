# Guía para agentes — IDE Pergamino

Espejo cloud-native de la IDE del Municipio de Pergamino (Buenos Aires, Argentina). 183 colecciones en 13 grupos temáticos.

## Cómo está organizado

El catálogo raíz enlaza a 13 subcatálogos temáticos; cada uno enlaza a sus colecciones. Los identificadores son rutas: `catastro/parcela`, `demografia/nbi`, `ambiente-y-agro/arbolado`.

- [`catastro/`](./catastro/AGENTS.md) — Catastro, 20 colecciones
- [`vialidad/`](./vialidad/AGENTS.md) — Vialidad, 18 colecciones
- [`transporte/`](./transporte/AGENTS.md) — Transporte, 19 colecciones
- [`servicios-sanitarios/`](./servicios-sanitarios/AGENTS.md) — Servicios sanitarios, 17 colecciones
- [`energia-y-conectividad/`](./energia-y-conectividad/AGENTS.md) — Energía y conectividad, 6 colecciones
- [`salud/`](./salud/AGENTS.md) — Salud, 7 colecciones
- [`educacion/`](./educacion/AGENTS.md) — Educación, 4 colecciones
- [`seguridad/`](./seguridad/AGENTS.md) — Seguridad, 8 colecciones
- [`demografia/`](./demografia/AGENTS.md) — Demografía e indicadores sociales, 12 colecciones
- [`ambiente-y-agro/`](./ambiente-y-agro/AGENTS.md) — Ambiente y agro, 29 colecciones
- [`limites/`](./limites/AGENTS.md) — Límites administrativos, 10 colecciones
- [`servicios-municipales/`](./servicios-municipales/AGENTS.md) — Servicios municipales, 15 colecciones
- [`comercio-y-cultura/`](./comercio-y-cultura/AGENTS.md) — Comercio y cultura, 18 colecciones

## Formato

- **GeoParquet 1.1.0**, geometría WKB en `geometry`, EPSG:4326, columna de cobertura `bbox` (struct xmin/ymin/xmax/ymax), ordenamiento espacial Hilbert, compresión ZSTD.
- **PMTiles** para visualización web, con estilo MapLibre en `styles/default.json` derivado del SLD oficial del municipio.
- Nombres de columna en español.

## Consulta

```python
import duckdb
duckdb.sql("INSTALL spatial; LOAD spatial;")
duckdb.sql("""
  SELECT nombre, ST_Area(geometry) AS area
  FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios/publico_barrios.parquet')
  ORDER BY area DESC LIMIT 5
""").df()
```

## Claves de unión útiles

- `partida` — número de partida inmobiliaria, une las capas catastrales entre sí.
- `id_calle` — identificador de calle municipal, une `vialidad/callejero` con `vialidad/callejero_listado`.
- `clavera` / `radio_id` — radio censal INDEC, une las capas de `demografia/` entre sí.
- `cpa` — Código Postal Argentino, único por lado de manzana; `vialidad/callejero` trae `cpa_par` y `cpa_impar`.

## Advertencias

- **`limites/zonas_electorales_celp` no es electoral en sentido político.** CELP es la Cooperativa Eléctrica Limitada de Pergamino; son los distritos de su gobernanza interna.
- **Las capas `cobertura_agua_*` y `cobertura_cloacas_*` usan períodos de gestión de gobierno, no ventanas de validez del dato.** `cobertura_agua_de_2023_a_2027` es la cobertura de la gestión actual, no una proyección.
- **`demografia/nbi`** se titula upstream "Niveles Básicos Insatisfechos"; el término correcto es *Necesidades* Básicas Insatisfechas (INDEC).
- La fecha de los metadatos es de republicación, no del contenido. Varias capas traen `fuente` y `actualizacion` por registro, que es la señal de vigencia más confiable. `ambiente-y-agro/arbolado` y `vialidad/tipo_de_vereda` provienen del censo de 2013.
- Cerca de 46 colecciones son datos de terceros (INTA, IGN, INDEC, RENABAP, CONICET, INA, ARBA, BAHRA, Correo Argentino) rehospedados por el municipio. Atribuir al organismo de origen, no al municipio.
