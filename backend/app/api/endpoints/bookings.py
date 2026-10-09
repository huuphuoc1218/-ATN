"""
Booking endpoints with VietQR payment integration
"""
import secrets
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from app.core.database import get_db, SessionLocal
from app.core.security import get_current_user, get_current_owner
from app.models.user import User
from app.models.court import PaymentMethod, BookingInvite, BookingParticipant
from app.models.friend import Friendship
from app.models.notification import Notification
from app.schemas.court import (
    BookingCreate,
    Booking,
    BookingWithPayment,
    PaymentInfo,
    PaymentPreviewRequest,
    BookingUpdate,
    UserBookingHistoryItem,
    BookingInviteCodeCreateResponse,
    BookingInviteCodePreviewRequest,
    BookingInviteCodePreviewResponse,
    BookingInviteCodeActionRequest,
    BookingInviteCodeActionResponse,
    BookingInviteSendRequest,
    BookingInviteSendResponse,
    BookingInviteNotificationActionRequest,
    BookingInviteNotificationActionResponse,
    BookingInviteDetailResponse,
)
from app.crud import court as court_crud
from app.crud import friend as friend_crud
from app.crud.user import get_user_by_id
from app.crud.notification import create_notification
from app.core.vietqr_service import VietQRService
from app.core.booking_qr_service import (
    generate_booking_access_token,
    decode_booking_access_token,
    build_booking_info_url,
    build_qr_image_url,
    build_booking_info_html,
)
from app.core.email_service import send_booking_qr_email
from app.schemas.notification import NotificationCreate

router = APIRouter()

LOCAL_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


def _is_social_session_expired(court, booking_date, end_time: str) -> bool:
    now = datetime.now(LOCAL_TIMEZONE)
    if getattr(booking_date, "tzinfo", None) is not None:
        booking_date = booking_date.astimezone(LOCAL_TIMEZONE).date()
    elif hasattr(booking_date, "date"):
        booking_date = booking_date.date()
    if booking_date < now.date():
        return True
    if booking_date > now.date():
        return False
    try:
        end_hour, end_minute = (int(part) for part in end_time.split(":", 1))
        end_datetime = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        return now >= end_datetime
    except (AttributeError, TypeError, ValueError):
        return False


def _is_social_booking_expired(booking, court) -> bool:
    return _is_social_session_expired(court, booking.booking_date, court.social_end_time or booking.end_time)


def _get_social_session_bookings(db: Session, booking, court):
    """Return all booking records that represent the same social session."""
    return (
        db.query(court_crud.Booking)
        .join(
            court_crud.IndividualCourt,
            court_crud.Booking.individual_court_id == court_crud.IndividualCourt.id,
        )
        .filter(
            court_crud.IndividualCourt.court_id == court.id,
            func.date(court_crud.Booking.booking_date) == booking.booking_date.date(),
            court_crud.Booking.start_time == booking.start_time,
            court_crud.Booking.end_time == booking.end_time,
            court_crud.Booking.status.in_(["pending", "confirmed", "active"]),
        )
        .order_by(court_crud.Booking.id.asc())
        .all()
    )


def _get_social_ticket_count(db: Session, court, booking_date, start_time: str, end_time: str) -> int:
    booking_date_value = booking_date.date() if hasattr(booking_date, "date") else booking_date
    booking_ids = [item.id for item in (
        db.query(court_crud.Booking)
        .join(
            court_crud.IndividualCourt,
            court_crud.Booking.individual_court_id == court_crud.IndividualCourt.id,
        )
        .filter(
            court_crud.IndividualCourt.court_id == court.id,
            func.date(court_crud.Booking.booking_date) == booking_date_value,
            court_crud.Booking.start_time == start_time,
            court_crud.Booking.end_time == end_time,
            court_crud.Booking.status.in_(["pending", "confirmed", "active"]),
        )
        .all()
    )]
    if not booking_ids:
        return 0

    return sum(
        participant.ticket_quantity
        for participant in db.query(BookingParticipant)
        .filter(BookingParticipant.booking_id.in_(booking_ids))
        .all()
    )

    try:
        end_hour, end_minute = (int(part) for part in booking.end_time.split(":", 1))
        end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        return now >= end_time
    except (AttributeError, TypeError, ValueError):
        return False


