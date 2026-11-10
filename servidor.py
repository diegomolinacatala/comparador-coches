"""
Fase 4: servidor HTTP del comparador (Flask).

Recibe los anuncios en JSON, los guarda en datos/catalogo.json y responde a
las búsquedas del cliente. Todas las respuestas tienen la misma forma:

    {"ok": true,  "datos": {...}, "error": null}      si ha ido bien
    {"ok": false, "datos": null,  "error": "..."}     si algo falla

Rutas (ejemplos completos en docs/API.md):
    GET  /estado     cuántos anuncios hay por web y de qué fecha son
    POST /anuncios   recibe una lista de anuncios y los guarda
    POST /buscar     recibe los filtros y devuelve los anuncios que los cumplen

Uso:  python servidor.py                       (solo este ordenador)
      python servidor.py --host 0.0.0.0        (accesible desde otros ordenadores de la red)
"""

import argparse
import threading

from flask import Flask, jsonify, request

from catalogo import (ORDENES, RUTA_CATALOGO, anadir_anuncios, buscar, cargar_catalogo,
                      guardar_catalogo, resumen, validar_filtros)
from esquema import validar_anuncio

PUERTO = 5000


def respuesta_ok(datos, codigo=200):
    return jsonify({"ok": True, "datos": datos, "error": None}), codigo


def respuesta_error(mensaje, codigo=400):
    return jsonify({"ok": False, "datos": None, "error": mensaje}), codigo


def crear_app(ruta_catalogo=RUTA_CATALOGO):
    """Crea la aplicación Flask. 'ruta_catalogo' permite usar otro fichero en los tests."""
    app = Flask(__name__)
    app.json.ensure_ascii = False  # que las tildes salgan tal cual en el JSON
    estado = {"catalogo": cargar_catalogo(ruta_catalogo)}
    cerrojo = threading.Lock()  # para que dos envíos a la vez no se pisen

    @app.get("/estado")
    def ver_estado():
        return respuesta_ok(resumen(estado["catalogo"]))

    @app.post("/anuncios")
    def recibir_anuncios():
        anuncios = request.get_json(silent=True)
        if not isinstance(anuncios, list):
            return respuesta_error("Hay que enviar una lista de anuncios en JSON")

        validos = []
        rechazados = []
        for anuncio in anuncios:
            if not isinstance(anuncio, dict):
                rechazados.append({"anuncio": anuncio, "problemas": ["No es un objeto JSON"]})
                continue
            problemas = validar_anuncio(anuncio)
            if problemas:
                rechazados.append({"fuente": anuncio.get("fuente"),
                                   "id_anuncio": anuncio.get("id_anuncio"),
                                   "problemas": problemas})
            else:
                validos.append(anuncio)

        with cerrojo:
            estado["catalogo"] = anadir_anuncios(estado["catalogo"], validos)
            guardar_catalogo(estado["catalogo"], ruta_catalogo)
            total = len(estado["catalogo"])

        return respuesta_ok({
            "recibidos": len(anuncios),
            "guardados": len(validos),
            "rechazados": rechazados,
            "total_catalogo": total,
        })

    @app.post("/buscar")
    def buscar_anuncios():
        consulta = request.get_json(silent=True)
        if not isinstance(consulta, dict):
            return respuesta_error("Hay que enviar la consulta como un objeto JSON")

        filtros = consulta.get("filtros", {})
        problemas = validar_filtros(filtros)
        orden = consulta.get("orden", "precio")
        if orden not in ORDENES:
            problemas.append("orden tiene que ser uno de: " + ", ".join(ORDENES))
        agrupar = consulta.get("agrupar", False)
        if not isinstance(agrupar, bool):
            problemas.append("agrupar tiene que ser true o false")
        if problemas:
            return respuesta_error("; ".join(problemas))

        return respuesta_ok(buscar(estado["catalogo"], filtros, orden=orden, agrupar=agrupar))

    @app.errorhandler(404)
    def no_encontrado(error):
        return respuesta_error("Ruta no encontrada: " + request.path, 404)

    @app.errorhandler(405)
    def metodo_no_permitido(error):
        return respuesta_error("Método " + request.method + " no permitido en " + request.path, 405)

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor del comparador de coches")
    parser.add_argument("--host", default="127.0.0.1",
                        help="0.0.0.0 para aceptar conexiones de otros ordenadores")
    parser.add_argument("--puerto", type=int, default=PUERTO)
    argumentos = parser.parse_args()

    app = crear_app()
    print("Catálogo con", resumen(cargar_catalogo())["total"], "anuncios")
    app.run(host=argumentos.host, port=argumentos.puerto)
