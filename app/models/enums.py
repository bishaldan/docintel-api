from enum import StrEnum


class DocumentStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class DocumentType(StrEnum):
    invoice = "invoice"
    receipt = "receipt"
    form = "form"
    report = "report"
    unknown = "unknown"


class JobStatus(StrEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ExportFormat(StrEnum):
    json = "json"
    csv = "csv"


class ExtractionType(StrEnum):
    heading = "heading"
    paragraph = "paragraph"
    field = "field"
    table = "table"


class ValidationSeverity(StrEnum):
    info = "info"
    warning = "warning"
    error = "error"