def _send_confirm_payment_email(
    booking_id: int,
    customer_email: str,
    customer_name: str,
    booking_info_url: str,
    qr_image_url: str,
    court_name: str,
    individual_court_name: str,
    booking_date_str: str,
    start_time: str,
    end_time: str,
    total_price_str: str,
) -> None:
    db = SessionLocal()
    try:
        booking = court_crud.get_booking(db, booking_id)
        if not booking:
            return

        sent_ok, sent_msg = send_booking_qr_email(
            to_email=customer_email,
            customer_name=customer_name,
            booking_id=booking_id,
            qr_image_url=qr_image_url,
            booking_info_url=booking_info_url,
            court_name=court_name,
            individual_court_name=individual_court_name,
            booking_date=booking_date_str,
            start_time=start_time,
            end_time=end_time,
            total_price=total_price_str,
            smtp_timeout=10.0,
        )

        booking.payment_note = f"EMAIL_SENT: {sent_msg}" if sent_ok else f"EMAIL_FAILED: {sent_msg}"
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _normalize_status_value(raw_status: object) -> str:
    """Normalize enum/string status values to plain lowercase text."""
    if raw_status is None:
        return ""

    if hasattr(raw_status, "value"):
        raw_status = getattr(raw_status, "value")

    status_text = str(raw_status).strip().lower()
    if "." in status_text:
        status_text = status_text.split(".")[-1]
    return status_text


def _get_effective_history_status(booking) -> str:
    """Return effective status for history cards based on booking lifecycle and end time."""
    primary_status = _normalize_status_value(booking.booking_status)
    legacy_status = _normalize_status_value(booking.status)

    # Prioritize terminal states when either field already has them.
    if "cancelled" in {primary_status, legacy_status}:
        return "cancelled"
    if "completed" in {primary_status, legacy_status}:
        return "completed"

    status_value = primary_status or legacy_status or "pending"

    if status_value in {"cancelled", "completed", "pending"}:
        return status_value

    if status_value in {"active", "confirmed"}:
        try:
            booking_end_time = datetime.strptime(booking.end_time, "%H:%M").time()
            booking_end_datetime = datetime.combine(booking.booking_date.date(), booking_end_time)
            if booking_end_datetime <= datetime.now():
                return "completed"
        except Exception:
            pass

        return "confirmed"

    return "pending"


def _is_invitable_booking(booking) -> bool:
    booking_status = _normalize_status_value(getattr(booking, "booking_status", None))
    legacy_status = _normalize_status_value(getattr(booking, "status", None))
    return booking_status in {"confirmed", "active"} or legacy_status in {"confirmed", "active"}


def _generate_booking_invite_code(db: Session) -> str:
    for _ in range(10):
        code = secrets.token_urlsafe(6).replace("-", "").replace("_", "").upper()[:8]
        exists = db.query(BookingInvite).filter(BookingInvite.code == code).first()
        if not exists:
            return code
    raise ValueError("Unable to generate unique invite code")


def _are_users_friends(db: Session, user_a_id: int, user_b_id: int) -> bool:
    low_id, high_id = (user_a_id, user_b_id) if user_a_id < user_b_id else (user_b_id, user_a_id)
    friendship = (
        db.query(Friendship)
        .filter(Friendship.user_low_id == low_id, Friendship.user_high_id == high_id)
        .first()
    )
    return friendship is not None


def _has_user_received_booking_invite(
    db: Session,
    booking_id: int,
    invitee_user_id: int,
    exclude_invite_id: Optional[int] = None,
) -> bool:
    """Return True if user has already received any invite for this booking."""
    query = db.query(BookingInvite).filter(
        BookingInvite.booking_id == booking_id,
        BookingInvite.invitee_user_id == invitee_user_id,
    )
    if exclude_invite_id is not None:
        query = query.filter(BookingInvite.id != exclude_invite_id)
    return query.first() is not None


def _increment_friendship_streak(db: Session, user_a_id: int, user_b_id: int):
    low_id, high_id = (user_a_id, user_b_id) if user_a_id < user_b_id else (user_b_id, user_a_id)
    friendship = (
        db.query(Friendship)
        .filter(Friendship.user_low_id == low_id, Friendship.user_high_id == high_id)
        .first()
    )
    if not friendship:
        return

    friendship.current_streak = (friendship.current_streak or 0) + 1
    friendship.best_streak = max(friendship.best_streak or 0, friendship.current_streak)


