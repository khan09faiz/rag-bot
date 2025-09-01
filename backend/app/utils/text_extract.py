from typing import Tuple
from pathlib import Path
from .normalize import normalize_text

from pypdf import PdfReader
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDoc
import docx

PDF_MIME = 'application/pdf'
DOCX_MIME = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
HTML_MIME = 'text/html'
PLAIN_MIME = 'text/plain'


def extract_text(file_path: Path, mime_type: str | None) -> Tuple[str, str]:
    suffix = file_path.suffix.lower()
    if mime_type == PDF_MIME or suffix == '.pdf':
        return _extract_pdf(file_path), PDF_MIME
    if mime_type == DOCX_MIME or suffix == '.docx':
        return _extract_docx(file_path), DOCX_MIME
    if mime_type == HTML_MIME or suffix in ('.html', '.htm'):
        return _extract_html(file_path), HTML_MIME
    # default plain
    text = file_path.read_text(encoding='utf-8', errors='ignore')
    return normalize_text(text), PLAIN_MIME

def _extract_pdf(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or '')
            except Exception:
                continue
        return normalize_text('\n'.join(pages))
    except Exception:
        # fallback naive
        return normalize_text(path.read_bytes().decode('utf-8', errors='ignore'))

def _extract_docx(path: Path) -> str:
    document = docx.Document(str(path))
    texts = [p.text for p in document.paragraphs if p.text.strip()]
    return normalize_text('\n'.join(texts))

def _extract_html(path: Path) -> str:
    raw = path.read_text(encoding='utf-8', errors='ignore')
    try:
        readable = ReadabilityDoc(raw)
        html = readable.summary()
    except Exception:
        html = raw
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup(['script','style']):
        tag.decompose()
    text = soup.get_text('\n')
    return normalize_text(text)
