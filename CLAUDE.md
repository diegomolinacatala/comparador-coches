# Proyecto de ATD: comparador de coches de segunda mano

Somos un grupo de cuatro estudiantes de 2º del Grado en Ciencia de Datos (UPV). Esta carpeta es el código del proyecto de **Adquisición y Transmisión de Datos (ATD)**, que vale el 60 % de la nota. Trabaja solo dentro de esta carpeta y responde siempre en **español**.

Si alguien quiere instrucciones solo para él, que las ponga en `CLAUDE.local.md` (no se sube a GitHub).

## El proyecto

Cada integrante se encarga de una web:

| Integrante | Web | Extractor |
|---|---|---|
| Álvaro Montoya | Flexicar | `flexicar.py` |
| Manuel Martí | OcasionPlus | `ocasionplus.py` |
| Diego Molina | AutoHero | `autohero_api.py` |
| Miguel Oltra | coches.com | `cochescom.py` |

Objetivo: un **comparador** que junta los anuncios de las cuatro webs en un catálogo común. El usuario pone filtros (presupuesto máximo, marca, modelo, año mínimo, km máximos, combustible, cambio, provincia) y ve los coches que los cumplen, ordenados por precio y con el enlace al anuncio. Si no hay ninguno, se le ofrecen alternativas que se pasan como mucho un 10 % del presupuesto. También se puede comparar el precio de un modelo entre las cuatro webs. No se estima el precio ni el estado del coche.

El comparador cubre **toda España**: Flexicar y OcasionPlus tienen coches de Valencia, pero AutoHero y coches.com venden a toda España. Cada anuncio guarda la provincia donde está el coche.

## Entregas

1. Propuesta inicial — entregada.
2. Propuesta en firme y viabilidad de las fuentes — entregada (`Entregable_2.docx`). CochesOk se descartó (Cloudflare, 403 en todo) y se cambió por coches.com.
3. Proyecto hasta el web scraping (22/11/2026) — hecha (`Entregable_3.docx`): extractores, limpieza, buscador y menú.
4. **Proyecto con modelo cliente/servidor (6/12/2026)** — en curso. Ya están hechos `servidor.py` y `cliente.py` (versión básica + mejoras 1 y 2).

Pendiente para la entrega 4:
- **Mejora 3:** que el servidor no sustituya el catálogo si llega un envío sin ningún anuncio válido.
- **Mejora 4:** una opción del cliente que descargue, limpie y envíe los datos seguidos.
- Probar cliente y servidor en dos ordenadores de la misma red (la wifi de la universidad puede bloquearlo: usar los datos del móvil).
- Opcional: una página web sencilla servida por el mismo Flask.
- Memoria final y presentación (con capturas del cliente y el servidor funcionando a la vez).

## Archivos

| Archivo | Qué hace |
|---|---|
| `flexicar.py`, `ocasionplus.py`, `autohero_api.py`, `cochescom.py` | Extractores. Misma estructura: `extraer(max_paginas)`, `coches_de_pagina()` (`pedir_pagina()` en AutoHero) y `convertir()` |
| `esquema.py` | Formato común: `crear_anuncio()` (14 campos, siempre en el mismo orden) y `validar_anuncio()` (devuelve la lista de problemas; `[]` si está bien) |
| `utils.py` | `descargar()` (User-Agent, 3 s de pausa, hasta 3 intentos), `guardar_json()`, `normalizar_combustible()` y `normalizar_cambio()` |
| `recoger.py` | Ejecuta los cuatro extractores con `PAGINAS_POR_WEB` (ahora 10) y guarda `datos/<web>.json` |
| `limpieza.py` | Unifica marcas, modelos, versiones y provincias, quita datos imposibles y repetidos y guarda `datos/catalogo.json` |
| `buscador.py` | Pide los filtros, busca, ofrece alternativas y muestra los coches de 10 en 10 (pregunta Sí/No) |
| `comparador.py` | Programa en local con menú: 1 descargar, 2 limpiar, 3 buscar, 4 comparar. Sirve para **preparar los datos** |
| `servidor.py` | Servidor Flask (puerto 8080): `GET /estado`, `POST /catalogo`, `POST /buscar`, `POST /comparar`. Guarda el catálogo en `datos/catalogo_servidor.json` y responde con código 400 si los datos que recibe están mal |
| `cliente.py` | Menú que habla con el servidor por HTTP y JSON: 1 enviar el catálogo, 2 buscar, 3 comparar. Avisa si no puede conectar o si el servidor rechaza la petición |
| `ver_datos.py` | Comprobación: muestra el primer anuncio de cada JSON de `datos/` |
| `requirements.txt` | requests, beautifulsoup4, lxml (para el sitemap XML de Flexicar) y flask |
| `datos/` | Un JSON por web (se suben a GitHub). `catalogo.json` y `catalogo_servidor.json` se generan y no se suben |
| `.github/workflows/tests.yml` | En cada push, GitHub instala las librerías y comprueba que ningún `.py` tiene errores de sintaxis |

Cómo se usa:
1. `pip install -r requirements.txt`
2. `python comparador.py` → opción 1 (descargar, unos 3 minutos) y opción 2 (limpiar).
3. Terminal 1: `python servidor.py`. Terminal 2: `python cliente.py` → Enter en la IP (o la IP del ordenador del servidor) → opción 1 para enviar el catálogo y luego buscar o comparar.

