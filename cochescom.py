import json

from bs4 import BeautifulSoup

from esquema import crear_anuncio
from utils import descargar, guardar_json, normalizar_cambio, normalizar_combustible

FUENTE = "cochescom"
DOMINIO = "https://www.coches.com"
URL_LISTADO = DOMINIO + "/coches-segunda-mano/coches-ocasion.htm"


def url_pagina(numero):
    """Devuelve la URL de la página 'numero' del listado."""
    if numero == 1:
        return URL_LISTADO
    return URL_LISTADO + "?page=" + str(numero)


def enlaces_de_pagina(soup):
    """Devuelve un diccionario {visibleId: enlace a la ficha} con los enlaces del HTML."""
    enlaces = {}
    for a in soup.find_all("a"):
        href = a.get("href")
        if href is not None and "?id=" in href:
            id_coche = href.split("?id=")[1]
            if href.startswith("/"):
                href = DOMINIO + href
            enlaces[id_coche] = href
    return enlaces


def coches_de_pagina(html):
    """Devuelve la lista de coches de una página, añadiendo a cada uno el enlace a su ficha."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if script is None:
        return []
    datos = json.loads(script.string)
    coches = datos["props"]["pageProps"]["classifieds"]["classifiedList"]
    enlaces = enlaces_de_pagina(soup)
    for coche in coches:
        coche["enlace"] = enlaces.get(coche["visibleId"])
    return coches


def convertir(coche):
    """Pasa un coche de coches.com al formato común."""
    anio = None
    if coche.get("registration") and coche["registration"].get("year"):
        anio = int(coche["registration"]["year"])  # viene como texto: "2022"

    tipo_vendedor = "profesional"
    if coche.get("dealer") and coche["dealer"].get("type") == "INDIVIDUAL":
        tipo_vendedor = "particular"

    provincia = None
    if coche.get("currentProvince"):
        provincia = coche["currentProvince"]["name"]

    return crear_anuncio(
        fuente=FUENTE,
        id_anuncio=coche["visibleId"],
        url=coche["enlace"],
        marca=coche["make"]["name"],
        modelo=coche["model"]["name"],
        version=coche["version"]["name"],
        anio=anio,
        km=coche["mileage"]["amount"],
        combustible=normalizar_combustible(coche["fuel"]["name"]),
        cambio=normalizar_cambio(coche["transmission"]["name"]),
        precio_contado=coche["price"]["amount"],
        provincia=provincia,
        tipo_vendedor=tipo_vendedor,
    )


def extraer(max_paginas=1):
    """Descarga las primeras 'max_paginas' páginas y devuelve la lista de anuncios
    (solo coches de ocasión, sin km 0 ni seminuevos)."""
    anuncios = []
    ids_vistos = set()
    for numero in range(1, max_paginas + 1):
        html = descargar(url_pagina(numero))
        coches = coches_de_pagina(html)
        print("  Página", numero, ":", len(coches), "coches")
        for coche in coches:
            if coche["isKm0"]:
                continue
            if coche["visibleId"] not in ids_vistos:
                ids_vistos.add(coche["visibleId"])
                anuncios.append(convertir(coche))
    return anuncios


if __name__ == "__main__":
    anuncios = extraer(max_paginas=5)
    guardar_json(anuncios, "datos/cochescom.json")
    print("Guardados", len(anuncios), "anuncios en datos/cochescom.json")
