from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure imports work even if the script is run from outside backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models.notification import Notification

STREAK_NOTIFICATION_TYPES = (
    "friend_request_received",
    "friend_request_result",
    "booking_invite_received",
    "booking_invite_result",
)


def delete_streak_notifications(user_id: int | None = None, dry_run: bool = False) -> int:
    """Delete streak-related notifications. Optionally scope to a specific user."""
    db = SessionLocal()
    try:
        query = db.query(Notification).filter(Notification.type.in_(STREAK_NOTIFICATION_TYPES))
        if user_id is not None:
            query = query.filter(Notification.user_id == user_id)

        total = query.count()
        if total == 0:
            print("No streak notifications found.")
            return 0

        if dry_run:
            print(f"Dry run: {total} notification(s) would be deleted.")
            return total

        query.delete(synchronize_session=False)
        db.commit()

        print(f"Deleted {total} streak notification(s).")
        return total
    except Exception as exc:
        db.rollback()
        print(f"Delete failed: {exc}")
        raise
    finally:
        db.close()


def _confirm(user_id: int | None, dry_run: bool) -> bool:
    if dry_run:
        return True

    scope = f"for user_id={user_id}" if user_id is not None else "for ALL users"
    answer = input(
        f"Delete streak notifications {scope}? Type 'yes' to continue: "
    ).strip().lower()
    return answer == "yes"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete streak-related notifications (friend + booking invite notifications)."
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=None,
        help="Only delete streak notifications for this user ID",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show how many notifications would be deleted without deleting",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    if not _confirm(args.user_id, args.dry_run):
        print("Cancelled.")
        raise SystemExit(0)

    delete_streak_notifications(user_id=args.user_id, dry_run=args.dry_run)
