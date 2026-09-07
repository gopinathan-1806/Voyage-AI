"""
Document extractor supporting HTML, PDF, and Markdown / Text formats.
"""

import io
from pathlib import Path
from typing import List, Optional
from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.ingestion.cleaner import clean_travel_text
from app.logging_config import get_logger

logger = get_logger(__name__)


def extract_from_html(html_content: str) -> str:
    """Extract clean readable text from HTML markup, discarding scripts, styles, and navigation."""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove unwanted tags
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
        tag.decompose()
        
    text = soup.get_text(separator="\n")
    return clean_travel_text(text)


def extract_from_pdf(pdf_path_or_bytes: Path | bytes) -> str:
    """Extract text from a PDF file using pypdf with robust error recovery."""
    try:
        if isinstance(pdf_path_or_bytes, (str, Path)):
            reader = PdfReader(str(pdf_path_or_bytes))
        else:
            reader = PdfReader(io.BytesIO(pdf_path_or_bytes))
            
        extracted_pages: List[str] = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_pages.append(f"--- Page {i + 1} ---\n{page_text}")
                
        full_text = "\n\n".join(extracted_pages)
        return clean_travel_text(full_text)
    except Exception as e:
        logger.error(f"Failed to extract PDF content: {e}")
        return ""


def extract_from_text(text_content: str) -> str:
    """Clean standard plain text or Markdown format."""
    return clean_travel_text(text_content)
