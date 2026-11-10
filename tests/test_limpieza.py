import pytest

from conftest import anuncio_ejemplo
from limpieza import (avisos_atipicos, clave, limpiar_anuncio, limpiar_anuncios,
                      normalizar_marca, normalizar_modelo, normalizar_provincia)


@pytest.mark.parametrize("texto, esperado", [
    ("C 3", "c3"), ("León", "leon"), ("Mercedes-Benz", "mercedesbenz"), (None, ""),
])
def test_clave(texto, esperado):
    assert clave(texto) == esperado


@pytest.mark.parametrize("marca, esperada", [
    ("CITROEN", "Citroën"), ("Citroen", "Citroën"), ("Citroën", "Citroën"),
    ("MERCEDES", "Mercedes-Benz"), ("Mercedes-Benz", "Mercedes-Benz"),
    ("DS Automobiles", "DS"), ("ALFA ROMEO", "Alfa Romeo"), ("KIA", "Kia"),
    ("PEUGEOT", "Peugeot"), ("BMW", "BMW"), ("MG", "MG"), ("Land Rover", "Land Rover"),
    ("DR AUTOMOBILES", "DR"), (None, None),
])
def test_normalizar_marca(marca, esperada):
    assert normalizar_marca(marca) == esperada


@pytest.mark.parametrize("modelo, esperado", [
    ("QASHQAI", "Qashqai"), ("C-HR", "C-HR"), ("EQS", "EQS"), ("  Clase   A ", "Clase A"),
    ("3008", "3008"), (None, None),
])
def test_normalizar_modelo(modelo, esperado):
    assert normalizar_modelo(modelo) == esperado


@pytest.mark.parametrize("provincia, esperada", [
    ("Valencia", "Valencia"), ("València", "Valencia"), ("Alicante/Alacant", "Alicante"),
    ("Castelló", "Castellón"), ("Vizcaya", "Bizkaia"), ("malaga", "Málaga"),
    ("", None), (None, None), ("Andorra", "Andorra"),
])
def test_normalizar_provincia(provincia, esperada):
    assert normalizar_provincia(provincia) == esperada


def test_limpiar_anuncio_no_modifica_el_original():
    original = anuncio_ejemplo(marca="CITROEN", modelo="C 3", provincia="València")
    limpio = limpiar_anuncio(original)
    assert limpio["marca"] == "Citroën"
    assert limpio["provincia"] == "Valencia"
    assert original["marca"] == "CITROEN"


def test_limpiar_anuncios_descarta_invalidos_y_repetidos():
    anuncios = [
        anuncio_ejemplo(id_anuncio="1"),
        anuncio_ejemplo(id_anuncio="1"),                      # repetido
        anuncio_ejemplo(id_anuncio="2", precio_contado=None),  # sin precio
        anuncio_ejemplo(id_anuncio="3", fuente="autohero"),
    ]
    limpios, descartados = limpiar_anuncios(anuncios)
    assert [a["id_anuncio"] for a in limpios] == ["1", "3"]
    assert descartados[0]["problemas"] == ["Repetido"]
    assert "Precio al contado no válido" in descartados[1]["problemas"]


def test_mismo_id_en_webs_distintas_no_es_repetido():
    limpios, _ = limpiar_anuncios([anuncio_ejemplo(fuente="flexicar"),
                                   anuncio_ejemplo(fuente="cochescom")])
    assert len(limpios) == 2


def test_avisos_atipicos():
    assert avisos_atipicos(anuncio_ejemplo()) == []
    raro = anuncio_ejemplo(precio_contado=100, km=2_000_000, anio=1900)
    assert len(avisos_atipicos(raro)) == 3
