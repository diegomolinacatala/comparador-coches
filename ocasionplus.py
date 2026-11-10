import json

from bs4 import BeautifulSoup

from esquema import crear_anuncio
from utils import descargar, guardar_json, normalizar_cambio, normalizar_combustible

FUENTE = "ocasionplus"
DOMINIO = "https://www.ocasionplus.com"
URL_VALENCIA = DOMINIO + "/coches-segunda-mano/valencia"


def url_pagina(numero):
    """Devuelve la URL de la página 'numero' del listado de Valencia."""
    if numero == 1:
        return URL_VALENCIA
    return URL_VALENCIA + "?page=" + str(numero)


def coches_de_pagina(html):
    """Devuelve la lista de coches (diccionarios del JSON) de una página,
    añadiendo a cada uno la ubicación que aparece en su tarjeta."""
    soup = BeautifulSoup(html, "html.parser")
    coches = []
    for script in soup.find_all("script", type="application/ld+json"):
        datos = json.loads(script.string)
        if datos.get("@type") == "ItemList":
            for coche in datos["itemListElement"]:
                if coche.get("@type") == "Vehicle":
                    coche["ubicacion"] = buscar_ubicacion(soup, coche)
                    coches.append(coche)
    return coches


def buscar_ubicacion(soup, coche):
    """Busca la tarjeta del coche en el HTML y devuelve su ubicación (p. ej. "Valencia - Alzira")."""
    ruta = coche["offers"]["url"].replace(DOMINIO, "")
    tarjeta = soup.find("a", href=ruta)
    if tarjeta is None:
        return None
    ubicacion = tarjeta.find("div", attrs={"data-test": "div-dealer"})
    if ubicacion is None:
        return None
    return ubicacion.get_text(" ", strip=True)


def convertir(coche):
    """Pasa un coche de OcasionPlus al formato común."""
    marca = coche["brand"]["name"]

    # "name" es "Audi A3": quitamos la marca para quedarnos con el modelo
    nombre = coche["name"]
    modelo = nombre
    if nombre.startswith(marca + " "):
        modelo = nombre[len(marca) + 1:]

    # "model" es "Audi A3 Sportback Attraction 1.4 TFSI...": quitamos marca y modelo.
    # Se compara en minúsculas porque a veces cambian ("Nissan QASHQAI" / "Nissan Qashqai")
    version = coche["model"]
    if version.lower().startswith(nombre.lower() + " "):
        version = version[len(nombre) + 1:]

    # La ubicación es "Valencia - Alzira": la provincia es lo que va antes del guion
    provincia = None
    if coche["ubicacion"] is not None:
        provincia = coche["ubicacion"].split(" - ")[0]

    url = coche["offers"]["url"]
    return crear_anuncio(
        fuente=FUENTE,
        id_anuncio=url.split("-")[-1],  # la URL acaba en un código único, p. ej. ...-2016-0rakfyak
        url=url,
        marca=marca,
        modelo=modelo,
        version=version,
        anio=int(coche["productionDate"][:4]),  # "2016-03-31T00:00..." -> 2016
        km=int(coche["mileageFromOdometer"]["value"]),
        combustible=normalizar_combustible(coche["fuelType"]),
        cambio=normalizar_cambio(coche["vehicleTransmission"]),
        precio_contado=int(coche["offers"]["price"]),
        provincia=provincia,
        tipo_vendedor="profesional",
    )


def extraer(max_paginas=1):
    """Descarga las primeras 'max_paginas' páginas y devuelve la lista de anuncios."""
    anuncios = []
    ids_vistos = set()
    for numero in range(1, max_paginas + 1):
        html = descargar(url_pagina(numero))
        coches = coches_de_pagina(html)
        print("  Página", numero, ":", len(coches), "coches")
        for coche in coches:
            anuncio = convertir(coche)
            if anuncio["id_anuncio"] not in ids_vistos:
                ids_vistos.add(anuncio["id_anuncio"])
                anuncios.append(anuncio)
    return anuncios


if __name__ == "__main__":
    anuncios = extraer(max_paginas=2)
    guardar_json(anuncios, "datos/ocasionplus.json")
    print("Guardados", len(anuncios), "anuncios en datos/ocasionplus.json")