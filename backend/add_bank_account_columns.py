from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

# Ensure imports work even if the script is run from outside backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal


BANK_COLUMNS = (
    "bank_account_number",
    "bank_account_name",
    "bank_name",
    "bank_code",
)


def add_bank_account_columns() -> None:
    db = SessionLocal()
    try:
        for column_name in BANK_COLUMNS:
            db.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} VARCHAR"))
        db.commit()
        print("Bank account columns ensured on users table.")
    except Exception as exc:
        db.rollback()
        print(f"Migration failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_bank_account_columns()
