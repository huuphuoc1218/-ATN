from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import Optional, List
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from app.models.court import Court, IndividualCourt, Booking
from app.schemas.court import CourtCreate, CourtUpdate, IndividualCourtUpdate, BookingCreate, BookingUpdate


try:
    LOCAL_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")
except ZoneInfoNotFoundError:
    LOCAL_TIMEZONE = ZoneInfo("UTC")


def normalize_booking_date(booking_date):
    """Convert incoming datetime/date to local calendar date for booking comparisons."""
    if isinstance(booking_date, datetime):
        if booking_date.tzinfo is not None:
            return booking_date.astimezone(LOCAL_TIMEZONE).date()
        return booking_date.date()

    if hasattr(booking_date, "date"):
        return booking_date.date()

    return booking_date


def calculate_multi_tier_price(start_time: str, end_time: str, time_slots: list) -> float:
    """
    Calculate price for multi-tier time slots.
    
    Iterate through 30-minute intervals and sum up prices for each interval
    that falls into a time slot tier. This matches the frontend calculation.
    """
    if not time_slots:
        return 0.0
    
    start_dt = datetime.strptime(start_time, "%H:%M")
    end_dt = datetime.strptime(end_time, "%H:%M")
    
    total_price = 0.0
    current_time = start_dt
    
    # Iterate through 30-minute intervals (0.5 hour each)
    while current_time < end_dt:
        next_time = current_time + timedelta(minutes=30)
        
        # Find which time_slot this interval belongs to
        for slot in time_slots:
            slot_start_str = slot.get("start_time", "")
            slot_end_str = slot.get("end_time", "")
            slot_price = slot.get("price", 0)
            
            slot_start = datetime.strptime(slot_start_str, "%H:%M")
            slot_end = datetime.strptime(slot_end_str, "%H:%M")
            
            # Check if current interval starts within this slot
            if current_time >= slot_start and current_time < slot_end:
                # Add price for this 30-minute interval (0.5 hour)
                total_price += slot_price * 0.5
                break
        
        current_time = next_time
    
    return total_price

# Court CRUD
def get_court(db: Session, court_id: int) -> Optional[Court]:
    """Get a court by ID"""
    return db.query(Court).filter(Court.id == court_id).first()


def get_courts(db: Session, skip: int = 0, limit: int = 100) -> List[Court]:
    """Get all courts"""
    return db.query(Court).offset(skip).limit(limit).all()


def get_courts_by_owner(db: Session, owner_id: int) -> List[Court]:
    """Get all courts owned by a specific owner"""
    return db.query(Court).filter(Court.owner_id == owner_id).all()


def create_court(db: Session, court: CourtCreate, owner_id: int, images: Optional[List[str]] = None) -> Court:
    """Create a new court and auto-generate individual courts based on quantity"""
    # Convert time_slots to dict format for JSON storage
    time_slots_dict = [slot.model_dump() for slot in court.time_slots] if court.time_slots else []
    
    db_court = Court(
        owner_id=owner_id,
        name=court.name,
        address=court.address,
        ward=court.ward,
        city=court.city,
        description=court.description,
        court_quantity=court.court_quantity,
        opening_time=court.opening_time,
        closing_time=court.closing_time,
        facilities=court.facilities,
        contact_phone=court.contact_phone,
        contact_email=court.contact_email,
        images=images or [],
        time_slots=time_slots_dict,
    )
    db.add(db_court)
    db.commit()
    db.refresh(db_court)
    
    # Auto-generate individual courts based on quantity
    for i in range(1, court.court_quantity + 1):
        individual_court = IndividualCourt(
            court_id=db_court.id,
            name=f"Sân {i}"
        )
        db.add(individual_court)
    
    db.commit()
    db.refresh(db_court)
    
    return db_court


