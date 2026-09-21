from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.notification import (
    Notification,
    NotificationCreate,
    CourtRequest,
    CourtRequestCreate,
    CourtRequestUpdate,
    AdvertisementRequest,
    AdvertisementRequestCreate,
    AdvertisementRequestUpdate,
)
from app.crud import notification as notification_crud
from app.crud import court as court_crud
from app.core.cloudinary_storage import upload_image_to_cloudinary
import json

router = APIRouter()


def _json_load(value, fallback):
    if not value:
        return fallback
    try:
        return json.loads(value)
    except Exception:
        return fallback


def _attach_court_request_metadata(db: Session, request: CourtRequest):
    owner_requests = notification_crud.get_owner_court_requests(db, request.owner_id)
    owner_requests_sorted = sorted(
        owner_requests,
        key=lambda item: ((item.created_at or 0), item.id),
    )
    first_request_id = owner_requests_sorted[0].id if owner_requests_sorted else request.id

    # Stable classification: first request of owner is create, subsequent requests are update.
    submission_type = "create" if request.id == first_request_id else "update"
    setattr(request, "submission_type", submission_type)

    if submission_type == "create":
        setattr(request, "changed_fields", [])
        setattr(request, "changed_details", [])
        return request

    owner_courts = court_crud.get_courts_by_owner(db, request.owner_id)
    if not owner_courts:
        setattr(request, "changed_fields", [])
        setattr(request, "changed_details", [])
        return request

    court = owner_courts[0]
    changed_fields = []
    changed_details = []

    def _to_text(value):
        if value is None:
            return ""
        if isinstance(value, (list, dict)):
            try:
                return json.dumps(value, ensure_ascii=False)
            except Exception:
                return str(value)
        return str(value)

    def _normalize_slot(slot):
        if not isinstance(slot, dict):
            return {"start_time": "", "end_time": "", "price": 0.0}

        start_time = slot.get("start_time") or slot.get("startTime") or ""
        end_time = slot.get("end_time") or slot.get("endTime") or ""

        raw_price = slot.get("price", 0)
        try:
            price = float(raw_price)
        except Exception:
            price = 0.0

        return {
            "start_time": str(start_time),
            "end_time": str(end_time),
            "price": round(price, 2),
        }

    def _normalize_slots(slots):
        normalized = [_normalize_slot(item) for item in (slots or [])]
        return sorted(normalized, key=lambda item: (item["start_time"], item["end_time"], item["price"]))

    def _append_change(label: str, old_value, new_value):
        old_text = _to_text(old_value).strip()
        new_text = _to_text(new_value).strip()
        if old_text != new_text:
            changed_fields.append(label)
            changed_details.append(
                {
                    "field": label,
                    "old_value": old_text or "(empty)",
                    "new_value": new_text or "(empty)",
                }
            )

    _append_change("Court Name", court.name, request.name)
    _append_change("Address", court.address, request.address)
    _append_change("Ward", court.ward, request.ward)
    _append_change("City", court.city, request.city)
    _append_change("Description", court.description, request.description)
    _append_change("Court Quantity", court.court_quantity, request.court_quantity)
    _append_change("Opening Time", court.opening_time, request.opening_time)
    _append_change("Closing Time", court.closing_time, request.closing_time)
    _append_change("Contact Phone", court.contact_phone, request.contact_phone)
    _append_change("Contact Email", court.contact_email, request.contact_email)

    req_facilities = _json_load(request.facilities, [])
    cur_facilities = court.facilities or []
    req_facilities_sorted = sorted(req_facilities)
    cur_facilities_sorted = sorted(cur_facilities)
    if req_facilities_sorted != cur_facilities_sorted:
        _append_change("Facilities", cur_facilities_sorted, req_facilities_sorted)

    req_images = _json_load(request.images, [])
    cur_images = court.images or []
    if req_images != cur_images:
        _append_change("Images", cur_images, req_images)

    req_slots = _json_load(request.time_slots, [])
    cur_slots = court.time_slots or []
    req_slots_normalized = _normalize_slots(req_slots)
    cur_slots_normalized = _normalize_slots(cur_slots)
    if req_slots_normalized != cur_slots_normalized:
        _append_change("Time Slots & Pricing", cur_slots_normalized, req_slots_normalized)

    setattr(request, "changed_fields", changed_fields)
    setattr(request, "changed_details", changed_details)
    return request


