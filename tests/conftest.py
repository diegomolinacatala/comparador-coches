"""Datos de ejemplo compartidos por los tests."""

import pytest

from esquema import crear_anuncio


def anuncio_ejemplo(**cambios):
    """Un anuncio válido del formato común; se puede cambiar cualquier campo."""
    datos = dict(
        fuente="flexicar", id_anuncio="1", url="https://www.flexicar.es/coches-ocasion/x/",
        marca="Fiat", modelo="500", version="1.2 Mirror", anio=2018, km=84111,
        combustible="gasolina", cambio="manual", precio_contado=9490,
        provincia="Valencia", tipo_vendedor="profesional",
    )
    datos.update(cambios)
    return crear_anuncio(**datos)


@pytest.fixture
def catalogo():
    """Un catálogo pequeño con coches de las cuatro webs."""
    return [
        anuncio_ejemplo(id_anuncio="1"),
        anuncio_ejemplo(id_anuncio="2", marca="Seat", modelo="León", precio_contado=14000,
                        anio=2020, km=60000, combustible="diesel"),
        anuncio_ejemplo(fuente="ocasionplus", id_anuncio="a", marca="Citroën", modelo="C3",
                        precio_contado=8400, anio=2019, km=70000),
        anuncio_ejemplo(fuente="autohero", id_anuncio="b", marca="Citroën", modelo="C 3",
                        precio_contado=8900, anio=2021, km=40000, provincia="Toledo",
                        cambio="automatico"),
        anuncio_ejemplo(fuente="cochescom", id_anuncio="c", marca="Audi", modelo="A3 Sportback",
                        precio_contado=21000, anio=2022, km=30000, provincia="Madrid",
                        tipo_vendedor="particular"),
        anuncio_ejemplo(fuente="cochescom", id_anuncio="d", marca="Audi", modelo="A3",
                        precio_contado=19000, anio=2017, km=None, provincia="Alicante"),
    ]
