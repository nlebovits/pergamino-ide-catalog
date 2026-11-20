# Datos de otros catálogos

Colecciones virtuales: la parte de conjuntos de datos publicados en otros catálogos Portolan que cae dentro del partido de Pergamino, sin copiar los datos. Peligro de inundación fluvial del JRC (GloFAS) y edificios, lugares, transporte y uso del suelo de Overture Maps.

## Subcatálogos

- [Peligro de inundación fluvial (JRC GloFAS)](./glofas/)
- [Overture Maps](./overture/)

## Cómo funciona una colección virtual

- El recurso `data` es el archivo del otro catálogo, con URL absoluta y los roles `data` y `external`. No se copia.
- Un recurso `recorte` (roles `metadata` y `recipe`) hace el recorte al leer: un VRT de GDAL para los ráster, un archivo de vistas DuckDB para los vectores. La misma operación está en `processing:expression` sobre el recurso `data`.
- El enlace `derived_from` apunta a la colección del otro catálogo; `via` a la página del productor; `canonical` al STAC del productor cuando existe.
- El estilo por defecto cubre con una máscara todo lo que queda fuera del partido.

El recorte usa el límite oficial del partido publicado en `https://data.source.coop/nlebovits/pergamino-ide/limites/partido_pergamino/partido_pergamino.parquet` (colección `limites/partido_pergamino`).

## Licencia

Cada colección conserva la licencia de su productor; ninguna se relicencia bajo la licencia de la IDE.
