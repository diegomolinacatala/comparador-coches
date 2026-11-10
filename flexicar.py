import json

from bs4 import BeautifulSoup

from esquema import crear_anuncio
from utils import descargar, guardar_json, normalizar_cambio, normalizar_combustible

FUENTE = "flexicar"
URL_SITEMAP = "https://www.flexicar.es/sitemap-marca-modelo-provincia.xml"



def urls_valencia():
    """Devuelve la lista de URLs del sitemap que son de Valencia."""
    urls = []
    xml = descargar(URL_SITEMAP)
    soup = BeautifulSoup(xml, "xml")
    for loc in soup.find_all("loc"):
        url = loc.text
        if "coches-valencia" in url:
            urls.append(url)
    return urls



def coches_de_pagina(html):
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if script is None:
        return []
    datos = json.loads(script.string)
    return datos["props"]["pageProps"]["initialVehicles"]


def convertir(coche):
    return crear_anuncio(
        fuente=FUENTE,
        id_anuncio=coche["id"],
        url="https://www.flexicar.es/coches-ocasion/" + coche["slug"] + "/",
        marca=coche["brand"],
        modelo=coche["model"],
        version=coche["version"],
        anio=coche["year"],
        km=coche["km"],
        combustible=normalizar_combustible(coche["fuel"]),
        cambio=normalizar_cambio(coche["transmission"]),
        precio_contado=coche["cashPrice"],
        provincia="Valencia",
        tipo_vendedor="profesional",
    )


def extraer(max_paginas=1):
    anuncios = []
    ids_vistos = set()
    for url in urls_valencia()[:max_paginas]:
        html = descargar(url)
        coches = coches_de_pagina(html)
        print(" ", url, ":", len(coches), "coches")
        for coche in coches:
            if coche["id"] not in ids_vistos:
                ids_vistos.add(coche["id"])
                anuncios.append(convertir(coche))
    return anuncios


if __name__ == "__main__":
    anuncios = extraer(max_paginas=5)
    guardar_json(anuncios, "datos/flexicar.json")
    print("Guardados", len(anuncios), "anuncios en datos/flexicar.json")

    