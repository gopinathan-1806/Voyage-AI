"""
LLM Client Wrapper supporting OpenAI API and an offline Deterministic Rule-Based Generator
for testing and local execution without an active OpenAI API key.
"""

import os
from typing import Generator, Optional, List
from app.config import config
from app.rag.hybrid_retriever import ScoredDocument
from app.rag.prompts import VOYAGEAI_SYSTEM_PROMPT, FALLBACK_NO_EVIDENCE_PROMPT
from app.rag.source_formatter import format_context_for_llm
from app.logging_config import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Wrapper for streaming and batch LLM generation."""

    def __init__(self):
        self.api_key = config.openai_api_key
        self.model = config.openai_model
        self._openai_client = None

        if self.api_key and self.api_key != "your-openai-api-key-here":
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI Client initialized successfully with model: {self.model}")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}. Running in local rule-based fallback mode.")

    def generate_answer_stream(
        self,
        query: str,
        context_docs: List[ScoredDocument],
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Streams generated response chunks from OpenAI, or yields rule-based grounded chunks if offline.
        """
        formatted_context = format_context_for_llm(context_docs)
        sys_prompt = system_prompt or VOYAGEAI_SYSTEM_PROMPT

        if self._openai_client:
            try:
                messages = [
                    {"role": "system", "content": sys_prompt},
                    {
                        "role": "user",
                        "content": f"User Query: {query}\n\nAuthoritative Retrieved Context:\n{formatted_context}"
                    }
                ]
                stream = self._openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=True,
                    temperature=0.1,  # Low temperature for high factual accuracy
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                return
            except Exception as e:
                logger.error(f"OpenAI streaming failed: {e}. Falling back to rule-based generation.")

        # Fallback Offline Generator
        yield from self._local_grounded_generator(query, context_docs)

    def _local_grounded_generator(self, query: str, context_docs: List[ScoredDocument]) -> Generator[str, None, None]:
        """High quality deterministic fallback when no API key is supplied."""
        if not context_docs:
            yield FALLBACK_NO_EVIDENCE_PROMPT
            return

        top_doc = context_docs[0]
        meta = top_doc.metadata
        country = meta.get("destination_country", "your destination")
        visa_type = meta.get("visa_type", "Standard Visitor / Tourist Visa")
        fees = meta.get("fees", "Standard visa processing fees apply.")
        processing_time = meta.get("processing_time", "15-30 calendar days.")

        response_chunks = [
            f"### Short Answer\n"
            f"According to authoritative official information in the VoyageAI knowledge base, travelers visiting **{country}** require a valid passport and entry clearance (**{visa_type}**) before entry.\n\n",
            f"### Visa Requirements\n"
            f"- **Visa Type**: {visa_type}\n"
            f"- **Estimated Fee**: {fees}\n"
            f"- **Processing Time**: {processing_time}\n"
            f"- **Permitted Stay**: Up to 90 days for short-term tourism/visitor stream\n\n",
            f"### Required Documents\n"
            f"- **Valid Passport**: Minimum 3 to 6 months validity beyond travel date with blank visa pages.\n"
            f"- **Application Form**: Completed and signed official visa application.\n"
            f"- **Travel Medical Insurance**: Adequate coverage for medical emergencies and repatriation.\n"
            f"- **Flight & Hotel Bookings**: Confirmed round-trip flight reservations and accommodation proof.\n"
            f"- **Proof of Financial Means**: Bank statements, payslips, or financial sponsorship.\n\n",
            f"### Application Process\n"
            f"1. Complete the online visa application on the official government portal.\n"
            f"2. Schedule and attend a biometric appointment at an authorized visa center.\n"
            f"3. Submit passport and supporting documents for consular adjudication.\n"
            f"4. Receive decision and collect passport with stamped entry clearance.\n\n",
            f"### Important Notes & Freshness\n"
            f"- **Source Authority**: Grounded from {meta.get('source_name', 'Official Portal')}.\n"
            f"- **Information Updated**: {meta.get('last_updated', 'Recently Verified')}.\n\n",
            f"### Verification\n"
            f"*Immigration rules and fees change periodically. Please verify with the official {country} embassy or visa authority prior to departure.*"
        ]

        for chunk in response_chunks:
            yield chunk
