from __future__ import annotations

from pathlib import Path
from typing import Optional

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def _ensure_cloudinary_configured() -> None:
    if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY or not settings.CLOUDINARY_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary is not configured. Missing CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET.",
        )

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def _normalized_extension(filename: str, fallback: str = ".jpg") -> str:
    ext = Path(filename or "").suffix.lower()
    return ext if ext else fallback


async def upload_image_to_cloudinary(
    file: UploadFile,
    *,
    subfolder: str,
    public_id_prefix: Optional[str] = None,
) -> str:
    """Upload an image file to Cloudinary and return secure URL."""
    _ensure_cloudinary_configured()

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    return upload_image_bytes_to_cloudinary(
        file_bytes,
        filename=file.filename or "",
        subfolder=subfolder,
        public_id_prefix=public_id_prefix,
    )


def upload_image_bytes_to_cloudinary(
    file_bytes: bytes,
    *,
    filename: str,
    subfolder: str,
    public_id_prefix: Optional[str] = None,
) -> str:
    """Upload raw image bytes to Cloudinary and return secure URL."""
    _ensure_cloudinary_configured()

    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    ext = _normalized_extension(filename)
    base_folder = settings.CLOUDINARY_FOLDER.strip("/")
    target_folder = f"{base_folder}/{subfolder.strip('/')}" if base_folder else subfolder.strip("/")

    upload_kwargs = {
        "folder": target_folder,
        "resource_type": "image",
    }

    if public_id_prefix:
        upload_kwargs["public_id"] = f"{public_id_prefix}{ext}"
        upload_kwargs["overwrite"] = True

    try:
        result = cloudinary.uploader.upload(file_bytes, **upload_kwargs)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to upload image to Cloudinary: {exc}",
        ) from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cloudinary upload did not return secure URL",
        )

    return secure_url
