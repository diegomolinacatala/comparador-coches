# Buscador de coches
# Pide los filtros al usuario, busca en datos/catalogo.json los coches que los
# cumplen y los muestra ordenados por precio. Si no hay ninguno, enseña
# alternativas que se pasan un poco del presupuesto.

import json

# Cuánto se puede pasar del presupuesto una alternativa (10 %)
MARGEN_ALTERNATIVAS = 0.10
MAXIMO_RESULTADOS = 10


def cargar_catalogo():
    with open("datos/catalogo.json", encoding="utf-8") as f:
        return json.load(f)


def pedir_numero(pregunta):
    # Pide un número. Si el usuario no escribe nada, devuelve None (sin filtro)
    while True:
        respuesta = input(pregunta).strip().replace(".", "")
        if respuesta == "":
            return None
        if respuesta.isdigit():
            return int(respuesta)
        print("  Escribe solo números, o pulsa Enter para no filtrar")


def pedir_texto(pregunta):
    # Pide un texto. Si el usuario no escribe nada, devuelve None (sin filtro)
    respuesta = input(pregunta).strip()
    if respuesta == "":
        return None
    return respuesta.lower()


def pedir_filtros():
    print("\nIndica tus filtros (pulsa Enter para dejar uno vacío)")
    filtros = {}
    filtros["presupuesto"] = pedir_numero("Presupuesto máximo (€): ")
    filtros["marca"] = pedir_texto("Marca: ")
    filtros["modelo"] = pedir_texto("Modelo: ")
    filtros["anio_minimo"] = pedir_numero("Año mínimo: ")
    filtros["km_maximo"] = pedir_numero("Kilómetros máximos: ")
    filtros["combustible"] = pedir_texto("Combustible (gasolina, diesel, hibrido, hibrido_enchufable, electrico): ")
    filtros["cambio"] = pedir_texto("Cambio (manual, automatico): ")
    filtros["provincia"] = pedir_texto("Provincia: ")
    return filtros


def cumple_filtros(anuncio, filtros, presupuesto):
    if presupuesto is not None and anuncio["precio_contado"] > presupuesto:
        return False
    if filtros["marca"] is not None and filtros["marca"] not in anuncio["marca"].lower():
        return False
    if filtros["modelo"] is not None and filtros["modelo"] not in anuncio["modelo"].lower():
        return False
    if filtros["anio_minimo"] is not None:
        if anuncio["anio"] is None or anuncio["anio"] < filtros["anio_minimo"]:
            return False
    if filtros["km_maximo"] is not None:
        if anuncio["km"] is None or anuncio["km"] > filtros["km_maximo"]:
            return False
    if filtros["combustible"] is not None and anuncio["combustible"] != filtros["combustible"]:
        return False
    if filtros["cambio"] is not None and anuncio["cambio"] != filtros["cambio"]:
        return False
    if filtros["provincia"] is not None:
        if anuncio["provincia"] is None or anuncio["provincia"].lower() != filtros["provincia"]:
            return False
    return True


def precio(anuncio):
    # Se usa para ordenar los resultados por precio
    return anuncio["precio_contado"]


def buscar(catalogo, filtros):
    resultados = []
    for anuncio in catalogo:
        if cumple_filtros(anuncio, filtros, filtros["presupuesto"]):
            resultados.append(anuncio)
    resultados.sort(key=precio)
    return resultados


def buscar_alternativas(catalogo, filtros):
    # Coches que cumplen todo menos el presupuesto, pasándose como mucho un 10 %
    if filtros["presupuesto"] is None:
        return []
    limite = int(filtros["presupuesto"] * (1 + MARGEN_ALTERNATIVAS))
    alternativas = []
    for anuncio in catalogo:
        if anuncio["precio_contado"] > filtros["presupuesto"]:
            if cumple_filtros(anuncio, filtros, limite):
                alternativas.append(anuncio)
    alternativas.sort(key=precio)
    return alternativas


def mostrar(anuncios, presupuesto=None):
    for anuncio in anuncios[:MAXIMO_RESULTADOS]:
        print("\n ", anuncio["marca"], anuncio["modelo"], "-", anuncio["version"])
        print("   ", anuncio["anio"], "|", anuncio["km"], "km |", anuncio["combustible"], "|",
              anuncio["cambio"], "|", anuncio["provincia"])
        texto_precio = "    " + str(anuncio["precio_contado"]) + " € al contado en " + anuncio["fuente"]
        if presupuesto is not None and anuncio["precio_contado"] > presupuesto:
            texto_precio += "  (se pasa " + str(anuncio["precio_contado"] - presupuesto) + " € del presupuesto)"
        print(texto_precio)
        print("   ", anuncio["url"])
    if len(anuncios) > MAXIMO_RESULTADOS:
        print("\n  ... y", len(anuncios) - MAXIMO_RESULTADOS, "más")


def ejecutar_busqueda(catalogo):
    filtros = pedir_filtros()
    resultados = buscar(catalogo, filtros)

    if len(resultados) > 0:
        print("\nSe han encontrado", len(resultados), "coches (ordenados por precio):")
        mostrar(resultados)
        return

    print("\nNo hay coches que cumplan todos los filtros.")
    alternativas = buscar_alternativas(catalogo, filtros)
    if len(alternativas) > 0:
        print("Pero hay", len(alternativas), "que se pasan un poco del presupuesto:")
        mostrar(alternativas, filtros["presupuesto"])
    else:
        print("Tampoco hay alternativas cercanas. Prueba a quitar algún filtro.")


if __name__ == "__main__":
    catalogo = cargar_catalogo()
    print("Catálogo cargado:", len(catalogo), "coches")
    ejecutar_busqueda(catalogo)