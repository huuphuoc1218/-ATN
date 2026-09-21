from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)

    sender = relationship("User", foreign_keys=[sender_id], overlaps="sent_friend_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], overlaps="received_friend_requests")


class Friendship(Base):
    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("user_low_id", "user_high_id", name="uq_friendships_pair"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_low_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_high_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    current_streak = Column(Integer, nullable=False, default=0)
    best_streak = Column(Integer, nullable=False, default=0)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_low = relationship("User", foreign_keys=[user_low_id], overlaps="friendships_as_low")
    user_high = relationship("User", foreign_keys=[user_high_id], overlaps="friendships_as_high")
