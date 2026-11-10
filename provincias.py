"""
Nombres de provincias y comunidades autónomas que usa todo el proyecto.

- PROVINCIAS: código postal (dos primeras cifras) -> nombre de la provincia.
  Lo usa autohero_api.py para sacar la provincia de la sede del coche.
- COMUNIDADES: comunidad autónoma -> lista de sus provincias. Lo usa el
  buscador para el filtro «comunidad» (p. ej. "Comunidad Valenciana").
- ALIAS_PROVINCIAS: otras formas de escribir una provincia que aparecen en
  las webs ("València", "Alacant", "Vizcaya"...). Las usa limpieza.py.
"""

PROVINCIAS = {
    "01": "Álava", "02": "Albacete", "03": "Alicante", "04": "Almería", "05": "Ávila",
    "06": "Badajoz", "07": "Baleares", "08": "Barcelona", "09": "Burgos", "10": "Cáceres",
    "11": "Cádiz", "12": "Castellón", "13": "Ciudad Real", "14": "Córdoba", "15": "A Coruña",
    "16": "Cuenca", "17": "Girona", "18": "Granada", "19": "Guadalajara", "20": "Gipuzkoa",
    "21": "Huelva", "22": "Huesca", "23": "Jaén", "24": "León", "25": "Lleida",
    "26": "La Rioja", "27": "Lugo", "28": "Madrid", "29": "Málaga", "30": "Murcia",
    "31": "Navarra", "32": "Ourense", "33": "Asturias", "34": "Palencia", "35": "Las Palmas",
    "36": "Pontevedra", "37": "Salamanca", "38": "Santa Cruz de Tenerife", "39": "Cantabria",
    "40": "Segovia", "41": "Sevilla", "42": "Soria", "43": "Tarragona", "44": "Teruel",
    "45": "Toledo", "46": "Valencia", "47": "Valladolid", "48": "Bizkaia", "49": "Zamora",
    "50": "Zaragoza", "51": "Ceuta", "52": "Melilla",
}

COMUNIDADES = {
    "Andalucía": ["Almería", "Cádiz", "Córdoba", "Granada", "Huelva", "Jaén", "Málaga", "Sevilla"],
    "Aragón": ["Huesca", "Teruel", "Zaragoza"],
    "Asturias": ["Asturias"],
    "Baleares": ["Baleares"],
    "Canarias": ["Las Palmas", "Santa Cruz de Tenerife"],
    "Cantabria": ["Cantabria"],
    "Castilla-La Mancha": ["Albacete", "Ciudad Real", "Cuenca", "Guadalajara", "Toledo"],
    "Castilla y León": ["Ávila", "Burgos", "León", "Palencia", "Salamanca", "Segovia",
                        "Soria", "Valladolid", "Zamora"],
    "Cataluña": ["Barcelona", "Girona", "Lleida", "Tarragona"],
    "Comunidad Valenciana": ["Alicante", "Castellón", "Valencia"],
    "Extremadura": ["Badajoz", "Cáceres"],
    "Galicia": ["A Coruña", "Lugo", "Ourense", "Pontevedra"],
    "La Rioja": ["La Rioja"],
    "Madrid": ["Madrid"],
    "Murcia": ["Murcia"],
    "Navarra": ["Navarra"],
    "País Vasco": ["Álava", "Bizkaia", "Gipuzkoa"],
    "Ceuta": ["Ceuta"],
    "Melilla": ["Melilla"],
}

# Clave en minúsculas, sin tildes ni espacios (ver limpieza.clave) -> nombre oficial
ALIAS_PROVINCIAS = {
    "valencia": "Valencia", "alacant": "Alicante", "castello": "Castellón",
    "castellondelaplana": "Castellón", "castellodelaplana": "Castellón",
    "illesbalears": "Baleares", "islasbaleares": "Baleares", "balears": "Baleares",
    "guipuzcoa": "Gipuzkoa", "vizcaya": "Bizkaia", "araba": "Álava",
    "lacoruna": "A Coruña", "coruna": "A Coruña", "gerona": "Girona", "lerida": "Lleida",
    "orense": "Ourense", "rioja": "La Rioja", "tenerife": "Santa Cruz de Tenerife",
    "grancanaria": "Las Palmas",
}
