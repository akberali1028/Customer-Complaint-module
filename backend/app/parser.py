from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf": "pdf", ".docx": "docx", ".txt": "txt", ".eml": "eml"}


def input_type_for_filename(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Supported file formats are PDF, DOCX, TXT, and EML.")
    return SUPPORTED_EXTENSIONS[extension]


def extract_document_text(content: bytes, input_type: str) -> str:
    """Small demo-only text extractor; it intentionally does not attempt OCR."""
    if input_type in {"txt", "eml"}:
        return content.decode("utf-8", errors="replace")
    if input_type == "pdf":
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if input_type == "docx":
        document = Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
    raise ValueError("Unsupported document type.")
