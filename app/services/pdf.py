from pathlib import Path

from pypdf import PdfReader


def extract_pdf_text(path: str) -> tuple[str, int]:
    reader = PdfReader(Path(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        pages.append(f"--- Page {index} ---\n{page_text.strip()}")
    return "\n\n".join(pages).strip(), max(len(reader.pages), 1)
