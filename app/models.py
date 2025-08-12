from pydantic import BaseModel
from typing import Any, Optional, List, Dict

class SyncPreview(BaseModel):
    doc_name: str
    excel_name: str
    detected_fields: Dict[str, Any]  # e.g., {"Nombre ficha": "x", "Vencimiento": "2025-10-30"}
    will_update_sheets: List[str]

class SyncResult(BaseModel):
    ok: bool = True
    message: str = "Sincronización realizada"
    updated_rows: int = 0
    sheet: Optional[str] = None
    details: Optional[dict] = None

class ErrorResponse(BaseModel):
    detail: str