def _attach_court_request_metadata_list(db: Session, requests: List[CourtRequest]):
    for request in requests:
        _attach_court_request_metadata(db, request)
    return requests


def _attach_click_counts(db: Session, requests: List[AdvertisementRequest]):
    request_ids = [item.id for item in requests]
    click_map = notification_crud.get_click_counts_by_request_ids(db, request_ids)
    for item in requests:
        setattr(item, "click_count", click_map.get(item.id, 0))
    return requests


@router.get("/advertisements/public", response_model=List[AdvertisementRequest])
async def list_public_approved_advertisements(
    db: Session = Depends(get_db),
):
    """Public endpoint for approved advertisements shown on home page."""
    requests = notification_crud.get_all_advertisement_requests(db, status="approved")
    return _attach_click_counts(db, requests)


@router.post("/advertisements/{request_id}/click")
async def track_public_advertisement_click(
    request_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Track user click on approved advertisement from home page."""
    ad_request = notification_crud.get_advertisement_request(db, request_id)
    if not ad_request or ad_request.status != "approved":
        raise HTTPException(status_code=404, detail="Advertisement not found")

    ip_address = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("user-agent")

    notification_crud.create_advertisement_click(
        db,
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return {"message": "Click tracked"}


@router.post("/enterprise/advertisements", response_model=AdvertisementRequest, status_code=status.HTTP_201_CREATED)
async def create_advertisement_request(
    name: str = Form(...),
    description: str = Form(...),
    detail_url: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enterprise uploads an advertisement request. Admin must approve before publishing."""
    if current_user.role != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only enterprise users can upload advertisements",
        )

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Image file is required")

    image_url = await upload_image_to_cloudinary(
        image,
        subfolder="advertisements",
    )

    request_data = AdvertisementRequestCreate(
        name=name,
        description=description,
        detail_url=detail_url,
        image_url=image_url,
    )
    db_request = notification_crud.create_advertisement_request(db, request_data, current_user.id)

    from app.crud.user import get_users_by_role

    admins = get_users_by_role(db, "admin")
    for admin in admins:
        notification = NotificationCreate(
            user_id=admin.id,
            title="New Advertisement Request",
            message=f"{current_user.full_name} submitted an advertisement request for '{name}'",
            type="advertisement_request_created",
            related_id=db_request.id,
        )
        notification_crud.create_notification(db, notification)

    return db_request


@router.get("/enterprise/advertisements", response_model=List[AdvertisementRequest])
async def list_enterprise_approved_advertisements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get approved advertisements for current enterprise."""
    if current_user.role != "enterprise":
        raise HTTPException(status_code=403, detail="Not authorized")

    requests = notification_crud.get_enterprise_advertisement_requests(
        db, current_user.id, status="approved"
    )
    return _attach_click_counts(db, requests)


@router.get("/enterprise/advertisement-requests", response_model=List[AdvertisementRequest])
async def list_my_advertisement_requests(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all advertisement requests for current enterprise (pending/approved/rejected)."""
    if current_user.role != "enterprise":
        raise HTTPException(status_code=403, detail="Not authorized")

    requests = notification_crud.get_enterprise_advertisement_requests(db, current_user.id, status_filter)
    return _attach_click_counts(db, requests)


