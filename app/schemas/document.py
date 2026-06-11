from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DocumentStatus, DocumentType, ExportFormat, ExtractionType, JobStatus, ValidationSeverity


class DocumentRead(BaseModel):
    id: int
    filename: str
    content_type: str
    status: DocumentStatus
    document_type: DocumentType
    page_count: int
    confidence: float
    error_message: str | None
    created_at: datetime
    processed_at: datetime | None

    model_config = {"from_attributes": True}


class ExtractionRead(BaseModel):
    id: int
    document_id: int
    type: ExtractionType
    label: str | None
    normalized_label: str | None
    value: str
    page_number: int
    confidence: float

    model_config = {"from_attributes": True}


class ValidationFindingRead(BaseModel):
    id: int
    document_id: int
    severity: ValidationSeverity
    code: str
    message: str

    model_config = {"from_attributes": True}


class DocumentDetail(DocumentRead):
    extractions: list[ExtractionRead]
    validations: list[ValidationFindingRead]


class ProcessingJobRead(BaseModel):
    id: int
    document_id: int
    status: JobStatus
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ExportJobCreate(BaseModel):
    format: ExportFormat


class ExportJobRead(BaseModel):
    id: int
    document_id: int
    format: ExportFormat
    status: JobStatus
    filename: str | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
