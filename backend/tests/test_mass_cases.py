from types import SimpleNamespace

import pytest

from app.api.endpoints.bookings import _normalize_status_value
from app.core.security import decode_access_token, get_password_hash, verify_password


PASSWORD_CASES = [
    "pw-01-Alpha!",
    "pw-02-Beta@",
    "pw-03-Gamma#",
    "pw-04-Delta$",
    "pw-05-Epsilon%",
    "pw-06-Zeta^",
    "pw-07-Eta&",
    "pw-08-Theta*",
    "pw-09-Iota(",
    "pw-10-Kappa)",
    "pw-11-Lambda_",
    "pw-12-Mu+",
    "pw-13-Nu=",
    "pw-14-Xi-",
    "pw-15-Omicron{",
    "pw-16-Pi}",
    "pw-17-Rho[",
    "pw-18-Sigma]",
    "pw-19-Tau:",
    "pw-20-Upsilon;",
    "pw-21-Phi<",
    "pw-22-Chi>",
    "pw-23-Psi,",
    "pw-24-Omega.",
    "pw-25-Case/",
    "pw-26-Case?",
    "pw-27-Case|",
    "pw-28-Case~",
    "pw-29-Case`",
    "pw-30-Case!",
]


INVALID_TOKEN_CASES = [
    "",
    "not-a-jwt",
    "...",
    "abc.def",
    "abc.def.ghi",
    "123.456.789",
    "Bearer token",
    "header.payload.signature",
    "a.b.c.d",
    "####",
    "null",
    "undefined",
    "   ",
    "jwt jwt jwt",
    "漢字.token.test",
    "x.y.z",
    "short.token.x",
    "a..c",
    "..",
    "corrupted-token-value",
]


NORMALIZE_CASES = [
    (None, ""),
    ("", ""),
    ("   ", ""),
    ("ACTIVE", "active"),
    (" pending ", "pending"),
    ("BookingStatus.ACTIVE", "active"),
    ("PaymentStatus.PAID", "paid"),
    ("user", "user"),
    ("ADMIN", "admin"),
    ("completed", "completed"),
    ("cancelled", "cancelled"),
    ("Active", "active"),
    ("PENDING", "pending"),
    ("status.with.dot", "dot"),
    ("x.y.z", "z"),
    (0, "0"),
    (1, "1"),
    (True, "true"),
    (False, "false"),
    (SimpleNamespace(value="ACTIVE"), "active"),
    (SimpleNamespace(value="BookingStatus.CONFIRMED"), "confirmed"),
    (SimpleNamespace(value=" pending "), "pending"),
    (SimpleNamespace(value=""), ""),
    (SimpleNamespace(value=None), "none"),
    (SimpleNamespace(value=123), "123"),
    (SimpleNamespace(value="user.role.owner"), "owner"),
    (SimpleNamespace(value="A.B.C"), "c"),
    (SimpleNamespace(value=" single "), "single"),
]


@pytest.mark.parametrize("password", PASSWORD_CASES)
def test_password_hash_roundtrip_mass(password: str) -> None:
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password(f"{password}-wrong", hashed) is False


@pytest.mark.parametrize("token", INVALID_TOKEN_CASES)
def test_decode_access_token_invalid_mass(token: str) -> None:
    payload = decode_access_token(token)

    assert payload is None


@pytest.mark.parametrize("raw_value,expected", NORMALIZE_CASES)
def test_normalize_status_value_mass(raw_value: object, expected: str) -> None:
    assert _normalize_status_value(raw_value) == expected
