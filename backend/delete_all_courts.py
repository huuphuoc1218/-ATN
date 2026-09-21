from __future__ import annotations

import sys
from pathlib import Path

# Ensure imports work even if the script is run from outside backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models.court import Booking, BookingInvite, Court, IndividualCourt


def _delete_court_images() -> int:
    """Delete uploaded court images under uploads/courts except .gitkeep."""
    courts_dir = Path(__file__).resolve().parent / "uploads" / "courts"
    if not courts_dir.exists():
        return 0

    deleted = 0
    for image_file in courts_dir.iterdir():
        if image_file.is_file() and image_file.name != ".gitkeep":
            try:
                image_file.unlink()
                deleted += 1
            except Exception as exc:
                print(f"Could not delete image {image_file.name}: {exc}")
    return deleted


def delete_all_courts() -> tuple[int, int, int, int]:
    """Delete all bookings, individual courts, courts, and related uploaded images."""
    db = SessionLocal()
    try:
        invite_count = db.query(BookingInvite).count()
        db.query(BookingInvite).delete()

        bookings_count = db.query(Booking).count()
        db.query(Booking).delete()

        individual_count = db.query(IndividualCourt).count()
        db.query(IndividualCourt).delete()

        courts_count = db.query(Court).count()
        db.query(Court).delete()

        db.commit()

        image_count = _delete_court_images()

        print(f"Deleted booking invite(s): {invite_count}")
        print(f"Deleted booking(s): {bookings_count}")
        print(f"Deleted individual court(s): {individual_count}")
        print(f"Deleted court(s): {courts_count}")
        print(f"Deleted image file(s): {image_count}")

        return bookings_count, individual_count, courts_count, image_count
    except Exception as exc:
        db.rollback()
        print(f"Delete failed: {exc}")
        raise
    finally:
        db.close()


def _confirm() -> bool:
    answer = input(
        "Delete ALL courts and related data (bookings, individual courts, images)? Type 'yes' to continue: "
    ).strip().lower()
    return answer == "yes"


if __name__ == "__main__":
    if not _confirm():
        print("Cancelled.")
        raise SystemExit(0)

    delete_all_courts()
