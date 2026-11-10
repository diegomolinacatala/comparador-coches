# Comparador de coches de segunda mano
# Programa principal: desde un menú se pueden descargar los datos de las webs,
# crear el catálogo limpio, buscar coches y comparar precios entre webs.
#
# Uso:  python comparador.py

import buscador
import limpieza
import recoger


def pedir_opcion():
    print("\n========== COMPARADOR DE COCHES ==========")
    print("1. Actualizar los datos de las webs")
    print("2. Limpiar los datos y crear el catálogo")
    print("3. Buscar coches")
    print("4. Comparar precios de un modelo entre webs")
    print("0. Salir")
    return input("Elige una opción: ").strip()


def comparar_precios(catalogo):
    # Para una marca y un modelo, muestra cuántos coches hay en cada web
    # y su precio más bajo y medio
    marca = buscador.pedir_texto("Marca: ")
    modelo = buscador.pedir_texto("Modelo: ")

    print("\nweb          coches   más barato   precio medio")
    hay_coches = False
    for web in limpieza.WEBS:
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
            hay_coches = True
            media = sum(precios) // len(precios)
            print(web.ljust(12), str(len(precios)).rjust(6), str(min(precios)).rjust(10), "€",
                  str(media).rjust(10), "€")
        else:
            print(web.ljust(12), "     0           -              -")

    if not hay_coches:
        print("\nNo hay coches de ese modelo en el catálogo.")


def main():
    while True:
        opcion = pedir_opcion()

        if opcion == "1":
            print("\nDescargando los anuncios (tarda un poco por las esperas entre peticiones)...")
            recoger.recoger()
        elif opcion == "2":
            limpieza.crear_catalogo()
        elif opcion == "3":
            catalogo = buscador.cargar_catalogo()
            print("Catálogo cargado:", len(catalogo), "coches")
            buscador.ejecutar_busqueda(catalogo)
        elif opcion == "4":
            catalogo = buscador.cargar_catalogo()
            comparar_precios(catalogo)
        elif opcion == "0":
            print("¡Hasta luego Lucas!")
            break
        else:
            print("Opción no válida, escribe un número del 0 al 4")


if __name__ == "__main__":
    main()