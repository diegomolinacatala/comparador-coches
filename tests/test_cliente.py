from cliente import crear_consulta, describir_anuncio, pedir_consulta, pedir_numero
from conftest import anuncio_ejemplo


def respuestas(*textos):
    """Simula lo que escribe el usuario, en orden."""
    pendientes = list(textos)
    return lambda pregunta: pendientes.pop(0)


def test_pedir_numero_acepta_puntos_y_repite_si_no_es_numero():
    assert pedir_numero("?", respuestas("doce", "12.000 €")) == 12000
    assert pedir_numero("?", respuestas("")) is None


def test_pedir_consulta_quita_los_filtros_vacios():
    entrada = respuestas("9000", "citroen", "", "", "", "gasolina", "", "", "", "", "km", "s")
    consulta = pedir_consulta(entrada)
    assert consulta == {"filtros": {"precio_max": 9000, "marca": "citroen", "combustible": "gasolina"},
                        "orden": "km", "agrupar": True}


def test_crear_consulta_por_defecto():
    assert crear_consulta({"marca": None, "modelo": ""}) == {"filtros": {}, "orden": "precio",
                                                             "agrupar": False}


def test_describir_anuncio_formatea_precio_y_km():
    linea = describir_anuncio(anuncio_ejemplo())
    assert "9.490 €" in linea and "84.111 km" in linea and "flexicar" in linea
    assert "? km" in describir_anuncio(anuncio_ejemplo(km=None))