def _respond_to_booking_invite(invite: BookingInvite, current_user: User, action: str, db: Session):
    action = action.strip().lower()
    if action not in {"accept", "reject"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

    if invite.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This invite has already been handled")

    invite.status = "accepted" if action == "accept" else "rejected"
    invite.responded_at = datetime.utcnow()

    if action == "accept" and invite.invitee_user_id:
        _increment_friendship_streak(db, invite.inviter_user_id, invite.invitee_user_id)

    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.type == "booking_invite_received",
        Notification.related_id == invite.id,
        Notification.is_read.is_(False),
    ).update({"is_read": True}, synchronize_session=False)

    db.commit()
    db.refresh(invite)

    create_notification(
        db,
        NotificationCreate(
            user_id=invite.inviter_user_id,
            title="Booking invite response",
            message=(
                f"{current_user.full_name} accepted your booking invite code {invite.code}."
                if action == "accept"
                else f"{current_user.full_name} rejected your booking invite code {invite.code}."
            ),
            type="booking_invite_result",
            related_id=invite.booking_id,
        ),
    )

    return {
        "invite_id": invite.id,
        "booking_id": invite.booking_id,
        "code": invite.code,
        "status": invite.status,
        "message": "Booking invite accepted" if action == "accept" else "Booking invite rejected",
        "responded_at": invite.responded_at,
    }


def calculate_multi_tier_price(start_time: str, end_time: str, time_slots: list) -> float:
    """
    Calculate price for multi-tier time slots.
    
    Similar to frontend calculation: iterate through 30-minute intervals
    and sum up prices for each interval that falls into a time slot tier.
    """
    if not time_slots:
        return 0.0
    
    from datetime import datetime as dt, timedelta
    
    # Parse times
    start_dt = dt.strptime(start_time, "%H:%M")
    end_dt = dt.strptime(end_time, "%H:%M")
    
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
            
            slot_start = dt.strptime(slot_start_str, "%H:%M")
            slot_end = dt.strptime(slot_end_str, "%H:%M")
            
            # Check if current interval starts within this slot
            if current_time >= slot_start and current_time < slot_end:
                # Add price for this 30-minute interval (0.5 hour)
                total_price += slot_price * 0.5
                break
        
        current_time = next_time
    
    return total_price


