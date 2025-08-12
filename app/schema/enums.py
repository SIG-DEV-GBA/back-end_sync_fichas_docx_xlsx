# app/schema/enums.py
from typing import List, TypedDict

# -------- Fallbacks (por si no cargamos desde Excel) --------
PORTALES_DEFAULT: List[str] = ["Mayores", "Discapacidad", "Familia", "Mujer", "Salud"]

CCAA_DEFAULT: List[str] = [
    "Andalucía","Aragón","Asturias","Baleares","Canarias","Cantabria","Castilla y León",
    "Castilla-La Mancha","Cataluña","Comunitat Valenciana","Extremadura","Galicia",
    "La Rioja","Madrid","Murcia","Navarra","País Vasco","Ceuta","Melilla"
]

PROVINCIAS_DEFAULT: List[str] = [
    "A Coruña","Álava","Albacete","Alicante","Almería","Asturias","Ávila","Badajoz","Barcelona",
    "Bizkaia","Burgos","Cáceres","Cádiz","Cantabria","Castellón","Ciudad Real","Córdoba",
    "Cuenca","Gipuzkoa","Girona","Granada","Guadalajara","Huelva","Huesca","Illes Balears",
    "Jaén","La Rioja","Las Palmas","León","Lleida","Lugo","Madrid","Málaga","Murcia","Navarra",
    "Ourense","Palencia","Pontevedra","Salamanca","Santa Cruz de Tenerife","Segovia","Sevilla",
    "Soria","Tarragona","Teruel","Toledo","Valencia","Valladolid","Zamora","Zaragoza"
]

# Si prefieres tener un fallback de temáticas, puedes dejar tu lista inicial:
TEMATICAS_DEFAULT: List[str] = [
    "Vivienda","Empleo","Formación","Educación","Energía","Fiscalidad","Familia",
    "Salud","Discapacidad","Mayores","Mujeres","Juventud","Empresas","Emprendimiento",
    "Tecnología","Cultura","Deporte","Transporte","Rural","Medio ambiente"
]

# Estos SIEMPRE se cargarán del Excel por petición; aquí los dejamos vacíos como fallback.
USUARIOS_HACE_FICHA_DEFAULT: List[str] = []
USUARIOS_SUBE_FICHA_DEFAULT: List[str] = []
ESTADO_UE_DEFAULT = ["UE", "Estado"]  

class Enums(TypedDict):
    PORTALES: List[str]
    TEMATICAS: List[str]
    CCAA: List[str]
    PROVINCIAS: List[str]
    ESTADO_UE: List[str]
    USUARIOS_HACE_FICHA: List[str]
    USUARIOS_SUBE_FICHA: List[str]

def get_defaults() -> Enums:
    """Fallback seguro cuando no hay Excel (tests/local)."""
    return Enums(
        PORTALES=PORTALES_DEFAULT,
        TEMATICAS=TEMATICAS_DEFAULT,
        CCAA=CCAA_DEFAULT,
        PROVINCIAS=PROVINCIAS_DEFAULT,
        ESTADO_UE=ESTADO_UE_DEFAULT,
        USUARIOS_HACE_FICHA=USUARIOS_HACE_FICHA_DEFAULT,
        USUARIOS_SUBE_FICHA=USUARIOS_SUBE_FICHA_DEFAULT,
    )

def from_excel_bytes(excel_bytes: bytes) -> Enums:
    """
    Carga las listas desde el Excel maestro recibido en la petición.
    Completa con fallbacks si falta alguna lista.
    """
    from app.services.enums_loader import load_enums_from_bytes
    e = load_enums_from_bytes(excel_bytes)  # {'PORTALES': [...], 'TEMATICAS': [...], ...}
    d = get_defaults()
    # Mezcla: lo que venga del Excel sobrescribe al fallback
    d.update({k: v for k, v in e.items() if isinstance(v, list)})
    return d
