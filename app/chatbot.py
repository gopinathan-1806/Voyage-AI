"""
Core VoyageAI Chatbot Engine & Runtime.
Orchestrates:
- Guardrail validation (input/output)
- Query understanding & entity extraction
- Session memory persistence
- Hybrid Corrective RAG
- Self-RAG answer validation
- LLM response generation with streaming support
"""

from typing import Generator, Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field

from app.config import config
from app.guardrails.input_guardrail import InputGuardrail
from app.guardrails.output_guardrail import OutputGuardrail
from app.memory.session_memory import BaseSessionMemory, InMemorySessionStore
from app.rag.query_understanding import TravelQueryUnderstanding, TripContext
from app.rag.corrective_rag import CorrectiveRAGEngine, RetrievalEvaluationResult
from app.rag.grounding_checker import GroundingValidator, ValidationReport
from app.rag.hybrid_retriever import ScoredDocument
from app.rag.source_formatter import format_context_for_llm, extract_unique_sources
from app.rag.prompts import VOYAGEAI_SYSTEM_PROMPT
from app.rag.readiness_calculator import TravelReadinessCalculator, TravelReadinessResult
from app.logging_config import get_logger

logger = get_logger(__name__)


class WhyThisAnswer(BaseModel):
    """Transparent, explainable summary of VoyageAI reasoning."""
    understood_destination: str = "Not specified"
    understood_origin: str = "Not specified"
    travel_purpose: str = "Tourism"
    total_candidate_chunks: int = 0
    passed_relevance_chunks: int = 0
    authoritative_sources_used: int = 0
    confidence_level: str = "High"
    retrieval_action: str = "DIRECT_GENERATION"
    grounding_summary: str = ""


class ChatResponse(BaseModel):
    """Complete response object from VoyageAI."""
    answer: str
    trip_context: TripContext
    readiness: TravelReadinessResult
    why_this_answer: WhyThisAnswer
    sources: List[dict] = Field(default_factory=list)
    is_safe: bool = True
    error_message: Optional[str] = None


