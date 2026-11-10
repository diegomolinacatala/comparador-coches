import pytest

from conftest import anuncio_ejemplo
from esquema import validar_anuncio
from utils import normalizar_cambio, normalizar_combustible, sin_tildes


def test_anuncio_completo_es_valido():
    assert validar_anuncio(anuncio_ejemplo()) == []


def test_anuncio_tiene_los_14_campos_y_fecha():
    anuncio = anuncio_ejemplo()
    assert len(anuncio) == 14
    assert len(anuncio["fecha_recogida"]) == 10  # AAAA-MM-DD


@pytest.mark.parametrize("campo, valor, problema", [
    ("precio_contado", None, "Precio al contado no válido"),
    ("precio_contado", 0, "Precio al contado no válido"),
    ("modelo", "", "Falta modelo"),
    ("anio", "2018", "Año no válido"),
    ("km", -5, "Kilometraje no válido"),
    ("combustible", "petroleo", "Combustible no reconocido: petroleo"),
    ("cambio", None, "Cambio no reconocido: None"),
    ("tipo_vendedor", "otro", "Tipo de vendedor no reconocido"),
])
def test_validar_anuncio_detecta_problemas(campo, valor, problema):
    assert problema in validar_anuncio(anuncio_ejemplo(**{campo: valor}))


def test_sin_tildes():
    assert sin_tildes(" Híbrido Enchufable ") == "hibrido enchufable"


@pytest.mark.parametrize("texto, esperado", [
    ("Híbrido Enchufable Gasolina", "hibrido_enchufable"),  # coches.com: híbrido antes que gasolina
    ("Híbrido no enchufable", "hibrido"),
    ("Gasolina", "gasolina"),
    ("Diésel", "diesel"),
    ("Eléctrico", "electrico"),
    ("GLP", "glp"),
    ("Gas natural", "gnc"),
    (None, None),
    ("Hidrógeno", "hidrogeno"),  # no reconocido: se devuelve tal cual para que lo señale validar_anuncio
])
def test_normalizar_combustible(texto, esperado):
    assert normalizar_combustible(texto) == esperado


@pytest.mark.parametrize("texto, esperado", [
    ("Manual", "manual"), ("Automático", "automatico"), ("AUTO", "automatico"),
    ("Semiautomático", "automatico"), ("Doble embrague", "automatico"), (None, None),
])
def test_normalizar_cambio(texto, esperado):
    assert normalizar_cambio(texto) == esperado
