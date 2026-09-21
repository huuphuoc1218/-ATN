from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class CourtRequest(Base):
    __tablename__ = "court_requests"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Court information
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    ward = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    court_quantity = Column(Integer, nullable=False)
    opening_time = Column(String(10), nullable=False)
    closing_time = Column(String(10), nullable=False)
    facilities = Column(JSON, nullable=True)
    contact_phone = Column(String(20), nullable=False)
    contact_email = Column(String(255), nullable=True)
    time_slots = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)  # List of image URLs
    
    # Request status
    status = Column(String(50), default="pending")  # 'pending', 'approved', 'rejected'
    admin_note = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Court ID after approval
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="court_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    court = relationship("Court", backref="request")
