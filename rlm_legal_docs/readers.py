"""File text extraction for supported document formats (.docx, .pdf, .txt)."""

from pathlib import Path

from docx import Document
from PyPDF2 import PdfReader


def extract_text_from_docx(filepath: Path) -> str:
    """Extract all paragraph text from a single .docx file."""
    doc = Document(str(filepath))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_pdf(filepath: Path) -> str:
    """Extract text from all pages of a PDF file."""
    reader = PdfReader(str(filepath))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_text_from_txt(filepath: Path) -> str:
    """Read plain text file."""
    return filepath.read_text(encoding="utf-8")


def extract_text(filepath: Path) -> str:
    """Dispatch to the correct extraction function based on file extension."""
    ext = filepath.suffix.lower()
    if ext == ".docx":
        return extract_text_from_docx(filepath)
    elif ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext == ".txt":
        return extract_text_from_txt(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
