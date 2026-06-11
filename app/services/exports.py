import csv
import json
from datetime import UTC, datetime
from io import StringIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ExportFormat, JobStatus
from app.models.extraction import Extraction
from app.models.job import ExportJob


def extractions_to_json(extractions: list[Extraction]) -> str:
    payload = [
        {
            "type": extraction.type.value,
            "label": extraction.label,
            "value": extraction.value,
            "page_number": extraction.page_number,
            "confidence": extraction.confidence,
        }
        for extraction in extractions
    ]
    return json.dumps(payload, indent=2)


def extractions_to_csv(extractions: list[Extraction]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["type", "label", "value", "page_number", "confidence"])
    for extraction in extractions:
        writer.writerow(
            [
                extraction.type.value,
                extraction.label or "",
                extraction.value,
                extraction.page_number,
                extraction.confidence,
            ]
        )
    return buffer.getvalue()


def generate_export_job(db: Session, export_job: ExportJob) -> ExportJob:
    export_job.status = JobStatus.processing
    extractions = list(
        db.scalars(select(Extraction).where(Extraction.document_id == export_job.document_id))
    )
    if export_job.format == ExportFormat.json:
        export_job.content = extractions_to_json(extractions)
        export_job.filename = f"document-{export_job.document_id}.json"
    else:
        export_job.content = extractions_to_csv(extractions)
        export_job.filename = f"document-{export_job.document_id}.csv"
    export_job.status = JobStatus.completed
    export_job.completed_at = datetime.now(UTC)
    return export_job
