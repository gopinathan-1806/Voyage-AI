"""
Travel Query Understanding Layer.
Extracts structured trip parameters (origin, destination, purpose, duration, date, question_type)
from user queries using pattern extraction and entity resolution.
"""

import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TripContext(BaseModel):
    """Structured representation of a user's trip context."""
    origin_country: Optional[str] = None
    destination_country: Optional[str] = None
    travel_purpose: Optional[str] = None  # Tourism, Business, Transit, Student, Work
    duration: Optional[str] = None        # e.g., "10 days", "2 weeks"
    travel_date: Optional[str] = None     # e.g., "December", "next month"
    question_type: Optional[str] = None   # visa_requirements, documents, fees, processing_time, entry_rules, general
    
    def is_empty(self) -> bool:
        return not any([
            self.origin_country,
            self.destination_country,
            self.travel_purpose,
            self.duration,
            self.travel_date
        ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origin_country": self.origin_country or "Not specified",
            "destination_country": self.destination_country or "Not specified",
            "travel_purpose": self.travel_purpose or "Tourism",
            "duration": self.duration or "Not specified",
            "travel_date": self.travel_date or "Not specified",
            "question_type": self.question_type or "general",
        }

    def merge_with(self, new_context: "TripContext") -> "TripContext":
        """Merge new entity updates without losing existing context."""
        return TripContext(
            origin_country=new_context.origin_country or self.origin_country,
            destination_country=new_context.destination_country or self.destination_country,
            travel_purpose=new_context.travel_purpose or self.travel_purpose,
            duration=new_context.duration or self.duration,
            travel_date=new_context.travel_date or self.travel_date,
            question_type=new_context.question_type or self.question_type,
        )


class TravelQueryUnderstanding:
    """Extracts structured travel parameters without hallucinating missing data."""

    KNOWN_COUNTRIES = {
        "india": "India",
        "indian": "India",
        "france": "France",
        "french": "France",
        "germany": "Germany",
        "german": "Germany",
        "united kingdom": "United Kingdom",
        "uk": "United Kingdom",
        "britain": "United Kingdom",
        "british": "United Kingdom",
        "england": "United Kingdom",
        "united states": "United States",
        "usa": "United States",
        "us": "United States",
        "america": "United States",
        "american": "United States",
        "uae": "UAE",
        "dubai": "UAE",
        "abu dhabi": "UAE",
        "united arab emirates": "UAE",
        "singapore": "Singapore",
        "singaporean": "Singapore",
        "japan": "Japan",
        "japanese": "Japan",
        "australia": "Australia",
        "australian": "Australia",
        "canada": "Canada",
        "canadian": "Canada",
        "china": "China",
        "chinese": "China",
    }

    @classmethod
    def extract_context(cls, query: str, existing_context: Optional[TripContext] = None) -> TripContext:
        """Extract trip context parameters from user query."""
        cleaned = query.strip()
        lower = cleaned.lower()

        extracted_origin = None
        extracted_destination = None
        extracted_purpose = None
        extracted_duration = None
        extracted_date = None
        extracted_qtype = None

        # 1. Origin & Destination Extraction
        # Explicit key-value pattern: "Origin: India, Destination: UK" or "Origin: India Destination: UK"
        origin_explicit = re.search(r"\borigin\s*[:=\-]\s*([a-zA-Z\s]+?)(?:,\s*|\s+dest|\s+to|\.|\?|$)", lower)
        if origin_explicit:
            extracted_origin = cls._match_country(origin_explicit.group(1))

        dest_explicit = re.search(r"\b(?:destination|dest)\s*[:=\-]\s*([a-zA-Z\s]+?)(?:,\s*|\s+what|\s+for|\.|\?|$)", lower)
        if dest_explicit:
            extracted_destination = cls._match_country(dest_explicit.group(1))

        # Pattern: "from X to Y", "travelling from X to Y", "citizen of X travelling to Y", "X citizen travelling to Y"
        if not (extracted_origin and extracted_destination):
            from_to_match = re.search(r"\bfrom\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+for|\s+in|\s+during|\.|\?|$)", lower)
            if from_to_match:
                o_raw = from_to_match.group(1).strip()
                d_raw = from_to_match.group(2).strip()
                if not extracted_origin:
                    extracted_origin = cls._match_country(o_raw)
                if not extracted_destination:
                    extracted_destination = cls._match_country(d_raw)

        # Pattern: "Indian citizen travelling to France"
        if not (extracted_origin and extracted_destination):
            citizen_to_match = re.search(r"\b([a-zA-Z]+)\s+citizen\s+(?:travelling|traveling|going|flying|visiting)?\s+to\s+([a-zA-Z\s]+?)(?:\s+for|\s+in|\.|\?|$)", lower)
            if citizen_to_match:
                if not extracted_origin:
                    extracted_origin = cls._match_country(citizen_to_match.group(1))
                if not extracted_destination:
                    extracted_destination = cls._match_country(citizen_to_match.group(2))

        # Direct destination match: "to France", "for France", "visa for Germany", "entry to Singapore"
        if not extracted_destination:
            dest_match = re.search(r"\b(?:to|in|for|visiting|enter|entering)\s+([a-zA-Z\s]+?)(?:\s+for|\s+in|\.|\?|$)", lower)
            if dest_match:
                extracted_destination = cls._match_country(dest_match.group(1))

        # Direct country scans if still missing
        if not extracted_destination or not extracted_origin:
            for term, country in cls.KNOWN_COUNTRIES.items():
                if re.search(rf"\b{re.escape(term)}\b", lower):
                    if re.search(rf"\bfrom\s+{re.escape(term)}\b", lower) or re.search(rf"\borigin\s*[:=\-]\s*{re.escape(term)}\b", lower):
                        if not extracted_origin:
                            extracted_origin = country
                    elif not extracted_destination and country != extracted_origin:
                        extracted_destination = country

        # 2. Purpose extraction
        if any(p in lower for p in ["tourism", "tourist", "holiday", "sightseeing", "vacation", "leisure"]):
            extracted_purpose = "Tourism"
        elif any(p in lower for p in ["business", "conference", "meeting", "expo"]):
            extracted_purpose = "Business"
        elif any(p in lower for p in ["transit", "layover", "stopover"]):
            extracted_purpose = "Transit"
        elif any(p in lower for p in ["study", "student", "university", "course"]):
            extracted_purpose = "Student"
        elif any(p in lower for p in ["work", "employment", "job"]):
            extracted_purpose = "Work"

        # 3. Duration extraction
        # Pattern: "10 days", "2 weeks", "3 months", "for 5 days", "staying 10 days"
        duration_match = re.search(r"\b(\d+\s*(?:day|days|week|weeks|month|months|year|years))\b", lower)
        if duration_match:
            extracted_duration = duration_match.group(1).strip()

        # 4. Travel Date extraction
        months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        for m in months:
            if re.search(rf"\b{m}\b", lower):
                extracted_date = m.capitalize()
                break

        # 5. Question Type
        if any(k in lower for k in ["document", "documents", "paperwork", "papers", "checklist"]):
            extracted_qtype = "documents"
        elif any(k in lower for k in ["fee", "fees", "cost", "price", "charge", "charges", "how much"]):
            extracted_qtype = "fees"
        elif any(k in lower for k in ["processing time", "how long", "wait time", "duration to get"]):
            extracted_qtype = "processing_time"
        elif any(k in lower for k in ["entry", "border", "arrival", "sg arrival", "customs"]):
            extracted_qtype = "entry_rules"
        elif any(k in lower for k in ["visa", "apply", "eligible", "eligibility", "what do i need"]):
            extracted_qtype = "visa_requirements"
        elif extracted_destination and (extracted_origin or extracted_purpose):
            extracted_qtype = "visa_requirements"
        else:
            extracted_qtype = "general"

        new_ctx = TripContext(
            origin_country=extracted_origin,
            destination_country=extracted_destination,
            travel_purpose=extracted_purpose,
            duration=extracted_duration,
            travel_date=extracted_date,
            question_type=extracted_qtype
        )

        if existing_context:
            return existing_context.merge_with(new_ctx)
        return new_ctx

    @classmethod
    def _match_country(cls, text: str) -> Optional[str]:
        cleaned = text.strip().lower()
        # Direct match
        if cleaned in cls.KNOWN_COUNTRIES:
            return cls.KNOWN_COUNTRIES[cleaned]
        # Multi-word phrase check
        for term, std_name in cls.KNOWN_COUNTRIES.items():
            if re.search(rf"\b{re.escape(term)}\b", cleaned):
                return std_name
        return None
