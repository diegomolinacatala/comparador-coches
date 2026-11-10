"""
Limpia los anuncios de datos/<fuente>.json y los envía al servidor por HTTP.

Es el paso entre la recogida (recoger.py) y el buscador (cliente.py):
    python recoger.py     -> datos/flexicar.json, datos/ocasionplus.json...
    python enviar.py      -> el servidor los guarda en datos/catalogo.json

Uso:  python enviar.py                                  (servidor en este ordenador)
      python enviar.py --servidor http://192.168.1.20:5000
"""

import argparse
import json
import os

import requests

from limpieza import limpiar_anuncios

FUENTES = ["flexicar", "ocasionplus", "autohero", "cochescom"]
SERVIDOR = "http://127.0.0.1:5000"


def leer_fuente(fuente, carpeta="datos"):
    """Devuelve los anuncios de datos/<fuente>.json ([] si el fichero no existe)."""
    ruta = os.path.join(carpeta, fuente + ".json")
    if not os.path.exists(ruta):
        print("  No existe", ruta, "(¿has ejecutado python recoger.py?)")
        return []
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def enviar(anuncios, servidor=SERVIDOR):
    """Envía una lista de anuncios al servidor y devuelve el campo 'datos' de su respuesta."""
    respuesta = requests.post(servidor + "/anuncios", json=anuncios, timeout=30)
    cuerpo = respuesta.json()
    if not cuerpo["ok"]:
        raise ValueError("El servidor ha rechazado el envío: " + cuerpo["error"])
    return cuerpo["datos"]


def main():
    parser = argparse.ArgumentParser(description="Envía los anuncios recogidos al servidor")
    parser.add_argument("--servidor", default=SERVIDOR)
    argumentos = parser.parse_args()

    print("web          leídos  limpios  descartados  guardados")
    resultado = None
    for fuente in FUENTES:
        anuncios = leer_fuente(fuente)
        if not anuncios:
            continue
        limpios, descartados = limpiar_anuncios(anuncios)
        try:
            resultado = enviar(limpios, argumentos.servidor)
        except requests.ConnectionError:
            print("No se puede conectar con el servidor en", argumentos.servidor)
            print("¿Está arrancado? (python servidor.py)")
            return
        print(fuente.ljust(12), str(len(anuncios)).rjust(6), str(len(limpios)).rjust(8),
              str(len(descartados)).rjust(12), str(resultado["guardados"]).rjust(10))
        for descartado in descartados:
            print("    descartado", descartado["anuncio"].get("id_anuncio"), descartado["problemas"])

    if resultado is not None:
        print("Total en el catálogo del servidor:", resultado["total_catalogo"])


if __name__ == "__main__":
    main()
