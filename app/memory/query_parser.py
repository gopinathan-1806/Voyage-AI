"""
Travel Query Understanding and Entity Extraction Layer.
Parses destination, nationality/origin, travel purpose, duration, and question types.
"""

import re
from typing import Optional, Dict, Any, Tuple
from app.memory.trip_context import TripContext
from app.logging_config import get_logger

logger = get_logger(__name__)


class TravelQueryParser:
    """Extracts structured trip parameters using deterministic regex and entity recognition rules."""

    # Standard country dictionary with demonyms & aliases
    COUNTRIES = {
        "france": "France",
        "french": "France",
        "paris": "France",
        "germany": "Germany",
        "german": "Germany",
        "berlin": "Germany",
        "frankfurt": "Germany",
        "munich": "Germany",
        "united kingdom": "United Kingdom",
        "uk": "United Kingdom",
        "britain": "United Kingdom",
        "british": "United Kingdom",
        "england": "United Kingdom",
        "london": "United Kingdom",
        "united states": "United States",
        "us": "United States",
        "usa": "United States",
        "american": "United States",
        "uae": "UAE",
        "dubai": "UAE",
        "abu dhabi": "UAE",
        "emirates": "UAE",
        "singapore": "Singapore",
        "singaporean": "Singapore",
        "japan": "Japan",
        "japanese": "Japan",
        "tokyo": "Japan",
        "australia": "Australia",
        "australian": "Australia",
        "sydney": "Australia",
        "india": "India",
        "indian": "India",
        "china": "China",
        "chinese": "China",
        "canada": "Canada",
        "canadian": "Canada",
        "brazil": "Brazil",
        "brazilian": "Brazil",
        "south africa": "South Africa",
        "nigeria": "Nigeria",
        "nigerian": "Nigeria",
        "philippines": "Philippines",
        "filipino": "Philippines",
    }

    # Demonym to origin country mapping
    NATIONALITIES = {
        "indian": "India",
        "american": "United States",
        "british": "United Kingdom",
        "french": "France",
        "german": "Germany",
        "singaporean": "Singapore",
        "japanese": "Japan",
        "australian": "Australia",
        "chinese": "China",
        "canadian": "Canada",
        "brazilian": "Brazil",
        "nigerian": "Nigeria",
        "filipino": "Philippines",
    }

    PURPOSES = {
        "tourism": "Tourism",
        "tourist": "Tourism",
        "vacation": "Tourism",
        "holiday": "Tourism",
        "sightseeing": "Tourism",
        "visit": "Tourism",
        "visiting": "Tourism",
        "leisure": "Tourism",
        "business": "Business",
        "meeting": "Business",
        "conference": "Business",
        "work": "Work",
        "job": "Work",
        "employment": "Work",
        "student": "Student",
        "study": "Student",
        "transit": "Transit",
        "layover": "Transit",
    }

    MONTHS = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]

    @classmethod
    def parse_query(cls, user_text: str, existing_context: Optional[TripContext] = None) -> TripContext:
        """
        Extract trip parameters from user message, resolving conversational references.
        """
        text_lower = user_text.lower()
        
        origin: Optional[str] = None
        destination: Optional[str] = None
        purpose: Optional[str] = None
        duration: Optional[str] = None
        travel_date: Optional[str] = None
        question_type: str = "general_requirements"

        # 1. Detect Origin
        # Pattern: "Indian citizen", "Indian passport", "from India", "citizen of India", "I am Indian"
        for dem, country in cls.NATIONALITIES.items():
            if re.search(rf"\b{dem}\b", text_lower):
                origin = country
                break
                
        from_match = re.search(r"\b(?:from|departing|living in|citizen of|passport from)\s+([a-zA-Z\s]+?)(?:\s+(?:to|for|in|during|\.|$))", text_lower)
        if from_match:
            candidate = from_match.group(1).strip()
            if candidate in cls.COUNTRIES:
                origin = cls.COUNTRIES[candidate]

        # 2. Detect Destination
        # Pattern: "travelling to France", "travel to Germany", "trip to UK", "visa for Japan"
        to_match = re.search(r"\b(?:to|in|for|visiting|destination|into)\s+([a-zA-Z\s]+?)(?:\s+(?:for|from|in|during|with|\.|$))", text_lower)
        if to_match:
            candidate = to_match.group(1).strip()
            if candidate in cls.COUNTRIES:
                destination = cls.COUNTRIES[candidate]

        # Direct search for country mentions if not captured by prep
        if not destination:
            for word, country in cls.COUNTRIES.items():
                if re.search(rf"\b{re.escape(word)}\b", text_lower):
                    # If this country wasn't assigned to origin, assign to destination
                    if origin != country:
                        destination = country
                        break

        # 3. Detect Purpose
        for keyword, p_name in cls.PURPOSES.items():
            if re.search(rf"\b{keyword}\b", text_lower):
                purpose = p_name
                break

        # 4. Detect Duration (e.g. "10 days", "2 weeks", "3 months", "a month")
        dur_match = re.search(r"\b(\d+\s*(?:day|days|week|weeks|month|months|year|years))\b", text_lower)
        if dur_match:
            duration = dur_match.group(1)
        elif "a week" in text_lower or "one week" in text_lower:
            duration = "1 week"
        elif "a month" in text_lower or "one month" in text_lower:
            duration = "1 month"

        # 5. Detect Month / Travel Date
        for m in cls.MONTHS:
            if re.search(rf"\b{m}\b", text_lower):
                travel_date = m.capitalize()
                break

        # 6. Detect Question Type
        if any(w in text_lower for w in ["document", "documents", "paper", "papers", "checklist"]):
            question_type = "documents"
        elif any(w in text_lower for w in ["cost", "fee", "fees", "price", "charge", "charges"]):
            question_type = "fees"
        elif any(w in text_lower for w in ["how long", "time", "processing", "timeline", "duration", "wait"]):
            question_type = "processing_time"
        elif any(w in text_lower for w in ["passport", "validity", "blank pages"]):
            question_type = "passport"
        elif any(w in text_lower for w in ["entry", "arrival card", "customs", "health"]):
            question_type = "entry"
        elif any(w in text_lower for w in ["transit", "layover", "stopover"]):
            question_type = "transit"
        elif any(w in text_lower for w in ["why", "evidence", "source", "reason"]):
            question_type = "why_explanation"

        # Create new parsed context
        new_ctx = TripContext(
            origin_country=origin,
            destination_country=destination,
            travel_purpose=purpose,
            duration=duration,
            travel_date=travel_date,
            question_type=question_type,
        )

        # Merge with existing context if present
        if existing_context:
            merged = existing_context.update_from_other(new_ctx)
        else:
            merged = new_ctx

        # Identify missing information
        missing = []
        if not merged.destination_country:
            missing.append("destination_country")
        if not merged.origin_country:
            missing.append("origin_country")
        
        merged.missing_fields = missing
        merged.is_clarification_needed = len(missing) == 2  # Missing both origin & dest

        return merged
