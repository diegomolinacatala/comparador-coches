import json
import time

import requests

from esquema import crear_anuncio
from provincias import PROVINCIAS
from utils import CABECERAS, ESPERA, guardar_json

FUENTE = "autohero"
DOMINIO = "https://www.autohero.com"
URL_API = DOMINIO + "/v1/retail-customer-gateway/graphql/searchAdV9AdsV2"
COCHES_POR_PAGINA = 24

# Cuerpo de la petición, copiado de la pestaña Red del navegador.
# Solo cambiamos "offset" para pedir cada página.
CUERPO = {
    "operationName": "searchAdV9AdsV2",
    "variables": {
        "search": {
            "offset": 0,
            "limit": COCHES_POR_PAGINA,
            "sort": "most_popular",
            "filter": {"field": "countryCode", "op": "eq", "value": "ES"},
            "aggs": [],
            "postFilter": None,
            "fields": [],
            "properties": {"filterByEligibleDate": True},
        }
    },
    "query": "query searchAdV9AdsV2($search: EsSearchRequestProjectionInput!, $tradeInId: UUID) {\n"
             "  searchAdV9AdsV2(search: $search, tradeInId: $tradeInId)\n}",
}

# Códigos de AutoHero comprobados con el texto de las tarjetas (23/10/2026).
# 1140 (semiautomático) y 1141 (doble embrague) se agrupan como automático.
COMBUSTIBLES = {1039: "gasolina", 1040: "diesel", 1044: "electrico", 1046: "hibrido"}
CAMBIOS = {1138: "manual", 1139: "automatico", 1140: "automatico", 1141: "automatico"}

# Las dos primeras cifras del código postal indican la provincia (ver provincias.py).


def pedir_pagina(offset):
    """Pide a la API 24 coches empezando en 'offset' y devuelve la lista."""
    time.sleep(ESPERA)
    CUERPO["variables"]["search"]["offset"] = offset
    cabecera = dict(CABECERAS)
    cabecera["Content-Type"] = "application/json"
    respuesta = requests.post(URL_API, headers=cabecera, data=json.dumps(CUERPO), timeout=20)
    respuesta.raise_for_status()
    datos = respuesta.json()
    return datos["data"]["searchAdV9AdsV2"]["data"]


def euros(precio):
    """Pasa un precio de AutoHero (en céntimos) a euros. None si no hay precio."""
    if not precio:
        return None
    return precio["amountMinorUnits"] // precio["conversionMajor"]


def convertir(coche):
    """Pasa un coche de AutoHero al formato común."""
    combustible = COMBUSTIBLES.get(coche["fuelType"])
    if combustible == "hibrido" and coche.get("isPluginSystem"):
        combustible = "hibrido_enchufable"

    # La versión es el subtítulo de la tarjeta: subType + subTypeExtra ("2.3 EcoBoost" + "Fastback")
    version = (coche.get("subType") or "") + " " + (coche.get("subTypeExtra") or "")
    version = version.strip()
    if version == "":
        version = None

    # Provincia de la sede donde está el coche, a partir de su código postal
    provincia = None
    sede = coche.get("esBranch")
    if sede is not None and sede.get("zipcode"):
        provincia = PROVINCIAS.get(str(sede["zipcode"])[:2])

    return crear_anuncio(
        fuente=FUENTE,
        id_anuncio=coche["id"],
        url=DOMINIO + "/es/" + coche["carUrlTitle"] + "/id/" + coche["id"] + "/",
        marca=coche["manufacturer"],
        modelo=coche["model"],
        version=version,
        anio=coche.get("firstRegistrationYear"),
        km=coche["mileage"]["distance"],
        combustible=combustible,
        cambio=CAMBIOS.get(coche["gearType"]),
        precio_contado=euros(coche.get("offerPrice")),
        provincia=provincia,
        tipo_vendedor="profesional",
    )


def extraer(max_paginas=1):
    """Pide las primeras 'max_paginas' páginas a la API y devuelve la lista de anuncios."""
    anuncios = []
    ids_vistos = set()
    for numero in range(max_paginas):
        coches = pedir_pagina(numero * COCHES_POR_PAGINA)  # offset 0, 24, 48...
        print("  Página", numero + 1, ":", len(coches), "coches")
        if len(coches) == 0:
            break
        for coche in coches:
            if coche["id"] not in ids_vistos:
                ids_vistos.add(coche["id"])
                anuncios.append(convertir(coche))
    return anuncios


if __name__ == "__main__":
    anuncios = extraer(max_paginas=5)
    guardar_json(anuncios, "datos/autohero.json")
    print("Guardados", len(anuncios), "anuncios en datos/autohero.json")
