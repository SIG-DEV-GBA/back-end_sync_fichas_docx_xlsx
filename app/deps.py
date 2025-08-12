from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from .config import settings

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.CORS_ORIGINS] or ["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
