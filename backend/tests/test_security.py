from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_and_verify_success() -> None:
    password = "S3cure!Pass"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True


def test_password_verify_fail_with_wrong_password() -> None:
    hashed = get_password_hash("CorrectPass123")

    assert verify_password("WrongPass123", hashed) is False


def test_create_and_decode_access_token_contains_subject() -> None:
    token = create_access_token({"sub": "tester@example.com"})
    payload = decode_access_token(token)

    assert payload is not None
    assert payload.get("sub") == "tester@example.com"
    assert "exp" in payload


def test_decode_access_token_returns_none_for_invalid_token() -> None:
    payload = decode_access_token("this.is.not.a.valid.token")

    assert payload is None


def test_create_access_token_with_custom_expiration() -> None:
    token = create_access_token(
        {"sub": "custom-exp@example.com"}, expires_delta=timedelta(minutes=2)
    )
    payload = decode_access_token(token)

    assert payload is not None
    assert payload.get("sub") == "custom-exp@example.com"
    assert "exp" in payload
