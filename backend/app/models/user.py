from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    user = "user"
    enterprise = "enterprise"
    owner = "owner"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) 
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.user, nullable=False)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Bank Account Information (for owners to receive payments)
    bank_account_number = Column(String, nullable=True)  # Số tài khoản
    bank_account_name = Column(String, nullable=True)    # Tên chủ tài khoản
    bank_name = Column(String, nullable=True)            # Tên ngân hàng (e.g., "Vietcombank")
    bank_code = Column(String, nullable=True)            # Mã ngân hàng (e.g., "970436" for VCB)

    # Relationships
    courts = relationship("Court", back_populates="owner")
    bookings = relationship("Booking", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    court_requests = relationship("CourtRequest", foreign_keys="CourtRequest.owner_id", back_populates="owner")
    advertisement_requests = relationship(
        "AdvertisementRequest",
        foreign_keys="AdvertisementRequest.enterprise_id",
        back_populates="enterprise",
    )
    sent_friend_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
    )
    received_friend_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
    )
    friendships_as_low = relationship(
        "Friendship",
        foreign_keys="Friendship.user_low_id",
    )
    friendships_as_high = relationship(
        "Friendship",
        foreign_keys="Friendship.user_high_id",
    )