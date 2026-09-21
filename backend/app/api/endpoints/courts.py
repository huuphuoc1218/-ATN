from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import json
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.court import (
    Court,
    CourtCreate,
    CourtUpdate,
    CourtWithIndividualCourts,
    IndividualCourt,
    IndividualCourtUpdate,
    IndividualCourtWithBookings,
    Booking,
    BookingCreate,
    BookingUpdate,
    BookingDetail,
    OwnerBookingsSummary,
)
from app.crud import court as court_crud

router = APIRouter()

try:
    LOCAL_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")
except ZoneInfoNotFoundError:
    LOCAL_TIMEZONE = ZoneInfo("UTC")

# Court endpoints
@router.post("/courts", response_model=Court, status_code=status.HTTP_201_CREATED)
async def create_court(
    court_data: str = Form(...),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new court (owner only)"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can create courts",
        )
    
    # Parse court data from JSON string
    court_dict = json.loads(court_data)
    court = CourtCreate(**court_dict)
    
    # TODO: Handle image uploads to storage (S3, local, etc.)
    image_urls = []
    if images:
        for image in images:
            # Save image and get URL
            # image_url = save_image(image)
            # image_urls.append(image_url)
            pass
    
    db_court = court_crud.create_court(db, court, current_user.id, image_urls)
    return db_court


@router.get("/courts", response_model=List[Court])
async def list_courts(
    skip: int = 0,
    limit: int = 100,
    booking_date: Optional[str] = Query(None, description="Booking date in YYYY-MM-DD"),
    start_time: Optional[str] = Query(None, description="Start time in HH:MM"),
    end_time: Optional[str] = Query(None, description="End time in HH:MM"),
    db: Session = Depends(get_db),
):
    """List all courts"""
    courts = court_crud.get_courts(db, skip=skip, limit=limit)

    # Optional availability filter by date and time range.
    has_availability_filter = booking_date or start_time or end_time
    if has_availability_filter:
        if not (booking_date and start_time and end_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="booking_date, start_time, and end_time are required together",
            )

        try:
            parsed_booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid booking_date format. Use YYYY-MM-DD",
            )

        try:
            parsed_start_time = datetime.strptime(start_time, "%H:%M").time()
            parsed_end_time = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time format. Use HH:MM",
            )

        if parsed_start_time >= parsed_end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be earlier than end_time",
            )

        now_local = datetime.now(LOCAL_TIMEZONE)
        now_time = now_local.time().replace(second=0, microsecond=0)

        if parsed_booking_date < now_local.date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="booking_date cannot be in the past",
            )

        if parsed_booking_date == now_local.date() and parsed_start_time <= now_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be later than current time for today",
            )

        filtered_courts = []
        for court in courts:
            if not court.is_active:
                continue

            # Requested range must be inside venue operating hours.
            if start_time < court.opening_time or end_time > court.closing_time:
                continue

            available_courts = court_crud.find_available_courts(
                db=db,
                court_id=court.id,
                booking_date=parsed_booking_date,
                start_time=start_time,
                end_time=end_time,
            )

            if available_courts:
                filtered_courts.append(court)

        return filtered_courts

    return courts


@router.get("/courts/my", response_model=List[CourtWithIndividualCourts])
async def list_my_courts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List courts owned by the current user"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can access this endpoint",
        )
    
    courts = court_crud.get_courts_by_owner(db, current_user.id)
    return courts


@router.get("/courts/{court_id}", response_model=CourtWithIndividualCourts)
async def get_court(
    court_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific court by ID"""
    court = court_crud.get_court(db, court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Court not found",
        )
    return court


@router.put("/courts/{court_id}", response_model=Court)
async def update_court(
    court_id: int,
    court_update: CourtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a court (owner only)"""
    court = court_crud.get_court(db, court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Court not found",
        )
    
    if court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this court",
        )
    
    updated_court = court_crud.update_court(db, court_id, court_update)
    return updated_court


@router.delete("/courts/{court_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_court(
    court_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a court (owner or admin only)"""
    court = court_crud.get_court(db, court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Court not found",
        )
    
    if court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this court",
        )
    
    court_crud.delete_court(db, court_id)


# Individual Court endpoints
@router.get("/courts/{court_id}/individual-courts", response_model=List[IndividualCourtWithBookings])
async def list_individual_courts(
    court_id: int,
    db: Session = Depends(get_db),
):
    """List all individual courts for a specific court"""
    court = court_crud.get_court(db, court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Court not found",
        )
    
    individual_courts = court_crud.get_individual_courts_by_court(db, court_id)
    return individual_courts


@router.put("/individual-courts/{individual_court_id}", response_model=IndividualCourt)
async def update_individual_court(
    individual_court_id: int,
    individual_court_update: IndividualCourtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an individual court (owner only)"""
    individual_court = court_crud.get_individual_court(db, individual_court_id)
    if not individual_court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Individual court not found",
        )
    
    # Check ownership
    court = court_crud.get_court(db, individual_court.court_id)
    if court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this individual court",
        )
    
    updated_individual_court = court_crud.update_individual_court(
        db, individual_court_id, individual_court_update
    )
    return updated_individual_court


