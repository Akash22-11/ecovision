"""Upload service: persists citizen-submitted images to disk."""

from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.utils.helpers import generate_unique_filename
from app.utils.logger import logger
from app.utils.validators import validate_image_upload

MAX_READ_CHUNK = 1024 * 1024  # 1 MB


async def save_uploaded_image(file: UploadFile) -> str:
    The path the file was saved to (relative to the project root).
    """
    contents = await file.read()
    validate_image_upload(file, size_bytes=len(contents))

    filename = generate_unique_filename(file.filename or "upload.jpg")
    destination_dir = Path(settings.UPLOAD_ORIGINAL_DIR)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = destination_dir / filename

    with open(destination_path, "wb") as out_file:
         out_file.write(contents)

    await file.seek(0)
    logger.info(f"Saved uploaded image to {destination_path} ({len(contents)} bytes)")
    return str(destination_path)

def processed_image_path_for(original_path: str) -> str:
    """Compute the destination path for the YOLO-annotated version of an image."""
    filename = Path(original_path).name
    destination_dir = Path(settings.UPLOAD_PROCESSED_DIR)
    return str(destination_dir / filename)
