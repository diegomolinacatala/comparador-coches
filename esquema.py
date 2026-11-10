"""
Formato común de los anuncios (Tabla 1 del Entregable 2).

Todos los extractores crean sus anuncios con crear_anuncio(), así los cuatro
JSON tienen exactamente los mismos campos y en el mismo orden.
"""

from datetime import date

COMBUSTIBLES = ["gasolina", "diesel", "hibrido", "hibrido_enchufable", "electrico", "glp", "gnc"]
CAMBIOS = ["manual", "automatico"]
TIPOS_VENDEDOR = ["profesional", "particular", "desconocido"]


def crear_anuncio(fuente, id_anuncio, url, marca, modelo, version, anio, km,
                  combustible, cambio, precio_contado, provincia, tipo_vendedor):
    """Devuelve un anuncio (diccionario) con los campos del formato común."""
    return {
        "fuente": fuente,
        "id_anuncio": str(id_anuncio),
        "url": url,
        "marca": marca,
        "modelo": modelo,
        "version": version,
        "anio": anio,
        "km": km,
        "combustible": combustible,
        "cambio": cambio,
        "precio_contado": precio_contado,
        "provincia": provincia,
        "tipo_vendedor": tipo_vendedor,
        "fecha_recogida": date.today().isoformat(),
    }


def validar_anuncio(anuncio):
    """Devuelve la lista de problemas del anuncio ([] si está bien).

    Sigue los criterios de la Tabla 1: sin precio o sin modelo no se puede
    comparar; año y kilómetros tienen que ser números; combustible, cambio y
    tipo de vendedor tienen que estar en el vocabulario común.
    """
    problemas = []
    for campo in ["fuente", "id_anuncio", "url", "marca", "modelo"]:
        if not anuncio.get(campo):
            problemas.append("Falta " + campo)

    precio = anuncio.get("precio_contado")
    if not isinstance(precio, (int, float)) or precio <= 0:
        problemas.append("Precio al contado no válido")
    if not isinstance(anuncio.get("anio"), int):
        problemas.append("Año no válido")
    if not isinstance(anuncio.get("km"), int) or anuncio["km"] < 0:
        problemas.append("Kilometraje no válido")

    if anuncio.get("combustible") not in COMBUSTIBLES:
        problemas.append("Combustible no reconocido: " + str(anuncio.get("combustible")))
    if anuncio.get("cambio") not in CAMBIOS:
        problemas.append("Cambio no reconocido: " + str(anuncio.get("cambio")))
    if anuncio.get("tipo_vendedor") not in TIPOS_VENDEDOR:
        problemas.append("Tipo de vendedor no reconocido")
    return problemas
