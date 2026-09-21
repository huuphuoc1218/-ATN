from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class FriendRequestCreate(BaseModel):
    email: EmailStr


class FriendRequestAction(BaseModel):
    action: str  # accept or reject


class FriendUser(BaseModel):
    id: int
    full_name: str
    email: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class FriendItem(BaseModel):
    user: FriendUser
    since: datetime
    current_streak: int
    best_streak: int


class FriendListResponse(BaseModel):
    friends: List[FriendItem]


class FriendRequestCreateResponse(BaseModel):
    request_id: int
    message: str


class FriendRequestActionResponse(BaseModel):
    request_id: int
    status: str
    message: str
    responded_at: Optional[datetime] = None
