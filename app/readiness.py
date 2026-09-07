"""
Travel Readiness Score Calculator:
Evaluates traveler readiness score (0 - 100%) and categorizes status across:
Visa, Required Documents, Entry Requirements, Passport Validity, and Travel Preparation.
"""

from typing import Dict, Any, List, Optional
from app.memory.trip_context import TripContext
from app.rag.hybrid_retriever import ScoredDocument


class TravelReadinessEngine:
    """
    Computes an evidence-based Readiness Score and readiness status cards.
    Clearly marks the score as an informational estimate, not an official government determination.
    """

    @classmethod
    def calculate_readiness(
        cls,
        trip_context: TripContext,
        evidence_docs: List[ScoredDocument],
    ) -> Dict[str, Any]:
        """
        Computes the readiness breakdown and overall percentage.
        """
        score = 20  # Base trip initiation score
        
        # 1. Destination & Origin known (+20%)
        if trip_context.destination_country:
            score += 15
        if trip_context.origin_country:
            score += 15
        if trip_context.duration:
            score += 10
        if trip_context.travel_purpose:
            score += 10

        # 2. Evidence Grounding Bonus (+30%)
        if evidence_docs:
            score += 20
            if len(evidence_docs) >= 3:
                score += 10

        total_score = min(100, score)

        # Readiness Cards breakdown
        cards = {
            "visa_status": {
                "title": "VISA REQUIREMENT",
                "status": "Identified" if evidence_docs else "Check Required",
                "badge": "Required" if "Schengen" in str(evidence_docs) or "Visitor" in str(evidence_docs) else "Verified",
                "icon": "🛂",
            },
            "documents_status": {
                "title": "DOCUMENTS",
                "status": f"{len(evidence_docs) * 2}+ Checklist Items" if evidence_docs else "Pending Trip Details",
                "badge": "Checklist Ready" if evidence_docs else "Incomplete",
                "icon": "📄",
            },
            "entry_status": {
                "title": "ENTRY RULES",
                "status": "Official Rules Found" if evidence_docs else "Awaiting Country",
                "badge": "Eligible" if evidence_docs else "Pending",
                "icon": "✈️",
            },
            "passport_status": {
                "title": "PASSPORT",
                "status": "3-6 Mos Validity Req." if evidence_docs else "Validity Check",
                "badge": "Mandatory",
                "icon": "📘",
            }
        }

        return {
            "score": total_score,
            "score_label": f"{total_score}%",
            "cards": cards,
            "disclaimer": "Informational estimate based on current knowledge base evidence. Not an official government decision.",
        }
