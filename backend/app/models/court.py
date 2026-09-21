from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    """Payment method options"""
    vietqr = "vietqr"  # VietQR bank transfer
    cash = "cash"      # Cash payment at venue


class PaymentStatus(str, enum.Enum):
    """Payment status tracking"""
    pending = "pending"      # Waiting for payment
    verifying = "verifying"  # Payment detected, verifying
    paid = "paid"           # Payment confirmed
    partial = "partial"      # Partial payment received
    failed = "failed"        # Payment failed/expired
    refunded = "refunded"    # Payment refunded


class BookingStatus(str, enum.Enum):
    """Booking status"""
    pending = "pending"      # Created, waiting payment
    confirmed = "confirmed"  # Payment confirmed
    active = "active"        # Currently active/in-use
    completed = "completed"  # Finished
    cancelled = "cancelled"  # Cancelled by user/owner


class Court(Base):
    """Main venue/court complex model"""
    __tablename__ = "courts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    ward = Column(String, nullable=False)
    city = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    court_quantity = Column(Integer, nullable=False, default=1)  # Number of individual courts
    opening_time = Column(String, nullable=False)  # Format: "HH:MM"
    closing_time = Column(String, nullable=False)  # Format: "HH:MM"
    facilities = Column(JSON, nullable=True)  # List of facility IDs
    contact_phone = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    images = Column(JSON, nullable=True)  # List of image URLs
    time_slots = Column(JSON, nullable=True)  # Pricing by time slots
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="courts")
    individual_courts = relationship("IndividualCourt", back_populates="court", cascade="all, delete-orphan")


class IndividualCourt(Base):
    """Individual court within a venue"""
    __tablename__ = "individual_courts"

    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "Sân 1", "Sân VIP A"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    court = relationship("Court", back_populates="individual_courts")
    bookings = relationship("Booking", back_populates="individual_court", cascade="all, delete-orphan")


class Booking(Base):
    """Booking for an individual court"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    individual_court_id = Column(Integer, ForeignKey("individual_courts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(String, nullable=False)  # Format: "HH:MM"
    end_time = Column(String, nullable=False)  # Format: "HH:MM"
    phone_number = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)  # Name of person who booked
    
    # Payment Information
    total_hours = Column(Numeric(4, 2), nullable=True)  # Total hours booked
    total_price = Column(Numeric(10, 2), nullable=True)  # Total amount
    customer_email = Column(String, nullable=True)  # Customer email
    
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.vietqr, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    booking_status = Column(SQLEnum(BookingStatus), default=BookingStatus.pending, nullable=False)
    
    # VietQR specific fields
    qr_code_url = Column(String, nullable=True)  # VietQR image URL
    bank_transaction_id = Column(String, nullable=True)  # Bank transaction reference
    payment_verified_at = Column(DateTime(timezone=True), nullable=True)  # When payment was verified
    payment_note = Column(Text, nullable=True)  # Payment notes/description
    
    # Legacy status field (deprecated, use booking_status instead)
    status = Column(String, default="pending", server_default="pending", nullable=False)  # pending, active, completed, cancelled
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    individual_court = relationship("IndividualCourt", back_populates="bookings")
    user = relationship("User", back_populates="bookings")


class BookingInvite(Base):
    """Single-use invitation code tied to a confirmed/active booking."""

    __tablename__ = "booking_invites"
    __table_args__ = (
        UniqueConstraint("code", name="uq_booking_invites_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, index=True)
    inviter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    invitee_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    code = Column(String(16), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, accepted, rejected
    responded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking")
    inviter = relationship("User", foreign_keys=[inviter_user_id])
    invitee = relationship("User", foreign_keys=[invitee_user_id])
