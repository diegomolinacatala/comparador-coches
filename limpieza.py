# Limpieza de los datos
# Junta los anuncios de las cuatro webs, unifica las marcas, los modelos y las
# provincias, quita los anuncios con datos raros o repetidos y guarda todo en
# datos/catalogo.json

import json

from esquema import validar_anuncio
from utils import guardar_json

WEBS = ["flexicar", "ocasionplus", "autohero", "cochescom"]

# Marcas que cada web escribe de forma distinta (en minúsculas y sin guiones)
MARCAS = {
    "mercedes": "Mercedes-Benz",
    "mercedes benz": "Mercedes-Benz",
    "citroen": "Citroën",
    "citroën": "Citroën",
    "kia": "Kia",
    "seat": "Seat",
    "cupra": "Cupra",
    "mini": "Mini",
    "bmw": "BMW",
    "mg": "MG",
    "ds": "DS",
    "ds automobiles": "DS",
    "byd": "BYD",
    "dr automobiles": "DR",
    "dr": "DR"}

# Provincias que coches.com escribe al revés o con otro nombre
PROVINCIAS = {
    "Palmas, Las": "Las Palmas",
    "Coruña, A": "A Coruña",
    "Rioja, La": "La Rioja",
    "Balears, Illes": "Baleares",
    "Guipúzcoa": "Gipuzkoa",
    "Vizcaya": "Bizkaia",
    "Tenerife": "Santa Cruz de Tenerife"}

# Límites para quitar valores que no tienen sentido
PRECIO_MINIMO = 500
PRECIO_MAXIMO = 500000
KM_MAXIMO = 1000000
ANIO_MINIMO = 1950
ANIO_MAXIMO = 2027


def cargar_anuncios():
    # Lee el JSON de cada web y junta todos los anuncios en una lista
    anuncios = []
    for web in WEBS:
        with open("datos/" + web + ".json", encoding="utf-8") as f:
            datos = json.load(f)
        print(" ", web, ":", len(datos), "anuncios")
        anuncios = anuncios + datos
    return anuncios


def unificar_marca(marca):
    clave = marca.lower().replace("-", " ")
    if clave in MARCAS:
        return MARCAS[clave]
    # Si viene todo en mayúsculas ("VOLKSWAGEN"), la ponemos como "Volkswagen"
    if marca.isupper():
        return marca.title()
    return marca


def unificar_modelo(marca, modelo):
    # Si el modelo repite la marca ("Mini Countryman"), la quitamos.
    # En DS no, porque el modelo se llama así ("DS 4")
    if marca != "DS" and modelo.lower().startswith(marca.lower() + " "):
        modelo = modelo[len(marca) + 1:]
    # Si el modelo es una palabra en mayúsculas ("QASHQAI"), la ponemos como "Qashqai"
    if modelo.isupper() and modelo.isalpha() and len(modelo) > 3:
        modelo = modelo.title()
    return modelo


def quitar_tildes(texto):
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i")
    texto = texto.replace("ó", "o").replace("ú", "u").replace("ë", "e")
    return texto


def unificar_version(marca, modelo, version):
    # Algunas webs repiten la marca y el modelo en la versión:
    # "Renault Scenic Dynamique dCi" -> "Dynamique dCi"
    if version is None:
        return None
    palabras = version.split(" ")
    if quitar_tildes(palabras[0].lower()) != quitar_tildes(marca.lower()):
        return version
    # Quitamos las primeras palabras mientras sean la marca o parte del modelo
    palabras_quitar = quitar_tildes(marca.lower() + " " + modelo.lower()).split(" ")
    while len(palabras) > 0 and quitar_tildes(palabras[0].lower()) in palabras_quitar:
        palabras = palabras[1:]
    return " ".join(palabras)


def unificar_provincia(provincia):
    if provincia in PROVINCIAS:
        return PROVINCIAS[provincia]
    return provincia


def es_correcto(anuncio):
    # Devuelve True si el anuncio tiene datos con sentido
    if validar_anuncio(anuncio) != []:
        return False
    if anuncio["precio_contado"] < PRECIO_MINIMO or anuncio["precio_contado"] > PRECIO_MAXIMO:
        return False
    if anuncio["km"] is not None and anuncio["km"] > KM_MAXIMO:
        return False
    if anuncio["anio"] is not None:
        if anuncio["anio"] < ANIO_MINIMO or anuncio["anio"] > ANIO_MAXIMO:
            return False
    return True


def limpiar(anuncios):
    catalogo = []
    vistos = []
    descartados = 0
    repetidos = 0

    for anuncio in anuncios:
        anuncio["marca"] = unificar_marca(anuncio["marca"])
        anuncio["modelo"] = unificar_modelo(anuncio["marca"], anuncio["modelo"])
        anuncio["version"] = unificar_version(anuncio["marca"], anuncio["modelo"], anuncio["version"])
        anuncio["provincia"] = unificar_provincia(anuncio["provincia"])

        # Para saber si está repetido usamos la web y el identificador del anuncio
        clave = anuncio["fuente"] + "-" + anuncio["id_anuncio"]

        if not es_correcto(anuncio):
            descartados = descartados + 1
        elif clave in vistos:
            repetidos = repetidos + 1
        else:
            vistos.append(clave)
            catalogo.append(anuncio)

    print("Descartados por datos incorrectos:", descartados)
    print("Descartados por estar repetidos:", repetidos)
    return catalogo


def contar_marcas(anuncios):
    marcas = []
    for anuncio in anuncios:
        if anuncio["marca"] not in marcas:
            marcas.append(anuncio["marca"])
    return len(marcas)


def crear_catalogo():
    print("Leyendo los datos de cada web:")
    anuncios = cargar_anuncios()
    marcas_antes = contar_marcas(anuncios)

    catalogo = limpiar(anuncios)
    marcas_despues = contar_marcas(catalogo)

    guardar_json(catalogo, "datos/catalogo.json")
    print("Anuncios leídos:", len(anuncios))
    print("Anuncios en el catálogo:", len(catalogo))
    print("Marcas distintas: antes", marcas_antes, "y después", marcas_despues)


if __name__ == "__main__":
    crear_catalogo()

