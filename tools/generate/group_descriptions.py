"""Spanish titles and descriptions for the thirteen sub-catalogs, and
hand-written titles for the layers whose upstream abstract is missing.

Written in the publisher's own language and vocabulary. Where a term is
Pergamino's own (DOSS, CELP, partida, catastro levels), it is kept rather
than translated.
"""

GROUP_DOCS = {
    "catastro": (
        "Catastro",
        "Parcelario y jerarquía catastral del Partido de Pergamino, desde la "
        "circunscripción hasta la subparcela y la propiedad horizontal, junto "
        "con zonificación, edificaciones y edificios de interés.",
    ),
    "vialidad": (
        "Vialidad",
        "Red vial del Partido de Pergamino: callejero, tipo de calzada y "
        "vereda, cordón cuneta, señalización, semáforos, alumbrado público y "
        "caminos rurales.",
    ),
    "transporte": (
        "Transporte",
        "Transporte público y movilidad: colectivos urbanos e interurbanos y "
        "sus líneas, paradas, ferrocarriles, ciclovías, remises y taxis, "
        "aeropuertos y estacionamiento.",
    ),
    "servicios-sanitarios": (
        "Servicios sanitarios",
        "Cobertura de agua corriente y red cloacal por período de gestión, "
        "medidores, pozos y estaciones de bombeo de la Dirección de Obras y "
        "Servicios Sanitarios (DOSS), desagües pluviales y zonas de "
        "facturación.",
    ),
    "energia-y-conectividad": (
        "Energía y conectividad",
        "Cobertura de gas natural, circuitos energéticos, red de fibra óptica "
        "municipal y federal, y puntos de acceso wifi en espacios verdes.",
    ),
    "salud": (
        "Salud",
        "Establecimientos y cobertura sanitaria: centros de salud, CAPS, áreas "
        "programáticas, desfibriladores de acceso público y guardias.",
    ),
    "educacion": (
        "Educación",
        "Establecimientos educativos por nivel y tipo de gestión, predios "
        "educativos y bibliotecas del Partido de Pergamino.",
    ),
    "seguridad": (
        "Seguridad",
        "Cuarteles de bomberos, cuadrículas y jurisdicciones policiales, "
        "cámaras de seguridad, dependencias, zonas de emergencia y riesgo, y "
        "centros de evacuados.",
    ),
    "demografia": (
        "Demografía e indicadores sociales",
        "Geografía censal y sus indicadores: radios censales INDEC 2010 y "
        "2022, NBI, Índice de Calidad de Vida (CONICET), hacinamiento, razón "
        "de sexo, pobreza crónica, calidad de vivienda, población y domicilios "
        "por manzana, y barrios populares RENABAP. Varias capas son datos "
        "nacionales rehospedados por el municipio.",
    ),
    "ambiente-y-agro": (
        "Ambiente y agro",
        "Arbolado urbano, espacios verdes, suelos y cultivos INTA, hidrografía "
        "y cuencas, curvas de nivel, isohietas, modelo digital de elevaciones, "
        "inundaciones históricas y el proyecto de presa. Incluye datos de "
        "INTA, IGN e INA rehospedados por el municipio.",
    ),
    "limites": (
        "Límites administrativos",
        "Límites del partido, barrios, localidades y pueblos, delegaciones, "
        "aglomerados urbanos, manchas urbanas históricas desde 1773, circuitos "
        "electorales y códigos postales.",
    ),
    "servicios-municipales": (
        "Servicios municipales",
        "Dependencias y trámites municipales, desarrollo social, higiene "
        "urbana, recolección de residuos, puntos de reciclado y sanitarios "
        "públicos.",
    ),
    "comercio-y-cultura": (
        "Comercio y cultura",
        "Actividad comercial, gastronomía y hospedaje, cultura, deporte y "
        "entretenimiento, medios de comunicación, entidades profesionales y "
        "sindicales, parques industriales y puntos de interés.",
    ),
}

# Layers with no usable upstream abstract. Written from the GeoNode record where
# one exists, otherwise from the layer's own schema and data.
HAND_WRITTEN = {
    "callejero_listado": (
        "Listado de calles",
        "Nomenclador de calles del Partido de Pergamino: nombre de la calle, "
        "localidad e identificador interno. Es una tabla de referencia sin "
        "geometría, pensada para vincular por `id_calle` con la capa de "
        "callejero y con cualquier dato que use el identificador de calle "
        "municipal.",
    ),
    "fibra_optica": (
        "Red de fibra óptica municipal",
        "Tramos de la red de fibra óptica del Municipio de Pergamino. Cada "
        "tramo registra su nombre, longitud en metros, categoría y entidad "
        "responsable.",
    ),
    "parcelario": (
        "Parcelario",
        "Capa parcelaria general del Partido de Pergamino, con la mayor "
        "cantidad de atributos disponibles por parcela. Es la capa de "
        "referencia para consultas parcelarias; la capa de contralor urbano "
        "remite explícitamente a ésta para obtener más datos.",
    ),
    "circuitos_electorales": (
        "Circuitos electorales",
        "Circuitos electorales del Partido de Pergamino.",
    ),
    "luminarias": (
        "Luminarias en vía pública",
        "Luminarias en vía pública del Partido de Pergamino. Permite "
        "distinguir las zonas con luminaria LED y de sodio, así como el tipo "
        "de soporte de poste.",
    ),
}
