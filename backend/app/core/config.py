import json
from typing import Any, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode
from sqlalchemy.engine import URL
from typing_extensions import Annotated

class Settings(BaseSettings):
    # Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_DATABASE: str = "pickleball_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    PGSSLMODE: str = "prefer"

    # JWT Settings
    SECRET_KEY: str = "change-this-secret-in-env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google Sign-In
    GOOGLE_CLIENT_ID: Optional[str] = None
    
    # Application Settings
    DEBUG: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: Annotated[
        List[str], NoDecode
    ] = ["http://localhost:5173", "http://localhost:3000"]

    # Public URL used in QR links
    BACKEND_PUBLIC_BASE_URL: str = "http://localhost:8000"

    # Optional absolute uploads directory for persistent storage in production
    UPLOADS_ROOT_DIR: Optional[str] = None

    # Cloudinary settings (recommended for free persistent image hosting)
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    CLOUDINARY_FOLDER: str = "pickleball"

    # SMTP settings for transactional email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "Pickleball NP SPORTCLUB"
    SMTP_USE_TLS: bool = True

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> List[str]:
        if isinstance(value, list):
            return value

        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return []

            # Accept JSON array string or comma-separated value.
            if cleaned.startswith("["):
                try:
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
                except json.JSONDecodeError:
                    return []

            return [origin.strip() for origin in cleaned.split(",") if origin.strip()]

        return []
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Tạo DATABASE_URL từ các thông tin
def get_database_url() -> str:
    return str(
        URL.create(
            drivername="postgresql+psycopg2",
            username=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=int(settings.DB_PORT),
            database=settings.DB_DATABASE,
        )
    )