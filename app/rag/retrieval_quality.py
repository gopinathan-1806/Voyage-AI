"""
Lexical and Keyword relevance scoring utilities.
"""

import re
from typing import Set


def compute_lexical_overlap(query: str, document_text: str) -> float:
    """
    Computes lexical term overlap ratio (Jaccard similarity on non-stopwords)
    between query and document text.
    """
    stopwords = {
        "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with",
        "by", "is", "are", "was", "were", "what", "do", "i", "need", "my", "me", "how",
        "can", "we", "you", "from", "traveling", "travelling", "going"
    }
    
    def tokenize(text: str) -> Set[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())
        return {w for w in words if w not in stopwords and len(w) > 1}
    
    query_tokens = tokenize(query)
    if not query_tokens:
        return 0.0
        
    doc_tokens = tokenize(document_text)
    if not doc_tokens:
        return 0.0
        
    intersection = query_tokens.intersection(doc_tokens)
    return len(intersection) / float(len(query_tokens))
