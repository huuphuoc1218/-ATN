from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

# Ensure imports work even if the script is run from outside backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal


def add_avatar_url_column() -> None:
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR"))
        db.commit()
        print("avatar_url column ensured on users table.")
    except Exception as exc:
        db.rollback()
        print(f"Migration failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_avatar_url_column()
