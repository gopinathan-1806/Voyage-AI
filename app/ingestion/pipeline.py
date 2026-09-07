"""
Ingestion Pipeline to process raw web/PDF/Markdown sources into standardized TravelDocuments.
"""

import json
from pathlib import Path
from typing import List, Optional
from app.config import config
from app.ingestion.cleaner import compute_content_hash
from app.ingestion.extractor import extract_from_pdf, extract_from_text
from app.ingestion.models import TravelDocument, TravelSource
from app.ingestion.sources import AUTHORITATIVE_SOURCES
from app.logging_config import get_logger

logger = get_logger(__name__)


class IngestionPipeline:
    """Manages loading, validating, and saving authoritative travel knowledge."""

    def __init__(self, processed_dir: Optional[Path] = None):
        self.processed_dir = processed_dir or config.processed_data_dir
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def ingest_document(self, doc: TravelDocument) -> Path:
        """Validate, compute hash, and persist a single TravelDocument to JSON."""
        doc.content_hash = compute_content_hash(doc.content)
        target_path = self.processed_dir / f"{doc.doc_id}.json"
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(doc.model_dump_json(indent=2))
            
        logger.info(f"Saved TravelDocument [{doc.doc_id}] for {doc.destination_country} -> {target_path}")
        return target_path

    def load_all_processed_documents(self) -> List[TravelDocument]:
        """Load all ingested TravelDocuments from the processed data directory."""
        documents: List[TravelDocument] = []
        if not self.processed_dir.exists():
            return documents

        for json_file in self.processed_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    doc = TravelDocument(**data)
                    documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to load document from {json_file}: {e}")

        logger.info(f"Loaded {len(documents)} processed travel documents from {self.processed_dir}")
        return documents


def run_pipeline():
    """CLI execution entrypoint for ingestion pipeline."""
    pipeline = IngestionPipeline()
    docs = pipeline.load_all_processed_documents()
    print(f"Ingestion pipeline complete. Total active documents: {len(docs)}")


if __name__ == "__main__":
    run_pipeline()
