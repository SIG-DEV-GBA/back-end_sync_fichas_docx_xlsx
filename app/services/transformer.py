from typing import Dict, Any, List, Tuple
import re
import unicodedata

# ==== Normalización / helpers ====

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn")

def _norm(s: str) -> str:
    s = _strip_accents(s or "").lower().strip()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s

def _initials_variants(name: str) -> List[str]:
    parts = [p for p in _norm(name).split() if p]
    if not parts:
        return []
    out = [" ".join(parts)]
    if len(parts) >= 2:
        out.append(f"{parts[0]} {parts[1][0]}")                # carmen r
        out.append(f"{parts[0][0]} {' '.join(parts[1:])}")     # c rio
    else:
        out.append(parts[0][0])
    # de-dup preservando orden
    seen=set(); res=[]
    for v in out:
        if v not in seen:
            seen.add(v); res.append(v)
    return res

def _ratio(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a or not b: return 0.0
    def bigrams(x): return {x[i:i+2] for i in range(len(x)-1)} if len(x) > 1 else {x}
    A, B = bigrams(a), bigrams(b)
    jacc = len(A & B) / (len(A | B) or 1)
    pref = 1.0 if a.startswith(b) or b.startswith(a) else 0.0
    return 0.7*jacc + 0.3*pref

def fuzzy_match(name: str, candidates: List[str], threshold: float = 0.72) -> Tuple[str | None, List[Tuple[str, float]]]:
    if not name:
        return None, []
    pats = {_norm(name)} | set(_initials_variants(name))
    scored = []
    for cand in candidates:
        scored.append((cand, max(_ratio(p, cand) for p in pats)))
    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[0] if scored else (None, 0.0)
    return (best[0] if best and best[1] >= threshold else None, scored[:3])

def coerce_list(v) -> List[str]:
    if v is None: return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s: return []
    return [p.strip() for p in s.replace(";", ",").split(",") if p.strip()]

# ==== Reglas específicas ====

PORTAL_COLUMNS = ["Mayores", "Discapacidad", "Familia", "Mujer", "Salud"]
TEMATICA_COLS = ["TEMÁTICA 1", "TEMÁTICA 2", "TEMÁTICA 3"]

def pick_ambito(value: str | None, enums: Dict[str, List[str]]) -> Dict[str, str]:
    """Devuelve un diccionario con SOLO una de las tres columnas de ámbito."""
    if not value:
        return {}
    t = (value or "").strip()
    # 1) UE/Estado exacto
    for x in enums.get("ESTADO_UE", ["UE", "Estado"]):
        if t.lower() == x.lower() or _norm(t) == _norm(x):
            return {"AMBITO UE/ESTADO": x}
    # 2) CCAA
    for x in enums.get("CCAA", []):
        if t.lower() == x.lower() or _norm(t) == _norm(x):
            return {"AMBITO CC AA": x}
    # 3) Provincias
    for x in enums.get("PROVINCIAS", []):
        if t.lower() == x.lower() or _norm(t) == _norm(x):
            return {"AMBITO PROVINCIAL": x}
    # 4) Heurística mínima para UE/Estado
    tl = t.lower()
    if "union europea" in _norm(t) or t.strip().upper() == "UE":
        return {"AMBITO UE/ESTADO": "UE"}
    if any(k in tl for k in ["estado", "nacional", "españa", "espana"]):
        return {"AMBITO UE/ESTADO": "Estado"}
    # sin match claro: lo dejamos como CCAA por defecto (o vacio si prefieres)
    return {"AMBITO CC AA": t}

def tramites_electronicos_flag(lugar_y_forma: str | None) -> str:
    """
    "Sí" si hay al menos un canal electrónico distinto de Red SARA,
    "No" si solo está Red SARA o no hay apartado electrónico.
    """
    if not lugar_y_forma:
        return "No"
    text = _norm(lugar_y_forma)
    has_any = "electr" in text  # 'electrónicamente' / 'electronico' etc.
    # casos típicos de Red SARA
    sara = any(k in text for k in [
        "rec redsara", "redsara", "registro electronico comun", "rec – red sara", "rec- red sara"
    ])
    # detectar otros canales (sede electrónica, portales propios, etc.)
    other = any(k in text for k in [
        "sede electronica", "sede electrónica", "tramita", "portal", "sede",
        "jccm.es", "sede.jcyl", "sede.gob", "gva.es", "xunta", "carm.es", "navarra.es"
    ])
    if other:
        return "Sí"
    if has_any and not sara:
        return "Sí"
    return "No"

def transform_from_docx(docx_fields: Dict[str, Any], enums: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Recibe los campos ya extraídos del DOCX (dict) y devuelve auto_fields (dict)
    listo para escribir en la fila nueva del Excel (el resto queda vacío para edición manual).
    """
    out: Dict[str, Any] = {}

    # Ámbito (exclusivo) — Municipal vacío
    out.update(pick_ambito(docx_fields.get("Ámbito territorial"), enums))
    out["AMBITO MUNICIPAL"] = ""   # manual

    # ID / NºF.TECNICA vacíos (manual)
    out["ID"] = ""
    out["NºF.TECNICA"] = ""

    # Portales → columnas literales
    portals = coerce_list(docx_fields.get("Portales"))
    allowed = {p.lower(): p for p in enums.get("PORTALES", PORTAL_COLUMNS)}
    for col in PORTAL_COLUMNS:
        out[col] = col if col.lower() in [p.lower() for p in portals if p.lower() in allowed] else ""

    # Temáticas desde "Tipo de ayuda" (máx 3, validar contra enum)
    tipo_vals = coerce_list(docx_fields.get("Tipo de ayuda"))
    valid_temas = []
    allowed_temas = {t.lower(): t for t in enums.get("TEMATICAS", [])}
    for v in tipo_vals:
        key = v.lower()
        if key in allowed_temas and allowed_temas[key] not in valid_temas:
            valid_temas.append(allowed_temas[key])
        if len(valid_temas) == 3:
            break
    for i, col in enumerate(TEMATICA_COLS):
        out[col] = valid_temas[i] if i < len(valid_temas) else ""

    # Nombre / fechas
    out["NOMBRE DE FICHA"] = docx_fields.get("Nombre de la ayuda") or ""
    out["VENCIMIENTO"] = docx_fields.get("Fecha fin") or ""

    # Trabajadora que hace la ficha ← USUARIO (fuzzy contra enum de "hace")
    docx_user = docx_fields.get("Usuario")
    match, _ = fuzzy_match(docx_user, enums.get("USUARIOS_HACE_FICHA", []))
    out["TRABAJADORA QUE HACE LA FICHA"] = match or ""

    # Fecha de redacción ← FECHA (Otros datos)
    out["FECHA DE REDACCIÓN"] = docx_fields.get("Fecha") or ""

    # Fechas/Valores manuales
    out["Fecha de Subida a la  WEB"] = ""
    out["TRABAJADOR QUE SUBE LA FICHA"] = ""
    out["COMPLEJIDAD"] = ""

    # Trámite electrónico (Sí/No)
    out["TRAMITE ELECTRONICO"] = tramites_electronicos_flag(docx_fields.get("Lugar y forma de presentación"))

    # Enlace web → manual (o lo autocalculamos en finalize si quieres)
    out["ENLACE WEB"] = ""

    # Resto manuales
    out["TEXTO para su DIVULGACIÓN"] = ""
    out["TEXTO"] = ""
    out["MES"] = ""
    out["AÑO"] = ""
    out["PARA ARCHIBO I.AYUDAS"] = ""
    out["DESTACABLE/NOVEDAD"] = ""

    return out
