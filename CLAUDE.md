# Proyecto de ATD: comparador de coches de segunda mano

Soy Miguel Oltra, de 2º del Grado en Ciencia de Datos (UPV). Esta carpeta es el código del proyecto de grupo de **Adquisición y Transmisión de Datos (ATD)**, que vale el 60 % de la nota. Trabaja solo dentro de esta carpeta.

Responde siempre en **español**.

## El proyecto

Somos cuatro y cada uno se encarga de una web:

| Integrante | Web | Extractor |
|---|---|---|
| Álvaro Montoya | Flexicar | `flexicar.py` |
| Manuel Martí | OcasionPlus | `ocasionplus.py` |
| Diego Molina | AutoHero | `autohero_api.py` |
| **Miguel Oltra (yo)** | **coches.com** | `cochescom.py` |

Objetivo: un **comparador** que junta los anuncios de las cuatro webs en un catálogo común. El usuario mete filtros (presupuesto máximo, marca, modelo, año mínimo, km máximos, combustible, cambio, provincia, tipo de vendedor); el **cliente** los manda en JSON por HTTP a un **servidor** en Python, que busca en el catálogo (un fichero JSON) y devuelve los resultados en JSON. Se pueden ordenar por precio, km o año y agrupar por modelo. Si no hay resultados, se avisa y se ofrecen alternativas cercanas aparte (p. ej. un coche que se pasa 400 € del presupuesto). No se estima precio ni estado del coche.

## En qué punto estamos (10/11/2026)

- **Entregable 2 entregado** (`Entregable_2.docx`, fechado el 2/11/2026). Demostró que las cuatro webs se pueden scrapear y que `recoger.py` saca 139 anuncios válidos con 2 páginas por web. CochesOk se descartó (Cloudflare, 403 en todo) y se sustituyó por coches.com.
- **Ahora toca la siguiente fase.** El reparto del Entregable 2 (servidor Álvaro y Diego, cliente Manuel y Miguel) se puso por poner: **todavía no hemos decidido cómo dividir el trabajo**. No des por hecho qué parte me toca; pregúntame.

Fases que quedan (apartado 6 del Entregable 2):

3. **Limpieza e integración**: unificar marcas y modelos («Citroën» / «Citroen» / «CITROEN», «Mercedes» / «Mercedes-Benz»), revisar atípicos y quitar repetidos dentro de cada web (no entre webs: pueden ser coches distintos). Encaja con la UD3 de teoría (filtrado de datos).
4. **Servidor**: recibir lotes en JSON, validarlos, guardarlos y responder a consultas por filtros. Distinguir error de conexión, datos inválidos y búsqueda correcta sin resultados. Aún no se ha elegido librería.
5. **Cliente**: pedir filtros, enviarlos, mostrar resultados con enlace al anuncio. Primero en el mismo ordenador y luego en dos ordenadores en red.
6. **Validación y memoria**: contrastar muestras con las webs y terminar la memoria.

Decisiones pendientes del grupo: cómo mostrar la provincia (AutoHero y coches.com venden a toda España), cómo tratar el «Micro Híbrido» (ahora va con los híbridos) y la librería del servidor.

## Archivos

- `recoger.py` — programa principal: ejecuta los cuatro extractores con `PAGINAS_POR_WEB` páginas, cuenta los válidos y guarda `datos/<fuente>.json`.
- `esquema.py` — formato común: `crear_anuncio()` (14 campos, siempre en el mismo orden) y `validar_anuncio()` (devuelve la lista de problemas). Vocabulario: combustible `gasolina, diesel, hibrido, hibrido_enchufable, electrico, glp, gnc`; cambio `manual, automatico`; vendedor `profesional, particular, desconocido`.
- `utils.py` — `descargar()` (User-Agent, 3 s de pausa, hasta 3 intentos), `guardar_json()`, `normalizar_combustible()`, `normalizar_cambio()`.
- `flexicar.py`, `ocasionplus.py`, `autohero_api.py`, `cochescom.py` — misma estructura: `extraer(max_paginas)`, `coches_de_pagina()` (`pedir_pagina()` en AutoHero) y `convertir()`.
- `ver_datos.py` — muestra el primer anuncio de cada JSON de `datos/`.
- `*.json` en la raíz — última recogida (10/11/2026): flexicar 18, ocasionplus 40, autohero 48, cochescom 33. Ojo: el código escribe y lee en `datos/`, que ahora no existe; estos JSON están sueltos en la raíz.
- `requirements.txt` — requests, beautifulsoup4, lxml (lxml hace falta para leer el sitemap XML de Flexicar).
- `Entregable_2.docx` — el entregable entregado. En él la carpeta se llama `comparador-coches`.

