"""Small PDF loader replacing the sunset ``langchain-community`` package."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


class PyPDFLoader:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> list[Document]:
        reader = PdfReader(self.path)
        return [
            Document(
                page_content=page.extract_text() or "",
                metadata={"source": str(self.path), "page": page_number},
            )
            for page_number, page in enumerate(reader.pages)
        ]
