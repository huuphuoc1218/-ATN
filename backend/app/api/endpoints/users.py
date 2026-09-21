from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.user import User
from app.models.notification import CourtRequest, AdvertisementRequest
from app.schemas.user import (
    UserResponse,
    UserListResponse,
    UserUpdate,
    AdminActivityItem,
    AdminRecentActivityResponse,
)
from app.crud import user as crud_user
from app.core.cloudinary_storage import upload_image_bytes_to_cloudinary

router = APIRouter()

ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024


def _get_role_value(user: User) -> str:
    role = getattr(user, "role", None)
    return getattr(role, "value", str(role))

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current authenticated user's profile (including bank account info)
    """
    # Only update non-None fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    # If updating email, check if email already exists (except current user's email)
    if 'email' in update_data:
        email_check = crud_user.get_user_by_email(db, update_data['email'])
        if email_check and email_check.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng bởi tài khoản khác"
            )
    
    user = crud_user.update_user(db, current_user.id, update_data)
    return user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_user_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload avatar image for user accounts."""
    if _get_role_value(current_user) != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only user accounts can update avatar",
        )

    file_ext = Path(avatar.filename or "").suffix.lower()
    if file_ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, JPEG, PNG and WEBP files are allowed",
        )

    file_bytes = await avatar.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Avatar file is empty")

    if len(file_bytes) > MAX_AVATAR_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar must be 5MB or smaller",
        )

    public_id = f"user_{current_user.id}_{uuid4().hex}"
    new_avatar_url = upload_image_bytes_to_cloudinary(
        file_bytes,
        filename=avatar.filename or "",
        subfolder="avatars",
        public_id_prefix=public_id,
    )

    user = crud_user.update_user(db, current_user.id, {"avatar_url": new_avatar_url})

    return user


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách users với phân trang (không bao gồm admin)
    """
    # Lọc bỏ users có role = 'admin'
    users = db.query(crud_user.User).filter(crud_user.User.role != 'admin').offset(skip).limit(limit).all()
    total = db.query(crud_user.User).filter(crud_user.User.role != 'admin').count()
    
    return {
        "users": users,
        "total": total
    }


@router.get("/admin/recent-activity", response_model=AdminRecentActivityResponse)
async def get_admin_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Get recent admin dashboard activity from real user/request data."""
    items: List[AdminActivityItem] = []

    recent_users = (
        db.query(User)
        .filter(User.role != "admin")
        .order_by(User.created_at.desc())
        .limit(limit)
        .all()
    )
    for user in recent_users:
        if not user.created_at:
            continue
        role_value = getattr(user.role, "value", str(user.role))
        items.append(
            AdminActivityItem(
                type="user_registered",
                title="New user registered",
                description=f"{user.full_name} ({role_value})",
                occurred_at=user.created_at,
                icon="👥",
                color="blue",
            )
        )

    recent_court_requests = db.query(CourtRequest).order_by(CourtRequest.created_at.desc()).limit(limit).all()
    for request in recent_court_requests:
        occurred_at = request.reviewed_at or request.created_at
        if not occurred_at:
            continue

        status_text = (request.status or "pending").lower()
        if status_text == "approved":
            title = f"Court '{request.name}' was approved"
            color = "green"
        elif status_text == "rejected":
            title = f"Court '{request.name}' was rejected"
            color = "orange"
        else:
            title = f"Court request '{request.name}' is pending"
            color = "orange"

        items.append(
            AdminActivityItem(
                type=f"court_request_{status_text}",
                title=title,
                description="Court listing review",
                occurred_at=occurred_at,
                icon="🏸",
                color=color,
            )
        )

    recent_ad_requests = (
        db.query(AdvertisementRequest).order_by(AdvertisementRequest.created_at.desc()).limit(limit).all()
    )
    for request in recent_ad_requests:
        occurred_at = request.reviewed_at or request.created_at
        if not occurred_at:
            continue

        status_text = (request.status or "pending").lower()
        if status_text == "approved":
            title = f"Advertisement '{request.name}' was approved"
            color = "green"
        elif status_text == "rejected":
            title = f"Advertisement '{request.name}' was rejected"
            color = "orange"
        else:
            title = f"Advertisement request '{request.name}' is pending"
            color = "orange"

        items.append(
            AdminActivityItem(
                type=f"advertisement_request_{status_text}",
                title=title,
                description="Advertisement review",
                occurred_at=occurred_at,
                icon="📣",
                color=color,
            )
        )

    pending_court_count = db.query(func.count(CourtRequest.id)).filter(CourtRequest.status == "pending").scalar() or 0
    pending_ad_count = (
        db.query(func.count(AdvertisementRequest.id))
        .filter(AdvertisementRequest.status == "pending")
        .scalar()
        or 0
    )
    total_pending = pending_court_count + pending_ad_count
    if total_pending > 0:
        latest_pending_court = (
            db.query(CourtRequest.created_at)
            .filter(CourtRequest.status == "pending")
            .order_by(CourtRequest.created_at.desc())
            .first()
        )
        latest_pending_ad = (
            db.query(AdvertisementRequest.created_at)
            .filter(AdvertisementRequest.status == "pending")
            .order_by(AdvertisementRequest.created_at.desc())
            .first()
        )
        latest_pending_time = None
        for row in [latest_pending_court, latest_pending_ad]:
            if row and row[0] and (latest_pending_time is None or row[0] > latest_pending_time):
                latest_pending_time = row[0]

        if latest_pending_time is not None:
            items.append(
                AdminActivityItem(
                    type="requests_pending_summary",
                    title=f"{total_pending} requests pending",
                    description=f"Court: {pending_court_count}, Advertisement: {pending_ad_count}",
                    occurred_at=latest_pending_time,
                    icon="📋",
                    color="orange",
                )
            )

    items.sort(key=lambda item: item.occurred_at, reverse=True)

    return AdminRecentActivityResponse(items=items[:limit])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Lấy thông tin user theo ID
    """
    user = crud_user.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin user
    """
    # Kiểm tra user có tồn tại không
    existing_user = crud_user.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    # Chỉ update các field không None
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Nếu update email, kiểm tra email đã tồn tại chưa (trừ email của chính user đó)
    if 'email' in update_data:
        email_check = crud_user.get_user_by_email(db, update_data['email'])
        if email_check and email_check.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng bởi tài khoản khác"
            )
    
    user = crud_user.update_user(db, user_id, update_data)
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Xóa user
    """
    success = crud_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    return {"message": "Xóa user thành công"}

@router.post("/test-hash")
async def test_password_hash(password: str):
    """
    Endpoint test để kiểm tra password hashing
    """
    from app.core.security import get_password_hash, verify_password
    
    hashed = get_password_hash(password)
    
    return {
        "original_password": password,
        "hashed_password": hashed,
        "hash_length": len(hashed),
        "is_bcrypt_format": hashed.startswith("$2b$"),
        "verify_result": verify_password(password, hashed),
        "info": {
            "algorithm": "bcrypt",
            "cost_factor": "12 (default)",
            "note": "Mỗi lần hash sẽ tạo ra kết quả khác nhau do salt ngẫu nhiên"
        }
    }