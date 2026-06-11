from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import DocumentStatus, DocumentType


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, native_enum=False),
        default=DocumentStatus.uploaded,
        index=True,
    )
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, native_enum=False),
        default=DocumentType.unknown,
        index=True,
    )
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, default=1)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    extractions = relationship("Extraction", back_populates="document", cascade="all, delete-orphan")
    validations = relationship("ValidationFinding", back_populates="document", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")
    export_jobs = relationship("ExportJob", back_populates="document", cascade="all, delete-orphan")