def update_court(db: Session, court_id: int, court_update: CourtUpdate) -> Optional[Court]:
    """Update a court"""
    db_court = get_court(db, court_id)
    if not db_court:
        return None
    
    update_data = court_update.model_dump(exclude_unset=True)
    
    # Convert time_slots if present (time_slots are already dicts from model_dump)
    if "time_slots" in update_data and update_data["time_slots"]:
        # time_slots are already in dict format, no need to convert
        pass
    
    for field, value in update_data.items():
        setattr(db_court, field, value)
    
    # If court_quantity changed, adjust individual courts
    if "court_quantity" in update_data:
        current_count = len(db_court.individual_courts)
        new_count = update_data["court_quantity"]
        
        if new_count > current_count:
            # Add more courts
            for i in range(current_count + 1, new_count + 1):
                individual_court = IndividualCourt(
                    court_id=court_id,
                    name=f"Sân {i}"
                )
                db.add(individual_court)
        elif new_count < current_count:
            # Remove excess courts (only if they have no bookings)
            courts_to_remove = db.query(IndividualCourt).filter(
                IndividualCourt.court_id == court_id
            ).order_by(IndividualCourt.id.desc()).limit(current_count - new_count).all()
            
            for court in courts_to_remove:
                if not court.bookings:
                    db.delete(court)
    
    db.commit()
    db.refresh(db_court)
    return db_court


def delete_court(db: Session, court_id: int) -> bool:
    """Delete a court"""
    db_court = get_court(db, court_id)
    if not db_court:
        return False
    
    db.delete(db_court)
    db.commit()
    return True


# Individual Court CRUD
def get_individual_court(db: Session, individual_court_id: int) -> Optional[IndividualCourt]:
    """Get an individual court by ID"""
    return db.query(IndividualCourt).filter(IndividualCourt.id == individual_court_id).first()


def get_individual_courts_by_court(db: Session, court_id: int) -> List[IndividualCourt]:
    """Get all individual courts for a specific court"""
    return (
        db.query(IndividualCourt)
        .filter(IndividualCourt.court_id == court_id)
        .options(joinedload(IndividualCourt.bookings))
        .order_by(IndividualCourt.id.asc())
        .all()
    )


def update_individual_court(db: Session, individual_court_id: int, individual_court_update: IndividualCourtUpdate) -> Optional[IndividualCourt]:
    """Update an individual court"""
    db_individual_court = get_individual_court(db, individual_court_id)
    if not db_individual_court:
        return None
    
    update_data = individual_court_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_individual_court, field, value)
    
    db.commit()
    db.refresh(db_individual_court)
    return db_individual_court


# Booking CRUD
def get_booking(db: Session, booking_id: int) -> Optional[Booking]:
    """Get a booking by ID"""
    return db.query(Booking).filter(Booking.id == booking_id).first()


def get_bookings_by_user(db: Session, user_id: int) -> List[Booking]:
    """Get all bookings for a user"""
    return db.query(Booking).filter(Booking.user_id == user_id).all()


def get_bookings_by_individual_court(db: Session, individual_court_id: int) -> List[Booking]:
    """Get all bookings for an individual court"""
    return db.query(Booking).filter(Booking.individual_court_id == individual_court_id).all()


def check_booking_overlap(db: Session, individual_court_id: int, booking_date, start_time: str, end_time: str, exclude_booking_id: int = None) -> bool:
    """Check if a booking overlaps with existing bookings"""
    
    # Get the date only (without time)
    booking_date_only = normalize_booking_date(booking_date)
    
    # Query all blocking bookings for the same court.
    # Pending/active/confirmed all block the slot.
    query = db.query(Booking).filter(
        Booking.individual_court_id == individual_court_id,
        Booking.status.in_(["pending", "active", "confirmed"])
    )
    
    # Exclude current booking if updating
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    bookings = query.all()
    
    # Filter by date (comparing date only)
    bookings = [b for b in bookings if b.booking_date.date() == booking_date_only]
    
    # Check time overlap
    for existing_booking in bookings:
        # Time overlap if:
        # new_start < existing_end AND new_end > existing_start
        if start_time < existing_booking.end_time and end_time > existing_booking.start_time:
            return True
    
    return False


