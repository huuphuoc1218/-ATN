from app.core.config import Settings


def test_parse_cors_origins_accepts_list() -> None:
    origins = ["http://localhost:5173", "http://localhost:3000"]

    parsed = Settings.parse_cors_origins(origins)

    assert parsed == origins


def test_parse_cors_origins_accepts_comma_separated_string() -> None:
    value = "http://localhost:5173, http://localhost:3000"

    parsed = Settings.parse_cors_origins(value)

    assert parsed == ["http://localhost:5173", "http://localhost:3000"]


def test_parse_cors_origins_accepts_json_array_string() -> None:
    value = '["http://localhost:5173", "http://localhost:3000"]'

    parsed = Settings.parse_cors_origins(value)

    assert parsed == ["http://localhost:5173", "http://localhost:3000"]


def test_parse_cors_origins_invalid_json_returns_empty_list() -> None:
    value = "[not-json]"

    parsed = Settings.parse_cors_origins(value)

    assert parsed == []


def test_parse_cors_origins_empty_string_returns_empty_list() -> None:
    parsed = Settings.parse_cors_origins("   ")

    assert parsed == []
