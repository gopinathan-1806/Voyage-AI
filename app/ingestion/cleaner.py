"""
Text cleaning and normalization utility for travel documents.
"""

import hashlib
import re
import unicodedata
from typing import Tuple


def clean_travel_text(text: str) -> str:
    """
    Clean, normalize, and strip excessive whitespace from scraped or extracted travel texts.
    Preserves list bullets and structured paragraph breaks.
    """
    if not text:
        return ""
    
    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)
    
    # Remove null bytes and non-printable control characters (keep newlines/tabs)
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or unicodedata.category(ch)[0] != "C")
    
    # Normalize bullet markers
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219]", "- ", text)
    
    # Fix repeated whitespace per line
    lines = []
    for line in text.splitlines():
        line_clean = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line_clean)
        
    cleaned = "\n".join(lines)
    
    # Collapse 3+ newlines into 2
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    
    return cleaned.strip()


def compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of cleaned text for version tracking."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
