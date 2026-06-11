from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ExportFormat, JobStatus


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False),
        default=JobStatus.pending,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    document = relationship("Document", back_populates="processing_jobs")


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    format: Mapped[ExportFormat] = mapped_column(Enum(ExportFormat, native_enum=False), index=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False),
        default=JobStatus.pending,
        index=True,
    )
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    document = relationship("Document", back_populates="export_jobs")
