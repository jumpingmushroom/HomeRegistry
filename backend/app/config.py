from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "/data/homeregistry.db"

    # Storage paths
    images_path: str = "/data/images"
    documents_path: str = "/data/documents"

    # AI Provider settings (defaults, can be overridden in app settings)
    ai_provider: str = "claude"
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ollama_endpoint: str = "http://ollama:11434"

    # App configuration
    default_currency: str = "NOK"
    max_image_size_mb: int = 10
    max_document_size_mb: int = 50

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins_str: str = "http://localhost:5173,http://localhost:8000,http://localhost:8180"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Parse CORS origins
cors_origins = [origin.strip() for origin in settings.cors_origins_str.split(',')]

# Ensure directories exist
db_dir = os.path.dirname(settings.database_url)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)
os.makedirs(settings.images_path, exist_ok=True)
os.makedirs(f"{settings.images_path}/thumbnails", exist_ok=True)
os.makedirs(settings.documents_path, exist_ok=True)
