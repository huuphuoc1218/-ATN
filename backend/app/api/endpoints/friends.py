from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.friend import (
    FriendRequestCreate,
    FriendRequestCreateResponse,
    FriendRequestAction,
    FriendRequestActionResponse,
    FriendListResponse,
)
from app.crud import friend as friend_crud


router = APIRouter()


def _require_user_role(current_user: User):
    role = getattr(current_user.role, "value", str(current_user.role))
    if role != "user":
        raise HTTPException(status_code=403, detail="Only user accounts can use friend features")


@router.post("/requests", response_model=FriendRequestCreateResponse, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    payload: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_user_role(current_user)

    try:
        friend_request = friend_crud.create_friend_request(db, current_user, payload.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "request_id": friend_request.id,
        "message": "Friend request sent successfully",
    }


@router.post("/requests/{request_id}/respond", response_model=FriendRequestActionResponse)
async def respond_friend_request(
    request_id: int,
    payload: FriendRequestAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_user_role(current_user)

    try:
        friend_request = friend_crud.respond_friend_request(db, request_id, current_user, payload.action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.type == "friend_request_received",
        Notification.related_id == request_id,
        Notification.is_read.is_(False),
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()

    return {
        "request_id": friend_request.id,
        "status": friend_request.status,
        "message": "Friend request accepted" if friend_request.status == "accepted" else "Friend request rejected",
        "responded_at": friend_request.responded_at,
    }


@router.get("/me", response_model=FriendListResponse)
async def get_my_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_user_role(current_user)

    friendships = friend_crud.list_friends(db, current_user.id)
    has_streak_updates = False
    for friendship in friendships:
        if friend_crud.refresh_friendship_streak_state(db, friendship):
            has_streak_updates = True

    if has_streak_updates:
        db.commit()

    items = []
    for friendship in friendships:
        friend_user = friend_crud.resolve_friend_user(db, friendship, current_user.id)
        if not friend_user:
            continue
        items.append(
            {
                "user": friend_user,
                "since": friendship.created_at,
                "current_streak": friendship.current_streak,
                "best_streak": friendship.best_streak,
            }
        )

    return {"friends": items}
