import pytest

from catalogo import (agrupar_por_modelo, anadir_anuncios, buscar, cargar_catalogo,
                      guardar_catalogo, ordenar, resumen, validar_filtros)
from conftest import anuncio_ejemplo


def ids(anuncios):
    return [a["id_anuncio"] for a in anuncios]


# ------------------------------------------------------------- guardar --

def test_cargar_catalogo_inexistente_devuelve_lista_vacia(tmp_path):
    assert cargar_catalogo(tmp_path / "no_existe.json") == []


def test_guardar_y_cargar_catalogo(tmp_path, catalogo):
    ruta = str(tmp_path / "catalogo.json")
    guardar_catalogo(catalogo, ruta)
    assert cargar_catalogo(ruta) == catalogo


def test_anadir_sustituye_el_mismo_anuncio_sin_modificar_el_original(catalogo):
    mas_barato = anuncio_ejemplo(id_anuncio="1", precio_contado=8000)
    nuevo = anadir_anuncios(catalogo, [mas_barato])
    assert len(nuevo) == len(catalogo)
    assert [a for a in nuevo if a["id_anuncio"] == "1"][0]["precio_contado"] == 8000
    assert catalogo[0]["precio_contado"] == 9490


def test_resumen(catalogo):
    datos = resumen(catalogo)
    assert datos["total"] == 6
    assert datos["por_fuente"] == {"flexicar": 2, "ocasionplus": 1, "autohero": 1, "cochescom": 2}
    assert datos["fecha_datos"] == catalogo[0]["fecha_recogida"]


# ------------------------------------------------------------- filtros --

def test_filtros_validos():
    assert validar_filtros({"precio_max": 10000, "marca": "seat", "comunidad": "comunidad valenciana",
                            "combustible": "diesel", "modelo": None}) == []


@pytest.mark.parametrize("filtros", [
    {"precio_max": "barato"}, {"precio_max": -1}, {"anio_min": True}, {"marca": 3},
    {"combustible": "petroleo"}, {"comunidad": "Narnia"}, {"color": "rojo"},
])
def test_filtros_no_validos(filtros):
    assert validar_filtros(filtros) != []


def test_filtros_que_no_son_diccionario():
    assert validar_filtros(["precio_max"]) != []


# ------------------------------------------------------------ búsqueda --

def test_sin_filtros_devuelve_todo_ordenado_por_precio(catalogo):
    respuesta = buscar(catalogo, {})
    assert respuesta["total"] == 6
    precios = [a["precio_contado"] for a in respuesta["resultados"]]
    assert precios == sorted(precios)


def test_presupuesto_incluye_el_valor_limite(catalogo):
    assert ids(buscar(catalogo, {"precio_max": 9490})["resultados"]) == ["a", "b", "1"]


def test_marca_sin_importar_como_se_escriba(catalogo):
    assert buscar(catalogo, {"marca": "CITROEN"})["total"] == 2


def test_modelo_unifica_espacios_y_tildes(catalogo):
    assert set(ids(buscar(catalogo, {"modelo": "c3"})["resultados"])) == {"a", "b"}
    assert ids(buscar(catalogo, {"modelo": "leon"})["resultados"]) == ["2"]


def test_modelo_encuentra_variantes_pero_no_otros_modelos(catalogo):
    assert set(ids(buscar(catalogo, {"modelo": "A3"})["resultados"])) == {"c", "d"}
    assert buscar(catalogo, {"modelo": "50"})["total"] == 0


def test_anio_y_km_minimos(catalogo):
    assert ids(buscar(catalogo, {"anio_min": 2021})["resultados"]) == ["b", "c"]
    # El anuncio "d" no tiene km: con filtro de km no se puede comprobar y no sale
    assert "d" not in ids(buscar(catalogo, {"km_max": 1_000_000})["resultados"])


def test_provincia_y_comunidad(catalogo):
    assert buscar(catalogo, {"provincia": "València"})["total"] == 3
    assert set(ids(buscar(catalogo, {"comunidad": "Comunidad Valenciana"})["resultados"])) == {"1", "2", "a", "d"}


def test_filtros_de_vocabulario_comun(catalogo):
    assert ids(buscar(catalogo, {"cambio": "automatico"})["resultados"]) == ["b"]
    assert ids(buscar(catalogo, {"tipo_vendedor": "particular"})["resultados"]) == ["c"]
    assert ids(buscar(catalogo, {"combustible": "diesel"})["resultados"]) == ["2"]


def test_todos_los_filtros_a_la_vez(catalogo):
    filtros = {"precio_max": 9000, "marca": "citroen", "anio_min": 2020, "cambio": "automatico"}
    assert ids(buscar(catalogo, filtros)["resultados"]) == ["b"]


def test_sin_resultados_ofrece_alternativas_cercanas(catalogo):
    respuesta = buscar(catalogo, {"precio_max": 8000})
    assert respuesta["total"] == 0
    # 8.400 € y 8.900 € están dentro del 15 % (hasta 9.200 €); 9.490 € ya no
    assert ids(respuesta["alternativas"]) == ["a", "b"]
    assert respuesta["alternativas"][0]["motivos"] == ["Supera tu presupuesto en 400 €"]


def test_alternativas_respetan_los_filtros_de_texto(catalogo):
    respuesta = buscar(catalogo, {"precio_max": 8000, "marca": "Seat"})
    assert respuesta["total"] == 0
    assert respuesta["alternativas"] == []


def test_con_resultados_no_hay_alternativas(catalogo):
    assert buscar(catalogo, {"precio_max": 9000})["alternativas"] == []


def test_limite_de_resultados(catalogo):
    respuesta = buscar(catalogo, {}, limite=2)
    assert respuesta["total"] == 6
    assert len(respuesta["resultados"]) == 2


# --------------------------------------------------- ordenar y agrupar --

def test_ordenar_por_km_y_anio(catalogo):
    assert ids(ordenar(catalogo, "km"))[-1] == "d"  # sin km, al final
    assert ids(ordenar(catalogo, "anio"))[0] == "c"  # el más nuevo primero


def test_ordenar_no_valido(catalogo):
    with pytest.raises(ValueError):
        ordenar(catalogo, "color")


def test_agrupar_por_modelo_junta_variantes_de_escritura(catalogo):
    grupos = agrupar_por_modelo(catalogo)
    citroen = grupos[0]
    assert (citroen["marca"], citroen["anuncios"]) == ("Citroën", 2)
    assert citroen["por_fuente"]["autohero"] == {"anuncios": 1, "precio_min": 8900, "precio_max": 8900}


def test_buscar_con_agrupar(catalogo):
    assert len(buscar(catalogo, {"marca": "audi"}, agrupar=True)["grupos"]) == 2
    assert buscar(catalogo, {"marca": "audi"})["grupos"] == []