@router.delete("/enterprise/advertisements/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_advertisement(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete own advertisement request/record."""
    request = notification_crud.get_advertisement_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.role != "enterprise" or request.enterprise_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    notification_crud.delete_advertisement_request(db, request_id)


@router.get("/admin/advertisement-requests", response_model=List[AdvertisementRequest])
async def list_advertisement_requests_for_admin(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin list advertisement requests."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view advertisement requests")

    requests = notification_crud.get_all_advertisement_requests(db, status_filter)
    return _attach_click_counts(db, requests)


@router.put("/admin/advertisement-requests/{request_id}", response_model=AdvertisementRequest)
async def update_advertisement_request(
    request_id: int,
    update: AdvertisementRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin approves or rejects advertisement requests."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can review advertisement requests")

    request = notification_crud.get_advertisement_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Advertisement request not found")

    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Request already reviewed")

    updated_request = notification_crud.update_advertisement_request_status(
        db, request_id, update, current_user.id
    )

    if update.status == "approved":
        notification = NotificationCreate(
            user_id=request.enterprise_id,
            title="Advertisement Approved",
            message=f"Your advertisement '{request.name}' has been approved.",
            type="advertisement_request_approved",
            related_id=request_id,
        )
    else:
        notification = NotificationCreate(
            user_id=request.enterprise_id,
            title="Advertisement Rejected",
            message=f"Your advertisement '{request.name}' was rejected. Reason: {update.rejection_reason or 'Unknown'}",
            type="advertisement_request_rejected",
            related_id=request_id,
        )

    notification_crud.create_notification(db, notification)
    return updated_request


@router.delete("/admin/advertisement-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_advertisement_request_by_admin(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin deletes any advertisement request."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete advertisement requests")

    request = notification_crud.get_advertisement_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Advertisement request not found")

    notification_crud.delete_advertisement_request(db, request_id)


# Image upload endpoint
@router.post("/upload-images")
async def upload_images(
    images: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload images and return URLs (owner only)"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can upload images",
        )
    
    image_urls = []
    for image in images:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="All uploaded files must be images")

        image_url = await upload_image_to_cloudinary(
            image,
            subfolder="courts",
        )
        image_urls.append(image_url)
    
    return {"urls": image_urls}


# Notification endpoints
@router.get("/notifications", response_model=List[Notification])
async def get_my_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all notifications for current user"""
    return notification_crud.get_user_notifications(db, current_user.id, skip, limit)


@router.get("/notifications/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get count of unread notifications"""
    count = notification_crud.get_unread_count(db, current_user.id)
    return {"count": count}


@router.put("/notifications/{notification_id}/read", response_model=Notification)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read"""
    notification = notification_crud.mark_as_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Verify ownership
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return notification


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read"""
    notification_crud.mark_all_as_read(db, current_user.id)
    return {"message": "All notifications marked as read"}


# Court Request endpoints
@router.post("/court-requests", response_model=CourtRequest, status_code=status.HTTP_201_CREATED)
async def create_court_request(
    request: CourtRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new court registration request (owner only)"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can submit court requests",
        )
    
    owner_courts = court_crud.get_courts_by_owner(db, current_user.id)
    is_update_request = len(owner_courts) > 0

    # Create court request
    db_request = notification_crud.create_court_request(db, request, current_user.id)
    _attach_court_request_metadata(db, db_request)
    
    # Create notification for all admins
    from app.crud.user import get_users_by_role
    admins = get_users_by_role(db, "admin")
    
    for admin in admins:
        admin_title = "Court update request" if is_update_request else "New court listing request"
        admin_message = (
            f"{current_user.full_name} submitted a court update request for '{request.name}'"
            if is_update_request
            else f"{current_user.full_name} submitted a new court listing request for '{request.name}'"
        )
        notification = NotificationCreate(
            user_id=admin.id,
            title=admin_title,
            message=admin_message,
            type="request_created",
            related_id=db_request.id,
        )
        notification_crud.create_notification(db, notification)
    
    return db_request


@router.get("/court-requests", response_model=List[CourtRequest])
async def list_court_requests(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List court requests (admin sees all, owner sees only their own)"""
    if current_user.role == "admin":
        requests = notification_crud.get_all_court_requests(db, status_filter)
        return _attach_court_request_metadata_list(db, requests)
    elif current_user.role == "owner":
        requests = notification_crud.get_owner_court_requests(db, current_user.id)
        return _attach_court_request_metadata_list(db, requests)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/court-requests/{request_id}", response_model=CourtRequest)
async def get_court_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific court request"""
    request = notification_crud.get_court_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Court request not found")
    
    # Check authorization
    if current_user.role != "admin" and request.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return _attach_court_request_metadata(db, request)


@router.put("/court-requests/{request_id}", response_model=CourtRequest)
async def update_court_request_status(
    request_id: int,
    update: CourtRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve or reject a court request (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can review requests")
    
    request = notification_crud.get_court_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Court request not found")
    
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Request already reviewed")
    
    # Update request status
    updated_request = notification_crud.update_court_request_status(
        db, request_id, update, current_user.id
    )
    
    # If approved, create a new court OR update existing owner court
    if update.status == "approved":
        from app.schemas.court import CourtCreate, CourtUpdate, TimeSlot
        
        # Parse JSON fields
        facilities = json.loads(request.facilities) if request.facilities else []
        images = json.loads(request.images) if request.images else []
        time_slots_data = json.loads(request.time_slots) if request.time_slots else []
        time_slots = [TimeSlot(**slot) for slot in time_slots_data]
        
        owner_courts = court_crud.get_courts_by_owner(db, request.owner_id)

        if owner_courts:
            # Update existing approved court after admin approval.
            target_court = owner_courts[0]
            update_data = CourtUpdate(
                name=request.name,
                address=request.address,
                ward=request.ward,
                city=request.city,
                description=request.description,
                court_quantity=request.court_quantity,
                opening_time=request.opening_time,
                closing_time=request.closing_time,
                facilities=facilities,
                contact_phone=request.contact_phone,
                contact_email=request.contact_email,
                time_slots=time_slots,
                images=images,
            )
            court = court_crud.update_court(db, target_court.id, update_data)

            notification = NotificationCreate(
                user_id=request.owner_id,
                title="Court update request approved",
                message=f"Your court update request for '{request.name}' has been approved.",
                type="request_approved",
                related_id=court.id,
            )
        else:
            court_data = CourtCreate(
                name=request.name,
                address=request.address,
                ward=request.ward,
                city=request.city,
                description=request.description,
                court_quantity=request.court_quantity,
                opening_time=request.opening_time,
                closing_time=request.closing_time,
                facilities=facilities,
                contact_phone=request.contact_phone,
                contact_email=request.contact_email,
                time_slots=time_slots,
            )

            court = court_crud.create_court(db, court_data, request.owner_id, images)

            notification = NotificationCreate(
                user_id=request.owner_id,
                title="Court listing request approved",
                message=f"Your court listing request for '{request.name}' has been approved.",
                type="request_approved",
                related_id=court.id,
            )
    else:
        is_update_request = len(court_crud.get_courts_by_owner(db, request.owner_id)) > 0
        reject_title = "Court update request rejected" if is_update_request else "Court listing request rejected"
        reject_message = (
            f"Your court update request for '{request.name}' was rejected. Reason: {update.rejection_reason or 'Unknown'}"
            if is_update_request
            else f"Your court listing request for '{request.name}' was rejected. Reason: {update.rejection_reason or 'Unknown'}"
        )
        # Create rejection notification for owner
        notification = NotificationCreate(
            user_id=request.owner_id,
            title=reject_title,
            message=reject_message,
            type="request_rejected",
            related_id=request_id,
        )
    
    notification_crud.create_notification(db, notification)
    
    return _attach_court_request_metadata(db, updated_request)


@router.delete("/court-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_court_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a court request (owner can delete own pending requests, admin can delete any)"""
    request = notification_crud.get_court_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Court request not found")
    
    # Check authorization
    if current_user.role != "admin" and request.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Owner can only delete pending requests
    if current_user.role == "owner" and request.status != "pending":
        raise HTTPException(status_code=400, detail="Cannot delete reviewed request")
    
    notification_crud.delete_court_request(db, request_id)
