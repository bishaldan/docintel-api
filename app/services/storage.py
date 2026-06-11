from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.services.pdf import extract_pdf_text


def save_upload(upload: UploadFile) -> str:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename or "document.txt").suffix or ".txt"
    path = upload_dir / f"{uuid4()}{suffix}"
    with path.open("wb") as target:
        target.write(upload.file.read())
    return str(path)


def read_text(path: str) -> str:
    data = Path(path).read_bytes()
    return data.decode("utf-8", errors="ignore")


def read_document_text(path: str, content_type: str) -> tuple[str, int]:
    if content_type == "application/pdf" or Path(path).suffix.lower() == ".pdf":
        return extract_pdf_text(path)
    return read_text(path), 1
