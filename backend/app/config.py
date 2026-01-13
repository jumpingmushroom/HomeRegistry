from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "/data/homeregistry.db")

    # Storage paths
    images_path: str = os.getenv("IMAGES_PATH", "/data/images")
    documents_path: str = os.getenv("DOCUMENTS_PATH", "/data/documents")

    # AI Provider settings (defaults, can be overridden in app settings)
    ai_provider: str = os.getenv("AI_PROVIDER", "claude")
    claude_api_key: Optional[str] = os.getenv("CLAUDE_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    ollama_endpoint: str = os.getenv("OLLAMA_ENDPOINT", "http://ollama:11434")

    # App configuration
    default_currency: str = os.getenv("DEFAULT_CURRENCY", "NOK")
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    max_document_size_mb: int = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "50"))

    # Server
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    cors_origins: list = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8000").split(",")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure directories exist
os.makedirs(os.path.dirname(settings.database_url), exist_ok=True)
os.makedirs(settings.images_path, exist_ok=True)
os.makedirs(f"{settings.images_path}/thumbnails", exist_ok=True)
os.makedirs(settings.documents_path, exist_ok=True)
