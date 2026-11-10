"""
Tests de las funciones convertir() y de lectura de HTML de cada extractor.

No se conectan a internet: usan trozos de datos con la misma forma que los
que devuelven las webs (ver docs/FUENTES.md). Si una web cambia su formato,
el extractor fallará al ejecutarlo, no aquí.
"""

import json

import autohero_api
import cochescom
import flexicar
import ocasionplus
from esquema import validar_anuncio


def test_flexicar_usa_cashprice_y_no_el_precio_financiado():
    coche = {"id": 903000000289106, "slug": "fiat-500-12-mirror-valencia_903000000289106",
             "brand": "Fiat", "model": "500", "version": "1.2 8v 51kW (69CV) Mirror",
             "year": 2018, "km": 84111, "fuel": "Gasolina", "transmission": "Manual",
             "price": 7990, "cashPrice": 9490}
    anuncio = flexicar.convertir(coche)
    assert anuncio["precio_contado"] == 9490
    assert anuncio["id_anuncio"] == "903000000289106"
    assert validar_anuncio(anuncio) == []


def test_flexicar_lee_next_data():
    datos = {"props": {"pageProps": {"initialVehicles": [{"id": 1}, {"id": 2}]}}}
    html = '<script id="__NEXT_DATA__">' + json.dumps(datos) + "</script>"
    assert len(flexicar.coches_de_pagina(html)) == 2
    assert flexicar.coches_de_pagina("<html></html>") == []


def test_ocasionplus_separa_marca_modelo_y_version():
    coche = {
        "brand": {"name": "Nissan"}, "name": "Nissan QASHQAI",
        "model": "Nissan Qashqai 1.3 DIG-T Acenta", "productionDate": "2019-03-31T00:00:00",
        "mileageFromOdometer": {"value": "45000"}, "fuelType": "Gasolina",
        "vehicleTransmission": "Manual", "ubicacion": "Valencia - Alzira",
        "offers": {"url": "https://www.ocasionplus.com/coches-segunda-mano/nissan-qashqai-x1y2",
                   "price": "15990"},
    }
    anuncio = ocasionplus.convertir(coche)
    assert (anuncio["modelo"], anuncio["version"]) == ("QASHQAI", "1.3 DIG-T Acenta")
    assert (anuncio["anio"], anuncio["km"], anuncio["precio_contado"]) == (2019, 45000, 15990)
    assert anuncio["provincia"] == "Valencia"
    assert anuncio["id_anuncio"] == "x1y2"


def test_autohero_precio_en_centimos_y_provincia_por_codigo_postal():
    coche = {
        "id": "5f130613", "carUrlTitle": "ford-mustang", "manufacturer": "Ford", "model": "Mustang",
        "subType": "2.3 EcoBoost", "subTypeExtra": "Fastback", "firstRegistrationYear": 2015,
        "mileage": {"distance": 113547}, "fuelType": 1039, "gearType": 1138,
        "offerPrice": {"amountMinorUnits": 2569900, "conversionMajor": 100},
        "esBranch": {"zipcode": "45224"},
    }
    anuncio = autohero_api.convertir(coche)
    assert anuncio["precio_contado"] == 25699
    assert anuncio["provincia"] == "Toledo"
    assert anuncio["version"] == "2.3 EcoBoost Fastback"
    assert (anuncio["combustible"], anuncio["cambio"]) == ("gasolina", "manual")


def test_autohero_hibrido_enchufable():
    coche = {"id": "x", "carUrlTitle": "t", "manufacturer": "Kia", "model": "Niro",
             "mileage": {"distance": 1}, "fuelType": 1046, "isPluginSystem": True,
             "gearType": 1139, "offerPrice": None}
    anuncio = autohero_api.convertir(coche)
    assert anuncio["combustible"] == "hibrido_enchufable"
    assert anuncio["precio_contado"] is None  # «venta en proceso»: sin precio
    assert anuncio["provincia"] is None


def test_cochescom_particular_y_anio_como_texto():
    coche = {
        "visibleId": "zFwRZ8tfQK_t", "enlace": "https://www.coches.com/x.htm?id=zFwRZ8tfQK_t",
        "make": {"name": "CUPRA"}, "model": {"name": "Leon"}, "version": {"name": "2.0 TSI VZ DSG"},
        "registration": {"year": "2021"}, "mileage": {"amount": 118966},
        "fuel": {"name": "Híbrido Enchufable Gasolina"}, "transmission": {"name": "Automático"},
        "price": {"amount": 24490}, "currentProvince": {"name": "Barcelona"},
        "dealer": {"type": "INDIVIDUAL"},
    }
    anuncio = cochescom.convertir(coche)
    assert anuncio["anio"] == 2021
    assert anuncio["combustible"] == "hibrido_enchufable"
    assert anuncio["tipo_vendedor"] == "particular"
    assert validar_anuncio(anuncio) == []


def test_cochescom_cruza_enlaces_por_visible_id():
    datos = {"props": {"pageProps": {"classifieds": {"classifiedList": [{"visibleId": "abc"}]}}}}
    html = ('<script id="__NEXT_DATA__">' + json.dumps(datos) + "</script>"
            '<a href="/coches-segunda-mano/ocasion-x.htm?id=abc">ver</a>')
    coches = cochescom.coches_de_pagina(html)
    assert coches[0]["enlace"] == "https://www.coches.com/coches-segunda-mano/ocasion-x.htm?id=abc"
