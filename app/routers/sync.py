# app/routers/sync.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Any, Dict
from io import BytesIO
import json

from app.schema.enums import from_excel_bytes
from app.services.transformer import transform_from_docx
from app.services.excel_writer import write_auto_fields, update_row_in_excel
from app.services.docx_reader import extract_fields_from_docx
from app.config import settings
from app.services.enums_loader import load_enums_from_bytes

from fastapi import Query
from app.config import settings
from app.services.enums_loader import load_enums_from_bytes
from app.services.enums_grouping import group_enums



router = APIRouter(prefix="/sync", tags=["sync"])

ALLOWED_DOCX = (".docx",)
ALLOWED_XLSX = (".xlsx", ".xlsm")

def _check_size(name: str, blob: bytes, max_mb: int):
    if len(blob) > max_mb * 1024 * 1024:
        raise HTTPException(413, detail=f"{name} supera el límite de {max_mb} MB")

def _read_bytes(f: UploadFile) -> bytes:
    return f.file.read()

def _ext_ok(filename: str, allowed: tuple[str, ...]) -> bool:
    fn = (filename or "").lower()
    return any(fn.endswith(e) for e in allowed)

# =========================
# 1) PREVIEW (JSON)
# =========================
@router.post("/preview")
async def preview(
    docx: UploadFile = File(...),
    excel: UploadFile = File(...),
):
    if not _ext_ok(docx.filename, ALLOWED_DOCX):
        raise HTTPException(400, detail="DOCX inválido")
    if not _ext_ok(excel.filename, ALLOWED_XLSX):
        raise HTTPException(400, detail="Excel inválido")

    docx_bytes = _read_bytes(docx)
    excel_bytes = _read_bytes(excel)
    _check_size("DOCX", docx_bytes, settings.MAX_DOCX_MB)
    _check_size("Excel", excel_bytes, settings.MAX_EXCEL_MB)

    enums = from_excel_bytes(excel_bytes)
    fields = extract_fields_from_docx(docx_bytes)
    auto_fields = transform_from_docx(fields, enums)
    written = write_auto_fields(excel_bytes, auto_fields)  # {sheet,row,updated_excel_bytes}

    return JSONResponse({
        "sheet": written["sheet"],
        "row": written["row"],  # base-0
        "detected_fields": fields,
        "auto_fields": auto_fields,
    })

# =========================
# 2) PROCESS (descarga .xlsx temporal)
# =========================
@router.post("/process")
async def process(
    docx: UploadFile = File(...),
    excel: UploadFile = File(...),
    filename: str | None = None
):
    if not _ext_ok(docx.filename, ALLOWED_DOCX):
        raise HTTPException(400, detail="DOCX inválido")
    if not _ext_ok(excel.filename, ALLOWED_XLSX):
        raise HTTPException(400, detail="Excel inválido")

    docx_bytes = _read_bytes(docx)
    excel_bytes = _read_bytes(excel)
    _check_size("DOCX", docx_bytes, settings.MAX_DOCX_MB)
    _check_size("Excel", excel_bytes, settings.MAX_EXCEL_MB)

    enums = from_excel_bytes(excel_bytes)
    fields = extract_fields_from_docx(docx_bytes)
    auto_fields = transform_from_docx(fields, enums)
    written = write_auto_fields(excel_bytes, auto_fields)

    fname = filename or "temporal.xlsx"
    return StreamingResponse(
        BytesIO(written["updated_excel_bytes"]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{fname}"',
            "X-Excel-Sheet": written["sheet"],
            "X-Excel-Row": str(written["row"]),  # base-0
        },
    )

# =========================
# 3) FINALIZE (PUT con payload JSON en multipart)
# =========================
class FinalizePayload(BaseModel):
    sheet: str
    row_index: int  # base-0
    filename: str | None = None
    updates: Dict[str, Any] = {}

@router.put("/finalize")
async def finalize(
    excel: UploadFile = File(...),
    payload: UploadFile = File(..., description='JSON con {"sheet","row_index","filename","updates"}'),
):
    if not _ext_ok(excel.filename, ALLOWED_XLSX):
        raise HTTPException(400, detail="Excel inválido")

    excel_bytes = _read_bytes(excel)
    _check_size("Excel", excel_bytes, settings.MAX_MULTIPART_MB)

    try:
        data = FinalizePayload(**json.loads(payload.file.read().decode("utf-8")))
    except Exception as e:
        raise HTTPException(400, detail=f"Payload inválido: {e}")

    result = update_row_in_excel(
        excel_bytes=excel_bytes,
        sheet=data.sheet,
        row_index_base0=data.row_index,
        updates=data.updates,
    )

    fname = data.filename or "salida.xlsx"
    return StreamingResponse(
        BytesIO(result["updated_excel_bytes"]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{fname}"',
            "X-Excel-Sheet": result["sheet"],
            "X-Excel-Row": str(result["row"]),  # base-0
        },
    )


@router.get("/enums")
async def enums_maestro(
    section: str | None = Query(None, description="apartado opcional: usuarios|portales|tematicas|ambito|otros"),
    raw: bool = Query(False, description="si true, devuelve el diccionario crudo sin agrupar")
):
    with open(settings.MASTER_EXCEL_PATH, "rb") as f:
        excel_bytes = f.read()

    enums_raw = load_enums_from_bytes(
        excel_bytes,
        data_sheet=getattr(settings, "MASTER_DATA_SHEET", "Fichas 2025"),
        header_row=getattr(settings, "MASTER_HEADER_ROW", 2),
    )

    if raw:
        return enums_raw

    grouped = group_enums(enums_raw)

    if section:
        sec = section.lower()
        if sec in grouped:
            return {sec: grouped[sec]}
        # nombre no reconocido -> vacío (o 404 si prefieres)
        return {}

    return grouped


