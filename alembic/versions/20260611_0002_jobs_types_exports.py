"""jobs types and exports

Revision ID: 20260611_0002
Revises: 20260611_0001
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260611_0002"
down_revision: str | None = "20260611_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("document_type", sa.String(length=40), server_default="unknown", nullable=False),
    )
    op.create_index(op.f("ix_documents_document_type"), "documents", ["document_type"], unique=False)

    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_processing_jobs_document_id"), "processing_jobs", ["document_id"], unique=False)
    op.create_index(op.f("ix_processing_jobs_id"), "processing_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_processing_jobs_status"), "processing_jobs", ["status"], unique=False)

    op.create_table(
        "export_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("format", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_export_jobs_document_id"), "export_jobs", ["document_id"], unique=False)
    op.create_index(op.f("ix_export_jobs_format"), "export_jobs", ["format"], unique=False)
    op.create_index(op.f("ix_export_jobs_id"), "export_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_export_jobs_status"), "export_jobs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_export_jobs_status"), table_name="export_jobs")
    op.drop_index(op.f("ix_export_jobs_id"), table_name="export_jobs")
    op.drop_index(op.f("ix_export_jobs_format"), table_name="export_jobs")
    op.drop_index(op.f("ix_export_jobs_document_id"), table_name="export_jobs")
    op.drop_table("export_jobs")
    op.drop_index(op.f("ix_processing_jobs_status"), table_name="processing_jobs")
    op.drop_index(op.f("ix_processing_jobs_id"), table_name="processing_jobs")
    op.drop_index(op.f("ix_processing_jobs_document_id"), table_name="processing_jobs")
    op.drop_table("processing_jobs")
    op.drop_index(op.f("ix_documents_document_type"), table_name="documents")
    op.drop_column("documents", "document_type")

