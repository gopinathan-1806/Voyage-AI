"""
Query Rewriter and Keyword Expansion for travel domain.
"""

import re
from typing import Dict, Optional


class TravelQueryRewriter:
    """Transforms conversational or vague user queries into search-optimized retrieval queries."""

    # Country aliases map
    COUNTRY_ALIASES = {
        "dubai": "UAE",
        "abu dhabi": "UAE",
        "emirates": "UAE",
        "paris": "France",
        "berlin": "Germany",
        "frankfurt": "Germany",
        "munich": "Germany",
        "london": "United Kingdom",
        "uk": "United Kingdom",
        "england": "United Kingdom",
        "britain": "United Kingdom",
        "great britain": "United Kingdom",
        "usa": "United States",
        "us": "United States",
        "america": "United States",
        "singapore": "Singapore",
        "japan": "Japan",
        "tokyo": "Japan",
        "australia": "Australia",
        "sydney": "Australia",
        "melbourne": "Australia",
    }

    @classmethod
    def rewrite_query(cls, query: str, context_metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Enhance query with explicit domain keywords, destination focus, and context expansions.
        """
        cleaned_query = query.strip()
        additions = []
        
        # Incorporate context if user asks follow-up (e.g. "What documents?")
        if context_metadata:
            dest = context_metadata.get("destination_country")
            origin = context_metadata.get("origin_country")
            purpose = context_metadata.get("travel_purpose")
            
            if dest and dest.lower() not in cleaned_query.lower():
                additions.append(dest)
            if origin and origin != "All" and origin.lower() not in cleaned_query.lower():
                additions.append(f"from {origin}")
            if purpose and purpose.lower() not in cleaned_query.lower():
                additions.append(purpose)

        # Detect aliases in text
        for alias, country in cls.COUNTRY_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", cleaned_query, re.IGNORECASE):
                if country.lower() not in cleaned_query.lower():
                    additions.append(country)

        # Domain intent enhancement
        query_lower = cleaned_query.lower()
        if any(term in query_lower for term in ["document", "documents", "papers", "requirements"]):
            additions.append("required documents checklist application")
        if any(term in query_lower for term in ["cost", "price", "fee", "fees"]):
            additions.append("visa application fee charges")
        if any(term in query_lower for term in ["time", "how long", "processing", "duration"]):
            additions.append("processing timeline working days")
        if any(term in query_lower for term in ["passport", "validity"]):
            additions.append("passport validity blank pages entry")

        if additions:
            return f"{cleaned_query} {' '.join(additions)}"
        return cleaned_query
