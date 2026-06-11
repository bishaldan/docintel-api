from datetime import UTC, datetime

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.enums import DocumentStatus, DocumentType, ExtractionType, JobStatus, ValidationSeverity
from app.models.extraction import Extraction, ValidationFinding
from app.models.job import ProcessingJob
from app.services.normalization import normalize_label, normalize_value
from app.services.storage import read_document_text_with_confidence

REQUIRED_FIELDS_BY_TYPE = {
    DocumentType.invoice: {"name", "date", "total"},
    DocumentType.receipt: {"merchant", "date", "total"},
    DocumentType.form: {"name", "date"},
    DocumentType.report: set(),
    DocumentType.unknown: {"date"},
}


def process_document(
    db: Session,
    document: Document,
    processing_job: ProcessingJob | None = None,
) -> Document:
    document.status = DocumentStatus.processing
    if processing_job is not None:
        processing_job.status = JobStatus.processing
        processing_job.started_at = datetime.now(UTC)
    db.flush()
    try:
        text, page_count, source_confidence = read_document_text_with_confidence(
            document.storage_path,
            document.content_type,
        )
        document.raw_text = text
        document.page_count = page_count
        document.document_type = detect_document_type(text)
        document.confidence = source_confidence
        db.execute(delete(Extraction).where(Extraction.document_id == document.id))
        db.execute(delete(ValidationFinding).where(ValidationFinding.document_id == document.id))
        extractions = extract_structure(document.id, text, source_confidence)
        for extraction in extractions:
            db.add(extraction)
        document.confidence = calculate_document_confidence(extractions, source_confidence)
        for finding in validate_document(document.id, text, document.document_type, document.confidence):
            db.add(finding)
        document.status = DocumentStatus.completed
        document.processed_at = datetime.now(UTC)
        if processing_job is not None:
            processing_job.status = JobStatus.completed
            processing_job.completed_at = datetime.now(UTC)
    except Exception as exc:
        document.status = DocumentStatus.failed
        document.error_message = str(exc)
        if processing_job is not None:
            processing_job.status = JobStatus.failed
            processing_job.error_message = str(exc)
            processing_job.completed_at = datetime.now(UTC)
    return document


def detect_document_type(text: str) -> DocumentType:
    normalized = text.lower()
    if "invoice" in normalized or {"invoice number", "bill to"} & set(normalized.splitlines()):
        return DocumentType.invoice
    if "receipt" in normalized or "merchant:" in normalized:
        return DocumentType.receipt
    if "form" in normalized or "application" in normalized:
        return DocumentType.form
    if "report" in normalized or "summary" in normalized:
        return DocumentType.report
    return DocumentType.unknown


def extract_structure(
    document_id: int,
    text: str,
    source_confidence: float = 0.9,
) -> list[Extraction]:
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
                    normalized_label="table",
                    value="\n".join(current_table),
                    confidence=min(source_confidence, 0.82),
                )
            )
            current_table = []
        if ":" in line and len(line.split(":", 1)[0]) <= 40:
            label, value = line.split(":", 1)
            normalized = normalize_label(label)
            extractions.append(
                Extraction(
                    document_id=document_id,
                    type=ExtractionType.field,
                    label=label.strip().lower(),
                    normalized_label=normalized,
                    value=normalize_value(normalized, value),
                    confidence=min(source_confidence, 0.94),
                )
            )
        elif line.isupper() or line.startswith("#"):
            extractions.append(
                Extraction(
                    document_id=document_id,
                    type=ExtractionType.heading,
                    label="heading",
                    normalized_label="heading",
                    value=line.lstrip("# ").strip(),
                    confidence=min(source_confidence, 0.9),
                )
            )
        else:
            extractions.append(
                Extraction(
                    document_id=document_id,
                    type=ExtractionType.paragraph,
                    label=None,
                    normalized_label=None,
                    value=line,
                    confidence=min(source_confidence, 0.86),
                )
            )
    if current_table:
        extractions.append(
            Extraction(
                document_id=document_id,
                type=ExtractionType.table,
                label="table",
                normalized_label="table",
                value="\n".join(current_table),
                confidence=min(source_confidence, 0.82),
            )
        )
    return extractions


def calculate_document_confidence(extractions: list[Extraction], source_confidence: float) -> float:
    if not extractions:
        return source_confidence
    average_extraction_confidence = sum(item.confidence for item in extractions) / len(extractions)
    return round((average_extraction_confidence + source_confidence) / 2, 3)


def validate_document(
    document_id: int,
    text: str,
    document_type: DocumentType,
    confidence: float,
) -> list[ValidationFinding]:
    found_fields = {
        normalize_label(line.split(":", 1)[0])
        for line in text.splitlines()
        if ":" in line and len(line.split(":", 1)[0]) <= 40
    }
    findings: list[ValidationFinding] = []
    required_fields = REQUIRED_FIELDS_BY_TYPE[document_type]
    for field in sorted(required_fields - found_fields):
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
    if confidence < 0.7:
        findings.append(
            ValidationFinding(
                document_id=document_id,
                severity=ValidationSeverity.warning,
                code="low_confidence",
                message="Document extraction confidence is below the recommended threshold.",
            )
        )
    return findings