@router.post("/payment-preview", response_model=PaymentInfo)
async def get_payment_preview(
    preview_data: PaymentPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate VietQR payment preview without creating a booking.

    Booking will only be created when user presses Complete on payment step.
    """
    court = court_crud.get_court(db, preview_data.court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin sân"
        )

    if court.court_type == "social" and court.social_start_time and court.social_end_time:
        if preview_data.start_time != court.social_start_time or preview_data.end_time != court.social_end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Social court chỉ mở từ {court.social_start_time} đến {court.social_end_time}.",
            )
    if court.court_type == "social" and court.social_date:
        if preview_data.booking_date.date() != court.social_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Social court chỉ mở vào ngày đã công bố.")
    if court.court_type == "social" and _is_social_session_expired(
        court, preview_data.booking_date, court.social_end_time or preview_data.end_time
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Social này đã hết hạn, không thể mua vé.")

    if court.court_type == "social":
        max_players = court.social_max_players or 2
        used_tickets = _get_social_ticket_count(
            db, court, preview_data.booking_date, preview_data.start_time, preview_data.end_time
        )
        if used_tickets + preview_data.ticket_quantity > max_players:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Chỉ còn {max_players - used_tickets} vé cho social này.",
            )

    available_courts = court_crud.find_available_courts(
        db,
        court.id,
        preview_data.booking_date,
        preview_data.start_time,
        preview_data.end_time,
    )

    if not available_courts and court.court_type != "social":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tất cả sân đã có lịch đặt trong khung giờ này. Vui lòng chọn khung giờ khác.",
        )

    owner = get_user_by_id(db, court.owner_id)
    if not owner or not owner.bank_account_number or not owner.bank_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chủ sân chưa cấu hình tài khoản ngân hàng để nhận thanh toán.",
        )

    # Calculate amount using multi-tier pricing (same as frontend)
    amount = calculate_multi_tier_price(
        preview_data.start_time,
        preview_data.end_time,
        court.time_slots or []
    )
    if court.court_type == "social" and court.social_ticket_price:
        amount = float(court.social_ticket_price)
    if court.court_type == "social":
        amount *= preview_data.ticket_quantity

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tính giá đặt sân cho khung giờ đã chọn.",
        )

    payment_content = (
        f"TMP{preview_data.court_id}-"
        f"{preview_data.booking_date.strftime('%d%m%y')}-"
        f"{preview_data.start_time.replace(':', '')}"
    )

    qr_url = VietQRService().generate_qr_url(
        bank_code=owner.bank_code,
        account_number=owner.bank_account_number,
        amount=int(amount),
        description=payment_content,
        account_name=owner.bank_account_name,
    )

    return {
        "qr_code_url": qr_url,
        "bank_name": owner.bank_name or "Ngân hàng",
        "account_number": owner.bank_account_number,
        "account_name": owner.bank_account_name or owner.full_name,
        "amount": amount,
        "content": payment_content,
        "booking_id": None,
        "expires_at": datetime.utcnow(),
    }


@router.post("/", response_model=BookingWithPayment, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new booking with payment info
    
    - For VietQR payment: generates QR code and returns payment info
    - For cash payment: booking is automatically confirmed
    """
    try:
        requested_individual = court_crud.get_individual_court(db, booking_data.individual_court_id)
        parent_court = court_crud.get_court(db, requested_individual.court_id) if requested_individual else None
        if parent_court and parent_court.court_type == "social" and parent_court.social_start_time and parent_court.social_end_time:
            if booking_data.start_time != parent_court.social_start_time or booking_data.end_time != parent_court.social_end_time:
                raise ValueError(
                    f"Social court chỉ mở từ {parent_court.social_start_time} đến {parent_court.social_end_time}."
                )
        if parent_court and parent_court.court_type == "social" and parent_court.social_date:
            if booking_data.booking_date.date() != parent_court.social_date:
                raise ValueError("Social court chỉ mở vào ngày đã công bố.")
        if parent_court and parent_court.court_type == "social" and _is_social_session_expired(
            parent_court, booking_data.booking_date, parent_court.social_end_time or booking_data.end_time
        ):
            raise ValueError("Social này đã hết hạn, không thể mua vé.")
        if parent_court and parent_court.court_type == "social":
            max_players = parent_court.social_max_players or 2
            used_tickets = _get_social_ticket_count(
                db,
                parent_court,
                booking_data.booking_date,
                booking_data.start_time,
                booking_data.end_time,
            )
            if used_tickets + booking_data.ticket_quantity > max_players:
                raise ValueError(f"Chỉ còn {max_players - used_tickets} vé cho social này.")
        # Create booking with payment
        booking = court_crud.create_booking(
            db=db,
            booking=booking_data,
            user_id=current_user.id
        )
        
        # Get payment info if VietQR
        payment_info = None
        if booking.payment_method == PaymentMethod.vietqr and booking.qr_code_url:
            payment_info = court_crud.get_payment_info(db, booking.id)
        
        return {
            **booking.__dict__,
            "payment_info": payment_info
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tạo booking: {str(e)}"
        )


@router.get("/social")
async def list_social_bookings(
    court_id: int,
    booking_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        requested_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid booking_date format. Use YYYY-MM-DD")

    bookings = (
        db.query(court_crud.Booking)
        .join(court_crud.IndividualCourt, court_crud.Booking.individual_court_id == court_crud.IndividualCourt.id)
        .filter(
            court_crud.IndividualCourt.court_id == court_id,
            func.date(court_crud.Booking.booking_date) == requested_date,
            court_crud.Booking.status.in_(["pending", "confirmed", "active"]),
        )
        .all()
    )
    court = court_crud.get_court(db, court_id)
    if not court or court.court_type != "social":
        return []

    sessions = []
    grouped_bookings = {}
    for booking in bookings:
        grouped_bookings.setdefault((booking.start_time, booking.end_time), []).append(booking)

    for session_bookings in grouped_bookings.values():
        booking = session_bookings[0]
        participants = db.query(BookingParticipant).filter(
            BookingParticipant.booking_id.in_([item.id for item in session_bookings])
        ).all()
        count = sum(participant.ticket_quantity for participant in participants)
        expired = _is_social_booking_expired(booking, court)
        sessions.append({
            "booking_id": booking.id,
            "booking_date": booking.booking_date,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "count": count,
            "max_players": court.social_max_players or 2,
            "status": "expired" if expired else ("full" if count >= (court.social_max_players or 2) else "active"),
            "participants": [
                {"user_id": participant.user_id, "full_name": participant.user.full_name, "tickets": participant.ticket_quantity}
                for participant in participants
            ],
        })
    return sessions


def _get_social_booking_context(db: Session, booking_id: int):
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy booking")

    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    court = court_crud.get_court(db, individual_court.court_id) if individual_court else None
    if not court or court.court_type != "social":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking này không phải social")
    return booking, court


@router.get("/{booking_id}/social-participants")
async def list_social_participants(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking, court = _get_social_booking_context(db, booking_id)
    if _is_social_booking_expired(booking, court):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Social booking đã hết hạn")
    if booking.status not in ["pending", "confirmed", "active"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Social booking không còn hoạt động")

    session_bookings = _get_social_session_bookings(db, booking, court)
    session_booking_ids = [item.id for item in session_bookings]
    participants = (
        db.query(BookingParticipant)
        .filter(BookingParticipant.booking_id == booking.id)
        .order_by(BookingParticipant.joined_at.asc())
        .all()
    )
    return {
        "booking_id": booking.id,
        "court_id": court.id,
        "max_players": court.social_max_players,
        "count": sum(participant.ticket_quantity for participant in participants),
        "participants": [
            {"user_id": participant.user_id, "full_name": participant.user.full_name, "tickets": participant.ticket_quantity, "joined_at": participant.joined_at}
            for participant in participants
        ],
    }


@router.post("/{booking_id}/join-social")
async def join_social_booking(
    booking_id: int,
    ticket_quantity: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking, court = _get_social_booking_context(db, booking_id)
    if _is_social_booking_expired(booking, court):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Social booking đã hết hạn")
    if booking.status not in ["pending", "confirmed", "active"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Social booking không còn hoạt động")

    session_bookings = _get_social_session_bookings(db, booking, court)
    session_booking_ids = [item.id for item in session_bookings]
    if ticket_quantity < 1 or ticket_quantity > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Số vé phải từ 1 đến 20")

    existing = db.query(BookingParticipant).filter(
        BookingParticipant.booking_id.in_(session_booking_ids),
        BookingParticipant.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bạn đã tham gia social booking này")

    participant_count = sum(
        participant.ticket_quantity
        for participant in db.query(BookingParticipant).filter(
            BookingParticipant.booking_id.in_(session_booking_ids)
        ).all()
    )
    max_players = court.social_max_players or 2
    if participant_count >= max_players:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Social booking đã đủ người")

    if participant_count + ticket_quantity > max_players:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Không đủ vé trống cho số lượng đã chọn")

    owner = get_user_by_id(db, court.owner_id)
    ticket_price = float(court.social_ticket_price or 0) if court.court_type == "social" else calculate_multi_tier_price(booking.start_time, booking.end_time, court.time_slots or [])
    total_price = ticket_price * ticket_quantity
    payment_info = None
    qr_code_url = None
    if owner and owner.bank_account_number and owner.bank_code:
        payment_content = f"SOCIAL{booking.id}-{current_user.id}"
        qr_code_url = VietQRService().generate_qr_url(
            bank_code=owner.bank_code,
            account_number=owner.bank_account_number,
            amount=int(total_price),
            description=payment_content,
            account_name=owner.bank_account_name,
        )
        payment_info = {
            "qr_code_url": qr_code_url,
            "bank_name": owner.bank_name or "Ngân hàng",
            "account_number": owner.bank_account_number,
            "account_name": owner.bank_account_name or owner.full_name,
            "amount": total_price,
            "content": payment_content,
            "booking_id": booking.id,
            "expires_at": datetime.utcnow(),
        }

    participant = BookingParticipant(
        booking_id=booking.id,
        user_id=current_user.id,
        ticket_quantity=ticket_quantity,
        total_price=total_price,
        qr_code_url=qr_code_url,
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return {
        "booking_id": booking.id,
        "user_id": current_user.id,
        "tickets": ticket_quantity,
        "count": participant_count + ticket_quantity,
        "max_players": max_players,
        "payment_info": payment_info,
    }


@router.delete("/{booking_id}/leave-social")
async def leave_social_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking, court = _get_social_booking_context(db, booking_id)
    participant = db.query(BookingParticipant).filter(
        BookingParticipant.booking_id == booking.id,
        BookingParticipant.user_id == current_user.id,
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bạn chưa tham gia social booking này")
    if current_user.id == booking.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Người tạo booking không thể rời booking")

    db.delete(participant)
    db.commit()
    remaining = sum(
        item.ticket_quantity
        for item in db.query(BookingParticipant).filter(BookingParticipant.booking_id == booking.id).all()
    )
    return {"booking_id": booking.id, "count": remaining, "max_players": court.social_max_players or 2}


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get booking details by ID
    
    - User can only view their own bookings
    - Owner can view bookings for their courts
    - Admin can view all bookings
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check permissions
    if current_user.role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem booking này"
        )
    
    # If owner, check if booking belongs to their court
    if current_user.role == "owner":
        individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
        if not individual_court:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
        
        parent_court = court_crud.get_court(db, individual_court.court_id)
        if not parent_court or parent_court.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xem booking này"
            )
    
    return booking


@router.get("/{booking_id}/payment-info", response_model=PaymentInfo)
async def get_booking_payment_info(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payment information for a booking (QR code, bank details, etc.)
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check permissions
    if current_user.role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem thông tin thanh toán này"
        )
    
    payment_info = court_crud.get_payment_info(db, booking_id)
    if not payment_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin thanh toán"
        )
    
    return payment_info


@router.post("/{booking_id}/verify-payment", response_model=Booking)
async def verify_payment(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify payment for a booking (checks bank transactions)
    
    - User can request auto-verification
    - System checks bank API for matching transaction
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check permissions
    if current_user.role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền verify booking này"
        )
    
    # Auto-verify payment
    verified_booking = await court_crud.auto_verify_booking_payment(db, booking_id)
    
    if not verified_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tìm thấy giao dịch thanh toán. Vui lòng kiểm tra lại hoặc liên hệ chủ sân."
        )
    
    return verified_booking


@router.post("/{booking_id}/manual-verify", response_model=Booking)
async def manual_verify_payment(
    booking_id: int,
    transaction_id: str,
    note: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_owner)  # Only owner/admin can manually verify
):
    """
    Manually verify payment for a booking (owner/admin action)
    
    - Owner can manually confirm payment after checking their bank account
    - Requires bank transaction ID
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check if owner owns the court
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    if not individual_court:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
    
    parent_court = court_crud.get_court(db, individual_court.court_id)
    if not parent_court:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
    
    # Only owner of the court or admin can manually verify
    if current_user.role == "owner" and parent_court.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền verify booking này"
        )
    
    # Manually verify
    verified_booking = court_crud.manual_verify_booking_payment(
        db=db,
        booking_id=booking_id,
        transaction_id=transaction_id,
        note=note
    )
    
    return verified_booking


@router.post("/{booking_id}/confirm-payment", response_model=Booking)
async def confirm_payment(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_owner)  # Only owner can confirm
):
    """
    Owner confirms they received payment and activates the booking
    
    - Owner checks their bank account and confirms payment manually
    - Changes booking status from 'pending' to 'active'
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check if booking is in pending status
    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking đang ở trạng thái '{booking.status}', không thể xác nhận"
        )
    
    # Check if owner owns the court
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    if not individual_court:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
    
    parent_court = court_crud.get_court(db, individual_court.court_id)
    if not parent_court:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
    
    # Only owner of the court can confirm
    if parent_court.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xác nhận booking này"
        )
    
    # Update booking status to active
    booking.status = "active"
    booking.booking_status = "active"
    booking.payment_status = "paid"
    booking.payment_verified_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)

    # Build email payload and send it in the background so the request returns quickly.
    customer = get_user_by_id(db, booking.user_id)
    customer_email = booking.customer_email or (customer.email if customer else None)
    customer_name = booking.customer_name or (customer.full_name if customer else "Khách hàng")

    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    parent_court = court_crud.get_court(db, individual_court.court_id) if individual_court else None

    if customer_email and individual_court and parent_court:
        token = generate_booking_access_token(booking.id)
        booking_info_url = build_booking_info_url(token)
        qr_image_url = build_qr_image_url(booking_info_url)

        booking_date_str = booking.booking_date.strftime("%d/%m/%Y") if booking.booking_date else "N/A"
        total_price_str = f"{int(float(booking.total_price or 0)):,}".replace(",", ".")

        background_tasks.add_task(
            _send_confirm_payment_email,
            booking.id,
            customer_email,
            customer_name,
            booking_info_url,
            qr_image_url,
            parent_court.name,
            individual_court.name,
            booking_date_str,
            booking.start_time,
            booking.end_time,
            total_price_str,
        )
        booking.payment_note = "EMAIL_QUEUED"
    else:
        booking.payment_note = "EMAIL_FAILED: Missing customer email or court information"

    db.commit()
    db.refresh(booking)
    
    return booking


@router.get("/qr-booking/{token}", response_class=HTMLResponse, include_in_schema=False)
async def view_booking_from_qr(
    token: str,
    db: Session = Depends(get_db),
):
    """Public booking details page opened when customer scans QR from email."""
    booking_id = decode_booking_access_token(token)
    if not booking_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired QR code"
        )

    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    customer = get_user_by_id(db, booking.user_id)
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    parent_court = court_crud.get_court(db, individual_court.court_id) if individual_court else None
    owner = get_user_by_id(db, parent_court.owner_id) if parent_court else None

    booking_date_str = booking.booking_date.strftime("%d/%m/%Y") if booking.booking_date else "N/A"
    total_price_str = f"{int(float(booking.total_price or 0)):,}".replace(",", ".")

    html = build_booking_info_html(
        booking_id=booking.id,
        customer_name=booking.customer_name or (customer.full_name if customer else "N/A"),
        customer_email=booking.customer_email or (customer.email if customer else "N/A"),
        phone_number=booking.phone_number or (customer.phone_number if customer else "N/A"),
        booking_date=booking_date_str,
        start_time=booking.start_time,
        end_time=booking.end_time,
        total_price=total_price_str,
        court_name=parent_court.name if parent_court else "N/A",
        individual_court_name=individual_court.name if individual_court else "N/A",
        owner_name=owner.full_name if owner else "N/A",
        owner_phone=owner.phone_number if owner and owner.phone_number else "N/A",
    )

    return HTMLResponse(content=html)


