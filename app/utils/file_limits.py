from fastapi import HTTPException, UploadFile
from ..config import settings

def ensure_limits(docx: UploadFile, excel: UploadFile):
    # FastAPI no expone size directo; depende del cliente/servidor.
    # Si estás detrás de Nginx, limita allí también (client_max_body_size).
    # Aquí validamos por extensión/MIME como primera barrera.
    if not docx.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=415, detail="El DOCX debe tener extensión .docx")

    if not (excel.filename.lower().endswith(".xlsx") or
            excel.filename.lower().endswith(".xlsm") or
            excel.filename.lower().endswith(".xls")):
        raise HTTPException(status_code=415, detail="El Excel debe ser .xlsx/.xlsm (o .xls)")

