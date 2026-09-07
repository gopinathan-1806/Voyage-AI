"""
Trip context model and entity extraction for structured query understanding.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TripContext(BaseModel):
    """Structured representation of travel parameters extracted from user messages."""
    origin_country: Optional[str] = Field(default=None, description="Country of citizenship / residence")
    destination_country: Optional[str] = Field(default=None, description="Destination country")
    travel_purpose: Optional[str] = Field(default="Tourism", description="Tourism, Business, Transit, Student, Work")
    duration: Optional[str] = Field(default=None, description="Trip duration e.g. '10 days', '2 weeks'")
    travel_date: Optional[str] = Field(default=None, description="Month or travel date e.g. 'December', '2025-01-10'")
    question_type: Optional[str] = Field(default="general_requirements", description="visa, documents, fee, processing_time, entry")
    is_clarification_needed: bool = False
    missing_fields: list[str] = Field(default_factory=list)

    def is_complete(self) -> bool:
        """Returns True if minimum required fields (destination, origin) are present."""
        return bool(self.destination_country and self.origin_country)

    def to_summary_string(self) -> str:
        """Generate human-readable summary for trip context card."""
        origin = self.origin_country or "Unknown Origin"
        dest = self.destination_country or "Unknown Destination"
        purpose = self.travel_purpose or "Tourism"
        dur = f" • {self.duration}" if self.duration else ""
        date = f" • {self.travel_date}" if self.travel_date else ""
        return f"{origin} ➔ {dest} | {purpose}{dur}{date}"

    def update_from_other(self, new_context: "TripContext") -> "TripContext":
        """Merge new context fields into existing trip context without overwriting known values with None."""
        return TripContext(
            origin_country=new_context.origin_country or self.origin_country,
            destination_country=new_context.destination_country or self.destination_country,
            travel_purpose=new_context.travel_purpose or self.travel_purpose,
            duration=new_context.duration or self.duration,
            travel_date=new_context.travel_date or self.travel_date,
            question_type=new_context.question_type or self.question_type,
            is_clarification_needed=new_context.is_clarification_needed,
            missing_fields=new_context.missing_fields,
        )
