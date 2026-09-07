"""
Formatting utilities for retrieved documents into prompt context and user-facing source citations.
"""

from typing import List
from app.rag.hybrid_retriever import ScoredDocument


def format_context_for_llm(scored_docs: List[ScoredDocument]) -> str:
    """Format retrieved passages into a structured XML-like context block for prompt grounding."""
    if not scored_docs:
        return "NO_RETRIEVED_DOCUMENTS"

    sections = []
    for i, item in enumerate(scored_docs):
        meta = item.metadata
        country = meta.get("destination_country", "Unknown")
        source = meta.get("source_name", "Official Source")
        url = meta.get("source_url", "")
        doc_type = meta.get("document_type", "visa_info")
        freshness = meta.get("last_updated", "Recent")

        section_text = (
            f"<document id=\"{i+1}\" destination=\"{country}\" source=\"{source}\" "
            f"type=\"{doc_type}\" url=\"{url}\" updated=\"{freshness}\" score=\"{item.combined_score}\">\n"
            f"{item.page_content}\n"
            f"</document>"
        )
        sections.append(section_text)

    return "\n\n".join(sections)


def extract_unique_sources(scored_docs: List[ScoredDocument]) -> List[dict]:
    """Extract deduplicated list of source dictionaries for UI and citation rendering."""
    seen = set()
    sources = []
    for item in scored_docs:
        meta = item.metadata
        url = meta.get("source_url", "")
        name = meta.get("source_name", "Official Immigration Authority")
        dest = meta.get("destination_country", "")
        doc_type = meta.get("document_type", "Visa Guidelines")
        updated = meta.get("last_updated", "Recently verified")

        key = (name, url)
        if key not in seen and url:
            seen.add(key)
            sources.append({
                "name": name,
                "url": url,
                "destination": dest,
                "document_type": doc_type,
                "last_updated": updated,
                "relevance_score": item.combined_score
            })
    return sources
