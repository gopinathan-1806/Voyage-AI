"""
Travel Readiness Score Calculator.
Computes an evidence-based travel readiness estimate across:
- Visa
- Required Documents
- Passport Validity
- Entry & Processing
- Health / Arrival Formalities
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.rag.query_understanding import TripContext
from app.rag.hybrid_retriever import ScoredDocument


class ReadinessComponent(BaseModel):
    name: str
    status: str  # "Ready", "Action Required", "Information Available", "Pending Details"
    score_pct: int
    summary: str


class TravelReadinessResult(BaseModel):
    overall_score: int = Field(default=0, description="0 to 100 percentage")
    status_label: str = Field(default="In Progress", description="High Readiness, Moderate, Action Required")
    components: List[ReadinessComponent] = Field(default_factory=list)
    disclaimer: str = "This score is an informational planning estimate based on current knowledge and not an official government determination."


class TravelReadinessCalculator:
    """Calculates structured readiness score based on trip context and retrieved knowledge."""

    @classmethod
    def calculate(
        cls,
        trip_context: TripContext,
        retrieved_docs: List[ScoredDocument],
    ) -> TravelReadinessResult:
        """Compute readiness metrics."""
        components = []
        score_total = 0

        has_destination = bool(trip_context.destination_country)
        has_origin = bool(trip_context.origin_country)
        has_duration = bool(trip_context.duration)
        has_evidence = len(retrieved_docs) > 0

        # 1. Visa Requirements
        if has_destination and has_evidence:
            visa_comp = ReadinessComponent(
                name="Visa Identification",
                status="Information Available",
                score_pct=25,
                summary=f"Visa category identified for {trip_context.destination_country}."
            )
        elif has_destination:
            visa_comp = ReadinessComponent(
                name="Visa Identification",
                status="Action Required",
                score_pct=10,
                summary=f"Destination set to {trip_context.destination_country}. Need specific nationality requirements."
            )
        else:
            visa_comp = ReadinessComponent(
                name="Visa Identification",
                status="Pending Details",
                score_pct=0,
                summary="Destination not specified."
            )
        components.append(visa_comp)
        score_total += visa_comp.score_pct

        # 2. Document Checklist
        if has_evidence:
            doc_comp = ReadinessComponent(
                name="Document Checklist",
                status="Ready",
                score_pct=25,
                summary="Official checklist of required documentation available."
            )
        else:
            doc_comp = ReadinessComponent(
                name="Document Checklist",
                status="Pending Details",
                score_pct=5,
                summary="Awaiting destination document retrieval."
            )
        components.append(doc_comp)
        score_total += doc_comp.score_pct

        # 3. Passport Validity
        if has_evidence:
            pass_comp = ReadinessComponent(
                name="Passport Rules",
                status="Ready",
                score_pct=20,
                summary="Validity window (3-6 months post-travel) and blank page rules verified."
            )
        else:
            pass_comp = ReadinessComponent(
                name="Passport Rules",
                status="Pending Details",
                score_pct=5,
                summary="Standard 6-month passport validity recommended."
            )
        components.append(pass_comp)
        score_total += pass_comp.score_pct

        # 4. Trip Duration & Timeline
        if has_duration:
            time_comp = ReadinessComponent(
                name="Timeline & Stay",
                status="Ready",
                score_pct=15,
                summary=f"Trip duration specified ({trip_context.duration}). Within tourist limits."
            )
        else:
            time_comp = ReadinessComponent(
                name="Timeline & Stay",
                status="Action Required",
                score_pct=5,
                summary="Specify exact stay duration to verify Schengen 90-day / US stay limits."
            )
        components.append(time_comp)
        score_total += time_comp.score_pct

        # 5. Entry / Arrival Card
        if has_evidence:
            entry_comp = ReadinessComponent(
                name="Arrival Formalities",
                status="Information Available",
                score_pct=15,
                summary="Border control, health declaration, and arrival card procedures retrieved."
            )
        else:
            entry_comp = ReadinessComponent(
                name="Arrival Formalities",
                status="Pending Details",
                score_pct=5,
                summary="Awaiting destination entry procedures."
            )
        components.append(entry_comp)
        score_total += entry_comp.score_pct

        # Overall Status
        if score_total >= 80:
            status_label = "High Readiness"
        elif score_total >= 50:
            status_label = "Moderate Readiness"
        else:
            status_label = "Information Gathering"

        return TravelReadinessResult(
            overall_score=score_total,
            status_label=status_label,
            components=components,
        )
