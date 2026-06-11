from datetime import UTC, datetime

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.enums import DocumentStatus, ExtractionType, ValidationSeverity
from app.models.extraction import Extraction, ValidationFinding
from app.services.storage import read_text

REQUIRED_FIELDS = {"name", "date", "total"}


def process_document(db: Session, document: Document) -> Document:
    document.status = DocumentStatus.processing
    db.flush()
    try:
        text = read_text(document.storage_path)
        document.raw_text = text
        db.execute(delete(Extraction).where(Extraction.document_id == document.id))
        db.execute(delete(ValidationFinding).where(ValidationFinding.document_id == document.id))
        for extraction in extract_structure(document.id, text):
            db.add(extraction)
        for finding in validate_document(document.id, text):
            db.add(finding)
        document.status = DocumentStatus.completed
        document.processed_at = datetime.now(UTC)
    except Exception as exc:
        document.status = DocumentStatus.failed
        document.error_message = str(exc)
    return document


def extract_structure(document_id: int, text: str) -> list[Extraction]:
    extractions: list[Extraction] = []
    current_table: list[str] = []
    for line in [line.strip() for line in text.splitlines() if line.strip()]:
        if "|" in line:
            current_table.append(line)
            continue
        if current_table:
            extractions.append(
                Extraction(
                    document_id=document_id,
                    type=ExtractionType.table,
                    label="table",
                    value="\n".join(current_table),
                    confidence=0.82,
                )
            )
            current_table = []
        if ":" in line and len(line.split(":", 1)[0]) <= 40:
            label, value = line.split(":", 1)
            extractions.append(
                Extraction(
                    document_id=document_id,
                    type=ExtractionType.field,
                    label=label.strip().lower(),
                    value=value.strip(),
                    confidence=0.94,
                )
            )
        elif line.isupper() or line.startswith("#"):
            extractions.append(
                Extraction(
                    document_id=document_id,
                    type=ExtractionType.heading,
                    label="heading",
                    value=line.lstrip("# ").strip(),
                    confidence=0.9,
                )
            )
        else:
            extractions.append(
                Extraction(
                    document_id=document_id,
                    type=ExtractionType.paragraph,
                    label=None,
                    value=line,
                    confidence=0.86,
                )
            )
    if current_table:
        extractions.append(
            Extraction(
                document_id=document_id,
                type=ExtractionType.table,
                label="table",
                value="\n".join(current_table),
                confidence=0.82,
            )
        )
    return extractions


def validate_document(document_id: int, text: str) -> list[ValidationFinding]:
    found_fields = {
        line.split(":", 1)[0].strip().lower()
        for line in text.splitlines()
        if ":" in line and len(line.split(":", 1)[0]) <= 40
    }
    findings: list[ValidationFinding] = []
    for field in sorted(REQUIRED_FIELDS - found_fields):
        findings.append(
            ValidationFinding(
                document_id=document_id,
                severity=ValidationSeverity.warning,
                code="missing_required_field",
                message=f"Required field '{field}' was not found.",
            )
        )
    if len(text.strip()) < 40:
        findings.append(
            ValidationFinding(
                document_id=document_id,
                severity=ValidationSeverity.warning,
                code="low_text_volume",
                message="Document contains very little extractable text.",
            )
        )
    return findings

