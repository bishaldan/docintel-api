from app.services.pdf import extract_pdf_text


class FakePage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class FakeReader:
    def __init__(self, _path):
        self.pages = [FakePage("Name: PDF Co"), FakePage("Total: 42")]


def test_extract_pdf_text_includes_page_markers(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.pdf.PdfReader", FakeReader)
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    text, page_count = extract_pdf_text(str(pdf_path))

    assert page_count == 2
    assert "--- Page 1 ---" in text
    assert "Total: 42" in text
