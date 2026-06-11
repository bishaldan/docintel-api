from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.document import Document
from app.models.enums import DocumentStatus, ExportFormat, JobStatus
from app.models.extraction import Extraction, ValidationFinding
from app.models.job import ExportJob, ProcessingJob
from app.schemas.document import (
    DocumentDetail,
    DocumentRead,
    ExportJobCreate,
    ExportJobRead,
    ExtractionRead,
    ProcessingJobRead,
    ValidationFindingRead,
)
from app.services.exports import extractions_to_csv, extractions_to_json, generate_export_job
from app.services.extraction import process_document
from app.services.storage import save_upload

router = APIRouter()


@router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Document:
    storage_path = save_upload(file)
    document = Document(
        filename=file.filename or "document.txt",
        content_type=file.content_type or "application/octet-stream",
        storage_path=storage_path,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return list(db.scalars(select(Document).order_by(Document.created_at.desc())))


@router.get("/documents/{document_id}", response_model=DocumentDetail)
def read_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.scalar(
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.extractions), selectinload(Document.validations))
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post(
    "/documents/{document_id}/process",
    response_model=ProcessingJobRead,
    status_code=status.HTTP_201_CREATED,
)
def process_document_endpoint(document_id: int, db: Session = Depends(get_db)) -> ProcessingJob:
    document = db.scalar(select(Document).where(Document.id == document_id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    processing_job = ProcessingJob(document_id=document.id)
    db.add(processing_job)
    db.flush()
    process_document(db, document, processing_job)
    db.commit()
    db.refresh(processing_job)
    return processing_job


@router.get("/documents/{document_id}/jobs", response_model=list[ProcessingJobRead])
def list_processing_jobs(document_id: int, db: Session = Depends(get_db)) -> list[ProcessingJob]:
    ensure_document_exists(db, document_id)
    return list(
        db.scalars(
            select(ProcessingJob)
            .where(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.created_at.desc())
        )
    )


@router.get("/documents/{document_id}/jobs/{job_id}", response_model=ProcessingJobRead)
def read_processing_job(
    document_id: int,
    job_id: int,
    db: Session = Depends(get_db),
) -> ProcessingJob:
    ensure_document_exists(db, document_id)
    job = db.scalar(
        select(ProcessingJob).where(
            ProcessingJob.id == job_id,
            ProcessingJob.document_id == document_id,
        )
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processing job not found")
    return job


@router.get("/documents/{document_id}/extractions", response_model=list[ExtractionRead])
def list_extractions(document_id: int, db: Session = Depends(get_db)) -> list[Extraction]:
    ensure_document_exists(db, document_id)
    return list(db.scalars(select(Extraction).where(Extraction.document_id == document_id)))


@router.get("/documents/{document_id}/validations", response_model=list[ValidationFindingRead])
def list_validations(document_id: int, db: Session = Depends(get_db)) -> list[ValidationFinding]:
    ensure_document_exists(db, document_id)
    return list(db.scalars(select(ValidationFinding).where(ValidationFinding.document_id == document_id)))


@router.get("/documents/{document_id}/exports/json")
def export_json(document_id: int, db: Session = Depends(get_db)) -> Response:
    ensure_processed(db, document_id)
    extractions = list(db.scalars(select(Extraction).where(Extraction.document_id == document_id)))
    return Response(content=extractions_to_json(extractions), media_type="application/json")


@router.get("/documents/{document_id}/exports/csv")
def export_csv(document_id: int, db: Session = Depends(get_db)) -> Response:
    ensure_processed(db, document_id)
    extractions = list(db.scalars(select(Extraction).where(Extraction.document_id == document_id)))
    return Response(
        content=extractions_to_csv(extractions),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="document-{document_id}.csv"'},
    )


@router.post(
    "/documents/{document_id}/export-jobs",
    response_model=ExportJobRead,
    status_code=status.HTTP_201_CREATED,
)
def create_export_job(
    document_id: int,
    payload: ExportJobCreate,
    db: Session = Depends(get_db),
) -> ExportJob:
    ensure_processed(db, document_id)
    export_job = ExportJob(document_id=document_id, format=payload.format)
    db.add(export_job)
    db.flush()
    generate_export_job(db, export_job)
    db.commit()
    db.refresh(export_job)
    return export_job


@router.get("/documents/{document_id}/export-jobs/{export_id}", response_model=ExportJobRead)
def read_export_job(document_id: int, export_id: int, db: Session = Depends(get_db)) -> ExportJob:
    ensure_document_exists(db, document_id)
    export_job = db.scalar(
        select(ExportJob).where(
            ExportJob.id == export_id,
            ExportJob.document_id == document_id,
        )
    )
    if export_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    return export_job


@router.get("/documents/{document_id}/export-jobs/{export_id}/download")
def download_export_job(document_id: int, export_id: int, db: Session = Depends(get_db)) -> Response:
    ensure_document_exists(db, document_id)
    export_job = db.scalar(
        select(ExportJob).where(
            ExportJob.id == export_id,
            ExportJob.document_id == document_id,
        )
    )
    if export_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    if export_job.status != JobStatus.completed or export_job.content is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Export job is not ready")
    media_type = "application/json" if export_job.format == ExportFormat.json else "text/csv"
    return Response(
        content=export_job.content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{export_job.filename}"'},
    )


def ensure_document_exists(db: Session, document_id: int) -> Document:
    document = db.scalar(select(Document).where(Document.id == document_id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


def ensure_processed(db: Session, document_id: int) -> Document:
    document = ensure_document_exists(db, document_id)
    if document.status != DocumentStatus.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document is not processed")
    return document
