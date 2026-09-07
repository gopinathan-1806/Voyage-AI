"""
Input Guardrail for Domain and Safety Enforcement.
Ensures queries belong to travel, visas, immigration, or are valid conversational follow-ups.
"""

import re
from typing import Tuple, Optional
from app.guardrails.injection_detector import PromptInjectionDetector
from app.rag.query_understanding import TripContext


class InputGuardrail:
    """
    Validates user input against safety attacks, illegal evasion, and out-of-domain scope.
    Gracefully allows conversational follow-ups (e.g. '10 days', 'tourism', 'how much?').
    """

    TRAVEL_KEYWORDS = {
        "visa", "visas", "passport", "passports", "immigration", "embassy", "consulate",
        "travel", "travelling", "traveling", "trip", "tourist", "tourism", "vacation",
        "holiday", "flight", "entry", "exit", "transit", "layover", "schengen", "eta",
        "esta", "vfs", "tlscontact", "border", "customs", "documents", "stay", "days",
        "months", "france", "germany", "uk", "usa", "uae", "dubai", "singapore",
        "japan", "australia", "india", "fees", "cost", "processing", "insurance",
        "arrival card", "declaration"
    }

    CONVERSATIONAL_FOLLOWUP_WORDS = {
        "yes", "no", "ok", "okay", "thanks", "thank you", "sure", "why", "what",
        "how", "when", "where", "tell me more", "explain", "why this answer",
        "10 days", "2 weeks", "tourism", "business", "next month", "december"
    }

    @classmethod
    def validate_input(
        cls,
        user_input: str,
        active_trip_context: Optional[TripContext] = None,
        has_conversation_history: bool = False
    ) -> Tuple[bool, str]:
        """
        Validates input.
        Returns (is_valid, message_if_invalid).
        """
        cleaned = user_input.strip()
        if not cleaned:
            return False, "Please provide a travel or visa related question."

        # 1. Check prompt injection & security
        is_unsafe, reason = PromptInjectionDetector.check_injection(cleaned)
        if is_unsafe:
            return False, reason

        # 2. Check Domain Alignment
        lower = cleaned.lower()
        words = set(re.findall(r"\b[a-zA-Z0-9_\-]+\b", lower))

        # Direct travel keyword match
        has_travel_kw = bool(words.intersection(cls.TRAVEL_KEYWORDS))

        # Follow-up match if conversation active or active trip context exists
        is_followup = False
        if has_conversation_history or (active_trip_context and not active_trip_context.is_empty()):
            # If user answers with numbers/dates/short answers like "10 days" or "tourism"
            if len(words) <= 8:
                is_followup = True
            elif any(phrase in lower for phrase in ["how much", "what about", "documents", "why", "how long"]):
                is_followup = True

        if has_travel_kw or is_followup:
            return True, ""

        # Out of domain refusal
        return False, (
            "I specialize exclusively in travel, visa requirements, immigration guidelines, "
            "and entry rules. How can I assist you with your upcoming journey or destination requirements?"
        )
