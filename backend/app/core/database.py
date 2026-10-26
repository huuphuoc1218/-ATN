from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Tạo database URL từ settings
SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=int(settings.DB_PORT),
    database=settings.DB_DATABASE,
)

# Tạo engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"sslmode": settings.PGSSLMODE},
)

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
    court_columns = {
        column["name"] for column in inspector.get_columns("courts")
    }
    booking_participant_columns = {
        column["name"] for column in inspector.get_columns("booking_participants")
    }

    updates = []
    if "court_id" not in court_request_columns:
        updates.append("ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS court_id INTEGER")
    for column, definition in {
        "court_type": "VARCHAR(20) NOT NULL DEFAULT 'standard'",
        "social_max_players": "INTEGER",
        "social_start_time": "VARCHAR(5)",
        "social_end_time": "VARCHAR(5)",
        "social_date": "DATE",
        "social_ticket_price": "NUMERIC(10, 2)",
        "is_new_court": "BOOLEAN NOT NULL DEFAULT FALSE",
    }.items():
        if column not in court_request_columns:
            updates.append(
                f"ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS {column} {definition}"
            )

    for column, definition in {
        "court_type": "VARCHAR(20) NOT NULL DEFAULT 'standard'",
        "social_max_players": "INTEGER",
        "social_start_time": "VARCHAR(5)",
        "social_end_time": "VARCHAR(5)",
        "social_date": "DATE",
        "social_ticket_price": "NUMERIC(10, 2)",
    }.items():
        if column not in court_columns:
            updates.append(f"ALTER TABLE courts ADD COLUMN IF NOT EXISTS {column} {definition}")

    for column, definition in {
        "ticket_quantity": "INTEGER NOT NULL DEFAULT 1",
        "total_price": "NUMERIC(10, 2)",
        "payment_status": "VARCHAR(20) NOT NULL DEFAULT 'pending'",
        "qr_code_url": "VARCHAR",
    }.items():
        if column not in booking_participant_columns:
            updates.append(
                f"ALTER TABLE booking_participants ADD COLUMN IF NOT EXISTS {column} {definition}"
            )

    if updates:
        with engine.begin() as connection:
            for update in updates:
                connection.execute(text(update))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()