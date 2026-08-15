from src.pdf_loader import PyPDFLoader


class _Page:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


def test_pdf_loader_preserves_page_order_and_metadata(monkeypatch, tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"not parsed by the fake")
    monkeypatch.setattr(
        "src.pdf_loader.PdfReader",
        lambda path: type("Reader", (), {"pages": [_Page("first"), _Page(None)]})(),
    )

    documents = PyPDFLoader(pdf).load()

    assert [document.page_content for document in documents] == ["first", ""]
    assert documents[1].metadata == {"source": str(pdf), "page": 1}
