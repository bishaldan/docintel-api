from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ExtractionType, ValidationSeverity


class Extraction(Base):
    __tablename__ = "extractions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    type: Mapped[ExtractionType] = mapped_column(Enum(ExtractionType, native_enum=False), index=True)
    label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    normalized_label: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    confidence: Mapped[float] = mapped_column(Float, default=0.9)

    document = relationship("Document", back_populates="extractions")


class ValidationFinding(Base):
    __tablename__ = "validation_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    severity: Mapped[ValidationSeverity] = mapped_column(Enum(ValidationSeverity, native_enum=False), index=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    document = relationship("Document", back_populates="validations")
