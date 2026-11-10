"""
Funciones que comparten los cuatro extractores: descargar páginas, guardar
JSON y pasar combustible y cambio al vocabulario común.
"""

import json
import os
import time
import unicodedata

import requests

# Cabecera de navegador y pausa entre peticiones para no sobrecargar las webs.
CABECERAS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
}
ESPERA = 3
# coches.com a veces no acepta la conexión a la primera (pasa unos 20 s sin
# responder y al siguiente intento contesta en 1 s): se reintenta hasta 3 veces.
REINTENTOS = 3


def descargar(url):
    """Descarga una página (esperando ESPERA segundos antes) y devuelve su texto."""
    for intento in range(1, REINTENTOS + 1):
        time.sleep(ESPERA)
        try:
            respuesta = requests.get(url, headers=CABECERAS, timeout=30)
            respuesta.raise_for_status()
            return respuesta.text
        except (requests.ConnectionError, requests.Timeout):
            if intento == REINTENTOS:
                raise
            print("    Sin respuesta, reintento", intento, "de", REINTENTOS - 1)


def guardar_json(datos, ruta):
    """Guarda 'datos' en un fichero JSON (crea la carpeta si no existe)."""
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def sin_tildes(texto):
    """'Híbrido Enchufable' -> 'hibrido enchufable'."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    return texto.encode("ascii", "ignore").decode().strip()


def normalizar_combustible(texto):
    """Pasa el combustible de cada web al vocabulario común (ver esquema.py).

    El orden importa: en coches.com todos los híbridos llevan también la
    palabra «Gasolina» («Híbrido Enchufable Gasolina»), así que se mira
    primero si es híbrido. Si no se reconoce, se devuelve el texto tal cual
    para que validar_anuncio() lo señale.
    """
    if texto is None:
        return None
    texto = sin_tildes(texto)
    if "enchufable" in texto and "no enchufable" not in texto:
        return "hibrido_enchufable"
    if "hibrid" in texto:
        return "hibrido"
    if "electric" in texto:
        return "electrico"
    if "diesel" in texto:
        return "diesel"
    if "gasolina" in texto:
        return "gasolina"
    if "glp" in texto or "licuado" in texto:
        return "glp"
    if "gnc" in texto or "natural" in texto:
        return "gnc"
    return texto


def normalizar_cambio(texto):
    """'Manual' -> 'manual'; 'Automático', 'AUTO', semiautomático... -> 'automatico'."""
    if texto is None:
        return None
    texto = sin_tildes(texto)
    if "manual" in texto:
        return "manual"
    if "auto" in texto or "embrague" in texto:
        return "automatico"
    return texto
