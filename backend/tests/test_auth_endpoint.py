from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.endpoints import auth
from app.models.user import UserRole
from app.schemas.user import GoogleAuthRequest, UserLogin, UserRegister


class FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class FakeDB:
    def __init__(self, query_result=None):
        self.query_result = query_result
        self.added = []
        self.committed = False
        self.refreshed = False

    def query(self, model):
        return FakeQuery(self.query_result)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed = True


def _build_user(**overrides):
    base = {
        "id": 1,
        "email": "user@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User",
        "role": "user",
        "phone_number": "0900000000",
        "avatar_url": None,
        "is_active": True,
        "bank_account_number": None,
        "bank_account_name": None,
        "bank_name": None,
        "bank_code": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_login_fails_when_user_not_found(monkeypatch):
    db = FakeDB(query_result=None)

    with pytest.raises(HTTPException) as exc_info:
        auth.login(UserLogin(email="none@example.com", password="123456"), db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Email không tồn tại"


def test_login_fails_when_password_invalid(monkeypatch):
    user = _build_user()
    db = FakeDB(query_result=user)
    monkeypatch.setattr(auth, "verify_password", lambda plain, hashed: False)

    with pytest.raises(HTTPException) as exc_info:
        auth.login(UserLogin(email="user@example.com", password="wrong"), db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Mật khẩu không chính xác"


def test_login_fails_when_user_inactive(monkeypatch):
    user = _build_user(is_active=False)
    db = FakeDB(query_result=user)
    monkeypatch.setattr(auth, "verify_password", lambda plain, hashed: True)

    with pytest.raises(HTTPException) as exc_info:
        auth.login(UserLogin(email="user@example.com", password="123456"), db)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Tài khoản đã bị khóa"


def test_login_success_returns_token_and_user(monkeypatch):
    user = _build_user(email="User@Example.com")
    db = FakeDB(query_result=user)

    monkeypatch.setattr(auth, "verify_password", lambda plain, hashed: True)
    monkeypatch.setattr(auth, "create_access_token", lambda data: "jwt-token")

    result = auth.login(UserLogin(email=" user@example.com ", password="123456"), db)

    assert result["access_token"] == "jwt-token"
    assert result["token_type"] == "bearer"
    assert result["user"]["email"] == "User@Example.com"


def test_register_fails_when_email_exists():
    existing_user = _build_user()
    db = FakeDB(query_result=existing_user)

    with pytest.raises(HTTPException) as exc_info:
        auth.register(
            UserRegister(
                email="user@example.com",
                password="123456",
                full_name="User",
                role="user",
            ),
            db,
        )

    assert exc_info.value.status_code == 400


def test_register_fails_when_role_invalid():
    db = FakeDB(query_result=None)

    with pytest.raises(HTTPException) as exc_info:
        auth.register(
            UserRegister(
                email="user2@example.com",
                password="123456",
                full_name="User 2",
                role="admin",
            ),
            db,
        )

    assert exc_info.value.status_code == 400


def test_register_success_creates_user(monkeypatch):
    db = FakeDB(query_result=None)
    monkeypatch.setattr(auth, "get_password_hash", lambda password: "hashed-new-pass")
    monkeypatch.setattr(auth, "create_access_token", lambda data: "new-jwt-token")

    payload = UserRegister(
        email=" NewUser@Example.com ",
        password="123456",
        full_name="  New User  ",
        phone_number=" 0901234567 ",
        role="owner",
    )

    result = auth.register(payload, db)

    assert db.committed is True
    assert db.refreshed is True
    assert len(db.added) == 1
    created_user = db.added[0]
    assert created_user.email == "newuser@example.com"
    assert created_user.full_name == "New User"
    assert created_user.phone_number == "0901234567"
    assert created_user.role == "owner"

    assert result["access_token"] == "new-jwt-token"
    assert result["user"]["email"] == "newuser@example.com"


def test_google_auth_creates_user_with_user_role(monkeypatch):
    db = FakeDB(query_result=None)
    monkeypatch.setattr(auth, "_verify_google_credential", lambda credential: {
        "email": "google.user@example.com",
        "name": "Google User",
        "picture": "https://example.com/avatar.png",
        "email_verified": True,
    })
    monkeypatch.setattr(auth, "get_password_hash", lambda password: "hashed-google-pass")
    monkeypatch.setattr(auth, "create_access_token", lambda data: "google-jwt-token")

    result = auth.google_auth(GoogleAuthRequest(credential="google-token", role=UserRole.user), db)

    assert db.committed is True
    assert db.refreshed is True
    assert len(db.added) == 1
    created_user = db.added[0]
    assert created_user.email == "google.user@example.com"
    assert created_user.role == UserRole.user
    assert created_user.avatar_url == "https://example.com/avatar.png"
    assert result["access_token"] == "google-jwt-token"
    assert result["user"]["role"] == UserRole.user


def test_google_auth_rejects_when_selected_role_mismatch_existing_account(monkeypatch):
    existing_user = _build_user(role=UserRole.owner)
    db = FakeDB(query_result=existing_user)
    monkeypatch.setattr(auth, "_verify_google_credential", lambda credential: {
        "email": "user@example.com",
        "name": "User",
        "picture": None,
        "email_verified": True,
    })

    with pytest.raises(HTTPException) as exc_info:
        auth.google_auth(GoogleAuthRequest(credential="google-token", role=UserRole.user), db)

    assert exc_info.value.status_code == 400
