from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Notification Schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    type: str
    related_id: Optional[int] = None


class NotificationCreate(NotificationBase):
    user_id: int


class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Court Request Schemas
class CourtRequestBase(BaseModel):
    name: str
    address: str
    ward: str
    city: str
    description: Optional[str] = None
    court_quantity: int
    opening_time: str
    closing_time: str
    facilities: Optional[str] = None
    contact_phone: str
    contact_email: Optional[str] = None
    images: Optional[str] = None
    time_slots: Optional[str] = None


class CourtRequestCreate(CourtRequestBase):
    pass


class CourtRequestUpdate(BaseModel):
    status: str  # approved, rejected
    rejection_reason: Optional[str] = None


class OwnerInfo(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True


class CourtRequestChangeDetail(BaseModel):
    field: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class CourtRequest(CourtRequestBase):
    id: int
    owner_id: int
    submission_type: str = "create"  # create, update
    changed_fields: List[str] = []
    changed_details: List[CourtRequestChangeDetail] = []
    status: str
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: Optional[OwnerInfo] = None

    class Config:
        from_attributes = True


# Advertisement Request Schemas
class AdvertisementRequestBase(BaseModel):
    name: str
    description: str
    detail_url: str
    image_url: str


class AdvertisementRequestCreate(AdvertisementRequestBase):
    pass


class AdvertisementRequestUpdate(BaseModel):
    status: str  # approved, rejected
    rejection_reason: Optional[str] = None


class AdvertisementRequest(AdvertisementRequestBase):
    id: int
    enterprise_id: int
    status: str
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    click_count: int = 0
    owner: Optional[OwnerInfo] = None

    class Config:
        from_attributes = True