Uso: `pip install -r requirements.txt` y `python recoger.py` dentro de esta carpeta.

Campos del formato común: `fuente, id_anuncio, url, marca, modelo, version, anio, km, combustible, cambio, precio_contado, provincia, tipo_vendedor, fecha_recogida`. Siempre el **precio al contado**, nunca el financiado ni la cuota. Si falta un dato se deja vacío, no se inventa. No se guardan datos personales de vendedores.

## Cómo saca los datos cada web

| Web | Páginas | Dónde están los datos | Precio al contado | Provincia |
|---|---|---|---|---|
| Flexicar | Páginas de marca y modelo de Valencia del sitemap (12 coches máx. cada una) | `__NEXT_DATA__` → `initialVehicles` | `cashPrice` (`price` es el financiado) | Valencia fija |
| OcasionPlus | Listado de Valencia con `?page=N` (20 por página) | JSON-LD (`ItemList` de `Vehicle`) + tarjeta HTML para la ubicación | `offers.price` | Texto de la tarjeta antes del guion |
| AutoHero | POST a la consulta `searchAdV9AdsV2`, de 24 en 24 (`offset`) | Respuesta JSON | `offerPrice` en céntimos | 2 primeras cifras del CP de la sede |
| coches.com | Listado general con `?page=N` (20 por página) | `__NEXT_DATA__` → `props.pageProps.classifieds.classifiedList` | `price` (`priceOffer` es el financiado) | `currentProvince` |

## Lo que sabemos de coches.com (mi web)

- El listado es `https://www.coches.com/coches-segunda-mano/coches-ocasion.htm`; `/coches-segunda-mano/` es solo una página de presentación.
- Responde 200 a `requests` con User-Agent; no hace falta Selenium. A veces no acepta la conexión a la primera (ConnectTimeout) y al reintentar responde en 1 s: por eso `descargar()` reintenta.
- `price` es el **contado** y `priceOffer` el **financiado** (al revés que Flexicar). No vale «el mayor es el contado»: hay coches (un DS 7) con el financiado más alto.
- El JSON no trae la URL de la ficha: se saca de los `<a>` con `?id=` y se cruza por `visibleId`. Cada coche está enlazado varias veces.
- El listado mezcla ocasión con km 0 y seminuevos: se descartan con `isKm0`.
- Todos los híbridos llevan «Gasolina» en el combustible («Híbrido Enchufable Gasolina»): `normalizar_combustible()` mira primero si es híbrido.
- `coches-ocasion-en-valencia.htm` filtra por **concesionarios con sede en Valencia**, no por dónde está el coche. La provincia real es `currentProvince`.
- Las marcas vienen en mayúsculas. Puede haber vendedores particulares (`dealer.type == "INDIVIDUAL"`); en las otras tres webs todos son profesionales.
- `financingQuote` viene vacío: no hay cuota mensual. El stock cambia mientras recorres páginas (puede haber repetidos entre páginas).
- `robots.txt`: para `User-agent: *` solo prohíbe `/reserva`, `/contacto` e `/index.php`, con `Allow: /`.

## Reglas para el código

- **Solo lo visto en clase.** Hasta ahora: `requests` (GET y POST) con cabecera `User-Agent`, HTML, JSON y BeautifulSoup (`find`, `find_all`, `get`, `get_text`, `parent`), y lo que se vaya dando en teoría (la UD3 va de filtrado de datos: pandas, distancias entre cadenas, fechas, OpenRefine). Nada de Selenium, Scrapy, expresiones regulares ni selectores CSS. Si algo no se puede hacer sin salirse de lo dado, **avísame antes**. Los apuntes están en `../TEORÍA` y las prácticas en `../PRÁCTICAS`.
- Código **sencillo y comentado en español**: lo tengo que entender y defender delante del profesor.
- Respetar el `robots.txt` de cada web y mantener la pausa entre peticiones.
- Los extractores de los demás y el código común (`esquema.py`, `utils.py`, `recoger.py`) son del grupo: no los cambies sin decírmelo, porque afecta a todos.
- Si no estás seguro de algo, pregunta antes de ejecutar.
