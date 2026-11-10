# API del servidor

Servidor: `python servidor.py` → `http://127.0.0.1:5000`. Todo se envía y se recibe en **JSON** (UTF-8).

Todas las respuestas tienen la misma forma:

```json
{"ok": true,  "datos": { ... }, "error": null}
{"ok": false, "datos": null,    "error": "precio_max tiene que ser un número positivo"}
```

| Código | Cuándo |
|---|---|
| 200 | Todo bien (también una búsqueda **sin resultados**: no es un error) |
| 400 | Datos o filtros no válidos (el motivo va en `error`) |
| 404 / 405 | Ruta que no existe / método equivocado (p. ej. `GET /buscar`) |
| — | Si el servidor está apagado, el cliente recibe un error de conexión (`requests.ConnectionError`) |

---

## `GET /estado`

Cuántos anuncios hay y de qué fecha son.

```json
{"ok": true, "error": null,
 "datos": {"total": 139, "fecha_datos": "2026-11-10",
           "por_fuente": {"flexicar": 18, "ocasionplus": 40, "autohero": 48, "cochescom": 33}}}
```

## `POST /anuncios`

Recibe una **lista** de anuncios en el formato común (`esquema.py`). Guarda los válidos en
`datos/catalogo.json` (si ya existía el mismo `fuente` + `id_anuncio`, lo sustituye) y devuelve los
rechazados con el motivo.

Petición:

```json
[
  {"fuente": "flexicar", "id_anuncio": "903000000289106",
   "url": "https://www.flexicar.es/coches-ocasion/fiat-500-12-8v-51kw-69cv-mirror-gasolina-manual-valencia_903000000289106/",
   "marca": "Fiat", "modelo": "500", "version": "1.2 8v 51kW (69CV) Mirror", "anio": 2018,
   "km": 84111, "combustible": "gasolina", "cambio": "manual", "precio_contado": 9490,
   "provincia": "Valencia", "tipo_vendedor": "profesional", "fecha_recogida": "2026-10-23"}
]
```

Respuesta:

```json
{"ok": true, "error": null,
 "datos": {"recibidos": 1, "guardados": 1, "rechazados": [], "total_catalogo": 139}}
```

Un rechazado se ve así: `{"fuente": "autohero", "id_anuncio": "…", "problemas": ["Precio al contado no válido"]}`.

## `POST /buscar`

Petición (todos los filtros son opcionales):

```json
{
  "filtros": {
    "precio_max": 12000,
    "marca": "citroen",
    "modelo": "C3",
    "anio_min": 2018,
    "km_max": 100000,
    "combustible": "gasolina",
    "cambio": "manual",
    "provincia": "Valencia",
    "comunidad": "Comunidad Valenciana",
    "tipo_vendedor": "profesional",
    "fuente": "ocasionplus"
  },
  "orden": "precio",
  "agrupar": false
}
```

| Filtro | Cómo se compara |
|---|---|
| `precio_max`, `km_max` | `≤` (el valor límite entra) |
| `anio_min` | `≥` |
| `marca` | Sin importar mayúsculas ni tildes, y unificando nombres: «mercedes» = «Mercedes-Benz» |
| `modelo` | «C3» = «C 3»; «A3» encuentra «A3 Sportback» pero «3» no encuentra «3008» |
| `provincia` | Sin importar tildes ni idioma: «València» = «Valencia» |
| `comunidad` | Una de `provincias.COMUNIDADES` (p. ej. «Comunidad Valenciana», «Madrid», «Cataluña») |
| `combustible`, `cambio`, `tipo_vendedor` | Exactamente el vocabulario común de `esquema.py` |
| `fuente` | flexicar, ocasionplus, autohero o cochescom |

Si un anuncio no tiene un dato (p. ej. km) y hay filtro sobre ese dato, no sale (no se puede comprobar).

`orden`: `precio` (más barato primero, por defecto), `km` (menos km primero) o `anio` (más nuevo primero).

Respuesta:

```json
{"ok": true, "error": null,
 "datos": {
   "total": 3,
   "resultados": [ {anuncio}, {anuncio}, {anuncio} ],
   "alternativas": [],
   "grupos": [],
   "fecha_datos": "2026-11-10"
 }}
```

- `resultados`: como mucho 100 (`LIMITE_RESULTADOS` en `catalogo.py`); `total` dice cuántos hay en realidad.
- `alternativas`: **solo si no hay resultados**. Anuncios que cumplen los filtros de texto y se pasan
  poco de los numéricos (hasta un 15 % del presupuesto o de los km, o un año más antiguos). Cada uno
  lleva `"motivos": ["Supera tu presupuesto en 400 €"]`. Como mucho 5.
- `grupos` (si `"agrupar": true`): un elemento por modelo:

```json
{"marca": "Citroën", "modelo": "C3", "anuncios": 2,
 "por_fuente": {"ocasionplus": {"anuncios": 1, "precio_min": 8400, "precio_max": 8400},
                "autohero":    {"anuncios": 1, "precio_min": 8900, "precio_max": 8900}}}
```

## Probarlo sin el cliente

```bash
curl http://127.0.0.1:5000/estado
curl -X POST http://127.0.0.1:5000/buscar -H "Content-Type: application/json" -d "{\"filtros\": {\"precio_max\": 10000}}"
```

O desde Python:

```python
import requests
requests.post("http://127.0.0.1:5000/buscar", json={"filtros": {"marca": "seat"}}).json()
```
