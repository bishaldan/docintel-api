from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import Document
from app.services.extraction import process_document
from app.tasks.celery_app import celery_app


@celery_app.task
def process_document_job(document_id: int) -> dict[str, str | int]:
    db = SessionLocal()
    try:
        document = db.scalar(select(Document).where(Document.id == document_id))
        if document is None:
            return {"document_id": document_id, "status": "not_found"}
        process_document(db, document)
        db.commit()
        return {"document_id": document_id, "status": document.status.value}
    finally:
        db.close()

