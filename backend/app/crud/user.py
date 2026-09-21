from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import get_password_hash
from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Tìm user theo email
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Tìm user theo ID
    """
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_data: UserRegister) -> User:
    """
    Tạo user mới
    
    Args:
        db: Database session
        user_data: UserRegister schema object
    
    Returns:
        User object đã tạo
    """
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Tạo user object
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role=user_data.role,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user_data: dict) -> Optional[User]:
    """
    Cập nhật thông tin user
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # Hash password if it's being updated
    if 'password' in user_data:
        user_data['hashed_password'] = get_password_hash(user_data['password'])
        del user_data['password']
    
    for key, value in user_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Xóa user và các dữ liệu liên quan
    """
    from app.models import Notification, CourtRequest, AdvertisementRequest, FriendRequest, Friendship
    from app.models.court import Court, IndividualCourt, Booking
    
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    # Delete related notifications first
    db.query(Notification).filter(Notification.user_id == user_id).delete()

    # Delete friend requests and friendships
    db.query(FriendRequest).filter(
        (FriendRequest.sender_id == user_id) | (FriendRequest.receiver_id == user_id)
    ).delete(synchronize_session=False)
    db.query(Friendship).filter(
        (Friendship.user_low_id == user_id) | (Friendship.user_high_id == user_id)
    ).delete(synchronize_session=False)
    
    # Delete related court requests
    db.query(CourtRequest).filter(CourtRequest.owner_id == user_id).delete()

    # Delete related advertisement requests (enterprise)
    db.query(AdvertisementRequest).filter(AdvertisementRequest.enterprise_id == user_id).delete()
    
    # Delete related bookings made by this user
    db.query(Booking).filter(Booking.user_id == user_id).delete()
    
    # If user is owner, delete all their courts (cascade will handle individual_courts and bookings)
    if db_user.role == 'owner':
        # Get all courts owned by this user
        courts = db.query(Court).filter(Court.owner_id == user_id).all()
        for court in courts:
            # Delete individual courts and their bookings
            db.query(IndividualCourt).filter(IndividualCourt.court_id == court.id).delete()
            # Delete the court itself
            db.delete(court)
    
    # Delete the user
    db.delete(db_user)
    db.commit()
    
    return True

def get_users_by_role(db: Session, role: str):
    """
    Get all users by role
    """
    return db.query(User).filter(User.role == role).all()