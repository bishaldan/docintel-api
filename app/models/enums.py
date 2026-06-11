from enum import StrEnum


class DocumentStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ExtractionType(StrEnum):
    heading = "heading"
    paragraph = "paragraph"
    field = "field"
    table = "table"


class ValidationSeverity(StrEnum):
    info = "info"
    warning = "warning"
    error = "error"

