"""Thematic grouping for the Pergamino IDE catalog.

Maps each upstream WFS layer to one of twelve sub-catalogs. Explicit rather than
pattern-matched: at this size a rules regex is harder to audit than a list, and a
misfiled collection is a permanent ID change.

Excluded layers are recorded separately with their reason.
"""

# Layers not mirrored. The reasons are deliberately not recorded here.
#
# Four of these were held back after a data review, and writing down what the
# review found would publish a description of exactly the material the decision
# was meant not to amplify — which is the mistake this comment exists to avoid
# repeating. The findings were sent to the publisher directly so they can act on
# them at the source, which is the only place they can be fixed.
#
# The fifth is a backup duplicate of another layer and is simply redundant.
#
# Direct questions about coverage to nlebovits@pm.me.
EXCLUDED = {
    "farmacias": "Not mirrored, following a data review.",
    "parcelario_tarifa_social": "Not mirrored, following a data review.",
    "partidos": "Not mirrored, following a data review.",
    "pozos_bombeo_doss": "Not mirrored, following a data review.",
    "luminarias_bckp": "Redundant: a backup duplicate of luminarias.",
}

GROUPS = {
    "catastro": [
        "catastro_circunscripcion", "catastro_seccion", "catastro_chacra",
        "catastro_quinta", "catastro_fraccion", "catastro_manzana",
        "catastro_parcela", "catastro_subparcela", "catastro_ph",
        "catastro_medida_lado", "parcelario", "parcelario_contralor",
        "estado_parcela", "zonificacion", "edificaciones_pa", "edificaciones_pb",
        "edificios_en_altura", "edificios_historicos", "complejos_habitacionales",
        "areas_fiscalizadas_construcciones",
    ],
    "vialidad": [
        "callejero", "callejero_listado", "altura_de_calle", "material_de_calzada",
        "cordon_cuneta", "tipo_de_vereda", "rampas_acceso_veredas", "semaforos",
        "carteles_viales", "reductores_de_velocidad", "alcantarillas_vialidad",
        "camaras_y_radares", "luminarias", "recambio_led", "puntos_fijos",
        "progresivas_rutas", "comisiones_caminos_rurales", "tranqueras_rurales",
    ],
    "transporte": [
        "colectivos_urbanos", "colectivos_interurbanos", "linea_a", "linea_b",
        "linea_c", "linea_d", "linea_e", "linea_parque_industrial",
        "paradas_de_colectivo", "sube", "ferrocarriles", "ciclovias",
        "cicloturismo_rural", "remis_taxi", "aeropuertos",
        "estacionamiento_medido", "estacionamiento_nocturno",
        "estacionamiento_privado", "estacionamiento_motos_bicicletas",
    ],
    "servicios-sanitarios": [
        "cobertura_agua_antes_de_2015", "cobertura_agua_de_2015_a_2019",
        "cobertura_agua_de_2019_a_2023", "cobertura_agua_de_2023_a_2027",
        "cobertura_cloacas_antes_de_2015", "cobertura_cloacas_de_2015_a_2019",
        "cobertura_cloacas_de_2019_a_2023", "cobertura_cloacas_de_2023_a_2027",
        "medidores_agua", "pozos_agua_doss", "estaciones_de_bombeo",
        "colectoras_cloacales_maximas", "pluviales", "sumideros",
        "zonas_facturacion", "codigo_reparto_facturacion",
        "coeficientes_zonales_doss",
    ],
    "energia-y-conectividad": [
        "cobertura_gas_natural", "circuitos_energeticos", "fibra_optica",
        "red_federal_fibra_optica_nodos", "red_federal_fibra_optica_tramos",
        "wifi_espacios_verdes",
    ],
    "salud": [
        "centros_de_salud", "caps", "areas_programaticas_salud",
        "desfibriladores", "guardias_medicas", "guardias_emergencias_servicios",
        "estaciones_de_salud",
    ],
    "educacion": [
        "educacion_gestion", "educacion_nivel", "predios_educativos",
        "bibliotecas",
    ],
    "seguridad": [
        "bomberos", "cuadriculas_policiales", "jurisdicciones_policiales",
        "camaras_seguridad", "dependencias_seguridad", "zonas_seguridad",
        "zonas_emergencias_y_riesgo", "centros_evacuados",
    ],
    "demografia": [
        "radios_censales_indec_2010", "redatam_censo_2022_radios", "nbi", "icv",
        "hacinamiento", "razon_de_sexo_2010", "pobreza_cronica",
        "calidad_vivienda", "habitantes_por_manzana_provisorio_2022",
        "proyeccion_habitantes_por_manzana_2010_2030", "domicilios_por_manzana",
        "renabap_barrios_populares",
    ],
    "ambiente-y-agro": [
        "arbolado", "cobertura_arbolado_urbano", "espacios_verdes",
        "luminarias_espacios_verdes", "limpieza_mantenimiento_espacios_verdes",
        "suelos_pergamino_50mil", "riego_por_pivote_central",
        "inta_mnc_2018_2019", "inta_mnc_2019_invierno", "inta_mnc_2020_invierno",
        "inta_mnc_2020_verano", "inta_mnc_2021_invierno", "inta_mnc_2021_verano",
        "inta_mnc_2022_invierno", "inta_mnc_2022_verano", "inta_mnc_2023_verano",
        "isohietas_precipitaciones_medias_anuales_pergamino_geointa",
        "cuencas_arroyo_pergamino", "cuencas_hidricas_norte_ba", "cursos_de_agua",
        "banados", "curvas_nivel_ign", "curvas_nivel_cuenca",
        "curvas_de_nivel_iatasa_abs", "puntos_de_nivel_iatasa_abs",
        "inundacion_1995", "inundacion_2016", "proyecto_presa",
        "proyecto_presa_area_inundable",
    ],
    "limites": [
        "partido_pergamino", "barrios", "localidades", "pueblos",
        "delegaciones_pueblos", "aglomerados_urbanos",
        "manchas_urbanas_historicas", "circuitos_electorales",
        "zonas_electorales_celp", "cpa",
    ],
    "servicios-municipales": [
        "dependencias_municipales", "bocas_pago_tasas",
        "centros_de_desarrollo_comunitario", "desarrollo_social",
        "areas_programaticas_desarrollo_social", "barrido_y_limpieza",
        "recoleccion_residuos_domiciliarios", "recoleccion_residuos_voluminosos",
        "contenedores_basura_reciclaje", "ecobotellas", "desecho_pilas_usadas",
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
        "puntos_de_interes", "beata_crescencia_perez",
    ],
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
