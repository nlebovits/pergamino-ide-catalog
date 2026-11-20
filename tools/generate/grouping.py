"""Thematic grouping for the Pergamino IDE catalog.

Maps each GeoNode vector dataset, by its bare layer name, to one of thirteen
sub-catalogs. Explicit rather than pattern-matched: at this size a rules regex
is harder to audit than a list, and a misfiled collection is a permanent ID
change.

A dataset that GeoNode publishes but that no group lists is not mirrored.
``python3 tools/geonode.py sources`` reports it, so a new dataset is added on
purpose, after the data review that every layer gets before it is mirrored.

Excluded layers are recorded separately with their reason.
"""

# Layers not mirrored. The reasons are deliberately not recorded here.
#
# Five of these were held back after a data review, and writing down what the
# review found would publish a description of exactly the material the decision
# was meant not to amplify — which is the mistake this comment exists to avoid
# repeating. The findings were sent to the publisher directly so they can act on
# them at the source, which is the only place they can be fixed.
#
# The sixth is a backup duplicate of another layer and is simply redundant.
#
# Direct questions about coverage to nlebovits@pm.me.
EXCLUDED = {
    "farmacias": "Not mirrored, following a data review.",
    "parcelario_tarifa_social": "Not mirrored, following a data review.",
    "partidos": "Not mirrored, following a data review.",
    "pozos_bombeo_doss": "Not mirrored, following a data review.",
    "tranqueras_rurales": "Not mirrored, following a data review.",
    "luminarias_bckp": "Redundant: a backup duplicate of luminarias.",
}

GROUPS = {
    "catastro": [
        "catastro_circunscripcion", "catastro_seccion", "catastro_chacra",
        "catastro_quinta", "catastro_fraccion", "catastro_manzana",
        "catastro_parcela", "catastro_subparcela", "catastro_ph",
        "catastro_medida_lado", "zonificacion", "edificaciones_automaticas",
        "edificios_en_altura", "edificios_historicos", "complejos_habitacionales",
        "areas_fiscalizadas_construcciones",
    ],
    "vialidad": [
        "callejero", "vista_callejero_1", "vista_callejero_2",
        "rampas_acceso_discapacidad", "semaforos", "carteles_viales",
        "reductor_de_velocidad", "alcantarillas_vialidad", "camaras_y_radares",
        "luminarias", "puntos_fijos", "red_nivelacion_ign_precision",
        "progresivas_rutas", "comisiones_caminos_rurales",
    ],
    "transporte": [
        "colectivos_urbanos", "colectivos_interurbanos", "paradas_de_colectivo",
        "sube", "ferrocarriles", "cicloturismo", "vuelta_partido", "remis_taxi",
        "aeropuertos", "estacionamiento_nocturno", "estacionamiento_privado",
        "estacionamiento_motos_bicicletas",
    ],
    "servicios-sanitarios": [
        "cobertura_agua", "cobertura_cloacas", "agua_lineas", "agua_nodos",
        "cloacas_lineas", "cloacas_nodos", "medidores_agua", "pozos_doss",
        "estaciones_de_bombeo", "pluviales", "sumideros", "compuertas_pluviales",
        "zonas_facturacion", "codigo_reparto_facturacion",
        "coeficientes_zonales_doss",
    ],
    "energia-y-conectividad": [
        "cobertura_gas_natural", "circuitos_energeticos",
        "red_federal_fibra_optica_nodos", "red_federal_fibra_optica_tramos",
        "wifi_espacios_verdes",
    ],
    "salud": [
        "centros_de_salud", "caps", "areas_programaticas_salud",
        "desfibriladores", "guardias_medicas", "guardias_emergencias_servicios",
        "estaciones_de_salud",
    ],
    "educacion": [
        "educacion", "educacion_gestion", "educacion_nivel", "predios_educativos",
        "bibliotecas",
    ],
    "seguridad": [
        "bomberos", "dependencias_seguridad", "zonas_seguridad",
        "zonas_emergencias_y_riesgo", "centros_evacuados",
    ],
    "demografia": [
        "radios_censales_indec_2010", "redatam_censo_2022_radios", "nbi", "icv",
        "hacinamiento", "razon_de_sexo_2010", "pobreza_cronica",
        "calidad_vivienda", "manzanas_isdd", "1991_poblacion",
        "2001_poblacion", "2010_poblacion", "2022_poblacion",
        "renabap_barrios_populares",
    ],
    "ambiente-y-agro": [
        "arbolado", "cobertura_arbolado_urbano", "espacios_verdes",
        "luminarias_espacios_verdes", "limpieza_mantenimiento_espacios_verdes",
        "suelos_pergamino_50mil", "riego_por_pivote_central",
        "inta_mnc_2018_2019", "inta_mnc_2019_invierno", "inta_mnc_2020_invierno",
        "inta_mnc_2020_verano", "inta_mnc_2021_invierno", "inta_mnc_2021_verano",
        "inta_mnc_2022_invierno", "inta_mnc_2022_verano", "inta_mnc_2023_verano",
        "inta_carbono_suelo_2015_2022",
        "isohietas_precipitaciones_medias_anuales_pergamino_geointa",
        "cuencas_arroyo_pergamino", "cuencas_hidricas_norte_ba", "cursos_de_agua",
        "banados", "curvas_nivel_ign", "curvas_nivel_cuenca",
        "curvas_de_nivel_iatasa_abs", "puntos_de_nivel_iatasa_abs",
        "inundacion_1995", "inundacion_2016", "proyecto_presa",
        "proyecto_presa_area_inundable",
    ],
    "limites": [
        "partido_pergamino", "barrios_y_pueblos", "localidades",
        "areas_localidades", "delegaciones_pueblos", "aglomerados_urbanos",
        "manchas_urbanas_historicas", "circuitos_electorales",
        "zonas_electorales_celp", "cpa",
    ],
    "servicios-municipales": [
        "dependencias_municipales", "bocas_pago_tasas",
        "centros_de_desarrollo_comunitario", "desarrollo_social",
        "areas_programaticas_desarrollo_social", "barrido_y_limpieza",
        "recoleccion_residuos_domiciliarios", "recoleccion_residuos_voluminosos",
        "contenedores_basura_reciclaje", "desecho_pilas_usadas",
        "sanitarios_publicos", "agencias_gubernamentales",
        "proyectos_infraestructura", "puntos_clickeados",
    ],
    "comercio-y-cultura": [
        "agencias_de_viaje", "asociaciones_sindicales",
        "colegios_de_profesionales", "medios_de_comunicacion",
        "museos_y_espacios_culturales", "oferentes_espacios_culturales",
        "entretenimiento", "deportivo", "gastronomia", "hospedajes", "gomerias",
        "estaciones_servicio", "paseos_comerciales", "extraccion_dinero",
        "puntos_venta_simple", "parques_industriales_y_anexos",
        "puntos_de_interes",
    ],
}

