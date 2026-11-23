# Cliente del comparador de coches
# Muestra el menú al usuario y se comunica con el servidor con peticiones POST
# y los datos en formato JSON (como en las Prácticas 4 y 5).
#
# Uso:  python cliente.py   (con el servidor encendido: python servidor.py)

import json

import requests

import buscador

cabeceras = {"Content-Type": "application/json"}


def respuesta_correcta(respuesta):
    # Mira el código de la respuesta del servidor (Tema 2.1):
    # 200 = todo bien, 400 = le hemos enviado datos incorrectos, otro = error del servidor
    if respuesta.status_code == 200:
        return True
    if respuesta.status_code == 400:
        print("\nEl servidor ha rechazado la petición:", respuesta.json()["error"])
    else:
        print("\nHa habido un error en el servidor (código", respuesta.status_code, ")")
    return False


def enviar_catalogo(servidor):
    # Si todavía no se ha creado el catálogo, avisamos en vez de cerrar el programa
    try:
        catalogo = buscador.cargar_catalogo()
    except FileNotFoundError:
        print("\nPrimero crea el catálogo con la opción 2 de comparador.py")
        return
    respuesta = requests.post(servidor + "/catalogo", headers=cabeceras, data=json.dumps(catalogo))
    if not respuesta_correcta(respuesta):
        return
    datos = respuesta.json()
    print("El servidor ha guardado", datos["guardados"], "anuncios")


def buscar_coches(servidor):
    # Primero preguntamos al servidor cuántos coches tiene (petición GET)
    respuesta = requests.get(servidor + "/estado")
    print("Catálogo cargado:", respuesta.json()["anuncios"], "coches")

    filtros = buscador.pedir_filtros()
    respuesta = requests.post(servidor + "/buscar", headers=cabeceras, data=json.dumps(filtros))
    if not respuesta_correcta(respuesta):
        return
    datos = respuesta.json()

    if len(datos["resultados"]) > 0:
        if len(datos["resultados"]) == 1:
            print("\nSe ha encontrado 1 coche:")
        else:
            print("\nSe han encontrado", len(datos["resultados"]), "coches (ordenados por precio):")
        buscador.mostrar(datos["resultados"])
    elif len(datos["alternativas"]) > 0:
        print("\nNo hay coches que cumplan todos los filtros.")
        if len(datos["alternativas"]) == 1:
            print("Pero hay 1 que se pasa un poco del presupuesto:")
        else:
            print("Pero hay", len(datos["alternativas"]), "que se pasan un poco del presupuesto:")
        buscador.mostrar(datos["alternativas"], filtros["presupuesto"])
    else:
        print("\nNo hay coches que cumplan todos los filtros.")
        print("Tampoco hay alternativas cercanas. Prueba a quitar algún filtro.")


def comparar_precios(servidor):
    marca = buscador.pedir_texto("Marca: ")
    modelo = buscador.pedir_texto("Modelo: ")
    peticion = {"marca": marca, "modelo": modelo}
    respuesta = requests.post(servidor + "/comparar", headers=cabeceras, data=json.dumps(peticion))
    if not respuesta_correcta(respuesta):
        return
    comparacion = respuesta.json()

    print("\nweb          coches   más barato   precio medio")
    hay_coches = False
    for fila in comparacion:
        if fila["coches"] > 0:
            hay_coches = True
            print(fila["web"].ljust(12), str(fila["coches"]).rjust(6), str(fila["mas_barato"]).rjust(10), "€",
                  str(fila["precio_medio"]).rjust(10), "€")
        else:
            print(fila["web"].ljust(12), "     0           -              -")

    if not hay_coches:
        print("\nNo hay coches de ese modelo en el catálogo.")


def main():
    # Para usarlo desde otro ordenador, se escribe la IP del ordenador del servidor
    ip = input("IP del servidor (pulsa Enter si está en este ordenador): ").strip()
    if ip == "":
        ip = "127.0.0.1"
    servidor = "http://" + ip + ":8080"

    while True:
        print("\n========== COMPARADOR DE COCHES ==========")
        print("1. Enviar el catálogo al servidor")
        print("2. Buscar coches")
        print("3. Comparar precios de un modelo entre webs")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()

        # Si el servidor está apagado o la IP está mal, requests da un error de
        # conexión: lo capturamos para avisar al usuario sin que se cierre el programa
        try:
            if opcion == "1":
                enviar_catalogo(servidor)
            elif opcion == "2":
                buscar_coches(servidor)
            elif opcion == "3":
                comparar_precios(servidor)
        except requests.exceptions.ConnectionError:
            print("\nNo se puede conectar con el servidor. ¿Está encendido y la IP es correcta?")

        if opcion == "0":
            print("¡Hasta luego!")
            break
        elif opcion not in ["1", "2", "3"]:
            print("Opción no válida, escribe un número del 0 al 3")


if __name__ == "__main__":
    main()
