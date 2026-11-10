# Comparador de coches de segunda mano

Proyecto de **Adquisición y Transmisión de Datos (ATD)** — Grado en Ciencia de Datos, UPV, 2026/2027.

Junta anuncios de **Flexicar, OcasionPlus, AutoHero y coches.com** en un formato común, los guarda en un
servidor y permite buscarlos con filtros (presupuesto, marca, modelo, año, km, combustible, cambio,
provincia, comunidad y tipo de vendedor). Si no hay resultados, propone alternativas cercanas.

Equipo: Álvaro Montoya Amores (Flexicar) · Manuel Martí Cuñat (OcasionPlus) ·
Diego Molina Catalá (AutoHero) · Miguel Oltra González (coches.com).

---

## Empezar (primera vez)

Necesitas **Git** y **Python 3.10 o superior** (`python --version`).

**1. Acepta la invitación** al repositorio: te ha llegado un correo de GitHub, o entra en
<https://github.com/diegomolinacatala/comparador-coches/invitations>.

**2. Clona el repositorio** (en la carpeta donde guardes tus proyectos):

```bash
git clone https://github.com/diegomolinacatala/comparador-coches.git
cd comparador-coches
```

También vale GitHub Desktop: *File → Clone repository → comparador-coches*.

**3. Crea un entorno virtual e instala las librerías:**

```bash
python -m venv .venv
```

Actívalo — Windows (PowerShell): `.venv\Scripts\Activate.ps1` · macOS/Linux: `source .venv/bin/activate`

```bash
pip install -r requirements.txt
```

**4. Comprueba que todo funciona:**

```bash
python -m pytest
```

Tienen que salir todos en verde (`passed`). No necesitan internet.

**5. Prueba el comparador entero** (con los datos de ejemplo que ya hay en `datos/`). Abre dos terminales:

```bash
python servidor.py
```

y en la otra:

```bash
python enviar.py
python cliente.py
```

**6. (Opcional) Claude Code:** si lo usas, ábrelo en esta carpeta; leerá `CLAUDE.md` y sabrá todo el
contexto del proyecto. Recuerda apuntar en `docs/USO_IA.md` lo que hagas con IA.

## Uso

| Comando | Qué hace |
|---|---|
| `python recoger.py` | Descarga anuncios nuevos de las cuatro webs → `datos/<web>.json` (tarda ~1 min) |
| `python ver_datos.py` | Enseña el primer anuncio de cada web, campo a campo |
| `python servidor.py` | Arranca el servidor en `http://127.0.0.1:5000` |
| `python servidor.py --host 0.0.0.0` | Igual, pero accesible desde otros ordenadores de la red |
| `python enviar.py [--servidor URL]` | Limpia los anuncios y los manda al servidor |
| `python cliente.py [--servidor URL]` | Buscador interactivo |
| `python cliente.py --precio-max 12000 --comunidad "Comunidad Valenciana" --agrupar` | Búsqueda directa |
| `python -m pytest` | Tests |

Para probar en **dos ordenadores**: en el que hace de servidor, `python servidor.py --host 0.0.0.0` y mira
su IP (`ipconfig` en Windows); en el otro, `python cliente.py --servidor http://<IP>:5000`.
Puede que el firewall de Windows pregunte si permite Python: hay que aceptarlo en redes privadas.

Las rutas del servidor y ejemplos de petición/respuesta están en [docs/API.md](docs/API.md).

## Estructura

```
├── esquema.py          formato común de los anuncios (Tabla 1 del entregable)
├── utils.py            descargar, guardar JSON, normalizar combustible y cambio
├── provincias.py       provincias y comunidades autónomas
├── flexicar.py         extractor de Flexicar        (Álvaro)
├── ocasionplus.py      extractor de OcasionPlus     (Manuel)
├── autohero_api.py     extractor de AutoHero        (Diego)
├── cochescom.py        extractor de coches.com      (Miguel)
├── recoger.py          ejecuta los cuatro extractores
├── ver_datos.py        comprobación visual de los JSON
├── limpieza.py         Fase 3: unificar marcas, modelos y provincias
├── catalogo.py         guardar y buscar en el catálogo
├── servidor.py         Fase 4: servidor HTTP (Flask)
├── enviar.py           manda los anuncios limpios al servidor
├── cliente.py          Fase 5: buscador de consola
├── tests/              tests con pytest
├── datos/              JSON de cada web (+ catalogo.json, que genera el servidor y no se sube)
└── docs/
    ├── API.md          rutas del servidor con ejemplos
    ├── FUENTES.md      cómo se saca cada web y sus trampas
    ├── USO_IA.md       registro de uso de IA (lo pide la asignatura)
    └── entregables/    Entregable 2 (propuesta y viabilidad)
```

## Estado

| Fase | Estado |
|---|---|
| 1. Definición y viabilidad | ✅ Entregable 2 |
| 2. Extractores | ✅ 4 webs funcionando (`recoger.py`) |
| 3. Limpieza e integración | ✅ `limpieza.py` (marcas, modelos, provincias, repetidos, atípicos) |
| 4. Comunicación y servidor | ✅ `servidor.py` con Flask + `enviar.py` |
| 5. Buscador | ✅ `cliente.py` de consola (orden, agrupar por modelo, alternativas) |
| 6. Validación y documentación | ⏳ pendiente |

## Qué falta

- [ ] **Confirmar en grupo que usamos Flask** para el servidor (el entregable lo dejaba abierto).
- [ ] Recoger más páginas por web (`PAGINAS_POR_WEB` en `recoger.py`) y revisar si salen marcas o
      provincias sin unificar → añadirlas en `limpieza.py` / `provincias.py`.
- [ ] Cada uno: revisar con su web los datos limpios y contrastar algún anuncio al azar con la ficha real.
- [ ] Probar cliente y servidor en dos ordenadores distintos.
- [ ] Decidir si el cliente se queda en consola o se hace una interfaz más completa.
- [ ] Preparar la demo: búsqueda con resultados, sin resultados y con alternativas.
- [ ] Rellenar `docs/USO_IA.md` y escribir la memoria final.

## Cómo trabajamos con Git

```bash
git pull                              # antes de empezar, trae lo último
git checkout -b nombre-de-la-tarea    # una rama por tarea
# ... cambios ...
python -m pytest                      # que todo siga en verde
git add <ficheros>
git commit -m "Añade filtro por color"
git push -u origin nombre-de-la-tarea
```

Luego abre un *Pull Request* en GitHub hacia `main` y que lo mire otro del grupo antes de juntarlo.
GitHub ejecuta los tests automáticamente en cada push y Pull Request.

Reglas del proyecto (ética del scraping, formato común, estilo de código): ver [CLAUDE.md](CLAUDE.md).
