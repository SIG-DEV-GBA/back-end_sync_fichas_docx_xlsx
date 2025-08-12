# app/services/validators.py
from typing import Dict
from app.schema.enums import from_excel_bytes

def normalize_ambito(raw_text: str | None, enums: Dict[str, list]) -> Dict[str, str]:
    """
    Devuelve un dict con **solo una** de las tres claves:
    - "AMBITO CC AA"
    - "AMBITO PROVINCIAL"
    - "AMBITO UE/ESTADO"
    según el valor detectado.
    """
    if not raw_text:
        return {}

    t = (raw_text or "").strip()

    # 1) UE/Estado exacto (según tu regla)
    if t.lower() in [x.lower() for x in enums.get("ESTADO_UE", ["UE", "Estado"])]:
        # Capitalizar como en la lista
        fixed = next(x for x in enums.get("ESTADO_UE", ["UE","Estado"]) if x.lower() == t.lower())
        return {"AMBITO UE/ESTADO": fixed}

    # 2) CCAA / PROVINCIA (se basan en los enums cargados del Excel)
    if any(t.lower() == x.lower() for x in enums.get("CCAA", [])):
        return {"AMBITO CC AA": t}
    if any(t.lower() == x.lower() for x in enums.get("PROVINCIAS", [])):
        return {"AMBITO PROVINCIAL": t}

    # 3) Heurística mínima: si contiene "UE" o "Estado", decide UE/Estado
    if t.lower() == "ue" or "unión europea" in t.lower() or "union europea" in t.lower():
        return {"AMBITO UE/ESTADO": "UE"}
    if t.lower() == "estado" or "nacional" in t.lower() or "españa" in t.lower():
        return {"AMBITO UE/ESTADO": "Estado"}

    # Si no cuadra, dejamos CCAA por defecto (o vacío si prefieres)
    return {"AMBITO CC AA": t}
