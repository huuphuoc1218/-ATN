from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.notification import Notification, CourtRequest, AdvertisementRequest, AdvertisementClick
from app.schemas.notification import (
    NotificationCreate,
    CourtRequestCreate,
    CourtRequestUpdate,
    AdvertisementRequestCreate,
    AdvertisementRequestUpdate,
)
from typing import Dict, List, Optional
from datetime import datetime


# Notification CRUD
def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    """Create a new notification"""
    db_notification = Notification(**notification.model_dump())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Notification]:
    """Get all notifications for a user"""
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_unread_count(db: Session, user_id: int) -> int:
    """Get count of unread notifications for a user"""
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read.is_(False)
    ).count()


def mark_as_read(db: Session, notification_id: int) -> Optional[Notification]:
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: int):
    """Mark all notifications as read for a user"""
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read.is_(False)
    ).update({"is_read": True})
    db.commit()


# Court Request CRUD
def create_court_request(db: Session, request: CourtRequestCreate, owner_id: int) -> CourtRequest:
    """Create a new court registration request"""
    db_request = CourtRequest(
        **request.model_dump(),
        owner_id=owner_id,
        status="pending"
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def get_court_request(db: Session, request_id: int) -> Optional[CourtRequest]:
    """Get a court request by ID"""
    from app.models.user import User
    request = db.query(CourtRequest).filter(CourtRequest.id == request_id).first()
    if request:
        request.owner = db.query(User).filter(User.id == request.owner_id).first()
    return request


def get_all_court_requests(db: Session, status: Optional[str] = None) -> List[CourtRequest]:
    """Get all court requests, optionally filtered by status"""
    from app.models.user import User
    query = db.query(CourtRequest)
    if status:
        query = query.filter(CourtRequest.status == status)
    requests = query.order_by(CourtRequest.created_at.desc()).all()
    
    # Load owner info for each request
    for request in requests:
        request.owner = db.query(User).filter(User.id == request.owner_id).first()
    
    return requests


def get_owner_court_requests(db: Session, owner_id: int) -> List[CourtRequest]:
    """Get all court requests by a specific owner"""
    from app.models.user import User
    requests = db.query(CourtRequest).filter(
        CourtRequest.owner_id == owner_id
    ).order_by(CourtRequest.created_at.desc()).all()
    
    # Load owner info for each request
    for request in requests:
        request.owner = db.query(User).filter(User.id == request.owner_id).first()
    
    return requests


def update_court_request_status(
    db: Session, 
    request_id: int, 
    update: CourtRequestUpdate, 
    reviewer_id: int
) -> Optional[CourtRequest]:
    """Update court request status (approve/reject)"""
    request = db.query(CourtRequest).filter(CourtRequest.id == request_id).first()
    if request:
        request.status = update.status
        request.rejection_reason = update.rejection_reason
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.utcnow()
        db.commit()
        db.refresh(request)
    return request


def delete_court_request(db: Session, request_id: int) -> bool:
    """Delete a court request"""
    request = db.query(CourtRequest).filter(CourtRequest.id == request_id).first()
    if request:
        db.delete(request)
        db.commit()
        return True
    return False


# Advertisement Request CRUD
def create_advertisement_request(
    db: Session, request: AdvertisementRequestCreate, enterprise_id: int
) -> AdvertisementRequest:
    db_request = AdvertisementRequest(
        **request.model_dump(),
        enterprise_id=enterprise_id,
        status="pending",
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def get_advertisement_request(db: Session, request_id: int) -> Optional[AdvertisementRequest]:
    from app.models.user import User

    request = db.query(AdvertisementRequest).filter(AdvertisementRequest.id == request_id).first()
    if request:
        request.owner = db.query(User).filter(User.id == request.enterprise_id).first()
    return request


def get_all_advertisement_requests(
    db: Session, status: Optional[str] = None
) -> List[AdvertisementRequest]:
    from app.models.user import User

    query = db.query(AdvertisementRequest)
    if status:
        query = query.filter(AdvertisementRequest.status == status)
    requests = query.order_by(AdvertisementRequest.created_at.desc()).all()

    for request in requests:
        request.owner = db.query(User).filter(User.id == request.enterprise_id).first()

    return requests


def get_enterprise_advertisement_requests(
    db: Session, enterprise_id: int, status: Optional[str] = None
) -> List[AdvertisementRequest]:
    from app.models.user import User

    query = db.query(AdvertisementRequest).filter(AdvertisementRequest.enterprise_id == enterprise_id)
    if status:
        query = query.filter(AdvertisementRequest.status == status)
    requests = query.order_by(AdvertisementRequest.created_at.desc()).all()

    for request in requests:
        request.owner = db.query(User).filter(User.id == request.enterprise_id).first()

    return requests


def update_advertisement_request_status(
    db: Session,
    request_id: int,
    update: AdvertisementRequestUpdate,
    reviewer_id: int,
) -> Optional[AdvertisementRequest]:
    request = db.query(AdvertisementRequest).filter(AdvertisementRequest.id == request_id).first()
    if request:
        request.status = update.status
        request.rejection_reason = update.rejection_reason
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.utcnow()
        db.commit()
        db.refresh(request)
    return request


def delete_advertisement_request(db: Session, request_id: int) -> bool:
    request = db.query(AdvertisementRequest).filter(AdvertisementRequest.id == request_id).first()
    if request:
        # Click records reference the advertisement and must be removed first.
        db.execute(
            AdvertisementClick.__table__.delete().where(
                AdvertisementClick.advertisement_request_id == request_id
            )
        )
        db.delete(request)
        db.flush()
        db.commit()
        return True
    return False


def create_advertisement_click(
    db: Session,
    request_id: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AdvertisementClick:
    click = AdvertisementClick(
        advertisement_request_id=request_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(click)
    db.commit()
    db.refresh(click)
    return click


def get_click_counts_by_request_ids(db: Session, request_ids: List[int]) -> Dict[int, int]:
    if not request_ids:
        return {}

    rows = (
        db.query(
            AdvertisementClick.advertisement_request_id,
            func.count(AdvertisementClick.id).label("click_count"),
        )
        .filter(AdvertisementClick.advertisement_request_id.in_(request_ids))
        .group_by(AdvertisementClick.advertisement_request_id)
        .all()
    )

    return {row.advertisement_request_id: int(row.click_count) for row in rows}
