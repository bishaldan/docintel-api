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
    assert process_response.status_code == 200
    assert process_response.json()["status"] == "completed"

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

