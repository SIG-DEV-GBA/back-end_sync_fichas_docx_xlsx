# app/services/sync_service.py
from typing import Dict, Any
from app.services.enums_loader import load_enums_from_bytes
from app.services.user_matcher import match_user
# from .docx_reader import extract_fields_from_docx
# from .excel_writer import apply_to_excel

def preview(docx_bytes: bytes, excel_bytes: bytes) -> Dict[str, Any]:
    enums = load_enums_from_bytes(excel_bytes)
    # fields = extract_fields_from_docx(docx_bytes)
    return {"enums": enums}  # y si quieres, añade fields para ver el mapeo

def process(docx_bytes: bytes, excel_bytes: bytes) -> Dict[str, Any]:
    enums = load_enums_from_bytes(excel_bytes)
    fields = extract_fields_from_docx(docx_bytes)

    # USUARIO del DOCX -> TRABAJADOR QUE SUBE LA FICHA (fuzzy)
    docx_user = fields.get("Usuario")
    candidates = enums.get("USUARIOS_SUBE_FICHA", [])
    match, suggestions = match_user(docx_user, candidates)

    # setea el valor ya normalizado para el writer
    fields["TRABAJADOR QUE SUBE LA FICHA"] = match or ""

    # ... aquí aplicarás portales, temáticas, ámbito, etc. con estos enums ...
    # result = apply_to_excel(excel_bytes, fields, enums=enums)

    return {
        "ok": True,
        "usuario_docx": docx_user,
        "usuario_match": match,
        "usuario_sugerencias": suggestions[:3],
        # "updated_excel_bytes": result["updated_excel_bytes"]
    }
