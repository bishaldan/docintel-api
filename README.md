# DocIntel API

Document intelligence and automation API for structured extraction, validation, and exports.

This project is designed as a senior Python backend portfolio project. It demonstrates document upload workflows, asynchronous processing architecture, structured extraction, validation findings, JSON/CSV exports, SQLAlchemy persistence, Celery-ready background jobs, Docker infrastructure, and automated tests.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Celery
- Redis
- Docker Compose
- Pytest
- GitHub Actions
- Structured request logging
- Request ID middleware
- Consistent error responses
- Lightweight rate limiting

## Features

- Document upload API
- Processing job lifecycle: pending, processing, completed, failed
- Processing job records with status tracking
- PDF text extraction support via `pypdf`
- Image upload support through an OCR provider interface
- Mock OCR provider for local development and tests
- Document type detection for invoices, receipts, forms, reports, and unknown documents
- Structure extraction for headings, paragraphs, key-value fields, and pipe-style tables
- Field normalization for common aliases such as `Grand Total`, `Amount Due`, and `Customer Name`
- Date and currency normalization
- Document-level and field-level confidence scores
- Type-specific validation findings for missing fields and low-confidence extraction
- JSON export endpoint
- CSV export endpoint
- Export job records with status and download endpoint
- Request ID middleware
- Celery task module for background processing
- Consistent validation/error response format
- Structured request logs with request IDs
- In-memory rate limiter for upload/process/export endpoints
- Demo seed script with invoice, receipt, form, and report samples
- Test suite covering upload, processing, validation, and exports

## Architecture

```text
Client / Swagger UI
        |
        v
FastAPI application
        |
        +-- Request IDs, structured logs, rate limiting
        +-- Upload and document lifecycle APIs
        +-- Processing jobs and export jobs
        +-- PDF reader service
        +-- OCR provider interface
        +-- Extraction, normalization, validation
        |
        v
SQLAlchemy models + Alembic migrations
        |
        +-- SQLite locally / database-ready persistence
        +-- Redis-backed Celery worker modules
```

## Local Setup

```bash
cp .env.example .env
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload --port 8001
```

Seed demo documents:

```bash
python scripts/seed_demo.py
```

API docs:

```text
http://localhost:8001/docs
```

## API Overview

```text
GET  /api/v1/health
POST /api/v1/documents
GET  /api/v1/documents
GET  /api/v1/documents/{document_id}
POST /api/v1/documents/{document_id}/process
GET  /api/v1/documents/{document_id}/jobs
GET  /api/v1/documents/{document_id}/jobs/{job_id}
GET  /api/v1/documents/{document_id}/extractions
GET  /api/v1/documents/{document_id}/validations
GET  /api/v1/documents/{document_id}/exports/json
GET  /api/v1/documents/{document_id}/exports/csv
POST /api/v1/documents/{document_id}/export-jobs
GET  /api/v1/documents/{document_id}/export-jobs/{export_id}
GET  /api/v1/documents/{document_id}/export-jobs/{export_id}/download
```

## Error Shape

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "request_id": "ec07726d-d282-4b92-b970-f072d05c02a8",
    "details": []
  }
}
```

## Portfolio Positioning

CV summary:

> Built a document intelligence API with FastAPI, PDF text extraction, OCR-ready image processing architecture, document type detection, field/table extraction, field normalization, confidence scoring, validation rules, JSON/CSV export jobs, SQLAlchemy/Alembic persistence, Celery-ready background processing, structured logging, rate limiting, Docker infrastructure, and automated tests.
