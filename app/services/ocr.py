from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import settings


class OCRProvider(ABC):
    @abstractmethod
    def extract_text(self, path: str) -> tuple[str, float]:
        raise NotImplementedError


class MockOCRProvider(OCRProvider):
    def extract_text(self, path: str) -> tuple[str, float]:
        sidecar_path = Path(f"{path}.txt")
        if sidecar_path.exists():
            return sidecar_path.read_text(encoding="utf-8"), 0.88
        return "OCR IMAGE\nDate: unknown\nTotal: unknown", 0.45


class TesseractOCRProvider(OCRProvider):
    def extract_text(self, path: str) -> tuple[str, float]:
        raise RuntimeError(
            f"Tesseract OCR is not configured for {path}. "
            "Install pytesseract/Pillow and implement this provider for production OCR."
        )


def get_ocr_provider() -> OCRProvider:
    if settings.ocr_provider == "tesseract":
        return TesseractOCRProvider()
    return MockOCRProvider()
