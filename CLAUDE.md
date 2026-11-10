# CLAUDE.md

Contexto para Claude Code (y para cualquiera del grupo que llegue nuevo).

## Qué es este proyecto

Comparador de coches de segunda mano para la asignatura **Adquisición y Transmisión de Datos (ATD)**,
Grado en Ciencia de Datos, UPV, curso 2026/2027. Junta anuncios de cuatro webs en un formato común,
los envía a un servidor por HTTP en JSON y un cliente permite buscar con filtros.

Equipo y web de la que se encarga cada uno:

| Integrante | Web | Fichero |
|---|---|---|
| Álvaro Montoya Amores | Flexicar | `flexicar.py` |
| Manuel Martí Cuñat | OcasionPlus | `ocasionplus.py` |
| Diego Molina Catalá | AutoHero | `autohero_api.py` |
| Miguel Oltra González | coches.com | `cochescom.py` |

Próximas fases: servidor → Álvaro y Diego; cliente → Manuel y Miguel; limpieza, memoria y presentación → todos.

El documento de referencia es `docs/entregables/Entregable_2.docx` (propuesta y viabilidad, 2/11/2026).
Las decisiones del proyecto salen de ahí; si algo de este fichero lo contradice, manda el entregable
y hay que actualizar este fichero.

## Comandos

```bash
pip install -r requirements.txt          # requests, beautifulsoup4, lxml, flask, pytest
python -m pytest                         # todos los tests (sin internet, ~2 s)
python recoger.py                        # descarga 2 páginas de cada web -> datos/<fuente>.json
python ver_datos.py                      # compara el primer anuncio de cada JSON
python servidor.py                       # servidor en http://127.0.0.1:5000 (--host 0.0.0.0 para la red)
python enviar.py                         # limpia datos/*.json y los manda al servidor
python cliente.py                        # buscador interactivo (o: --precio-max 12000 --marca seat)
python flexicar.py                       # cada extractor también se puede ejecutar solo
```

`recoger.py` hace peticiones reales a las webs (con 3 s de pausa entre ellas): no lo ejecutes en
bucle ni subas `PAGINAS_POR_WEB` sin motivo.

## Arquitectura (flujo de los datos)

```
flexicar.py ─┐
ocasionplus.py ─┤ recoger.py ──> datos/<fuente>.json ──> enviar.py ──HTTP POST /anuncios──> servidor.py
autohero_api.py ─┤                                       (limpieza.py)                       │
cochescom.py ─┘                                                                              ▼
                                                     cliente.py ──HTTP POST /buscar──> catalogo.py
                                                                                     datos/catalogo.json
```

| Fichero | Qué hace |
|---|---|
| `esquema.py` | Formato común (Tabla 1 del entregable). `crear_anuncio()` y `validar_anuncio()`. Vocabulario: `COMBUSTIBLES`, `CAMBIOS`, `TIPOS_VENDEDOR`. |
| `utils.py` | `descargar()` (User-Agent, `ESPERA`=3 s, 3 reintentos), `guardar_json()`, `normalizar_combustible()`, `normalizar_cambio()`. |
| `provincias.py` | Código postal → provincia, comunidades autónomas y alias («València», «Alacant»…). |
| `<web>.py` | Un extractor por web. Todos tienen `FUENTE`, `extraer(max_paginas)` y `convertir(coche)`. |
| `recoger.py` | Ejecuta los cuatro extractores y guarda `datos/<fuente>.json`. |
| `limpieza.py` | Fase 3: unifica marcas («CITROEN» → «Citroën»), modelos, provincias; quita repetidos e inválidos. |
| `catalogo.py` | Guardar el catálogo y buscar: filtros, orden, agrupar por modelo, alternativas. Sin HTTP. |
| `servidor.py` | Fase 4: Flask. `GET /estado`, `POST /anuncios`, `POST /buscar`. Ver `docs/API.md`. |
| `enviar.py` | Limpia los JSON de `datos/` y los envía al servidor. |
| `cliente.py` | Fase 5: buscador de consola. |
| `tests/` | pytest. Sin internet: usan datos con la misma forma que los de las webs. |

## El formato común (no cambiarlo sin hablarlo con el grupo)

