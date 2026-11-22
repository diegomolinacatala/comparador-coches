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
    filtros["año_minimo"] = pedir_numero("Año mínimo: ")
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
    if filtros["año_minimo"] is not None:
        if anuncio["año"] is None or anuncio["año"] < filtros["año_minimo"]:
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


def ordenar_por_precio(anuncios):
    # Vamos metiendo cada coche en su sitio, de más barato a más caro
    ordenados = []
    for anuncio in anuncios:
        posicion = len(ordenados)
        for i in range(len(ordenados)):
            if anuncio["precio_contado"] < ordenados[i]["precio_contado"]:
                posicion = i
                break
        ordenados.insert(posicion, anuncio)
    return ordenados


def buscar(catalogo, filtros):
    resultados = []
    for anuncio in catalogo:
        if cumple_filtros(anuncio, filtros, filtros["presupuesto"]):
            resultados.append(anuncio)
    resultados = ordenar_por_precio(resultados)
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
    alternativas = ordenar_por_precio(alternativas)
    return alternativas


def mostrar(anuncios, presupuesto=None):
    # Muestra los coches de 10 en 10 y pregunta si se quieren ver los siguientes
    for i in range(len(anuncios)):
        anuncio = anuncios[i]
        print("\n ", anuncio["marca"], anuncio["modelo"], "-", anuncio["version"])
        print("   ", anuncio["año"], "|", anuncio["km"], "km |", anuncio["combustible"], "|",
              anuncio["cambio"], "|", anuncio["provincia"])
        texto_precio = "    " + str(anuncio["precio_contado"]) + " € al contado en " + anuncio["fuente"]
        if presupuesto is not None and anuncio["precio_contado"] > presupuesto:
            texto_precio += "  (se pasa " + str(anuncio["precio_contado"] - presupuesto) + " € del presupuesto)"
        print(texto_precio)
        print("   ", anuncio["url"])

        # Cada 10 coches, si quedan más, preguntamos si seguir
        quedan = len(anuncios) - (i + 1)
        if (i + 1) % MAXIMO_RESULTADOS == 0 and quedan > 0:
            if quedan == 1:
                pregunta = "\nQueda 1 coche. ¿Quieres verlo? (Sí/No): "
            else:
                pregunta = ("\nQuedan " + str(quedan) + " coches. ¿Quieres ver los siguientes " +
                            str(min(MAXIMO_RESULTADOS, quedan)) + "? (Sí/No): ")

            # Repetimos la pregunta hasta que responda sí o no
            respuesta = input(pregunta).strip().lower()
            while respuesta not in ["sí", "si", "s", "no", "n"]:
                print("  Responde Sí o No")
                respuesta = input(pregunta).strip().lower()

            if respuesta in ["no", "n"]:
                break


def ejecutar_busqueda(catalogo):
    filtros = pedir_filtros()
    resultados = buscar(catalogo, filtros)

    if len(resultados) > 0:
        if len(resultados) == 1:
            print("\nSe ha encontrado 1 coche:")
        else:
            print("\nSe han encontrado", len(resultados), "coches (ordenados por precio):")
        mostrar(resultados)
        return

    print("\nNo hay coches que cumplan todos los filtros.")
    alternativas = buscar_alternativas(catalogo, filtros)
    if len(alternativas) > 0:
        if len(alternativas) == 1:
            print("Pero hay 1 que se pasa un poco del presupuesto:")
        else:
            print("Pero hay", len(alternativas), "que se pasan un poco del presupuesto:")
        mostrar(alternativas, filtros["presupuesto"])
    else:
        print("Tampoco hay alternativas cercanas. Prueba a quitar algún filtro.")


if __name__ == "__main__":
    catalogo = cargar_catalogo()
    print("Catálogo cargado:", len(catalogo), "coches")
    ejecutar_busqueda(catalogo)