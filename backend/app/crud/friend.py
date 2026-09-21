from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.models.friend import FriendRequest, Friendship
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.crud.notification import create_notification


STREAK_WARNING_TYPE = "friend_streak_warning"
STREAK_WARNING_DAYS = 5
STREAK_EXPIRY_DAYS = 7


def _normalize_pair(user_a_id: int, user_b_id: int) -> Tuple[int, int]:
    return (user_a_id, user_b_id) if user_a_id < user_b_id else (user_b_id, user_a_id)


def _user_role_value(user: User) -> str:
    role = getattr(user, "role", None)
    return getattr(role, "value", str(role))


def _to_naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def _apply_streak_expiry(friendship: Friendship, now_utc: datetime) -> bool:
    """Reset expired streaks and update best_streak when needed."""
    last_activity = _to_naive_utc(friendship.last_activity_at)
    if not last_activity:
        return False

    if now_utc - last_activity < timedelta(days=STREAK_EXPIRY_DAYS):
        return False

    current_streak = friendship.current_streak or 0
    best_streak = friendship.best_streak or 0
    has_changes = False

    if current_streak > best_streak:
        friendship.best_streak = current_streak
        has_changes = True

    if current_streak != 0:
        friendship.current_streak = 0
        has_changes = True

    return has_changes


def touch_friendship_invite_activity(
    db: Session,
    user_a_id: int,
    user_b_id: int,
    activity_time: Optional[datetime] = None,
) -> Optional[Friendship]:
    """Update the last invite activity timestamp for a friendship pair."""
    friendship = get_friendship(db, user_a_id, user_b_id)
    if not friendship:
        return None

    now_utc = _to_naive_utc(activity_time) or datetime.utcnow()
    _apply_streak_expiry(friendship, now_utc)
    friendship.last_activity_at = now_utc
    db.flush()
    return friendship


def _create_streak_warning_notifications(
    db: Session,
    friendship: Friendship,
    warning_anchor: datetime,
):
    user_low = db.query(User).filter(User.id == friendship.user_low_id).first()
    user_high = db.query(User).filter(User.id == friendship.user_high_id).first()
    if not user_low or not user_high:
        return

    pairs = [
        (user_low.id, user_high.full_name),
        (user_high.id, user_low.full_name),
    ]

    for recipient_id, friend_name in pairs:
        exists = (
            db.query(Notification)
            .filter(
                Notification.user_id == recipient_id,
                Notification.type == STREAK_WARNING_TYPE,
                Notification.related_id == friendship.id,
                Notification.created_at >= warning_anchor,
            )
            .first()
        )
        if exists:
            continue

        create_notification(
            db,
            NotificationCreate(
                user_id=recipient_id,
                title="Streak ending soon",
                message=f"Your streak with {friend_name} is about to end. Create an invite now to keep it alive.",
                type=STREAK_WARNING_TYPE,
                related_id=friendship.id,
            ),
        )


def refresh_friendship_streak_state(db: Session, friendship: Friendship) -> bool:
    """Apply streak expiry rules and trigger day-5 warning notifications."""
    now_utc = datetime.utcnow()
    has_changes = _apply_streak_expiry(friendship, now_utc)

    last_activity_raw = friendship.last_activity_at
    last_activity = _to_naive_utc(last_activity_raw)
    if not last_activity:
        return has_changes

    elapsed = now_utc - last_activity
    if timedelta(days=STREAK_WARNING_DAYS) <= elapsed < timedelta(days=STREAK_EXPIRY_DAYS):
        _create_streak_warning_notifications(db, friendship, last_activity_raw or now_utc)

    return has_changes


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    normalized_email = email.strip().lower()
    return db.query(User).filter(func.lower(User.email) == normalized_email).first()


def get_friendship(db: Session, user_a_id: int, user_b_id: int) -> Optional[Friendship]:
    low_id, high_id = _normalize_pair(user_a_id, user_b_id)
    return (
        db.query(Friendship)
        .filter(Friendship.user_low_id == low_id, Friendship.user_high_id == high_id)
        .first()
    )


