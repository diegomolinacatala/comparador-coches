# Servidor del comparador de coches
# Guarda el catálogo de anuncios y responde a las búsquedas de los clientes,
# con los datos en formato JSON (como el servidor de libros de la Práctica 5).
#
# Uso:  python servidor.py

import json

from flask import Flask, jsonify, request

import buscador
from utils import guardar_json

app = Flask(__name__)

FICHERO_CATALOGO = "datos/catalogo_servidor.json"
WEBS = ["flexicar", "ocasionplus", "autohero", "cochescom"]
FILTROS = ["presupuesto", "marca", "modelo", "año_minimo", "km_maximo", "combustible", "cambio", "provincia"]

# Al arrancar, recuperamos el último catálogo que recibió el servidor
try:
    with open(FICHERO_CATALOGO, encoding="utf-8") as f:
        catalogo = json.load(f)
except FileNotFoundError:
    catalogo = []


@app.route("/estado", methods=["GET"])
def getEstado():
    return jsonify({"anuncios": len(catalogo)})


@app.route("/catalogo", methods=["POST"])
def postCatalogo():
    # El cliente nos envía todos los anuncios y sustituimos los que teníamos
    anuncios = request.json

    # Comprobamos que nos ha llegado una lista; si no, avisamos con el código 400
    if not isinstance(anuncios, list):
        return jsonify({"error": "Hay que enviar una lista de anuncios"}), 400

    catalogo.clear()
    for anuncio in anuncios:
        catalogo.append(anuncio)
    guardar_json(catalogo, FICHERO_CATALOGO)
    return jsonify({"guardados": len(catalogo)})


@app.route("/buscar", methods=["POST"])
def postBuscar():
    # El cliente nos envía los filtros y le devolvemos los coches que los cumplen
    filtros = request.json

    # Comprobamos que nos han llegado todos los filtros (aunque estén vacíos, con None)
    if not isinstance(filtros, dict):
        return jsonify({"error": "Los filtros tienen que enviarse como un diccionario"}), 400
    for clave in FILTROS:
        if clave not in filtros:
            return jsonify({"error": "Falta el filtro " + clave}), 400

    # Los filtros numéricos tienen que ser números enteros (o None si están vacíos)
    for clave in ["presupuesto", "año_minimo", "km_maximo"]:
        if filtros[clave] is not None and not isinstance(filtros[clave], int):
            return jsonify({"error": "El filtro " + clave + " tiene que ser un número"}), 400

    resultados = buscador.buscar(catalogo, filtros)
    alternativas = []
    if len(resultados) == 0:
        alternativas = buscador.buscar_alternativas(catalogo, filtros)
    return jsonify({"resultados": resultados, "alternativas": alternativas})


@app.route("/comparar", methods=["POST"])
def postComparar():
    # Para una marca y un modelo, contamos los coches de cada web,
    # el más barato y el precio medio
    datos = request.json

    # Comprobamos que nos han llegado la marca y el modelo
    if not isinstance(datos, dict) or "marca" not in datos or "modelo" not in datos:
        return jsonify({"error": "Hay que enviar la marca y el modelo"}), 400

    marca = datos["marca"]
    modelo = datos["modelo"]

    comparacion = []
    for web in WEBS:
        precios = []
        for anuncio in catalogo:
            if anuncio["fuente"] != web:
                continue
            if marca is not None and marca not in anuncio["marca"].lower():
                continue
            if modelo is not None and modelo not in anuncio["modelo"].lower():
                continue
            precios.append(anuncio["precio_contado"])

        if len(precios) > 0:
            comparacion.append({"web": web, "coches": len(precios), "mas_barato": min(precios),
                                "precio_medio": sum(precios) // len(precios)})
        else:
            comparacion.append({"web": web, "coches": 0})
    return jsonify(comparacion)


if __name__ == '__main__':
    print("Catálogo cargado:", len(catalogo), "anuncios")
    # host="0.0.0.0" deja que se conecten otros ordenadores de la misma red
    app.run(host="0.0.0.0", port=8080)
