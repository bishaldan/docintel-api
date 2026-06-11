SAMPLE_DOCUMENT = """# INVOICE
Name: Acme School
Date: 2026-06-11
Grand Total: $1,250.50

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
    assert detail_response.json()["confidence"] > 0.8

    extractions_response = client.get(f"/api/v1/documents/{document_id}/extractions")
    assert extractions_response.status_code == 200
    extraction_types = {item["type"] for item in extractions_response.json()}
    assert {"heading", "field", "paragraph", "table"}.issubset(extraction_types)
    normalized_fields = {item["normalized_label"]: item["value"] for item in extractions_response.json()}
    assert normalized_fields["total"] == "1250.50"

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


def test_image_upload_uses_ocr_sidecar_and_low_confidence_warning(client, tmp_path):
    image_response = client.post(
        "/api/v1/documents",
        files={"file": ("scan.png", b"fake-image-bytes", "image/png")},
    )
    document_id = image_response.json()["id"]

    detail_response = client.get(f"/api/v1/documents/{document_id}")
    # The upload filename is stored under a generated path; create a sidecar OCR text file beside it.
    storage_path = tmp_path / "uploads"
    stored_files = list(storage_path.glob("*.png"))
    assert stored_files
    stored_files[0].with_suffix(stored_files[0].suffix + ".txt").write_text(
        "INVOICE\nCustomer Name: Image Buyer\nInvoice Date: 06/11/2026\nAmount Due: $99.95",
        encoding="utf-8",
    )
    assert detail_response.status_code == 200

    process_response = client.post(f"/api/v1/documents/{document_id}/process")
    assert process_response.status_code == 201
    processed_detail = client.get(f"/api/v1/documents/{document_id}").json()
    assert processed_detail["document_type"] == "invoice"
    assert processed_detail["confidence"] > 0.7

    extractions = client.get(f"/api/v1/documents/{document_id}/extractions").json()
    normalized_fields = {item["normalized_label"]: item["value"] for item in extractions}
    assert normalized_fields["name"] == "Image Buyer"
    assert normalized_fields["date"] == "2026-06-11"
    assert normalized_fields["total"] == "99.95"


def test_image_without_sidecar_gets_low_confidence_warning(client):
    image_response = client.post(
        "/api/v1/documents",
        files={"file": ("scan.png", b"fake-image-bytes", "image/png")},
    )
    document_id = image_response.json()["id"]

    client.post(f"/api/v1/documents/{document_id}/process")
    validations = client.get(f"/api/v1/documents/{document_id}/validations").json()

    codes = {item["code"] for item in validations}
    assert "low_confidence" in codes


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
