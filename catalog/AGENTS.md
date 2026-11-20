# Guía para agentes — IDE Pergamino

Espejo cloud-native de la IDE del Municipio de Pergamino (Buenos Aires, Argentina), con las capas vectoriales que el municipio publica en GeoNode.

## Cómo está organizado

El catálogo raíz enlaza a subcatálogos temáticos, y cada uno enlaza a sus colecciones. Los identificadores son rutas: `catastro/parcela`, `demografia/nbi`, `ambiente-y-agro/arbolado`.

- [`catastro/`](./catastro/AGENTS.md): Catastro
- [`vialidad/`](./vialidad/AGENTS.md): Vialidad
- [`transporte/`](./transporte/AGENTS.md): Transporte
- [`servicios-sanitarios/`](./servicios-sanitarios/AGENTS.md): Servicios sanitarios
- [`energia-y-conectividad/`](./energia-y-conectividad/AGENTS.md): Energía y conectividad
- [`salud/`](./salud/AGENTS.md): Salud
- [`educacion/`](./educacion/AGENTS.md): Educación
- [`seguridad/`](./seguridad/AGENTS.md): Seguridad
- [`demografia/`](./demografia/AGENTS.md): Demografía e indicadores sociales
- [`ambiente-y-agro/`](./ambiente-y-agro/AGENTS.md): Ambiente y agro
- [`limites/`](./limites/AGENTS.md): Límites administrativos
- [`servicios-municipales/`](./servicios-municipales/AGENTS.md): Servicios municipales
- [`comercio-y-cultura/`](./comercio-y-cultura/AGENTS.md): Comercio y cultura

## Formato

- **GeoParquet 1.1**, geometría WKB en `geometry`, EPSG:4326, columna de cobertura `bbox` (struct xmin/ymin/xmax/ymax), orden espacial Hilbert, compresión ZSTD.
- **PMTiles** para visualización web, con estilo MapLibre en `styles/default.json` derivado del estilo SLD que publica GeoNode.
- Nombres de columna en español, tal como los publica la fuente.
- Cada `collection.json` registra sus versiones como activos `version-*`. La versión actual de una colección siempre está en `<grupo>/<colección>/<colección>.parquet`.

## Consulta

```sql
SELECT nombre, ST_Area(ST_Transform(geometry, 'EPSG:4326', 'EPSG:22175', always_xy := true)) / 10000 AS hectareas
FROM read_parquet('https://data.source.coop/nlebovits/pergamino-ide/limites/barrios_y_pueblos/barrios_y_pueblos.parquet')
ORDER BY hectareas DESC
LIMIT 5;
```

## Claves de unión

Medidas en los datos: se listan las que tienen valores en común entre colecciones. Cada `AGENTS.md` de colección muestra la unión concreta.

- `clavera` une `demografia/radios_censales_indec_2010` con: `demografia/icv`, `demografia/redatam_censo_2022_radios`.
- `id_calle` une `vialidad/callejero` con: `vialidad/cordon_cuneta`, `vialidad/material_de_calzada`.
- `partida` une `catastro/parcela` con: `ambiente-y-agro/espacios_verdes`, `catastro/edificios_historicos`, `catastro/ph`, `catastro/subparcela`.

## Advertencias

- **`limites/zonas_electorales_celp` no es electoral en sentido político.** GeoNode la describe como "Capa de zonas electorales de la Cooperativa Eléctrica Limitada de Pergamino".
- **`demografia/nbi`**: la descripción en GeoNode dice "Niveles Básicos Insatisfechos". El término del INDEC, que usa el título, es *Necesidades* Básicas Insatisfechas.
- La fecha de los metadatos es de publicación, no del contenido. Varias capas traen `fuente` y `actualizacion` por registro, que es la señal de vigencia más confiable. `ambiente-y-agro/arbolado` proviene del censo de arbolado de 2013.
- Varias colecciones son datos de terceros (INTA, IGN, INDEC, RENABAP, CONICET, INA, ARBA, BAHRA, Correo Argentino) rehospedados por el municipio. Atribuir al organismo de origen, no al municipio.
