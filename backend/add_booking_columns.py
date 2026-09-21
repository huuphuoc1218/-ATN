from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

# Ensure imports work even if the script is run from outside backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal


BOOKING_COLUMNS = {
    "customer_name": "VARCHAR",
    "total_hours": "NUMERIC(4, 2)",
    "total_price": "NUMERIC(10, 2)",
    "customer_email": "VARCHAR",
    "payment_method": "VARCHAR",
    "payment_status": "VARCHAR",
    "booking_status": "VARCHAR",
    "qr_code_url": "VARCHAR",
    "bank_transaction_id": "VARCHAR",
    "payment_verified_at": "TIMESTAMP WITH TIME ZONE",
    "payment_note": "TEXT",
}


def add_booking_columns() -> None:
    db = SessionLocal()
    try:
        for column_name, sql_type in BOOKING_COLUMNS.items():
            db.execute(
                text(
                    f"ALTER TABLE bookings ADD COLUMN IF NOT EXISTS "
                    f"{column_name} {sql_type}"
                )
            )

        # Preserve existing legacy status values for the new booking status field.
        db.execute(
            text(
                "UPDATE bookings SET booking_status = status "
                "WHERE booking_status IS NULL AND status IS NOT NULL"
            )
        )
        db.commit()
        print("Booking columns ensured on bookings table.")
    except Exception as exc:
        db.rollback()
        print(f"Migration failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_booking_columns()
