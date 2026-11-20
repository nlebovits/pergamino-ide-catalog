# Peligro de inundación fluvial (JRC GloFAS)

Mapas globales de peligro de inundación fluvial del JRC (CEMS-GloFAS), recortados al partido de Pergamino sin copiar los datos: profundidad del agua y clases de profundidad para siete períodos de retorno, y la máscara de agua permanente.

Esta colección es **virtual**: describe datos que publica otro catálogo y no copia sus bytes. El recurso `data` apunta al archivo original con una URL absoluta y lleva el rol `external`. El recorte al partido lo hace un archivo pequeño de este catálogo al leer los datos.

## Colecciones

| Colección | Contenido |
|---|---|
| [Profundidad de inundación, retorno de 10 años](./profundidad_rp10/) | `depth-rp10` |
| [Profundidad de inundación, retorno de 20 años](./profundidad_rp20/) | `depth-rp20` |
| [Profundidad de inundación, retorno de 50 años](./profundidad_rp50/) | `depth-rp50` |
| [Profundidad de inundación, retorno de 75 años](./profundidad_rp75/) | `depth-rp75` |
| [Profundidad de inundación, retorno de 100 años](./profundidad_rp100/) | `depth-rp100` |
| [Profundidad de inundación, retorno de 200 años](./profundidad_rp200/) | `depth-rp200` |
| [Profundidad de inundación, retorno de 500 años](./profundidad_rp500/) | `depth-rp500` |
| [Clases de profundidad de inundación, retorno de 10 años](./peligro_rp10/) | `hazard-rp10` |
| [Clases de profundidad de inundación, retorno de 20 años](./peligro_rp20/) | `hazard-rp20` |
| [Clases de profundidad de inundación, retorno de 50 años](./peligro_rp50/) | `hazard-rp50` |
| [Clases de profundidad de inundación, retorno de 75 años](./peligro_rp75/) | `hazard-rp75` |
| [Clases de profundidad de inundación, retorno de 100 años](./peligro_rp100/) | `hazard-rp100` |
| [Clases de profundidad de inundación, retorno de 200 años](./peligro_rp200/) | `hazard-rp200` |
| [Clases de profundidad de inundación, retorno de 500 años](./peligro_rp500/) | `hazard-rp500` |
| [Cuerpos de agua permanentes (GloFAS)](./agua_permanente/) | `permanent-water` |

La capa `spurious-depths` del JRC no se incluye: no tiene ninguna celda válida dentro del partido.

## Licencia

Ver el README de cada colección: el JRC publica dos declaraciones de licencia distintas y ambas se citan textualmente.

## Procedencia

JRC, *Global river flood hazard maps* (https://doi.org/10.2905/JRC.VD32YWG), convertidos a COG por nlebovits/jrc-glofas (https://source.coop/nlebovits/jrc-glofas).