# GeoNode layer name -> collection leaf, for a layer that GeoNode renamed.
# The collection keeps the id it had before the move to GeoNode, so links to
# it keep working. Each pair has the same title in GeoNode, and the schemas
# were compared before the pair was added.
KEEP_ID = {
    "rampas_acceso_discapacidad": "rampas_acceso_veredas",
    "reductor_de_velocidad": "reductores_de_velocidad",
    "cicloturismo": "cicloturismo_rural",
    "pozos_doss": "pozos_agua_doss",
    "vista_callejero_1": "material_de_calzada",
    "vista_callejero_2": "cordon_cuneta",
}

# GeoNode layer name -> collection leaf, for a layer whose name is not a
# valid collection id. An id starts with a letter (rashid PTL-COL-003).
RENAME = {
    "1991_poblacion": "poblacion_1991",
    "2001_poblacion": "poblacion_2001",
    "2010_poblacion": "poblacion_2010",
    "2022_poblacion": "poblacion_2022",
}

TITLES = {
    "catastro": "Catastro",
    "vialidad": "Vialidad",
    "transporte": "Transporte",
    "servicios-sanitarios": "Servicios sanitarios",
    "energia-y-conectividad": "Energía y conectividad",
    "salud": "Salud",
    "educacion": "Educación",
    "seguridad": "Seguridad",
    "demografia": "Demografía",
    "ambiente-y-agro": "Ambiente y agro",
    "limites": "Límites administrativos",
    "servicios-municipales": "Servicios municipales",
    "comercio-y-cultura": "Comercio y cultura",
}

LAYER_TO_GROUP = {
    layer: group for group, layers in GROUPS.items() for layer in layers
}


def leaf_name(group: str, layer: str) -> str:
    """The collection directory for a GeoNode layer in ``group``.

    A renamed layer keeps its earlier id (KEEP_ID), and a layer whose name
    is not a valid id takes the one in RENAME. Otherwise the group's
    own prefix is dropped: ``catastro_parcela`` in ``catastro`` is
    ``catastro/parcela``.
    """
    if layer in KEEP_ID:
        return KEEP_ID[layer]
    if layer in RENAME:
        return RENAME[layer]
    prefix = group.split("-")[0] + "_"
    if layer.startswith(prefix) and len(layer) > len(prefix):
        return layer[len(prefix):]
    return layer
