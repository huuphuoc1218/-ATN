from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import GoogleAuthRequest, UserLogin, UserRegister, Token

router = APIRouter()


def _serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "phone_number": user.phone_number,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "bank_account_number": user.bank_account_number,
        "bank_account_name": user.bank_account_name,
        "bank_name": user.bank_name,
        "bank_code": user.bank_code,
    }


def _build_auth_response(user: User) -> dict:
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": _serialize_user(user),
    }


def _verify_google_credential(credential: str) -> dict:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google client ID is not configured",
        )

    try:
        payload = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID.strip(),
            clock_skew_in_seconds=10,
        )
    except ValueError as exc:
        print(f"❌ GOOGLE VERIFY FAILED REASON: {exc}")  
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google token verify error: {exc}",  
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Không thể xác minh Google token. Vui lòng kiểm tra kết nối backend tới Google.",
        ) from exc

    if not payload.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account has not been verified",
        )

    return payload

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    
    # Clean email
    email = user_data.email.strip().lower()
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email không tồn tại"  
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mật khẩu không chính xác" 
        )
    
    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa"
        )
    
    return _build_auth_response(user)

@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    
    # Clean email
    email = user_data.email.strip().lower()
    # Check if email exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký. Vui lòng sử dụng email khác."
        )
    
    # Validate role
    valid_roles = [UserRole.user.value, UserRole.owner.value, UserRole.enterprise.value]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role không hợp lệ. Chỉ chấp nhận: {', '.join(valid_roles)}"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=user_data.full_name.strip(),
        phone_number=user_data.phone_number.strip() if user_data.phone_number else None,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return _build_auth_response(new_user)


@router.post("/google", response_model=Token)
def google_auth(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    google_payload = _verify_google_credential(payload.credential)
    allowed_google_roles = {UserRole.user, UserRole.owner, UserRole.enterprise}
    selected_role = payload.role

    if selected_role is not None and selected_role not in allowed_google_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google sign-in/sign-up chỉ hỗ trợ user, owner, enterprise",
        )

    email = str(google_payload.get("email", "")).strip().lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account does not contain an email address",
        )

    full_name = str(google_payload.get("name") or email.split("@", 1)[0]).strip() or email.split("@", 1)[0]
    avatar_url = google_payload.get("picture")

    user = db.query(User).filter(User.email == email).first()

    if user:
        if user.role not in allowed_google_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Google sign-in/sign-up chỉ hỗ trợ user, owner, enterprise",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị khóa",
            )

        # For existing accounts, allow login regardless of selected role
        # (only role-match is enforced during signup for new accounts)
        return _build_auth_response(user)

    if selected_role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng chọn role trước khi đăng ký bằng Google",
        )

    google_password = token_urlsafe(32)
    new_user = User(
        email=email,
        hashed_password=get_password_hash(google_password),
        full_name=full_name,
        phone_number=None,
        avatar_url=avatar_url,
        role=selected_role,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return _build_auth_response(new_user)