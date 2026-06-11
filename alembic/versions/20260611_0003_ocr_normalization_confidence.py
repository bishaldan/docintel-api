"""ocr normalization and confidence

Revision ID: 20260611_0003
Revises: 20260611_0002
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260611_0003"
down_revision: str | None = "20260611_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("confidence", sa.Float(), server_default="0.0", nullable=False),
    )
    op.add_column("extractions", sa.Column("normalized_label", sa.String(length=160), nullable=True))
    op.create_index(
        op.f("ix_extractions_normalized_label"),
        "extractions",
        ["normalized_label"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_extractions_normalized_label"), table_name="extractions")
    op.drop_column("extractions", "normalized_label")
    op.drop_column("documents", "confidence")

