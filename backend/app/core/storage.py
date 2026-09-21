from pathlib import Path
from app.core.config import settings


BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _resolve_uploads_root() -> Path:
    """Resolve uploads root, allowing override for persistent production disks."""
    if settings.UPLOADS_ROOT_DIR:
        return Path(settings.UPLOADS_ROOT_DIR).expanduser().resolve()
    return BACKEND_ROOT / "uploads"


def ensure_uploads_root() -> Path:
    """Ensure uploads root exists and return it."""
    uploads_root = _resolve_uploads_root()
    uploads_root.mkdir(parents=True, exist_ok=True)
    return uploads_root


def ensure_uploads_subdir(*parts: str) -> Path:
    """Ensure uploads subdirectory exists and return it."""
    base = ensure_uploads_root()
    target = base.joinpath(*parts)
    target.mkdir(parents=True, exist_ok=True)
    return target