# Booking endpoints
# Legacy endpoint - DEPRECATED: Use /api/bookings from bookings.py instead
# This endpoint is kept for backward compatibility with owner manual bookings
@router.post("/courts/bookings", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking_legacy(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new booking (Legacy endpoint for owner manual bookings)"""
    # Check if individual court exists
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    if not individual_court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Individual court not found",
        )
    
    # If user is owner, they can create booking for their courts (manual booking)
    # Otherwise, user is creating booking for themselves
    if current_user.role == "owner":
        # Check if the court belongs to this owner
        court = court_crud.get_court(db, individual_court.court_id)
        if not court or court.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this court",
            )
    
    try:
        db_booking = court_crud.create_booking(db, booking, current_user.id)
        return db_booking
    except ValueError as e:
        # Find available alternative courts
        court = court_crud.get_court(db, individual_court.court_id)
        available_courts = court_crud.find_available_courts(
            db, 
            court.id, 
            booking.booking_date, 
            booking.start_time, 
            booking.end_time,
            exclude_court_id=booking.individual_court_id
        )
        
        # Format suggestions
        suggestions = [
            {
                "id": c.id,
                "name": c.name,
                "court_name": court.name
            }
            for c in available_courts
        ]
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(e),
                "suggested_courts": suggestions
            }
        )


@router.get("/bookings/my", response_model=List[Booking])
async def list_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List bookings for the current user"""
    bookings = court_crud.get_bookings_by_user(db, current_user.id)
    return bookings


@router.put("/bookings/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a booking"""
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    
    # Only the booking owner or court owner can update
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    court = court_crud.get_court(db, individual_court.court_id)
    
    if booking.user_id != current_user.id and court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this booking",
        )
    
    try:
        updated_booking = court_crud.update_booking(db, booking_id, booking_update)
        return updated_booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a booking"""
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    
    # Only the booking owner or court owner can delete
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    court = court_crud.get_court(db, individual_court.court_id)
    
    if booking.user_id != current_user.id and court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this booking",
        )
    
    court_crud.delete_booking(db, booking_id)


# Owner booking management endpoints
@router.get("/owner/bookings", response_model=List[BookingDetail])
async def list_owner_bookings(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    court_id: Optional[int] = Query(None, description="Filter by court complex ID"),
    individual_court_id: Optional[int] = Query(None, description="Filter by individual court ID"),
    status: Optional[str] = Query(None, description="Filter by status: active, completed, cancelled"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all bookings for courts owned by the current owner.
    Supports filtering by date range, court, and status.
    """
    # Only owners can access this endpoint
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only court owners can access this endpoint",
        )
    
    # Parse dates if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD",
            )
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            # Set to end of day
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD",
            )
    
    # Get bookings
    bookings = court_crud.get_bookings_by_owner(
        db,
        owner_id=current_user.id,
        start_date=start_datetime,
        end_date=end_datetime,
        court_id=court_id,
        individual_court_id=individual_court_id,
        status=status
    )
    
    # Enrich booking data with court info
    booking_details = []
    for booking in bookings:
        individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
        court = court_crud.get_court(db, individual_court.court_id)
        
        booking_detail = BookingDetail(
            id=booking.id,
            individual_court_id=booking.individual_court_id,
            user_id=booking.user_id,
            booking_date=booking.booking_date,
            start_time=booking.start_time,
            end_time=booking.end_time,
            phone_number=booking.phone_number,
            customer_name=booking.customer_name,
            customer_email=booking.customer_email,
            status=booking.status,
            total_hours=booking.total_hours,
            total_price=booking.total_price,
            payment_method=booking.payment_method,
            payment_status=booking.payment_status,
            booking_status=booking.booking_status,
            qr_code_url=booking.qr_code_url,
            bank_transaction_id=booking.bank_transaction_id,
            payment_verified_at=booking.payment_verified_at,
            payment_note=booking.payment_note,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            individual_court=individual_court,
            user=booking.user,
            court_name=court.name
        )
        booking_details.append(booking_detail)
    
    return booking_details


@router.get("/owner/bookings/summary", response_model=OwnerBookingsSummary)
async def get_owner_bookings_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get booking statistics summary for the owner (last 30 days)
    """
    # Only owners can access this endpoint
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only court owners can access this endpoint",
        )
    
    summary = court_crud.get_owner_bookings_summary(db, current_user.id)
    return summary

