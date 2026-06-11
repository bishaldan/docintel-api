from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.models.extraction import Extraction, ValidationFinding
from app.schemas.document import DocumentDetail, DocumentRead, ExtractionRead, ValidationFindingRead
from app.services.exports import extractions_to_csv, extractions_to_json
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


@router.post("/documents/{document_id}/process", response_model=DocumentRead)
def process_document_endpoint(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.scalar(select(Document).where(Document.id == document_id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    process_document(db, document)
    db.commit()
    db.refresh(document)
    return document


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

