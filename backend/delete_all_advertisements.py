from __future__ import annotations

import sys
from pathlib import Path

# Ensure imports work even if the script is run from outside backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models import AdvertisementClick, AdvertisementRequest


def _delete_advertisement_images() -> int:
    """Delete uploaded advertisement images under uploads/advertisements except .gitkeep."""
    ads_dir = Path(__file__).resolve().parent / "uploads" / "advertisements"
    if not ads_dir.exists():
        return 0

    deleted = 0
    for image_file in ads_dir.iterdir():
        if image_file.is_file() and image_file.name != ".gitkeep":
            try:
                image_file.unlink()
                deleted += 1
            except Exception as exc:
                print(f"Could not delete image {image_file.name}: {exc}")
    return deleted


def delete_all_advertisements() -> tuple[int, int, int]:
    """Delete all advertisement clicks, advertisement requests, and related image files."""
    db = SessionLocal()
    try:
        clicks_count = db.query(AdvertisementClick).count()
        db.query(AdvertisementClick).delete()

        ads_count = db.query(AdvertisementRequest).count()
        db.query(AdvertisementRequest).delete()

        db.commit()

        image_count = _delete_advertisement_images()

        print(f"Deleted advertisement click(s): {clicks_count}")
        print(f"Deleted advertisement request(s): {ads_count}")
        print(f"Deleted advertisement image file(s): {image_count}")

        return clicks_count, ads_count, image_count
    except Exception as exc:
        db.rollback()
        print(f"Delete failed: {exc}")
        raise
    finally:
        db.close()


def _confirm() -> bool:
    answer = input(
        "Delete ALL advertisements and related data (click history, uploaded images)? Type 'yes' to continue: "
    ).strip().lower()
    return answer == "yes"


if __name__ == "__main__":
    if not _confirm():
        print("Cancelled.")
        raise SystemExit(0)

    delete_all_advertisements()