def find_available_courts(db: Session, court_id: int, booking_date, start_time: str, end_time: str, exclude_court_id: int = None) -> List[IndividualCourt]:
    """Find all individual courts in the same venue that are available for the given time slot"""
    
    # Get the date only (without time)
    booking_date_only = normalize_booking_date(booking_date)
    
    # Get all individual courts for this venue
    all_courts = get_individual_courts_by_court(db, court_id)
    
    # Filter out the excluded court if provided
    if exclude_court_id:
        all_courts = [c for c in all_courts if c.id != exclude_court_id]
    
    available_courts = []

    for court in all_courts:
        if not court.is_active:
            continue

        conflict_query = db.query(Booking).filter(
            Booking.individual_court_id == court.id,
            func.date(Booking.booking_date) == booking_date_only,
            Booking.start_time < end_time,
            Booking.end_time > start_time,
            or_(
                Booking.status.in_(["pending", "active", "confirmed"]),
                Booking.booking_status.in_(["pending", "active", "confirmed"]),
            ),
        )

        if not conflict_query.first():
            available_courts.append(court)
    
    return available_courts


def create_booking(db: Session, booking: BookingCreate, user_id: int) -> Booking:
    """Create a new booking with payment info"""
    from datetime import datetime as dt
    from app.models.court import PaymentMethod, PaymentStatus, BookingStatus
    from app.core.vietqr_service import VietQRService
    from app.crud.user import get_user_by_id
    
    # Resolve parent court from requested individual court
    requested_court = get_individual_court(db, booking.individual_court_id)
    if not requested_court:
        raise ValueError("Không tìm thấy sân")
    
    parent_court = get_court(db, requested_court.court_id)
    if not parent_court:
        raise ValueError("Không tìm thấy thông tin sân")

    # Always allocate from the first available individual court to the last.
    available_courts = find_available_courts(
        db,
        parent_court.id,
        booking.booking_date,
        booking.start_time,
        booking.end_time,
    )

    if not available_courts:
        raise ValueError("Tất cả sân đã có lịch đặt trong khung giờ này. Vui lòng chọn khung giờ khác.")

    allocated_court = available_courts[0]
    
    # Calculate price using multi-tier pricing (same as payment preview endpoint)
    total_price = calculate_multi_tier_price(
        booking.start_time,
        booking.end_time,
        parent_court.time_slots or []
    )
    
    # Calculate total hours
    start_dt = dt.strptime(booking.start_time, "%H:%M")
    end_dt = dt.strptime(booking.end_time, "%H:%M")
    total_hours = (end_dt - start_dt).seconds / 3600
    
    booking_date_only = normalize_booking_date(booking.booking_date)
    booking_datetime = datetime.combine(booking_date_only, datetime.min.time())

    # Create booking
    db_booking = Booking(
        individual_court_id=allocated_court.id,
        user_id=user_id,
        booking_date=booking_datetime,
        start_time=booking.start_time,
        end_time=booking.end_time,
        phone_number=booking.phone_number,
        customer_name=booking.customer_name,
        customer_email=booking.customer_email,
        total_hours=total_hours,
        total_price=total_price,
        payment_method=PaymentMethod.vietqr if booking.payment_method == "vietqr" else PaymentMethod.cash,
        payment_status=PaymentStatus.pending,
        booking_status=BookingStatus.pending,
        status="pending"  # Legacy field
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    # Generate VietQR code if payment method is vietqr
    if booking.payment_method == "vietqr":
        owner = get_user_by_id(db, parent_court.owner_id)
        if owner and owner.bank_account_number and owner.bank_code:
            vietqr_service = VietQRService()
            payment_content = f"BOOKING{db_booking.id}"
            
            qr_url = vietqr_service.generate_qr_url(
                bank_code=owner.bank_code,
                account_number=owner.bank_account_number,
                amount=int(total_price),
                description=payment_content,
                account_name=owner.bank_account_name
            )
            
            db_booking.qr_code_url = qr_url
            db_booking.payment_status = PaymentStatus.pending
            db.commit()
            db.refresh(db_booking)
    
    # Cash payments are automatically confirmed
    elif booking.payment_method == "cash":
        db_booking.payment_status = PaymentStatus.paid
        db_booking.booking_status = BookingStatus.confirmed
        db_booking.status = "confirmed"
        db.commit()
        db.refresh(db_booking)
    
    return db_booking


def update_booking(db: Session, booking_id: int, booking_update: BookingUpdate) -> Optional[Booking]:
    """Update a booking"""
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return None
    
    update_data = booking_update.model_dump(exclude_unset=True)
    
    # Check for booking overlap if time or date is being updated
    if any(key in update_data for key in ['booking_date', 'start_time', 'end_time']):
        # Use updated values or existing values
        check_date = update_data.get('booking_date', db_booking.booking_date)
        check_start = update_data.get('start_time', db_booking.start_time)
        check_end = update_data.get('end_time', db_booking.end_time)
        
        if check_booking_overlap(db, db_booking.individual_court_id, check_date, check_start, check_end, exclude_booking_id=booking_id):
            raise ValueError("Sân đã được đặt trong khung giờ này. Vui lòng chọn khung giờ khác.")

    # Keep legacy status and booking_status aligned to avoid inconsistent UI state.
    if 'status' in update_data and 'booking_status' not in update_data:
        normalized_status = str(update_data['status']).strip().lower()
        if normalized_status in {'pending', 'confirmed', 'active', 'completed', 'cancelled'}:
            update_data['booking_status'] = normalized_status

    if 'booking_status' in update_data and 'status' not in update_data:
        booking_status_value = update_data['booking_status']
        if hasattr(booking_status_value, 'value'):
            booking_status_value = booking_status_value.value
        normalized_booking_status = str(booking_status_value).strip().lower()
        if normalized_booking_status in {'pending', 'confirmed', 'active', 'completed', 'cancelled'}:
            update_data['status'] = normalized_booking_status
    
    for field, value in update_data.items():
        setattr(db_booking, field, value)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking


def delete_booking(db: Session, booking_id: int) -> bool:
    """Delete a booking"""
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return False
    
    db.delete(db_booking)
    db.commit()
    return True


def get_bookings_by_owner(
    db: Session, 
    owner_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    court_id: Optional[int] = None,
    individual_court_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Booking]:
    """
    Get all bookings for courts owned by a specific owner with optional filters
    
    Args:
        owner_id: The owner's user ID
        start_date: Filter bookings from this date onwards
        end_date: Filter bookings up to this date
        court_id: Filter by specific court complex
        individual_court_id: Filter by specific individual court
        status: Filter by booking status (active, completed, cancelled)
    """
    # Start with base query joining through individual_court and court
    query = db.query(Booking).join(
        IndividualCourt, Booking.individual_court_id == IndividualCourt.id
    ).join(
        Court, IndividualCourt.court_id == Court.id
    ).filter(
        Court.owner_id == owner_id
    )
    
    # Apply filters
    if start_date:
        query = query.filter(Booking.booking_date >= start_date)
    
    if end_date:
        query = query.filter(Booking.booking_date <= end_date)
    
    if court_id:
        query = query.filter(Court.id == court_id)
    
    if individual_court_id:
        query = query.filter(Booking.individual_court_id == individual_court_id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    # Order by booking date and start time
    query = query.order_by(Booking.booking_date.desc(), Booking.start_time)
    
    return query.all()


def get_owner_bookings_summary(db: Session, owner_id: int) -> dict:
    """
    Get summary statistics of bookings for an owner
    """
    
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Get all bookings in last 30 days
    bookings = get_bookings_by_owner(
        db, 
        owner_id,
        start_date=datetime.combine(thirty_days_ago, datetime.min.time()),
        end_date=datetime.combine(today, datetime.max.time())
    )
    
    total_bookings = len(bookings)
    active_bookings = len([b for b in bookings if b.status == 'active'])
    completed_bookings = len([b for b in bookings if b.status == 'completed'])
    cancelled_bookings = len([b for b in bookings if b.status == 'cancelled'])
    
    return {
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "period_days": 30
    }


# Payment CRUD
async def auto_verify_booking_payment(db: Session, booking_id: int) -> Optional[Booking]:
    """
    Automatically verify payment for a booking using bank transaction API
    
    Args:
        booking_id: ID of the booking to verify
        
    Returns:
        Updated booking if payment verified, None otherwise
    """
    from app.core.bank_verification_service import get_bank_verification_service
    from app.models.court import PaymentStatus
    from app.crud.user import get_user_by_id
    
    booking = get_booking(db, booking_id)
    if not booking or booking.payment_status == PaymentStatus.paid:
        return booking
    
    # Get court and owner info
    individual_court = get_individual_court(db, booking.individual_court_id)
    if not individual_court:
        return None
    
    parent_court = get_court(db, individual_court.court_id)
    if not parent_court:
        return None
    
    owner = get_user_by_id(db, parent_court.owner_id)
    if not owner or not owner.bank_account_number:
        return None
    
    # Try to verify payment
    bank_service = get_bank_verification_service()
    verified = await bank_service.auto_verify_booking(
        db=db,
        booking=booking,
        owner_bank_code=owner.bank_code,
        owner_account_number=owner.bank_account_number
    )
    
    if verified:
        db.refresh(booking)
        return booking
    
    return None


def manual_verify_booking_payment(
    db: Session,
    booking_id: int,
    transaction_id: str,
    note: Optional[str] = None
) -> Optional[Booking]:
    """
    Manually verify payment for a booking (owner/admin action)
    
    Args:
        booking_id: ID of the booking to verify
        transaction_id: Bank transaction ID
        note: Optional verification note
        
    Returns:
        Updated booking
    """
    from datetime import datetime as dt
    from app.models.court import PaymentStatus, BookingStatus
    
    booking = get_booking(db, booking_id)
    if not booking:
        return None
    
    # Manually verify
    booking.payment_status = PaymentStatus.paid
    booking.booking_status = BookingStatus.confirmed
    booking.status = "confirmed"  # Legacy field
    booking.bank_transaction_id = transaction_id
    booking.payment_verified_at = dt.now()
    booking.payment_note = note or "Manually verified"
    
    db.commit()
    db.refresh(booking)
    
    return booking


def get_payment_info(db: Session, booking_id: int) -> Optional[dict]:
    """
    Get payment information for a booking
    
    Args:
        booking_id: ID of the booking
        
    Returns:
        Dict with payment information including QR code
    """
    from datetime import timedelta
    from app.crud.user import get_user_by_id
    
    booking = get_booking(db, booking_id)
    if not booking:
        return None
    
    # Get court and owner info
    individual_court = get_individual_court(db, booking.individual_court_id)
    if not individual_court:
        return None
    
    parent_court = get_court(db, individual_court.court_id)
    if not parent_court:
        return None
    
    owner = get_user_by_id(db, parent_court.owner_id)
    if not owner:
        return None
    
    # Calculate expiration (30 minutes from creation)
    expires_at = booking.created_at + timedelta(minutes=30)
    
    return {
        "qr_code_url": booking.qr_code_url,
        "bank_name": owner.bank_name or "",
        "account_number": owner.bank_account_number or "",
        "account_name": owner.bank_account_name or "",
        "amount": float(booking.total_price) if booking.total_price else 0,
        "content": f"BOOKING{booking.id}",
        "booking_id": booking.id,
        "expires_at": expires_at
    }


