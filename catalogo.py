"""
El catálogo del servidor: guardar los anuncios y buscar en ellos.

El catálogo es una lista de anuncios (formato común) que se guarda en
datos/catalogo.json, así no se pierde aunque se reinicie el servidor.
Este módulo no sabe nada de HTTP: lo usa servidor.py, y se puede probar
directamente con pytest.
"""

import json
import os

from esquema import CAMBIOS, COMBUSTIBLES, TIPOS_VENDEDOR
from limpieza import clave, normalizar_marca, normalizar_provincia
from provincias import COMUNIDADES
from utils import guardar_json

RUTA_CATALOGO = "datos/catalogo.json"

# Filtros que acepta la búsqueda y el tipo de valor que esperan
FILTROS_NUMERICOS = ["precio_max", "anio_min", "km_max"]
FILTROS_TEXTO = ["marca", "modelo", "combustible", "cambio", "provincia",
                 "comunidad", "tipo_vendedor", "fuente"]
ORDENES = ["precio", "km", "anio"]

# Alternativas cuando no hay resultados: cuánto nos podemos pasar de cada límite
MARGEN_PRECIO = 0.15   # hasta un 15 % por encima del presupuesto
MARGEN_KM = 0.15       # hasta un 15 % más de kilómetros
MARGEN_ANIO = 1        # hasta un año más antiguo
MAX_ALTERNATIVAS = 5
LIMITE_RESULTADOS = 100


# ---------------------------------------------------------------- guardar --

def cargar_catalogo(ruta=RUTA_CATALOGO):
    """Lee el catálogo del disco. Si todavía no existe, devuelve []."""
    if not os.path.exists(ruta):
        return []
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_catalogo(catalogo, ruta=RUTA_CATALOGO):
    """Guarda el catálogo en disco."""
    guardar_json(catalogo, ruta)


def anadir_anuncios(catalogo, nuevos):
    """Devuelve un catálogo nuevo con los anuncios añadidos.

    Si un anuncio ya estaba (misma fuente e id_anuncio) se sustituye por el
    nuevo, porque puede haber cambiado de precio. No modifica 'catalogo'.
    """
    por_clave = {}
    for anuncio in catalogo + nuevos:
        por_clave[(anuncio["fuente"], anuncio["id_anuncio"])] = anuncio
    return list(por_clave.values())


def resumen(catalogo):
    """Número de anuncios por web y fecha de los datos más recientes."""
    por_fuente = {}
    for anuncio in catalogo:
        por_fuente[anuncio["fuente"]] = por_fuente.get(anuncio["fuente"], 0) + 1
    return {
        "total": len(catalogo),
        "por_fuente": por_fuente,
        "fecha_datos": fecha_datos(catalogo),
    }


def fecha_datos(anuncios):
    """Fecha de recogida más reciente (texto 'AAAA-MM-DD') o None."""
    fechas = [a["fecha_recogida"] for a in anuncios if a.get("fecha_recogida")]
    if not fechas:
        return None
    return max(fechas)


# ---------------------------------------------------------------- filtros --

def validar_filtros(filtros):
    """Devuelve la lista de problemas de los filtros ([] si están bien)."""
    if not isinstance(filtros, dict):
        return ["Los filtros tienen que ser un objeto JSON"]
    problemas = []
    for nombre, valor in filtros.items():
        if valor is None:
            continue
        if nombre in FILTROS_NUMERICOS:
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
                problemas.append(nombre + " tiene que ser un número positivo")
        elif nombre in FILTROS_TEXTO:
            if not isinstance(valor, str):
                problemas.append(nombre + " tiene que ser un texto")
        else:
            problemas.append("Filtro desconocido: " + nombre)

    listas = {"combustible": COMBUSTIBLES, "cambio": CAMBIOS, "tipo_vendedor": TIPOS_VENDEDOR}
    for nombre, permitidos in listas.items():
        if isinstance(filtros.get(nombre), str) and filtros[nombre] not in permitidos:
            problemas.append(nombre + " tiene que ser uno de: " + ", ".join(permitidos))
    comunidad = filtros.get("comunidad")
    if isinstance(comunidad, str) and buscar_comunidad(comunidad) is None:
        problemas.append("Comunidad desconocida: " + comunidad)
    return problemas


