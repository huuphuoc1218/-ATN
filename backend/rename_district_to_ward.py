from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

# Ensure imports work even if the script is run from outside backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal


def rename_district_to_ward() -> None:
    db = SessionLocal()
    try:
        # Check if column exists before attempting to rename
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='courts' AND column_name='district'"
        )).fetchone()
        
        if result:
            # Rename column in courts table
            db.execute(text("ALTER TABLE courts RENAME COLUMN district TO ward"))
            print("✓ Renamed 'district' to 'ward' in courts table")
        else:
            print("✓ Column 'ward' already exists in courts table")
        
        # Check and rename in court_requests table
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='court_requests' AND column_name='district'"
        )).fetchone()
        
        if result:
            # Rename column in court_requests table
            db.execute(text("ALTER TABLE court_requests RENAME COLUMN district TO ward"))
            print("✓ Renamed 'district' to 'ward' in court_requests table")
        else:
            print("✓ Column 'ward' already exists in court_requests table")
        
        db.commit()
        print("\n✓ Migration completed successfully!")
    except Exception as exc:
        db.rollback()
        print(f"✗ Migration failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    rename_district_to_ward()