Campos del formato común: `fuente, id_anuncio, url, marca, modelo, version, año, km, combustible, cambio, precio_contado, provincia, tipo_vendedor, fecha_recogida`. El campo del año se llama **`año`** (con ñ) en todo el proyecto, también en los JSON y en el filtro `año_minimo`. Siempre el **precio al contado**, nunca el financiado ni la cuota. Si falta un dato se deja vacío, no se inventa. No se guardan datos personales de los vendedores.

Vocabulario: combustible `gasolina, diesel, hibrido, hibrido_enchufable, electrico, glp, gnc`; cambio `manual, automatico`; vendedor `profesional, particular, desconocido`.

## Cómo saca los datos cada web

| Web | Páginas | Dónde están los datos | Precio al contado | Provincia |
|---|---|---|---|---|
| Flexicar | Páginas de marca y modelo de Valencia del sitemap (12 coches máx. cada una) | `__NEXT_DATA__` → `initialVehicles` | `cashPrice` (`price` es el financiado) | Valencia fija |
| OcasionPlus | Listado de Valencia con `?page=N` (20 por página; la página 1 va sin parámetro) | JSON-LD (`ItemList` de `Vehicle`) + tarjeta HTML para la ubicación | `offers.price` (el número grande de la tarjeta es el precio anterior a la oferta) | Texto de la tarjeta antes del guion |
| AutoHero | POST a la consulta `searchAdV9AdsV2`, de 24 en 24 (`offset`) | Respuesta JSON | `offerPrice` en céntimos | 2 primeras cifras del código postal de la sede |
| coches.com | Listado general con `?page=N` (20 por página) | `__NEXT_DATA__` → `props.pageProps.classifieds.classifiedList` | `price` (`priceOffer` es el financiado) | `currentProvince` |

Flexicar: la API `services.flexicar.es` carga el resto de coches al hacer scroll, pero su `robots.txt` lo prohíbe todo, así que no se usa.

## Lo que sabemos de coches.com

- El listado es `https://www.coches.com/coches-segunda-mano/coches-ocasion.htm`; `/coches-segunda-mano/` es solo una página de presentación.
- Responde 200 a `requests` con User-Agent; no hace falta Selenium. A veces no acepta la conexión a la primera (ConnectTimeout) y al reintentar responde en 1 s: por eso `descargar()` reintenta.
- `price` es el **contado** y `priceOffer` el **financiado** (al revés que Flexicar). No vale «el mayor es el contado»: hay coches con el financiado más alto.
- El JSON no trae la URL de la ficha: se saca de los `<a>` con `?id=` y se cruza por `visibleId`.
- El listado mezcla ocasión con km 0 y seminuevos: se descartan con `isKm0`.
- Todos los híbridos llevan «Gasolina» en el combustible («Híbrido Enchufable Gasolina»): `normalizar_combustible()` mira primero si es híbrido.
- `coches-ocasion-en-valencia.htm` filtra por **concesionarios con sede en Valencia**, no por dónde está el coche.
- Las marcas vienen en mayúsculas (`limpieza.py` las unifica). Puede haber vendedores particulares (`dealer.type == "INDIVIDUAL"`); en las otras tres webs todos son profesionales.
- `robots.txt`: para `User-agent: *` solo prohíbe `/reserva`, `/contacto` e `/index.php`, con `Allow: /`.

## Ramas de Git: `dev` y `main`

Repositorio: `github.com/diegomolinacatala/comparador-coches`.

- **`main`** — la versión estable. **Nunca se trabaja ni se hace commit directamente en `main`.**
- **`dev`** — la rama de desarrollo. Todo el trabajo se hace aquí.

Forma de trabajar:
1. Antes de empezar: `git checkout dev` y `git pull`.
2. Trabajar, probar que funciona y hacer commit en `dev`.
3. `git push origin dev`.
4. Cuando lo de `dev` está probado y el grupo está de acuerdo, se pasa a `main` con un Pull Request `dev` → `main`.
5. Si alguien sube algo a `main`, hay que traerlo también a `dev`.

Reglas para Claude:
- Antes de cualquier commit, comprobar con `git branch --show-current` que estamos en `dev`. Si estamos en `main`, **parar y avisar**.
- No hacer merge de `dev` en `main`, ni push a `main`, ni push con `--force`, salvo que se pida expresamente.
- Antes de cambiar de rama, comprobar con `git status` que no hay cambios sin guardar.
- Los JSON de `datos/` cambian cada vez que se descarga: preguntar antes de subirlos.

## Reglas para el código

- **Solo lo visto en clase**: `requests` (GET y POST) con cabeceras, HTML, JSON, XML, BeautifulSoup (`find`, `find_all`, `get`, `get_text`), Flask como en la Práctica 5, el filtrado de datos del Tema 3 y Python básico. Nada de Selenium, Scrapy, expresiones regulares, selectores CSS ni `sort(key=...)`. Si algo no se puede hacer sin salirse de lo dado, **avisar antes**.
- Código **sencillo y comentado en español**: lo tenemos que entender y defender delante del profesor.
- Antes de simplificar o cambiar algo, comprobar que el resultado es **exactamente el mismo** que antes.
- Respetar el `robots.txt` de cada web y mantener la pausa entre peticiones.
- El código común (`esquema.py`, `utils.py`, `recoger.py`, `buscador.py`) y los extractores de los demás afectan a todos: avisar al grupo antes de cambiarlos.
- **Uso de IA:** la asignatura exige indicar en cada entrega qué ha hecho la IA y con qué modelo. Lo que escriba Claude hay que declararlo, aunque luego lo simplifiquemos o adaptemos.
- Si no estás seguro de algo, pregunta antes de ejecutar.
