"""
Fase 5: cliente de consola del comparador.

Pide los filtros al usuario, los envía al servidor (POST /buscar) y muestra
los resultados. Si no hay ninguno, enseña alternativas cercanas por separado.

Uso:  python cliente.py                                   (pregunta los filtros)
      python cliente.py --precio-max 12000 --marca seat   (una búsqueda directa)
      python cliente.py --servidor http://192.168.1.20:5000
"""

import argparse

import requests

from catalogo import formatear_numero
from esquema import CAMBIOS, COMBUSTIBLES, TIPOS_VENDEDOR

SERVIDOR = "http://127.0.0.1:5000"
ORDENES = ["precio", "km", "anio"]
ANCHO_COCHE = 42


class ErrorServidor(Exception):
    """El servidor ha respondido con ok = false."""


# ------------------------------------------------------- pedir los filtros --

def pedir_numero(pregunta, entrada=input):
    """Pregunta un número entero. Enter = sin filtro (None)."""
    while True:
        texto = entrada(pregunta).replace(".", "").replace("€", "").strip()
        if texto == "":
            return None
        if texto.isdigit():
            return int(texto)
        print("  Escribe un número sin decimales (o pulsa Enter para no filtrar).")


def pedir_opcion(pregunta, opciones, entrada=input, por_defecto=None):
    """Pregunta una de las 'opciones'. Enter = 'por_defecto'."""
    while True:
        texto = entrada(pregunta + " (" + "/".join(opciones) + "): ").strip().lower()
        if texto == "":
            return por_defecto
        if texto in opciones:
            return texto
        print("  Opción no válida.")


def pedir_consulta(entrada=input):
    """Pregunta todos los filtros y devuelve la consulta lista para enviar."""
    print("Pulsa Enter para dejar un filtro vacío.")
    filtros = {
        "precio_max": pedir_numero("Presupuesto máximo (€): ", entrada),
        "marca": entrada("Marca: ").strip(),
        "modelo": entrada("Modelo: ").strip(),
        "anio_min": pedir_numero("Año mínimo: ", entrada),
        "km_max": pedir_numero("Kilómetros máximos: ", entrada),
        "combustible": pedir_opcion("Combustible", COMBUSTIBLES, entrada),
        "cambio": pedir_opcion("Cambio", CAMBIOS, entrada),
        "provincia": entrada("Provincia: ").strip(),
        "comunidad": entrada("Comunidad autónoma (p. ej. Comunidad Valenciana): ").strip(),
        "tipo_vendedor": pedir_opcion("Tipo de vendedor", TIPOS_VENDEDOR, entrada),
    }
    orden = pedir_opcion("Ordenar por", ORDENES, entrada, por_defecto="precio")
    agrupar = pedir_opcion("¿Agrupar por modelo?", ["s", "n"], entrada, por_defecto="n") == "s"
    return crear_consulta(filtros, orden, agrupar)


def crear_consulta(filtros, orden="precio", agrupar=False):
    """Quita los filtros vacíos y monta el JSON que espera POST /buscar."""
    filtros = {nombre: valor for nombre, valor in filtros.items() if valor not in (None, "")}
    return {"filtros": filtros, "orden": orden, "agrupar": agrupar}


# ------------------------------------------------------ hablar con el servidor --

def consultar(consulta, servidor=SERVIDOR):
    """Envía la consulta al servidor y devuelve el campo 'datos' de la respuesta."""
    respuesta = requests.post(servidor + "/buscar", json=consulta, timeout=30)
    cuerpo = respuesta.json()
    if not cuerpo["ok"]:
        raise ErrorServidor(cuerpo["error"])
    return cuerpo["datos"]


# ----------------------------------------------------------- mostrar datos --

