"""Add social court fields and the booking participant table to an existing database.

Run from the backend directory:
    python add_social_court_columns.py
"""
from sqlalchemy import text

from app.core.database import Base, engine
from app.models.court import BookingParticipant


with engine.begin() as connection:
    connection.execute(text(
        "ALTER TABLE courts ADD COLUMN IF NOT EXISTS court_type VARCHAR(20) NOT NULL DEFAULT 'standard'"
    ))
    connection.execute(text(
        "ALTER TABLE courts ADD COLUMN IF NOT EXISTS social_max_players INTEGER"
    ))
    connection.execute(text(
        "ALTER TABLE courts ADD COLUMN IF NOT EXISTS social_start_time VARCHAR(5)"
    ))
    connection.execute(text(
        "ALTER TABLE courts ADD COLUMN IF NOT EXISTS social_end_time VARCHAR(5)"
    ))
    connection.execute(text(
        "ALTER TABLE courts ADD COLUMN IF NOT EXISTS social_date DATE"
    ))
    connection.execute(text(
        "ALTER TABLE courts ADD COLUMN IF NOT EXISTS social_ticket_price NUMERIC(10, 2)"
    ))
    connection.execute(text(
        "ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS court_type VARCHAR(20) NOT NULL DEFAULT 'standard'"
    ))
    connection.execute(text(
        "ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS social_max_players INTEGER"
    ))
    connection.execute(text(
        "ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS social_start_time VARCHAR(5)"
    ))
    connection.execute(text(
        "ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS social_end_time VARCHAR(5)"
    ))
    connection.execute(text(
        "ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS social_date DATE"
    ))
    connection.execute(text(
        "ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS social_ticket_price NUMERIC(10, 2)"
    ))
    connection.execute(text(
        "ALTER TABLE court_requests ADD COLUMN IF NOT EXISTS is_new_court BOOLEAN NOT NULL DEFAULT FALSE"
    ))
    connection.execute(text(
        "ALTER TABLE booking_participants ADD COLUMN IF NOT EXISTS ticket_quantity INTEGER NOT NULL DEFAULT 1"
    ))
    connection.execute(text(
        "ALTER TABLE booking_participants ADD COLUMN IF NOT EXISTS total_price NUMERIC(10, 2)"
    ))
    connection.execute(text(
        "ALTER TABLE booking_participants ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'"
    ))
    connection.execute(text(
        "ALTER TABLE booking_participants ADD COLUMN IF NOT EXISTS qr_code_url VARCHAR"
    ))

BookingParticipant.__table__.create(bind=engine, checkfirst=True)
print("Social court schema is ready.")
