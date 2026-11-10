"""
Muestra, campo a campo, el primer anuncio guardado de cada web para comprobar
que los cuatro JSON de datos/ tienen el mismo formato.

Uso:  python ver_datos.py   (después de python recoger.py)
"""

import json

FUENTES = ["flexicar", "ocasionplus", "autohero", "cochescom"]
ANCHO = 22

primeros = []
for fuente in FUENTES:
    with open("datos/" + fuente + ".json", encoding="utf-8") as archivo:
        anuncios = json.load(archivo)
    print(fuente.ljust(12), len(anuncios), "anuncios en datos/" + fuente + ".json")
    primeros.append(anuncios[0])

print()
print("campo".ljust(15) + "".join(f.ljust(ANCHO) for f in FUENTES))
for campo in primeros[0]:
    if campo in ["fuente", "url"]:
        continue
    fila = campo.ljust(15)
    for anuncio in primeros:
        valor = str(anuncio[campo])
        if len(valor) > ANCHO - 2:
            valor = valor[:ANCHO - 4] + ".."
        fila += valor.ljust(ANCHO)
    print(fila)