def get_pending_request_between(db: Session, sender_id: int, receiver_id: int) -> Optional[FriendRequest]:
    return (
        db.query(FriendRequest)
        .filter(
            FriendRequest.sender_id == sender_id,
            FriendRequest.receiver_id == receiver_id,
            FriendRequest.status == "pending",
        )
        .first()
    )


def create_friend_request(db: Session, sender: User, receiver_email: str) -> FriendRequest:
    receiver = get_user_by_email(db, receiver_email)
    if not receiver or not receiver.is_active or _user_role_value(receiver) != "user":
        raise ValueError("User not found for this email")

    if sender.id == receiver.id:
        raise ValueError("You cannot add yourself as a friend")

    if get_friendship(db, sender.id, receiver.id):
        raise ValueError("You are already friends")

    if get_pending_request_between(db, sender.id, receiver.id):
        raise ValueError("You have already sent a friend request")

    if get_pending_request_between(db, receiver.id, sender.id):
        raise ValueError("This user already sent you a request. Please check your notifications")

    friend_request = FriendRequest(
        sender_id=sender.id,
        receiver_id=receiver.id,
        status="pending",
    )
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)

    create_notification(
        db,
        NotificationCreate(
            user_id=receiver.id,
            title="New Friend Request",
            message=f"{sender.full_name} sent you a friend request",
            type="friend_request_received",
            related_id=friend_request.id,
        ),
    )

    return friend_request


def _create_friendship_if_needed(db: Session, user_a_id: int, user_b_id: int) -> Friendship:
    friendship = get_friendship(db, user_a_id, user_b_id)
    if friendship:
        return friendship

    low_id, high_id = _normalize_pair(user_a_id, user_b_id)
    friendship = Friendship(
        user_low_id=low_id,
        user_high_id=high_id,
        current_streak=0,
        best_streak=0,
        last_activity_at=None,
    )
    db.add(friendship)
    db.flush()
    return friendship


def respond_friend_request(db: Session, request_id: int, receiver: User, action: str) -> FriendRequest:
    friend_request = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id,
            FriendRequest.receiver_id == receiver.id,
            FriendRequest.status == "pending",
        )
        .first()
    )
    if not friend_request:
        raise ValueError("No valid friend request found")

    sender = db.query(User).filter(User.id == friend_request.sender_id).first()
    if not sender:
        raise ValueError("Sender not found")

    normalized_action = action.strip().lower()
    if normalized_action not in {"accept", "reject"}:
        raise ValueError("Invalid action")

    now = datetime.utcnow()
    if normalized_action == "accept":
        friend_request.status = "accepted"
        _create_friendship_if_needed(db, sender.id, receiver.id)
        sender_title = "Friend Request Accepted"
        sender_message = f"{receiver.full_name} accepted your friend request"
    else:
        friend_request.status = "rejected"
        sender_title = "Friend Request Rejected"
        sender_message = f"{receiver.full_name} rejected your friend request"

    friend_request.responded_at = now

    create_notification(
        db,
        NotificationCreate(
            user_id=sender.id,
            title=sender_title,
            message=sender_message,
            type="friend_request_result",
            related_id=friend_request.id,
        ),
    )

    db.commit()
    db.refresh(friend_request)
    return friend_request


def list_friends(db: Session, user_id: int) -> List[Friendship]:
    return (
        db.query(Friendship)
        .filter(or_(Friendship.user_low_id == user_id, Friendship.user_high_id == user_id))
        .order_by(Friendship.created_at.desc())
        .all()
    )


def resolve_friend_user(db: Session, friendship: Friendship, current_user_id: int) -> User:
    friend_id = friendship.user_high_id if friendship.user_low_id == current_user_id else friendship.user_low_id
    return db.query(User).filter(User.id == friend_id).first()