def buscar_comunidad(nombre):
    """Devuelve la lista de provincias de la comunidad (sin importar tildes) o None."""
    for comunidad, provincias in COMUNIDADES.items():
        if clave(comunidad) == clave(nombre):
            return provincias
    return None


def mismo_modelo(modelo_anuncio, modelo_buscado):
    """True si el modelo del anuncio es el buscado.

    'C 3' es 'C3' y 'León' es 'Leon'. También vale si el buscado es la
    primera palabra: 'A3' encuentra 'A3 Sportback', pero '3' no encuentra '3008'.
    """
    if clave(modelo_anuncio) == clave(modelo_buscado):
        return True
    texto = sin_tildes_minusculas(modelo_anuncio)
    return texto.startswith(sin_tildes_minusculas(modelo_buscado) + " ")


def sin_tildes_minusculas(texto):
    return " ".join(clave(palabra) for palabra in str(texto or "").split())


def cumple_texto(anuncio, filtros):
    """True si el anuncio cumple los filtros de texto (marca, modelo, provincia...)."""
    if filtros.get("marca") and clave(anuncio["marca"]) != clave(normalizar_marca(filtros["marca"])):
        return False
    if filtros.get("modelo") and not mismo_modelo(anuncio["modelo"], filtros["modelo"]):
        return False
    for nombre in ["combustible", "cambio", "tipo_vendedor", "fuente"]:
        if filtros.get(nombre) and anuncio.get(nombre) != filtros[nombre]:
            return False
    if filtros.get("provincia"):
        buscada = normalizar_provincia(filtros["provincia"])
        if clave(anuncio.get("provincia")) != clave(buscada):
            return False
    if filtros.get("comunidad"):
        provincias = buscar_comunidad(filtros["comunidad"]) or []
        if anuncio.get("provincia") not in provincias:
            return False
    return True


def motivos_numericos(anuncio, filtros):
    """Lista de filtros numéricos que el anuncio no cumple, explicados.

    Si un dato falta (p. ej. el año) y hay filtro sobre él, no se puede
    comprobar y cuenta como no cumplido.
    """
    motivos = []
    precio_max = filtros.get("precio_max")
    if precio_max is not None and anuncio["precio_contado"] > precio_max:
        exceso = anuncio["precio_contado"] - precio_max
        motivos.append("Supera tu presupuesto en " + formatear_numero(exceso) + " €")

    km_max = filtros.get("km_max")
    if km_max is not None:
        if anuncio.get("km") is None:
            motivos.append("No indica los kilómetros")
        elif anuncio["km"] > km_max:
            exceso = anuncio["km"] - km_max
            motivos.append("Tiene " + formatear_numero(exceso) + " km más de los que pides")

    anio_min = filtros.get("anio_min")
    if anio_min is not None:
        if anuncio.get("anio") is None:
            motivos.append("No indica el año")
        elif anuncio["anio"] < anio_min:
            motivos.append("Es de " + str(anuncio["anio"]) + ", anterior a " + str(anio_min))
    return motivos


def cerca_de_los_limites(anuncio, filtros):
    """True si el anuncio no se pasa de los límites más que los márgenes permitidos."""
    if filtros.get("precio_max") is not None:
        if anuncio["precio_contado"] > filtros["precio_max"] * (1 + MARGEN_PRECIO):
            return False
    if filtros.get("km_max") is not None:
        if anuncio.get("km") is None or anuncio["km"] > filtros["km_max"] * (1 + MARGEN_KM):
            return False
    if filtros.get("anio_min") is not None:
        if anuncio.get("anio") is None or anuncio["anio"] < filtros["anio_min"] - MARGEN_ANIO:
            return False
    return True


def formatear_numero(numero):
    """12345 -> '12.345' (separador de miles español)."""
    return "{:,}".format(round(numero)).replace(",", ".")


