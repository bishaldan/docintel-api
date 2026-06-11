from pathlib import Path

from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models.document import Document
from app.models.job import ProcessingJob
from app.services.extraction import process_document

SAMPLES = {
    "invoice.txt": """# INVOICE
Customer Name: Acme School
Invoice Date: 2026-06-11
Amount Due: $1,250.50

Item | Qty | Amount
Laptop | 2 | 1000
Training | 1 | 250.50
""",
    "receipt.txt": """RECEIPT
Merchant: Corner Store
Date: 2026-06-11
Total: $20.00
""",
    "application-form.txt": """APPLICATION FORM
Name: Demo Student
Date: 2026-06-11
Program: Python Backend Engineering
""",
    "quarterly-report.txt": """QUARTERLY REPORT
Summary: Backend automation reduced manual processing time.
The document contains operational highlights and project metrics.
""",
}


def main() -> None:
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    db = session_local()
    try:
        for filename, content in SAMPLES.items():
            storage_path = upload_dir / filename
            storage_path.write_text(content, encoding="utf-8")
            document = db.scalar(select(Document).where(Document.filename == filename))
            if document is None:
                document = Document(
                    filename=filename,
                    content_type="text/plain",
                    storage_path=str(storage_path),
                )
                db.add(document)
                db.flush()
            job = ProcessingJob(document_id=document.id)
            db.add(job)
            db.flush()
            process_document(db, document, job)
        db.commit()
        print("Demo documents ready")
        print("Created invoice, receipt, form, and report samples")
    finally:
        db.close()


if __name__ == "__main__":
    main()
