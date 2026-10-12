from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Tạo database URL từ settings
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"

# Tạo engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tạo SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho models
Base = declarative_base()


def ensure_schema_updates():
    """Apply small additive schema updates for deployments without migrations."""
    inspector = inspect(engine)
    court_request_columns = {
        column["name"] for column in inspector.get_columns("court_requests")
    }
    if "court_id" not in court_request_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE court_requests ADD COLUMN court_id INTEGER"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()