@router.get("/user/my-bookings", response_model=List[Booking])
async def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings for current user
    """
    bookings = court_crud.get_bookings_by_user(db, current_user.id)
    return bookings


@router.get("/user/my-bookings/history", response_model=List[UserBookingHistoryItem])
async def get_my_bookings_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get enriched booking history for current user (court/location/status)."""
    bookings = court_crud.get_bookings_by_user(db, current_user.id)
    result: List[UserBookingHistoryItem] = []
    has_status_updates = False

    for booking in bookings:
        individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
        parent_court = court_crud.get_court(db, individual_court.court_id) if individual_court else None

        if parent_court:
            location = f"{parent_court.address}, {parent_court.ward}, {parent_court.city}"
            court_name = f"{parent_court.name} - {individual_court.name}" if individual_court else parent_court.name
        else:
            location = "N/A"
            court_name = "N/A"

        status_value = _get_effective_history_status(booking)

        # Keep stored values in sync for terminal states.
        if status_value in {"completed", "cancelled"}:
            current_booking_status = _normalize_status_value(booking.booking_status)
            current_legacy_status = _normalize_status_value(booking.status)
            if current_booking_status != status_value or current_legacy_status != status_value:
                booking.booking_status = status_value
                booking.status = status_value
                has_status_updates = True

        result.append(
            UserBookingHistoryItem(
                id=booking.id,
                court_name=court_name,
                location=location,
                booking_date=booking.booking_date,
                start_time=booking.start_time,
                end_time=booking.end_time,
                total_hours=float(booking.total_hours) if booking.total_hours is not None else None,
                total_price=float(booking.total_price) if booking.total_price is not None else None,
                status=status_value,
            )
        )

    if has_status_updates:
        db.commit()

    result.sort(key=lambda item: (item.booking_date, item.start_time), reverse=True)
    return result