# --------------------------------------------------------------- búsqueda --

def ordenar(anuncios, orden="precio"):
    """Devuelve una lista nueva ordenada: precio y km de menor a mayor, año de más nuevo a más viejo.

    Los anuncios a los que les falta el dato van al final.
    """
    if orden == "precio":
        return sorted(anuncios, key=lambda a: a["precio_contado"])
    if orden == "km":
        return sorted(anuncios, key=lambda a: (a.get("km") is None, a.get("km") or 0))
    if orden == "anio":
        return sorted(anuncios, key=lambda a: (a.get("anio") is None, -(a.get("anio") or 0)))
    raise ValueError("Orden no válido: " + str(orden))


def agrupar_por_modelo(anuncios):
    """Agrupa los anuncios por marca y modelo.

    Para cada modelo devuelve cuántos anuncios hay y, en cada web, cuántos
    y entre qué precios se mueven. Ordenado de más a menos anuncios.
    """
    grupos = {}
    for anuncio in anuncios:
        clave_grupo = (clave(anuncio["marca"]), clave(anuncio["modelo"]))
        if clave_grupo not in grupos:
            grupos[clave_grupo] = {
                "marca": anuncio["marca"],
                "modelo": anuncio["modelo"],
                "anuncios": 0,
                "por_fuente": {},
            }
        grupo = grupos[clave_grupo]
        grupo["anuncios"] += 1
        precio = anuncio["precio_contado"]
        fuente = grupo["por_fuente"].setdefault(
            anuncio["fuente"], {"anuncios": 0, "precio_min": precio, "precio_max": precio})
        fuente["anuncios"] += 1
        fuente["precio_min"] = min(fuente["precio_min"], precio)
        fuente["precio_max"] = max(fuente["precio_max"], precio)
    return sorted(grupos.values(), key=lambda g: (-g["anuncios"], g["marca"], g["modelo"]))


def buscar_alternativas(catalogo, filtros, maximo=MAX_ALTERNATIVAS):
    """Anuncios que cumplen los filtros de texto y se pasan poco de los numéricos.

    Cada alternativa es una copia del anuncio con la lista "motivos" que
    explica en qué no cumple (p. ej. "Supera tu presupuesto en 400 €").
    Primero las que fallan en menos cosas y, a igualdad, las más baratas.
    """
    alternativas = []
    for anuncio in catalogo:
        if not cumple_texto(anuncio, filtros) or not cerca_de_los_limites(anuncio, filtros):
            continue
        motivos = motivos_numericos(anuncio, filtros)
        if motivos:
            alternativa = dict(anuncio)
            alternativa["motivos"] = motivos
            alternativas.append(alternativa)
    alternativas.sort(key=lambda a: (len(a["motivos"]), a["precio_contado"]))
    return alternativas[:maximo]


def buscar(catalogo, filtros, orden="precio", agrupar=False, limite=LIMITE_RESULTADOS):
    """Busca en el catálogo los anuncios que cumplen TODOS los filtros.

    Devuelve un diccionario con:
    - total: cuántos anuncios cumplen los filtros
    - resultados: los primeros 'limite', ordenados según 'orden'
    - alternativas: solo si no hay resultados (ver buscar_alternativas)
    - grupos: solo si agrupar=True (ver agrupar_por_modelo)
    - fecha_datos: fecha de los datos más recientes del catálogo
    """
    filtros = {nombre: valor for nombre, valor in filtros.items() if valor not in (None, "")}
    encontrados = [a for a in catalogo
                   if cumple_texto(a, filtros) and not motivos_numericos(a, filtros)]
    encontrados = ordenar(encontrados, orden)

    respuesta = {
        "total": len(encontrados),
        "resultados": encontrados[:limite],
        "alternativas": [],
        "grupos": [],
        "fecha_datos": fecha_datos(catalogo),
    }
    if not encontrados:
        respuesta["alternativas"] = buscar_alternativas(catalogo, filtros)
    if agrupar:
        respuesta["grupos"] = agrupar_por_modelo(encontrados)
    return respuesta
