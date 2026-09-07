"""
VoyageAI Ingestion module initialization.
"""

from app.ingestion.models import TravelDocument, TravelSource
from app.ingestion.sources import AUTHORITATIVE_SOURCES, get_all_sources, get_sources_by_destination
from app.ingestion.cleaner import clean_travel_text, compute_content_hash
from app.ingestion.extractor import extract_from_html, extract_from_pdf, extract_from_text
from app.ingestion.scraper import WebScraper
from app.ingestion.pipeline import IngestionPipeline

__all__ = [
    "TravelDocument",
    "TravelSource",
    "AUTHORITATIVE_SOURCES",
    "get_all_sources",
    "get_sources_by_destination",
    "clean_travel_text",
    "compute_content_hash",
    "extract_from_html",
    "extract_from_pdf",
    "extract_from_text",
    "WebScraper",
    "IngestionPipeline",
]
