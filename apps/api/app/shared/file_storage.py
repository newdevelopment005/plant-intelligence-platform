import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings


def get_upload_path(module: str, filename: str) -> Path:
    base = Path(settings.STORAGE_LOCAL_PATH)
    unique_name = f"{uuid.uuid4()}_{filename}"
    upload_dir = base / module
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir / unique_name


def get_file_url(module: str, filename: str) -> str:
    path = get_upload_path(module, filename)
    return f"/storage/{module}/{path.name}"


async def save_uploaded_file(file: UploadFile, module: str) -> str:
    filename = file.filename or "upload"
    path = get_upload_path(module, filename)
    content = await file.read()
    path.write_bytes(content)
    return get_file_url(module, path.name)
