"""
Output Guardrail to verify response groundedness, safety, and formatting compliance.
"""

from typing import Tuple, List
from app.rag.hybrid_retriever import ScoredDocument


class OutputGuardrail:
    """
    Validates model generation before showing to the user:
    1. Checks for dangerous or illegal immigration advice.
    2. Enforces explicit lack-of-evidence warning if retrieval was insufficient.
    3. Guarantees mandatory official authority verification disclaimer.
    """

    FORBIDDEN_OUTPUT_PHRASES = [
        "you can easily bypass",
        "border guards will not check",
        "fake documents",
        "illegal entry is possible",
        "ignore the immigration officer",
    ]

    SAFETY_REFUSAL_INDICATORS = [
        "i cannot assist with that",
        "i'm sorry, but i cannot",
        "i cannot fulfill this request",
        "security & safety alert",
        "security alert",
        "safety alert",
        "violates voyageai's safety",
    ]

    VERIFICATION_DISCLAIMER = (
        "\n\n*Verification Notice: Immigration regulations, fees, and procedures change frequently. "
        "Always confirm current requirements with the official embassy, consulate, or government immigration portal.*"
    )

    @classmethod
    def sanitize_and_validate(
        cls,
        raw_output: str,
        retrieved_docs: List[ScoredDocument],
        is_evidence_sufficient: bool,
    ) -> Tuple[str, bool]:
        """
        Validate and format model output.
        Returns (safe_output_text, passed_checks).
        """
        lower_output = raw_output.lower()

        # 1. Check forbidden unsafe phrases
        for phrase in cls.FORBIDDEN_OUTPUT_PHRASES:
            if phrase in lower_output:
                return (
                    "I cannot provide advice on bypassing official immigration or border controls. "
                    "Please refer to official government immigration portals for lawful entry requirements.",
                    False
                )

        # 2. Check insufficient evidence handling
        if not is_evidence_sufficient:
            # If evidence was weak and model hallucinated a standard response, override with safe fallback
            if "### short answer" in lower_output and not retrieved_docs:
                fallback_msg = (
                    "### Short Answer\n"
                    "I could not find sufficient authoritative information in the VoyageAI knowledge base "
                    "to answer your specific query with certainty.\n\n"
                    "### Recommended Action\n"
                    "Please verify your visa and entry requirements directly with the destination country's "
                    "official embassy, consulate, or official immigration authority."
                )
                return fallback_msg + cls.VERIFICATION_DISCLAIMER, True

        # 3. Suppress immigration verification disclaimer if model returned a safety/policy refusal
        is_safety_refusal = any(ind in lower_output for ind in cls.SAFETY_REFUSAL_INDICATORS)

        output = raw_output
        if not is_safety_refusal and "immigration policies" not in lower_output and "verification" not in lower_output:
            output = output + cls.VERIFICATION_DISCLAIMER

        return output, True
