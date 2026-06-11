from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DocumentStatus, ExtractionType, ValidationSeverity


class DocumentRead(BaseModel):
    id: int
    filename: str
    content_type: str
    status: DocumentStatus
    page_count: int
    error_message: str | None
    created_at: datetime
    processed_at: datetime | None

    model_config = {"from_attributes": True}


class ExtractionRead(BaseModel):
    id: int
    document_id: int
    type: ExtractionType
    label: str | None
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