class TravelImmigrationChatbot:
    """
    Production-grade Travel & Immigration Chatbot engine.
    """

    def __init__(
        self,
        memory: Optional[BaseSessionMemory] = None,
        corrective_rag: Optional[CorrectiveRAGEngine] = None,
    ):
        self.memory = memory or InMemorySessionStore()
        self.corrective_rag = corrective_rag or CorrectiveRAGEngine()

    def process_query(self, user_query: str) -> ChatResponse:
        """
        Execute full synchronous pipeline:
        Input Guardrails -> Query Understanding -> Corrective RAG -> LLM -> Output Guardrails.
        """
        active_ctx = self.memory.get_trip_context()
        has_history = len(self.memory.get_messages()) > 0

        # 1. Input Guardrails
        is_valid, guardrail_msg = InputGuardrail.validate_input(
            user_input=user_query,
            active_trip_context=active_ctx,
            has_conversation_history=has_history,
        )
        if not is_valid:
            readiness = TravelReadinessCalculator.calculate(active_ctx, [])
            why = WhyThisAnswer(
                grounding_summary=f"Blocked by input security/domain guardrail: {guardrail_msg}"
            )
            return ChatResponse(
                answer=guardrail_msg,
                trip_context=active_ctx,
                readiness=readiness,
                why_this_answer=why,
                sources=[],
                is_safe=False,
            )

        # 2. Query Understanding & Context Tracking
        updated_ctx = TravelQueryUnderstanding.extract_context(user_query, active_ctx)
        self.memory.update_trip_context(updated_ctx)
        self.memory.add_message("user", user_query)

        # 3. Corrective RAG Retrieval
        retrieved_docs, eval_result = self.corrective_rag.retrieve_with_correction(
            query=user_query,
            destination_country=updated_ctx.destination_country,
            context_metadata=updated_ctx.to_dict(),
        )

        # 4. Format Context & Generate Answer
        raw_answer = self._generate_llm_answer(
            user_query=user_query,
            trip_context=updated_ctx,
            retrieved_docs=retrieved_docs,
            is_evidence_sufficient=eval_result.is_sufficient,
        )

        # 5. Output Guardrail & Grounding
        safe_answer, passed_output = OutputGuardrail.sanitize_and_validate(
            raw_output=raw_answer,
            retrieved_docs=retrieved_docs,
            is_evidence_sufficient=eval_result.is_sufficient,
        )

        validation_report = GroundingValidator.validate_answer(
            generated_answer=safe_answer,
            retrieved_docs=retrieved_docs,
            is_evidence_sufficient=eval_result.is_sufficient,
        )

        # 6. Readiness Score & Why-This-Answer
        readiness = TravelReadinessCalculator.calculate(updated_ctx, retrieved_docs)
        sources = extract_unique_sources(retrieved_docs)

        why_this_answer = WhyThisAnswer(
            understood_destination=updated_ctx.destination_country or "General / Not specified",
            understood_origin=updated_ctx.origin_country or "Not specified",
            travel_purpose=updated_ctx.travel_purpose or "Tourism",
            total_candidate_chunks=eval_result.total_retrieved,
            passed_relevance_chunks=eval_result.relevant_documents_count,
            authoritative_sources_used=len(sources),
            confidence_level=validation_report.confidence_level,
            retrieval_action=eval_result.action_taken,
            grounding_summary=eval_result.explanation + " " + validation_report.summary_explanation,
        )

        self.memory.add_message("assistant", safe_answer, metadata={"sources": sources})

        return ChatResponse(
            answer=safe_answer,
            trip_context=updated_ctx,
            readiness=readiness,
            why_this_answer=why_this_answer,
            sources=sources,
            is_safe=passed_output,
        )

    def stream_query(self, user_query: str) -> Generator[Tuple[str, Optional[ChatResponse]], None, None]:
        """
        Streaming generation generator.
        Yields (chunk_text, None) while streaming, and ("", full_chat_response) upon completion.
        """
        active_ctx = self.memory.get_trip_context()
        has_history = len(self.memory.get_messages()) > 0

        # Input Guardrails
        is_valid, guardrail_msg = InputGuardrail.validate_input(
            user_input=user_query,
            active_trip_context=active_ctx,
            has_conversation_history=has_history,
        )
        if not is_valid:
            readiness = TravelReadinessCalculator.calculate(active_ctx, [])
            why = WhyThisAnswer(
                grounding_summary=f"Blocked by input guardrail: {guardrail_msg}"
            )
            response = ChatResponse(
                answer=guardrail_msg,
                trip_context=active_ctx,
                readiness=readiness,
                why_this_answer=why,
                sources=[],
                is_safe=False,
            )
            yield guardrail_msg, response
            return

        # Context & Retrieval
        updated_ctx = TravelQueryUnderstanding.extract_context(user_query, active_ctx)
        self.memory.update_trip_context(updated_ctx)
        self.memory.add_message("user", user_query)

        retrieved_docs, eval_result = self.corrective_rag.retrieve_with_correction(
            query=user_query,
            destination_country=updated_ctx.destination_country,
            context_metadata=updated_ctx.to_dict(),
        )

        # LLM Streaming
        accumulated_chunks = []
        for text_chunk in self._stream_llm_answer(
            user_query=user_query,
            trip_context=updated_ctx,
            retrieved_docs=retrieved_docs,
            is_evidence_sufficient=eval_result.is_sufficient,
        ):
            accumulated_chunks.append(text_chunk)
            yield text_chunk, None

        full_raw_answer = "".join(accumulated_chunks)

        safe_answer, passed_output = OutputGuardrail.sanitize_and_validate(
            raw_output=full_raw_answer,
            retrieved_docs=retrieved_docs,
            is_evidence_sufficient=eval_result.is_sufficient,
        )

        validation_report = GroundingValidator.validate_answer(
            generated_answer=safe_answer,
            retrieved_docs=retrieved_docs,
            is_evidence_sufficient=eval_result.is_sufficient,
        )

        readiness = TravelReadinessCalculator.calculate(updated_ctx, retrieved_docs)
        sources = extract_unique_sources(retrieved_docs)

        why_this_answer = WhyThisAnswer(
            understood_destination=updated_ctx.destination_country or "General / Not specified",
            understood_origin=updated_ctx.origin_country or "Not specified",
            travel_purpose=updated_ctx.travel_purpose or "Tourism",
            total_candidate_chunks=eval_result.total_retrieved,
            passed_relevance_chunks=eval_result.relevant_documents_count,
            authoritative_sources_used=len(sources),
            confidence_level=validation_report.confidence_level,
            retrieval_action=eval_result.action_taken,
            grounding_summary=eval_result.explanation + " " + validation_report.summary_explanation,
        )

        self.memory.add_message("assistant", safe_answer, metadata={"sources": sources})

        final_response = ChatResponse(
            answer=safe_answer,
            trip_context=updated_ctx,
            readiness=readiness,
            why_this_answer=why_this_answer,
            sources=sources,
            is_safe=passed_output,
        )
        yield "", final_response

    def _generate_llm_answer(
        self,
        user_query: str,
        trip_context: TripContext,
        retrieved_docs: List[ScoredDocument],
        is_evidence_sufficient: bool,
    ) -> str:
        """Call LLM or deterministic grounded generator if no API key present."""
        chunks = list(self._stream_llm_answer(user_query, trip_context, retrieved_docs, is_evidence_sufficient))
        return "".join(chunks)

    def _stream_llm_answer(
        self,
        user_query: str,
        trip_context: TripContext,
        retrieved_docs: List[ScoredDocument],
        is_evidence_sufficient: bool,
    ) -> Generator[str, None, None]:
        """Stream chunks from OpenAI or deterministic local grounded response."""
        if not is_evidence_sufficient or not retrieved_docs:
            dest = trip_context.destination_country or "your destination"
            fallback = (
                f"### Short Answer\n"
                f"I could not locate sufficient authoritative information in the current VoyageAI knowledge base "
                f"for **{dest}** regarding your specific query.\n\n"
                f"### Recommended Steps\n"
                f"1. Check the official embassy, consulate, or immigration authority portal for {dest}.\n"
                f"2. Ensure you review current passport validity and visa requirements prior to departure."
            )
            yield fallback
            return

        formatted_context = format_context_for_llm(retrieved_docs)
        user_prompt = (
            f"<trip_context>\n"
            f"Origin: {trip_context.origin_country or 'Not specified'}\n"
            f"Destination: {trip_context.destination_country or 'Not specified'}\n"
            f"Purpose: {trip_context.travel_purpose or 'Tourism'}\n"
            f"Duration: {trip_context.duration or 'Not specified'}\n"
            f"</trip_context>\n\n"
            f"<context>\n{formatted_context}\n</context>\n\n"
            f"User Question: {user_query}\n"
            f"Answer thoroughly based ONLY on the provided context."
        )

        # Check for OpenAI API Key
        if config.openai_api_key and config.openai_api_key != "your-openai-api-key-here":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=config.openai_api_key)
                response = client.chat.completions.create(
                    model=config.openai_model,
                    messages=[
                        {"role": "system", "content": VOYAGEAI_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    stream=True,
                )
                for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    if content:
                        yield content
                return
            except Exception as e:
                logger.error(f"OpenAI API call error: {e}. Falling back to grounded context synthesis.")

        # Local deterministic synthesis from retrieved documents
        yield self._synthesize_grounded_local_response(trip_context, retrieved_docs, user_query)

    def _synthesize_grounded_local_response(
        self,
        trip_context: TripContext,
        docs: List[ScoredDocument],
        query: str,
    ) -> str:
        """Deterministic, grounded template formatter for offline / test execution."""
        primary_doc = docs[0]
        country = trip_context.destination_country or primary_doc.metadata.get("destination_country", "your destination")
        origin = trip_context.origin_country or "foreign nationals"
        v_type = primary_doc.metadata.get("visa_type", "Standard Tourist Visa")
        fees = primary_doc.metadata.get("fees", "Check official portal")
        time_est = primary_doc.metadata.get("processing_time", "15 calendar days")

        return (
            f"### Short Answer\n"
            f"Travelers from **{origin}** visiting **{country}** for {trip_context.travel_purpose or 'tourism'} "
            f"must apply for a **{v_type}** before departure unless eligible for an exemption.\n\n"
            f"### Visa Requirements\n"
            f"- **Visa Type**: {v_type}\n"
            f"- **Permitted Stay**: Up to 90 days in a 180-day window (standard short stay)\n"
            f"- **Official Fee**: {fees}\n"
            f"- **Estimated Processing**: {time_est}\n\n"
            f"### Required Documents\n"
            f"- **Passport**: Valid for at least 3-6 months beyond departure with blank pages\n"
            f"- **Travel Medical Insurance**: Minimum €30,000 / adequate emergency medical coverage\n"
            f"- **Itinerary**: Confirmed round-trip flight bookings and accommodation reservations\n"
            f"- **Financial Proof**: Recent bank statements (3-6 months) showing sufficient maintenance funds\n"
            f"- **Employment Proof**: Leave authorization letter from employer\n\n"
            f"### Application & Entry Process\n"
            f"1. Complete the online visa application form on the official government portal.\n"
            f"2. Book an appointment at an accredited visa application centre (VFS Global / TLScontact).\n"
            f"3. Submit biometric data (fingerprints & photo) and supporting documentation.\n"
            f"4. Receive decision and stamped passport vignette / electronic visa.\n\n"
            f"### Important Notes & Caveats\n"
            f"- Apply at least 15 to 45 days in advance of your scheduled travel.\n"
            f"- Border officials at entry points may request proof of accommodation and medical insurance."
        )