14 campos, siempre en este orden (los crea `crear_anuncio()`):
`fuente, id_anuncio, url, marca, modelo, version, anio, km, combustible, cambio, precio_contado,
provincia, tipo_vendedor, fecha_recogida`.

- `precio_contado` es **siempre el precio al contado**, nunca el financiado ni la cuota. Cada web lo
  llama distinto (ver `docs/FUENTES.md`): es el error más fácil de cometer.
- `combustible` ∈ gasolina, diesel, hibrido, hibrido_enchufable, electrico, glp, gnc.
  `cambio` ∈ manual, automatico. `tipo_vendedor` ∈ profesional, particular, desconocido.
- Si falta un dato se guarda `None`, **nunca se inventa**. Sin precio o sin modelo el anuncio no entra
  en el catálogo.
- No se guardan datos personales de vendedores (nombres, teléfonos).
- Un anuncio se identifica por `(fuente, id_anuncio)`. El mismo coche en dos webs **no** se elimina.

## Reglas del proyecto

**Ética del scraping (lo evalúa la asignatura):**
- Respetar el `robots.txt` de cada web. Flexicar prohíbe `services.flexicar.es`: por eso se usa el sitemap.
- Mantener la pausa de `ESPERA` segundos entre peticiones y limitar el número de páginas.
- No intentar saltarse bloqueos (Cloudflare, captchas, cambiar IP…). Si una web bloquea, se documenta y
  se cambia de web, como se hizo con CochesOk.

**Estilo de código:**
- Python sencillo, nombres y comentarios **en español**, como el código que ya hay. Cada integrante
  tiene que poder explicar en la defensa el código de su parte: nada de abstracciones innecesarias,
  clases complejas ni librerías nuevas sin motivo.
- Funciones cortas con docstring que diga qué devuelven. No modificar los datos recibidos: devolver copias.
- Todo lo que se añada o arregle lleva su test en `tests/`. Antes de subir nada: `python -m pytest`.
- Al tocar un extractor, comprobar a mano un anuncio en el navegador (precio al contado, km, año,
  combustible, cambio), como en el apartado 4 del entregable.

**Uso de IA (lo pide la asignatura):** cada vez que se use Claude (u otra IA) para algo del proyecto,
añadir una fila a `docs/USO_IA.md` (qué hizo la IA y qué hicimos nosotros). Claude: cuando hagas
cambios en este repo, propón al final la fila correspondiente para ese fichero.

**Git:** ramas por tarea (`servidor-filtros`, `cliente-menu`…) y Pull Request a `main`; mensajes de
commit en español y en presente («Añade filtro por comunidad»). No subir `datos/catalogo.json`
(se genera) ni entornos virtuales.

## Estado (10/11/2026)

- Fase 1 (viabilidad) y Fase 2 (extractores): hechas y documentadas en el Entregable 2.
- Fase 3 (limpieza): `limpieza.py` hecho. Pendiente: revisar con datos de más páginas si salen marcas
  o provincias nuevas sin unificar (añadirlas a `MARCAS` en `limpieza.py` o a `ALIAS_PROVINCIAS`).
- Fase 4 (servidor): hecho con Flask (el entregable decía «librería por decidir»; **el grupo tiene que
  confirmar Flask**). Persistencia en `datos/catalogo.json`.
- Fase 5 (cliente): cliente de consola hecho. Pendiente decidir si se hace una interfaz más completa.
- Fase 6: falta probar cliente y servidor en dos ordenadores distintos, preparar la demo (búsqueda con
  resultados, sin resultados y con alternativas) y la memoria final.

Decisiones abiertas y tareas: ver la sección «Qué falta» de `README.md`.

## Problemas conocidos

- coches.com a veces no responde al primer intento: `descargar()` reintenta 3 veces.
- `flexicar.py` necesita `lxml` para leer el sitemap en modo XML.
- AutoHero y coches.com tienen coches de toda España (casi todos los de AutoHero en Toledo); Flexicar y
  OcasionPlus solo de Valencia. Por eso existe el filtro `comunidad`.
- OcasionPlus: algún anuncio sale sin provincia (la tarjeta no aparece en el HTML). Se deja `None`.
- Las webs cambian: si un extractor devuelve 0 coches, mirar primero si ha cambiado el HTML/JSON.
