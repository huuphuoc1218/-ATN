from datetime import datetime, timedelta
from types import SimpleNamespace

from app.api.endpoints.bookings import _get_effective_history_status, _is_invitable_booking, _normalize_status_value


def test_normalize_status_value_from_enum_like_object() -> None:
    enum_like = SimpleNamespace(value="BookingStatus.ACTIVE")

    normalized = _normalize_status_value(enum_like)

    assert normalized == "active"


def test_get_effective_history_status_prioritizes_cancelled() -> None:
    booking = SimpleNamespace(
        booking_status="active",
        status="cancelled",
        booking_date=datetime.utcnow(),
        end_time="23:59",
    )

    status_value = _get_effective_history_status(booking)

    assert status_value == "cancelled"


def test_get_effective_history_status_marks_completed_for_past_active_booking() -> None:
    booking = SimpleNamespace(
        booking_status="active",
        status="active",
        booking_date=datetime.utcnow() - timedelta(days=1),
        end_time="00:01",
    )

    status_value = _get_effective_history_status(booking)

    assert status_value == "completed"


def test_is_invitable_booking_true_for_confirmed_status() -> None:
    booking = SimpleNamespace(booking_status="confirmed", status="pending")

    assert _is_invitable_booking(booking) is True


def test_is_invitable_booking_false_for_pending_status() -> None:
    booking = SimpleNamespace(booking_status="pending", status="pending")

    assert _is_invitable_booking(booking) is False
