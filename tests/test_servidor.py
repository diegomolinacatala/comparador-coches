import pytest

from conftest import anuncio_ejemplo
from servidor import crear_app


@pytest.fixture
def cliente(tmp_path):
    app = crear_app(str(tmp_path / "catalogo.json"))
    return app.test_client()


@pytest.fixture
def ruta(tmp_path):
    return str(tmp_path / "catalogo.json")


def test_estado_con_catalogo_vacio(cliente):
    respuesta = cliente.get("/estado")
    assert respuesta.status_code == 200
    assert respuesta.json == {"ok": True, "error": None,
                              "datos": {"total": 0, "por_fuente": {}, "fecha_datos": None}}


def test_recibir_anuncios_guarda_los_validos_y_rechaza_los_demas(cliente):
    anuncios = [anuncio_ejemplo(id_anuncio="1"), anuncio_ejemplo(id_anuncio="2", precio_contado=None)]
    datos = cliente.post("/anuncios", json=anuncios).json["datos"]
    assert datos["recibidos"] == 2
    assert datos["guardados"] == 1
    assert datos["rechazados"][0]["id_anuncio"] == "2"
    assert datos["total_catalogo"] == 1


def test_los_datos_siguen_tras_reiniciar_el_servidor(ruta):
    crear_app(ruta).test_client().post("/anuncios", json=[anuncio_ejemplo()])
    reiniciado = crear_app(ruta).test_client()
    assert reiniciado.get("/estado").json["datos"]["total"] == 1


@pytest.mark.parametrize("cuerpo", [{"no": "es una lista"}, "texto"])
def test_recibir_anuncios_con_formato_incorrecto(cliente, cuerpo):
    respuesta = cliente.post("/anuncios", json=cuerpo)
    assert respuesta.status_code == 400
    assert respuesta.json["ok"] is False


def test_recibir_algo_que_no_es_json(cliente):
    respuesta = cliente.post("/anuncios", data="hola", content_type="text/plain")
    assert respuesta.status_code == 400


def test_buscar_con_resultados(cliente):
    cliente.post("/anuncios", json=[anuncio_ejemplo(id_anuncio="1"),
                                    anuncio_ejemplo(id_anuncio="2", precio_contado=20000)])
    datos = cliente.post("/buscar", json={"filtros": {"precio_max": 10000}}).json["datos"]
    assert datos["total"] == 1
    assert datos["resultados"][0]["id_anuncio"] == "1"


def test_buscar_sin_resultados_devuelve_alternativas(cliente):
    cliente.post("/anuncios", json=[anuncio_ejemplo(precio_contado=8400)])
    respuesta = cliente.post("/buscar", json={"filtros": {"precio_max": 8000}})
    assert respuesta.status_code == 200
    assert respuesta.json["datos"]["total"] == 0
    assert respuesta.json["datos"]["alternativas"][0]["motivos"] == ["Supera tu presupuesto en 400 €"]


@pytest.mark.parametrize("consulta", [
    {"filtros": {"precio_max": "mucho"}},
    {"filtros": {"color": "rojo"}},
    {"filtros": {}, "orden": "color"},
    {"filtros": {}, "agrupar": "si"},
    ["no", "es", "un", "objeto"],
])
def test_buscar_con_consulta_incorrecta(cliente, consulta):
    respuesta = cliente.post("/buscar", json=consulta)
    assert respuesta.status_code == 400
    assert respuesta.json["ok"] is False
    assert respuesta.json["error"]


def test_ruta_y_metodo_incorrectos(cliente):
    assert cliente.get("/no-existe").status_code == 404
    assert cliente.get("/buscar").status_code == 405
