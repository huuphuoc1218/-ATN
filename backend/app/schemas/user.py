from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str
    role: Optional[UserRole] = None

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None
    role: Optional[UserRole] = UserRole.user

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None
    
    # Bank account fields (for owners)
    bank_account_number: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_name: Optional[str] = None
    bank_code: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    role: UserRole
    
    # Bank account info (for owners)
    bank_account_number: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_name: Optional[str] = None
    bank_code: Optional[str] = None

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int


class AdminActivityItem(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    occurred_at: datetime
    icon: str
    color: str


class AdminRecentActivityResponse(BaseModel):
    items: List[AdminActivityItem]

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Aliases for backward compatibility
User = UserResponse
UserCreate = UserRegister