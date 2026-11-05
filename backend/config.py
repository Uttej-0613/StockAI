from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_name: str = "StockAI"
    environment: str = os.getenv("ENVIRONMENT", "development").lower()
    api_key: str | None = os.getenv("STOCKAI_API_KEY") or None
    database_path: str = os.getenv("DATABASE_PATH", "./data/stockai.db")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    max_upload_bytes: int = min(max(int(os.getenv("MAX_UPLOAD_BYTES", str(15 * 1024 * 1024))), 1024), 50 * 1024 * 1024)
    cors_origins: list[str] = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",") if x.strip()]

    def ensure_data_dir(self) -> None:
        Path(self.database_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

@lru_cache
def get_settings() -> Settings:
    return Settings()