@router.post("/{booking_id}/invite-codes", response_model=BookingInviteCodeCreateResponse)
async def create_booking_invite_code(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for this booking")

    if not _is_invitable_booking(booking):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code is only available for confirmed bookings",
        )

    code = _generate_booking_invite_code(db)
    invite = BookingInvite(
        booking_id=booking.id,
        inviter_user_id=current_user.id,
        code=code,
        status="pending",
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    return {
        "booking_id": invite.booking_id,
        "code": invite.code,
        "status": invite.status,
        "created_at": invite.created_at,
    }


@router.post("/invite-codes/preview", response_model=BookingInviteCodePreviewResponse)
async def preview_booking_invite_code(
    payload: BookingInviteCodePreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite = db.query(BookingInvite).filter(BookingInvite.code == payload.code.strip().upper()).first()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite code not found")

    booking = court_crud.get_booking(db, invite.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    inviter = get_user_by_id(db, invite.inviter_user_id)
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    parent_court = court_crud.get_court(db, individual_court.court_id) if individual_court else None

    if invite.inviter_user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot use your own invite code")

    if invite.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This invite code has already been used")

    return {
        "booking_id": booking.id,
        "code": invite.code,
        "court_name": parent_court.name if parent_court else "N/A",
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "inviter_name": inviter.full_name if inviter else "Unknown",
        "status": invite.status,
    }


@router.post("/invite-codes/respond", response_model=BookingInviteCodeActionResponse)
async def respond_booking_invite_code(
    payload: BookingInviteCodeActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite = db.query(BookingInvite).filter(BookingInvite.code == payload.code.strip().upper()).first()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite code not found")

    if invite.inviter_user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot respond to your own invite")

    if invite.invitee_user_id and invite.invitee_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This invite code is assigned to another user")

    if _has_user_received_booking_invite(
        db,
        booking_id=invite.booking_id,
        invitee_user_id=current_user.id,
        exclude_invite_id=invite.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only join this booking once. Please use a different friend for a new invite code.",
        )

    invite.invitee_user_id = current_user.id
    friend_crud.touch_friendship_invite_activity(db, invite.inviter_user_id, current_user.id)
    result = _respond_to_booking_invite(invite, current_user, payload.action, db)
    return {
        "booking_id": result["booking_id"],
        "code": result["code"],
        "status": result["status"],
        "message": result["message"],
        "responded_at": result["responded_at"],
    }


@router.post("/invite-codes/send", response_model=BookingInviteSendResponse)
async def send_booking_invite_to_friend(
    payload: BookingInviteSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite = db.query(BookingInvite).filter(BookingInvite.code == payload.code.strip().upper()).first()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite code not found")

    if invite.inviter_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only send your own invite code")

    if invite.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This invite code has already been used")

    if payload.friend_user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot invite yourself")

    if not _are_users_friends(db, current_user.id, payload.friend_user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only invite users from your friend list")

    booking = court_crud.get_booking(db, invite.booking_id)
    if not booking or not _is_invitable_booking(booking):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This booking is not eligible for invitations")

    if invite.invitee_user_id and invite.invitee_user_id != payload.friend_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This invite code was already sent to another friend")

    if _has_user_received_booking_invite(
        db,
        booking_id=invite.booking_id,
        invitee_user_id=payload.friend_user_id,
        exclude_invite_id=invite.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This friend has already received an invite for this booking. Please invite another friend.",
        )

    invite.invitee_user_id = payload.friend_user_id
    friend_crud.touch_friendship_invite_activity(db, current_user.id, payload.friend_user_id)
    db.commit()
    db.refresh(invite)

    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    parent_court = court_crud.get_court(db, individual_court.court_id) if individual_court else None
    court_name = parent_court.name if parent_court else "your booking"

    create_notification(
        db,
        NotificationCreate(
            user_id=payload.friend_user_id,
            title="Booking invite",
            message=f"{current_user.full_name} invited you to join booking at {court_name}.",
            type="booking_invite_received",
            related_id=invite.id,
        ),
    )

    return {
        "invite_id": invite.id,
        "booking_id": invite.booking_id,
        "code": invite.code,
        "invitee_user_id": payload.friend_user_id,
        "status": invite.status,
        "message": "Invite sent successfully",
    }


@router.post("/invite-codes/{invite_id}/respond", response_model=BookingInviteNotificationActionResponse)
async def respond_booking_invite_from_notification(
    invite_id: int,
    payload: BookingInviteNotificationActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite = db.query(BookingInvite).filter(BookingInvite.id == invite_id).first()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    if invite.invitee_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the receiver of this invite")

    result = _respond_to_booking_invite(invite, current_user, payload.action, db)
    return result


@router.get("/invite-codes/{invite_id}/details", response_model=BookingInviteDetailResponse)
async def get_booking_invite_details(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite = db.query(BookingInvite).filter(BookingInvite.id == invite_id).first()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    if current_user.id not in {invite.inviter_user_id, invite.invitee_user_id}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view this invite")

    booking = court_crud.get_booking(db, invite.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    parent_court = court_crud.get_court(db, individual_court.court_id) if individual_court else None
    inviter = get_user_by_id(db, invite.inviter_user_id)
    invitee = get_user_by_id(db, invite.invitee_user_id) if invite.invitee_user_id else None

    location = (
        f"{parent_court.address}, {parent_court.ward}, {parent_court.city}"
        if parent_court
        else "N/A"
    )
    court_name = (
        f"{parent_court.name} - {individual_court.name}"
        if parent_court and individual_court
        else (parent_court.name if parent_court else "N/A")
    )

    return {
        "invite_id": invite.id,
        "booking_id": invite.booking_id,
        "code": invite.code,
        "status": invite.status,
        "court_name": court_name,
        "location": location,
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "total_price": float(booking.total_price) if booking.total_price is not None else None,
        "inviter_name": inviter.full_name if inviter else "Unknown",
        "invitee_name": invitee.full_name if invitee else None,
    }


@router.put("/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update booking (change status, etc.)
    
    - User can cancel their own bookings
    - Owner can update booking status for their courts
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check permissions
    if current_user.role == "user":
        if booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền cập nhật booking này"
            )
        # Users can only cancel their bookings
        if booking_update.status and booking_update.status != "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chỉ có thể hủy booking"
            )
    
    if current_user.role == "owner":
        individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
        if not individual_court:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
        
        parent_court = court_crud.get_court(db, individual_court.court_id)
        if not parent_court or parent_court.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền cập nhật booking này"
            )
    
    try:
        updated_booking = court_crud.update_booking(db, booking_id, booking_update)
        return updated_booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
