"""
Ejecuta los cuatro extractores, comprueba los anuncios y guarda los resultados
en la carpeta datos/.

Uso:  python recoger.py
"""


import flexicar
import ocasionplus
import cochescom
import autohero_api
from esquema import validar_anuncio
from utils import guardar_json

EXTRACTORES = [flexicar, ocasionplus, autohero_api, cochescom]
PAGINAS_POR_WEB = 2

print("web          anuncios  válidos")
for extractor in EXTRACTORES:
    anuncios = extractor.extraer(max_paginas=PAGINAS_POR_WEB)

    validos = 0
    for anuncio in anuncios:
        if validar_anuncio(anuncio) == []:
            validos += 1

    if len(anuncios) > 0:
        guardar_json(anuncios, "datos/" + extractor.FUENTE + ".json")

    print(extractor.FUENTE.ljust(12), str(len(anuncios)).rjust(8), str(validos).rjust(8))


