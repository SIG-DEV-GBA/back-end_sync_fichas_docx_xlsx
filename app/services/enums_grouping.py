# app/services/enums_grouping.py
from typing import Dict, List

def _dedup(seq: List[str]) -> List[str]:
    seen = set(); out = []
    for s in seq:
        s = s.strip()
        if s and s not in seen:
            seen.add(s); out.append(s)
    return out

def group_enums(enums_raw: Dict[str, List[str]]) -> Dict:
    # normaliza claves para búsqueda suave sin perder las originales
    keys_uc = {k.upper(): k for k in enums_raw.keys()}

    def g(name: str) -> List[str]:
        k = keys_uc.get(name.upper())
        return list(enums_raw.get(k, [])) if k else []

    # usuarios
    usuarios = {
        "hace_ficha": g("USUARIOS_HACE_FICHA"),
        "sube_ficha": g("USUARIOS_SUBE_FICHA"),
    }

    # portales
    portales = g("PORTALES")

    # temáticas (unión de tabla TEMATICAS + validaciones TEMÁTICA 1/2/3)
    t1 = g("TEMÁTICA 1")
    t2 = g("TEMÁTICA 2")
    t3 = g("TEMÁTICA 3")
    ttab = g("TEMATICAS")
    tematicas = _dedup(ttab + t1 + t2 + t3)

    # ámbito
    ambito = {
        "estado_ue": g("ESTADO_UE"),
        "ccaa": g("CCAA"),
        "provincias": g("PROVINCIAS"),
    }

    # construir set de claves ya consumidas
    consumed = set(
        [keys_uc.get(k) for k in [
            "USUARIOS_HACE_FICHA", "USUARIOS_SUBE_FICHA",
            "PORTALES", "TEMATICAS", "TEMÁTICA 1", "TEMÁTICA 2", "TEMÁTICA 3",
            "ESTADO_UE", "CCAA", "PROVINCIAS"
        ] if k in keys_uc]
    )

    # otros: cualquier cabecera/lista detectada no mapeada arriba
    otros = { k: v for k, v in enums_raw.items() if k not in consumed and v }

    return {
        "usuarios": usuarios,
        "portales": portales,
        "tematicas": tematicas,
        "ambito": ambito,
        "otros": otros
    }
