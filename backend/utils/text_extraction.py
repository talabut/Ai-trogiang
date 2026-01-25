from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if ext in [".docx"]:
        doc = DocxDocument(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    if ext in [".txt"]:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            return f.read()

    raise ValueError(f"Unsupported file type: {ext}")