def describir_anuncio(anuncio):
    """Una línea con lo principal del anuncio."""
    coche = " ".join(str(p) for p in [anuncio["marca"], anuncio["modelo"], anuncio.get("version")] if p)
    if len(coche) > ANCHO_COCHE:
        coche = coche[:ANCHO_COCHE - 2] + ".."
    km = formatear_numero(anuncio["km"]) + " km" if anuncio.get("km") is not None else "? km"
    return "  ".join([
        (formatear_numero(anuncio["precio_contado"]) + " €").rjust(9),
        coche.ljust(ANCHO_COCHE),
        str(anuncio.get("anio") or "?").rjust(4),
        km.rjust(11),
        str(anuncio.get("combustible") or "?").ljust(18),
        str(anuncio.get("cambio") or "?").ljust(10),
        str(anuncio.get("provincia") or "?").ljust(12),
        anuncio["fuente"],
    ])


def mostrar_anuncios(anuncios):
    for anuncio in anuncios:
        print(describir_anuncio(anuncio))
        for motivo in anuncio.get("motivos", []):
            print(" " * 11 + "-> " + motivo)
        print(" " * 11 + anuncio["url"])


def mostrar_grupos(grupos):
    print("\nAnuncios por modelo:")
    for grupo in grupos:
        print("  " + grupo["marca"] + " " + grupo["modelo"] + ": " + str(grupo["anuncios"]) + " anuncios")
        for fuente, datos in grupo["por_fuente"].items():
            print("      " + fuente.ljust(12) + str(datos["anuncios"]).rjust(3) + " anuncios, de "
                  + formatear_numero(datos["precio_min"]) + " a "
                  + formatear_numero(datos["precio_max"]) + " €")


def mostrar_resultados(datos):
    print("\nDatos recogidos el", datos["fecha_datos"])
    if datos["total"] == 0:
        print("No hay ningún coche que cumpla todos los filtros.")
        if datos["alternativas"]:
            print("\nAlternativas que se pasan un poco de lo que pides:")
            mostrar_anuncios(datos["alternativas"])
        return

    mostrados = len(datos["resultados"])
    print(datos["total"], "coches cumplen los filtros", end="")
    print(" (se muestran los " + str(mostrados) + " primeros)" if mostrados < datos["total"] else "")
    mostrar_anuncios(datos["resultados"])
    if datos["grupos"]:
        mostrar_grupos(datos["grupos"])


def buscar_y_mostrar(consulta, servidor):
    """Hace la búsqueda y muestra el resultado o un mensaje de error claro."""
    try:
        mostrar_resultados(consultar(consulta, servidor))
    except requests.ConnectionError:
        print("No se puede conectar con el servidor en", servidor, "(¿está arrancado?)")
    except requests.Timeout:
        print("El servidor ha tardado demasiado en responder.")
    except ErrorServidor as error:
        print("El servidor no acepta la búsqueda:", error)


def main():
    parser = argparse.ArgumentParser(description="Buscador del comparador de coches")
    parser.add_argument("--servidor", default=SERVIDOR)
    parser.add_argument("--precio-max", type=int)
    parser.add_argument("--marca")
    parser.add_argument("--modelo")
    parser.add_argument("--anio-min", type=int)
    parser.add_argument("--km-max", type=int)
    parser.add_argument("--combustible", choices=COMBUSTIBLES)
    parser.add_argument("--cambio", choices=CAMBIOS)
    parser.add_argument("--provincia")
    parser.add_argument("--comunidad")
    parser.add_argument("--tipo-vendedor", choices=TIPOS_VENDEDOR)
    parser.add_argument("--orden", choices=ORDENES, default="precio")
    parser.add_argument("--agrupar", action="store_true")
    argumentos = vars(parser.parse_args())

    servidor = argumentos.pop("servidor")
    orden = argumentos.pop("orden")
    agrupar = argumentos.pop("agrupar")
    if any(valor is not None for valor in argumentos.values()):
        buscar_y_mostrar(crear_consulta(argumentos, orden, agrupar), servidor)
        return

    while True:
        buscar_y_mostrar(pedir_consulta(), servidor)
        if pedir_opcion("\n¿Otra búsqueda?", ["s", "n"], por_defecto="n") != "s":
            break


if __name__ == "__main__":
    main()
