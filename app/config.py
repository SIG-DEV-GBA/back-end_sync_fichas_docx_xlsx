# app/config/settings.py
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    APP_NAME: str = "FichaSync Service"
    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    CORS_ORIGINS: List[AnyHttpUrl] = []
    CORS_ALLOW_CREDENTIALS: bool = True

    MAX_DOCX_MB: int = 20
    MAX_EXCEL_MB: int = 25
    MAX_MULTIPART_MB: int = 60

    # 👇 AÑADIR ESTO
    MASTER_EXCEL_PATH: str = os.path.join(BASE_DIR, "data", "excel_maestro.xlsx")
    MASTER_DATA_SHEET: str = "Fichas 2025"
    MASTER_HEADER_ROW: int = 2

    class Config:
        env_file = ".env"

settings = Settings()

