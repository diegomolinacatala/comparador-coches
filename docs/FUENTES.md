# Cómo se sacan los datos de cada web

Resumen técnico de las pruebas del Entregable 2 (apartado 4). Si una web cambia y un extractor deja de
funcionar, empezar por aquí.

| | Flexicar | OcasionPlus | AutoHero | coches.com |
|---|---|---|---|---|
| Responsable | Álvaro | Manuel | Diego | Miguel |
| Fichero | `flexicar.py` | `ocasionplus.py` | `autohero_api.py` | `cochescom.py` |
| Páginas | Sitemap `sitemap-marca-modelo-provincia.xml`, URLs con `coches-valencia` (máx. 12 coches cada una) | Listado `/coches-segunda-mano/valencia?page=N` (20 por página) | API `searchAdV9AdsV2` (POST, 24 por petición, `offset` 0, 24, 48…) | `/coches-segunda-mano/coches-ocasion.htm?page=N` (20 por página) |
| Dónde están los datos | `<script id="__NEXT_DATA__">` → `props.pageProps.initialVehicles` | `<script type="application/ld+json">` con `ItemList` de `Vehicle` + tarjeta HTML (`data-test="div-dealer"`) | Respuesta JSON de la API (`data.searchAdV9AdsV2.data`) | `__NEXT_DATA__` → `props.pageProps.classifieds.classifiedList` + enlaces `<a href="...?id=">` |
| **Precio al contado** | `cashPrice` (¡`price` es el financiado!) | `offers.price` | `offerPrice` en **céntimos** (`amountMinorUnits / conversionMajor`) | `price.amount` (`priceOffer` es el financiado) |
| Provincia | Siempre Valencia | Texto de la tarjeta antes del guion («Valencia - Alzira») | 2 primeras cifras del código postal de la sede (`esBranch.zipcode`) | `currentProvince.name` |
| Vendedor | profesional | profesional | profesional | `dealer.type == "INDIVIDUAL"` → particular |
| Ámbito | Valencia | Valencia | Toda España (casi todo en Seseña, Toledo) | Toda España |

## Trampas conocidas

**Flexicar**
- El resto de coches del listado se cargan desde `services.flexicar.es`, que el `robots.txt` prohíbe.
  Por eso se recorre el sitemap: se pierden coches de los modelos con más de 12 anuncios.
- Leer el sitemap con `BeautifulSoup(xml, "xml")` necesita `lxml`.

**OcasionPlus**
- En la primera prueba 8 de 20 anuncios tenían mal el precio (precio de la tarjeta ≠ JSON). La versión
  actual usa `offers.price` del JSON-LD y coincide con la ficha.
- `name` = «Marca Modelo» y `model` = «Marca Modelo Versión»: se quitan prefijos comparando en minúsculas
  porque a veces cambian («Nissan QASHQAI» / «Nissan Qashqai»).
- Si la tarjeta del coche no está en el HTML, la provincia queda `None`.

**AutoHero**
- Combustible y cambio vienen como códigos: 1039 gasolina, 1040 diésel, 1044 eléctrico, 1046 híbrido
  (`isPluginSystem` → enchufable); 1138 manual, 1139/1140/1141 automático.
- Anuncios «venta en proceso»: la web no muestra precio → `precio_contado` None → se descartan.
- La ciudad de la sede no es fiable (el taller de Seseña dice «Madrid»): por eso se usa el código postal.
- El cuerpo de la petición (`CUERPO`) se copió de la pestaña Red del navegador.

**coches.com**
- `/coches-segunda-mano/` no es el listado; el listado es `coches-ocasion.htm`.
- Mezcla coches de ocasión con km 0 y seminuevos → se descartan con `isKm0`.
- Todos los híbridos llevan la palabra «Gasolina» («Híbrido Enchufable Gasolina»): por eso
  `normalizar_combustible()` mira primero si es híbrido.
- Marcas en mayúsculas («CITROEN», «MERCEDES»): las unifica `limpieza.py`.
- A veces no responde al primer intento: `descargar()` reintenta.

**CochesOk (descartada)**
- Cloudflare devolvía 403 «Sorry, you have been blocked» a todas las peticiones (también en el navegador).
  No se intentó sortear el bloqueo. Sustituida por coches.com.
