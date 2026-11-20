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
        "con zonificación, edificaciones detectadas sobre imágenes y "
        "edificios de interés.",
    ),
    "vialidad": (
        "Vialidad",
        "Red vial del Partido de Pergamino: callejero, material de calzada, "
        "cordón cuneta, rampas de acceso, señalización, semáforos, "
        "reductores de velocidad, alumbrado público, puntos fijos y red de "
        "nivelación del IGN, y caminos rurales.",
    ),
    "transporte": (
        "Transporte",
        "Transporte público y movilidad: colectivos urbanos e interurbanos, "
        "paradas, puntos de carga SUBE, ferrocarriles, circuitos de "
        "cicloturismo y la Vuelta al Partido, remises y taxis, aeropuertos y "
        "estacionamiento.",
    ),
    "servicios-sanitarios": (
        "Servicios sanitarios",
        "Redes de agua corriente y cloacas (líneas, nodos y cobertura), "
        "medidores, pozos y estaciones de bombeo de la Dirección de Obras y "
        "Servicios Sanitarios (DOSS), desagües pluviales, sumideros y "
        "compuertas, y zonas de facturación.",
    ),
    "energia-y-conectividad": (
        "Energía y conectividad",
        "Cobertura de gas natural, circuitos energéticos, nodos y tramos de "
        "la Red Federal de Fibra Óptica, y puntos de acceso wifi en espacios "
        "verdes.",
    ),
    "salud": (
        "Salud",
        "Establecimientos y cobertura sanitaria: centros de salud, CAPS, áreas "
        "programáticas, desfibriladores de acceso público y guardias.",
    ),
    "educacion": (
        "Educación",
        "Establecimientos educativos, por nivel y por tipo de gestión, "
        "predios educativos y bibliotecas del Partido de Pergamino.",
    ),
    "seguridad": (
        "Seguridad",
        "Cuarteles de bomberos, dependencias de seguridad, zonas de "
        "seguridad, zonas de emergencia y riesgo, y centros de evacuados.",
    ),
    "demografia": (
        "Demografía e indicadores sociales",
        "Geografía censal y sus indicadores: radios censales INDEC 2010 y "
        "2022, NBI, Índice de Calidad de Vida (CONICET), hacinamiento, razón "
        "de sexo, pobreza crónica, calidad de vivienda, densidad de población "
        "por censo, población por manzana por mapeo dasimétrico, y barrios "
        "populares RENABAP. Varias capas son datos nacionales rehospedados "
        "por el municipio.",
    ),
    "ambiente-y-agro": (
        "Ambiente y agro",
        "Arbolado urbano, espacios verdes, suelos y cultivos INTA, hidrografía "
        "y cuencas, curvas de nivel, isohietas, carbono en el suelo, "
        "inundaciones históricas y el proyecto de presa. Incluye datos de "
        "INTA, IGN e INA rehospedados por el municipio.",
    ),
    "limites": (
        "Límites administrativos",
        "Límites del partido, barrios y pueblos, localidades y sus áreas, "
        "delegaciones, "
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
HAND_WRITTEN: dict[str, tuple[str, str]] = {}
