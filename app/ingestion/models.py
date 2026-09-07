"""
Data models for VoyageAI Ingestion and Document representation.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TravelSource(BaseModel):
    """Represents an authoritative travel/immigration source definition."""
    source_id: str
    destination_country: str
    origin_country: Optional[str] = "All"
    source_name: str
    source_url: str
    source_type: str = Field(default="government", description="government, embassy, consulate, official_portal")
    document_type: str = Field(default="visa_information", description="visa_information, entry_rules, customs, transit")
    authority_score: float = Field(default=1.0, description="Authority multiplier 0.0 - 1.0")
    description: Optional[str] = None
    is_active: bool = True


class TravelDocument(BaseModel):
    """Standardized representation of an ingested travel/immigration document."""
    doc_id: str
    title: str
    destination_country: str
    origin_country: Optional[str] = "All"
    travel_purpose: Optional[str] = "General"  # Tourism, Business, Transit, Student, Work, General
    document_type: str = "visa_information"
    
    # Content
    content: str
    
    # Metadata for filtering and grounding
    source_name: str
    source_url: str
    source_type: str = "government"
    visa_type: Optional[str] = None
    eligibility: Optional[str] = None
    required_documents: List[str] = Field(default_factory=list)
    application_process: Optional[str] = None
    fees: Optional[str] = None
    processing_time: Optional[str] = None
    entry_requirements: Optional[str] = None
    transit_requirements: Optional[str] = None
    passport_requirements: Optional[str] = None
    
    # Freshness & Tracking
    last_updated: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    content_hash: Optional[str] = None
    
    def to_metadata(self) -> Dict:
        """Convert fields into metadata dict for vector / BM25 storage."""
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "destination_country": self.destination_country,
            "origin_country": self.origin_country or "All",
            "travel_purpose": self.travel_purpose or "General",
            "document_type": self.document_type,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "visa_type": self.visa_type or "",
            "fees": self.fees or "",
            "processing_time": self.processing_time or "",
            "last_updated": self.last_updated or "Recent",
            "retrieved_at": self.retrieved_at,
        }
