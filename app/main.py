from fastapi import FastAPI
from app.routers.sync import router as sync_router

app = FastAPI(title="FichaSync Service")

app.include_router(sync_router)

# opcional: health
@app.get("/health")
def health():
    return {"ok": True}
