"""Reusable validation helpers used by routes and services."""

from datetime import date

from fastapi import UploadFile

from app.utils.constants import ALLOWED_IMAGE_CONTENT_TYPES, MAX_IMAGE_SIZE_BYTES


class ValidationError(Exception):
    """Raised for domain-level validation failures (caught by exception handlers)."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_coordinates(latitude: float, longitude: float) -> None:
    """Ensure latitude/longitude fall within valid geographic ranges."""
    if not (-90.0 <= latitude <= 90.0):
        raise ValidationError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
    if not (-180.0 <= longitude <= 180.0):
        raise ValidationError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")


def validate_image_upload(file: UploadFile, size_bytes: int) -> None:
    """Validate an uploaded image's content type and size before persisting it."""
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(
            f"Unsupported file type '{file.content_type}'. "
            f"Allowed types: {', '.join(sorted(ALLOWED_IMAGE_CONTENT_TYPES))}."
        )
    if size_bytes > MAX_IMAGE_SIZE_BYTES:
        max_mb = MAX_IMAGE_SIZE_BYTES // (1024 * 1024)
        raise ValidationError(f"Image exceeds maximum allowed size of {max_mb} MB.")
    if size_bytes == 0:
        raise ValidationError("Uploaded image file is empty.")


def validate_date_range(start: date | None, end: date | None) -> None:
    """Ensure a filter date range is logically ordered."""
    if start and end and start > end:
        raise ValidationError("start_date cannot be after end_date.")
