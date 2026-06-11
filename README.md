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

## Features

- Document upload API
- Processing job lifecycle: pending, processing, completed, failed
- Structure extraction for headings, paragraphs, key-value fields, and pipe-style tables
- Validation findings for missing fields and low-confidence extraction
- JSON export endpoint
- CSV export endpoint
- Request ID middleware
- Celery task module for background processing
- Test suite covering upload, processing, validation, and exports

## Local Setup

```bash
cp .env.example .env
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload --port 8001
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
GET  /api/v1/documents/{document_id}/extractions
GET  /api/v1/documents/{document_id}/validations
GET  /api/v1/documents/{document_id}/exports/json
GET  /api/v1/documents/{document_id}/exports/csv
```

## Portfolio Positioning

CV summary:

> Built a document intelligence API with FastAPI, SQLAlchemy, Alembic, document upload workflows, structured extraction, validation findings, JSON/CSV exports, Celery-ready background processing, Docker infrastructure, request tracing, and automated tests.

