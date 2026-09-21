from __future__ import annotations

import sys
from pathlib import Path

# Ensure imports work even if the script is run from outside backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models import CourtRequest


def delete_all_requests() -> int:
    """Delete all rows in court_requests table and return deleted count."""
    db = SessionLocal()
    try:
        total = db.query(CourtRequest).count()
        if total == 0:
            print("No requests to delete.")
            return 0

        db.query(CourtRequest).delete()
        db.commit()

        print(f"Deleted {total} request(s).")
        return total
    except Exception as exc:
        db.rollback()
        print(f"Delete failed: {exc}")
        raise
    finally:
        db.close()


def _confirm() -> bool:
    answer = input("Delete ALL court requests? Type 'yes' to continue: ").strip().lower()
    return answer == "yes"


if __name__ == "__main__":
    if not _confirm():
        print("Cancelled.")
        raise SystemExit(0)

    delete_all_requests()
