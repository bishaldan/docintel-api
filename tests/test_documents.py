SAMPLE_DOCUMENT = """# INVOICE
Name: Acme School
Date: 2026-06-11
Total: 1250.50

This document describes classroom technology purchases.

Item | Qty | Amount
Laptop | 2 | 1000
Training | 1 | 250.50
"""


def upload_sample(client):
    return client.post(
        "/api/v1/documents",
        files={"file": ("invoice.txt", SAMPLE_DOCUMENT.encode(), "text/plain")},
    )


def test_upload_process_and_extract_document(client):
    upload_response = upload_sample(client)
    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")
    assert process_response.status_code == 201
    assert process_response.json()["status"] == "completed"

    detail_response = client.get(f"/api/v1/documents/{document_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["document_type"] == "invoice"

    extractions_response = client.get(f"/api/v1/documents/{document_id}/extractions")
    assert extractions_response.status_code == 200
    extraction_types = {item["type"] for item in extractions_response.json()}
    assert {"heading", "field", "paragraph", "table"}.issubset(extraction_types)

    validations_response = client.get(f"/api/v1/documents/{document_id}/validations")
    assert validations_response.status_code == 200
    assert validations_response.json() == []


def test_exports_require_processed_document(client):
    upload_response = upload_sample(client)
    document_id = upload_response.json()["id"]

    early_export = client.get(f"/api/v1/documents/{document_id}/exports/json")
    assert early_export.status_code == 409

    client.post(f"/api/v1/documents/{document_id}/process")
    json_export = client.get(f"/api/v1/documents/{document_id}/exports/json")
    csv_export = client.get(f"/api/v1/documents/{document_id}/exports/csv")

    assert json_export.status_code == 200
    assert "Acme School" in json_export.text
    assert csv_export.status_code == 200
    assert "text/csv" in csv_export.headers["content-type"]
    assert "Acme School" in csv_export.text


def test_processing_jobs_and_export_jobs(client):
    upload_response = upload_sample(client)
    document_id = upload_response.json()["id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")
    assert process_response.status_code == 201
    job_id = process_response.json()["id"]

    job_response = client.get(f"/api/v1/documents/{document_id}/jobs/{job_id}")
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "completed"

    export_response = client.post(
        f"/api/v1/documents/{document_id}/export-jobs",
        json={"format": "csv"},
    )
    assert export_response.status_code == 201
    assert export_response.json()["status"] == "completed"
    export_id = export_response.json()["id"]

    download_response = client.get(
        f"/api/v1/documents/{document_id}/export-jobs/{export_id}/download"
    )
    assert download_response.status_code == 200
    assert "Acme School" in download_response.text


def test_validation_flags_missing_required_fields(client):
    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("note.txt", b"SHORT NOTE\nNo fields here.", "text/plain")},
    )
    document_id = upload_response.json()["id"]

    client.post(f"/api/v1/documents/{document_id}/process")
    response = client.get(f"/api/v1/documents/{document_id}/validations")

    assert response.status_code == 200
    codes = {item["code"] for item in response.json()}
    assert "missing_required_field" in codes


def test_receipt_type_uses_receipt_validation_rules(client):
    receipt = b"RECEIPT\nMerchant: Corner Store\nDate: 2026-06-11\nTotal: 20.00"
    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("receipt.txt", receipt, "text/plain")},
    )
    document_id = upload_response.json()["id"]

    client.post(f"/api/v1/documents/{document_id}/process")
    detail_response = client.get(f"/api/v1/documents/{document_id}")
    validations_response = client.get(f"/api/v1/documents/{document_id}/validations")

    assert detail_response.json()["document_type"] == "receipt"
    assert validations_response.json() == []
