"""
Fase 3: limpieza e integración de los anuncios de las cuatro webs.

Los extractores ya devuelven el formato común (esquema.py), pero cada web
escribe las cosas a su manera: «CITROEN», «Citroen» y «Citroën»; «MERCEDES» y
«Mercedes-Benz»; «QASHQAI» y «Qashqai»; «C 3» y «C3». Aquí se unifican para
que los filtros del buscador funcionen igual con todas las webs.

Las funciones no modifican el anuncio original: devuelven uno nuevo.

Uso:  from limpieza import limpiar_anuncios
"""

from datetime import date

from esquema import validar_anuncio
from provincias import ALIAS_PROVINCIAS, PROVINCIAS
from utils import sin_tildes

# Nombre que usaremos para cada marca. La clave es clave(marca), así
# "CITROEN", "Citroen" y "Citroën" acaban todas en "Citroën".
MARCAS = {
    "citroen": "Citroën",
    "mercedes": "Mercedes-Benz",
    "mercedesbenz": "Mercedes-Benz",
    "ds": "DS",
    "dsautomobiles": "DS",
    "alfaromeo": "Alfa Romeo",
    "kia": "Kia",
    "dr": "DR",
    "drautomobiles": "DR",
    "seat": "Seat",
    "mini": "Mini",
    "vw": "Volkswagen",
    "landrover": "Land Rover",
    "lynkco": "Lynk & Co",
    "byd": "BYD",
    "mg": "MG",
    "bmw": "BMW",
}

# Nombre oficial de cada provincia, a partir de su clave
PROVINCIAS_POR_CLAVE = {}
for _nombre in PROVINCIAS.values():
    PROVINCIAS_POR_CLAVE[sin_tildes(_nombre).replace(" ", "")] = _nombre
PROVINCIAS_POR_CLAVE.update(ALIAS_PROVINCIAS)

# Límites para avisar de valores atípicos (no se descartan, solo se avisa)
PRECIO_MIN = 500
PRECIO_MAX = 300_000
KM_MAX = 1_000_000
ANIO_MIN = 1950


def clave(texto):
    """Texto para comparar: minúsculas, sin tildes y solo letras y números.

    'C 3' -> 'c3', 'León' -> 'leon', 'Mercedes-Benz' -> 'mercedesbenz'.
    """
    if texto is None:
        return ""
    return "".join(letra for letra in sin_tildes(str(texto)) if letra.isalnum())


def quitar_mayusculas(texto):
    """'PEUGEOT' -> 'Peugeot', 'ALFA ROMEO' -> 'Alfa Romeo'.

    Solo cambia textos que están enteros en mayúsculas y cuyas palabras son
    solo letras y de más de 3 caracteres, para no estropear siglas como
    'BMW', 'C-HR', 'EQS' o 'UX'.
    """
    palabras = texto.split()
    if texto.isupper() and all(p.isalpha() and len(p) > 3 for p in palabras):
        return texto.title()
    return texto


def normalizar_marca(marca):
    """Devuelve el nombre común de la marca ('CITROEN' -> 'Citroën')."""
    if marca is None:
        return None
    marca = " ".join(str(marca).split())
    if clave(marca) in MARCAS:
        return MARCAS[clave(marca)]
    return quitar_mayusculas(marca)


def normalizar_modelo(modelo):
    """Quita espacios sobrantes y mayúsculas enteras ('QASHQAI' -> 'Qashqai')."""
    if modelo is None:
        return None
    return quitar_mayusculas(" ".join(str(modelo).split()))


def normalizar_provincia(provincia):
    """Devuelve el nombre oficial de la provincia ('València' -> 'Valencia').

    Si viene en dos idiomas ('Alicante/Alacant') se mira la primera parte.
    Si no se reconoce, se devuelve tal cual (sin inventar nada).
    """
    if provincia is None or str(provincia).strip() == "":
        return None
    primera = str(provincia).split("/")[0].strip()
    return PROVINCIAS_POR_CLAVE.get(clave(primera), primera)


def limpiar_anuncio(anuncio):
    """Devuelve una copia del anuncio con marca, modelo, versión y provincia unificados."""
    limpio = dict(anuncio)
    limpio["marca"] = normalizar_marca(anuncio.get("marca"))
    limpio["modelo"] = normalizar_modelo(anuncio.get("modelo"))
    if anuncio.get("version"):
        limpio["version"] = " ".join(str(anuncio["version"]).split())
    limpio["provincia"] = normalizar_provincia(anuncio.get("provincia"))
    return limpio


def avisos_atipicos(anuncio):
    """Devuelve la lista de valores raros del anuncio ([] si no hay ninguno)."""
    avisos = []
    precio = anuncio.get("precio_contado")
    if isinstance(precio, (int, float)) and not PRECIO_MIN <= precio <= PRECIO_MAX:
        avisos.append("Precio atípico: " + str(precio))
    km = anuncio.get("km")
    if isinstance(km, int) and km > KM_MAX:
        avisos.append("Kilómetros atípicos: " + str(km))
    anio = anuncio.get("anio")
    if isinstance(anio, int) and not ANIO_MIN <= anio <= date.today().year + 1:
        avisos.append("Año atípico: " + str(anio))
    return avisos


def limpiar_anuncios(anuncios):
    """Limpia una lista de anuncios.

    Devuelve (limpios, descartados):
    - limpios: anuncios unificados, válidos y sin repetir (misma fuente e id).
    - descartados: lista de {"anuncio", "problemas"} con los que no pasan
      validar_anuncio() (p. ej. sin precio o sin modelo) o están repetidos.
    """
    limpios = []
    descartados = []
    vistos = set()
    for anuncio in anuncios:
        limpio = limpiar_anuncio(anuncio)
        problemas = validar_anuncio(limpio)
        identificador = (limpio.get("fuente"), limpio.get("id_anuncio"))
        if identificador in vistos:
            problemas.append("Repetido")
        if problemas:
            descartados.append({"anuncio": anuncio, "problemas": problemas})
            continue
        vistos.add(identificador)
        limpios.append(limpio)
    return limpios, descartados
