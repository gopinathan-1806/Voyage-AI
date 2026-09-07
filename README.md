# ✈️ VoyageAI — Travel & Immigration Intelligence Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![FAISS](https://img.shields.io/badge/VectorStore-FAISS-00599C.svg)](https://github.com/facebookresearch/faiss)
[![BM25](https://img.shields.io/badge/KeywordSearch-BM25Okapi-green.svg)](https://github.com/dorianbrown/rank_bm25)
[![Tests Passing](https://img.shields.io/badge/tests-22%2F22%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen.svg)]()

**VoyageAI** is a competition-grade, enterprise-ready **Travel & Immigration Intelligence Assistant** built to provide accurate, grounded, authoritative, and fresh immigration advice.

Unlike simple wrapper chatbots, VoyageAI combines **Hybrid Search (Dense Vector + Sparse BM25 + Lexical Overlap)**, **Corrective Retrieval-Augmented Generation (CRAG)**, **Self-RAG Grounding Verification**, **Structured Query Understanding**, **Multi-Layer Guardrails**, and an interactive **Travel Readiness Scoring Engine**.

---

## 📌 Table of Contents
1. [System Architecture](#-system-architecture)
2. [End-to-End Execution Flow](#-end-to-end-execution-flow)
3. [Key Features & Differentiation](#-key-features--differentiation)
4. [Authoritative Knowledge Base](#-authoritative-knowledge-base)
5. [Directory Structure](#-directory-structure)
6. [Installation & Setup](#-installation--setup)
7. [Running the Application](#-running-the-application)
8. [Evaluation & Testing](#-evaluation--testing)
9. [Security & Guardrails](#-security--guardrails)
10. [Future Roadmap](#-future-roadmap)

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph INGESTION["Knowledge Ingestion Pipeline (Offline / Scheduled)"]
        A[Official Source Registry] --> B1[Web Scraper: Playwright / Requests]
        A --> B2[PDF Extractor: pypdf]
        B1 --> C[Text Normalization & Cleaner]
        B2 --> C
        C --> D[Travel Metadata Extractor]
        D --> E[Semantic Text Splitter]
        E --> F1[BM25Okapi Indexer]
        E --> F2[FAISS Vector Store: Embeddings]
    end

    subgraph RUNTIME["Real-Time Execution Pipeline"]
        User([User Prompt]) --> G[Input Guardrails & Injection Detector]
        G -->|Violation / Unsafe| Refusal[Security & Policy Alert]
        G -->|Safe / Valid| H[Query Parser & Trip Context Extractor]
        H --> I[Hybrid Retriever: Vector 0.60 + BM25 0.30 + Lexical 0.10]
        I --> J{Relevance Evaluator: CRAG}
        J -->|Low Confidence / Weak| K[Query Reformulation Loop]
        K --> I
        J -->|High Confidence| L[Context Assembly & Grounding]
        L --> M[LLM Streaming: GPT-4o-mini / Local Grounded]
        M --> N[Self-RAG Grounding & Output Guardrails]
        N --> O[Answer + Citations + Readiness Score + Why-This-Answer]
        O --> UI[Streamlit UI Dashboard]
    end
```

---

## 🔄 End-to-End Execution Flow

Here is the step-by-step lifecycle of every user query in VoyageAI:

```mermaid
sequenceDiagram
    autonumber
    actor Traveler as Traveler (UI)
    participant Guard as Input Guardrails
    participant Parser as Query Understanding
    participant CRAG as Corrective RAG
    participant Retriever as Hybrid Retriever (FAISS + BM25)
    participant LLM as LLM Generation
    participant OutGuard as Output Guardrails & Self-RAG
    participant Memory as Session Memory

    Traveler->>Guard: "Origin: India, Destination: France for 10 days"
    Guard->>Guard: Check Prompt Injection, Weapons/Harm, Domain Boundary
    Guard-->>Traveler: (If violation: Refuse with Security Alert)
    
    Guard->>Parser: Safe Query
    Parser->>Parser: Extract Origin: India, Destination: France, Purpose: Tourism, Stay: 10d
    Parser->>Memory: Update Session TripContext
    
    Parser->>CRAG: Evaluate & Retrieve(Query, Destination=France)
    CRAG->>Retriever: Hybrid Search (Vector + BM25 + Boosts)
    Retriever-->>CRAG: Ranked Scored Documents
    CRAG->>CRAG: Check Relevance Threshold (0.35)
    alt Low Confidence
        CRAG->>Retriever: Corrective Query Reformulation Search
        Retriever-->>CRAG: Expanded Evidence
    end

    CRAG->>LLM: Formatted XML Context + Trip Context + Grounding Rules
    LLM-->>Traveler: Streamed Answer Tokens (Progressive)
    
    LLM->>OutGuard: Full Raw Answer
    OutGuard->>OutGuard: Check Groundedness, Hallucinations, Append Disclaimer
    OutGuard->>Memory: Persist Turn + Citations
    OutGuard-->>Traveler: Verified Sources Drawer + Travel Readiness Score + Why-This-Answer
```

### Detailed Flow Steps:

1. **Input Guardrail Check (`app/guardrails/input_guardrail.py`)**:
   - Inspects for prompt injection (`ignore previous instructions`, `DAN mode`), hazardous requests (explosives, weapons), and border evasion (illegal crossing, fake passports).
   - Allows natural conversational follow-ups (`"10 days"`, `"tourism"`, `"what documents?"`) when active trip context exists.

2. **Query Understanding (`app/rag/query_understanding.py`)**:
   - Parses structured travel entities: `origin_country`, `destination_country`, `travel_purpose`, `duration`, `travel_date`, and `question_type`.
   - Supports both conversational sentences and key-value inputs (`Origin: India, Destination: UK`).

3. **Hybrid Retrieval (`app/rag/hybrid_retriever.py`)**:
   - Dense semantic vector search via **FAISS** (`text-embedding-3-small`).
   - Sparse keyword search via **BM25Okapi**.
   - Non-stopword Jaccard lexical overlap computation.
   - Metadata boost applied for exact destination matches.

4. **Corrective RAG (`app/rag/corrective_rag.py`)**:
   - Measures candidate relevance against `RELEVANCE_THRESHOLD=0.35`.
   - If confidence is low or documents are sparse, reformulates the query and triggers secondary retrieval.
   - Prevents hallucinations by returning an explicit insufficient-evidence notice if no authoritative knowledge exists.

5. **Self-RAG Grounding & Output Guardrails (`app/guardrails/output_guardrail.py` & `app/rag/grounding_checker.py`)**:
   - Validates generated fees and numbers against retrieved text.
   - Attaches official immigration verification notices while suppressing them on security refusals.

6. **Travel Readiness Scoring (`app/rag/readiness_calculator.py`)**:
   - Computes an informational 0–100% readiness score evaluating Visa Category, Document Checklist, Passport Validity, Timeline, and Arrival Formalities.

7. **Explainability (`Why this answer?`)**:
   - Displays parsed parameters, candidate chunk counts, relevance pass rates, and source citations without exposing private system prompts.

---

## 🌟 Key Features & Differentiation

| Feature | Description |
|---|---|
| **Authoritative Government Sources** | Data curated directly from official government portals (France-Visas, Auswärtiges Amt, UKVI, US State Dept, UAE ICP, Singapore ICA, Japan MOFA, Australian Home Affairs). |
| **Hybrid Search Fusion** | Weighted score formula: `(0.60 * Vector) + (0.30 * BM25) + (0.10 * Lexical) * DestinationBoost`. |
| **Zero-Hallucination Fallback** | Explicitly refuses to guess visa rules or fees when authoritative evidence is missing. |
| **Multi-Turn Context Retention** | Remembers trip context across conversation turns without re-asking established details. |
| **Session Isolation** | Clean in-memory session boundary (`InMemorySessionStore`), ready to swap for Redis or PostgreSQL. |
| **Offline Fallback Generator** | Includes deterministic grounded template generation when running without an OpenAI API key. |
| **Premium Streamlit UI** | Modern deep navy dashboard with real-time streaming, country badges, progress gauges, and collapsible source cards. |

---

## 🏛️ Authoritative Knowledge Base

VoyageAI contains pre-indexed official immigration knowledge for major global destinations:

- 🇫🇷 **France**: Short-Stay Schengen Type C Visa, €90 fees, 15–45 day processing, €30k insurance rules.
- 🇩🇪 **Germany**: VIDEX application requirements, biometrics, blocked account / Verpflichtungserklärung.
- 🇬🇧 **United Kingdom**: Standard Visitor Visa (£115), 3-week processing, financial documentation.
- 🇺🇸 **United States**: B1/B2 Visitor Visa ($185 MRV fee), DS-160 application, 214(b) ties to home country.
- 🇦🇪 **UAE (Dubai/Abu Dhabi)**: 30/60-day tourist visas, GCC entry rules, 14-day VoA facility for Indian passport holders with US/UK/EU visas.
- 🇸🇬 **Singapore**: SG Arrival Card (SGAC), Level I/II assessment countries, Form 14A, SGD $30 fee.
- 🇯🇵 **Japan**: Short-Term Tourist Visa, Japan eVISA portal, Visit Japan Web immigration/customs QR.
- 🇦🇺 **Australia**: Visitor Visa Subclass 600 (Tourist Stream), AUD $190 fee, biometrics.

---

## 📂 Directory Structure

```
voyage_AI/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuration & environment loader (.env)
│   ├── logging_config.py         # Structured logging configuration
│   ├── chatbot.py                # Core TravelImmigrationChatbot engine & streaming
│   ├── runtime.py                # Singleton runtime manager
│   ├── main.py                   # Premium Streamlit UI application
│   │
│   ├── guardrails/               # Security & domain enforcement
│   │   ├── __init__.py
│   │   ├── injection_detector.py # Prompt injection & weapons/harm detector
│   │   ├── input_guardrail.py    # Domain scope & conversational tolerance
│   │   └── output_guardrail.py   # Output sanitizer & disclaimer manager
│   │
│   ├── ingestion/                # Knowledge ingestion pipeline
│   │   ├── __init__.py
│   │   ├── models.py             # TravelDocument & TravelSource Pydantic models
│   │   ├── sources.py            # Official immigration source registry
│   │   ├── cleaner.py            # Text cleaner & Unicode normalizer
│   │   ├── extractor.py          # HTML & PDF (pypdf) extractors
│   │   ├── scraper.py            # Playwright / Requests ethical scraper
│   │   └── pipeline.py           # Ingestion pipeline runner
│   │
│   ├── rag/                      # RAG & Retrieval Engine
│   │   ├── __init__.py
│   │   ├── embeddings.py         # OpenAI & Deterministic Hash embeddings
│   │   ├── indexer.py            # FAISS vector store & BM25Okapi indexer
│   │   ├── hybrid_retriever.py   # Hybrid fusion retriever
│   │   ├── retrieval_quality.py  # Lexical overlap scoring
│   │   ├── query_rewriter.py     # Domain keyword expansion
│   │   ├── query_understanding.py# Structured TripContext extractor
│   │   ├── corrective_rag.py     # Corrective RAG evaluation & retry engine
│   │   ├── grounding_checker.py  # Self-RAG groundedness validator
│   │   ├── readiness_calculator.py# Travel Readiness Score (0-100%)
│   │   ├── prompts.py            # Grounded system prompts & templates
│   │   └── source_formatter.py   # Citation & XML context formatting
│   │
│   ├── memory/                   # Conversational memory abstraction
│   │   ├── __init__.py
│   │   └── session_memory.py     # Session-isolated memory store
│   │
│   ├── evaluation/               # Automated benchmark evaluation
│   │   ├── __init__.py
│   │   ├── datasets.py           # Curated travel & adversarial test cases
│   │   ├── metrics.py            # Accuracy & latency metrics
│   │   └── evaluator.py          # Evaluation runner
│   │
│   └── observability/            # LangSmith tracing (optional)
│       ├── __init__.py
│       └── langsmith.py
│
├── data/
│   └── travel/
│       ├── seed_data.py          # Seed authoritative documents
│       └── processed/            # Processed TravelDocument JSON files
│
├── indexes/                      # Generated FAISS & BM25 binary indexes
│   ├── faiss_index/
│   ├── bm25_index.pkl
│   └── metadata.json
│
├── tests/                        # Comprehensive PyTest test suite (22 tests)
│   ├── test_guardrails.py
│   ├── test_query_understanding.py
│   ├── test_retrieval.py
│   ├── test_corrective_rag.py
│   ├── test_memory.py
│   └── test_chatbot.py
│
├── .env.example
├── requirements.txt
├── run.py                        # Python execution entrypoint
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone & Set Up Virtual Environment
```bash
git clone <repo-url>
cd voyage_AI

python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

*(Optional) Install Playwright Chromium for dynamic browser scraping:*
```bash
playwright install chromium
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to configure your API keys:
```ini
APP_NAME=VoyageAI
APP_ENV=development
LOG_LEVEL=INFO

# OpenAI API Settings
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# RAG & Chunking Parameters
CHUNK_SIZE=800
CHUNK_OVERLAP=150
RETRIEVAL_TOP_K=6
RELEVANCE_THRESHOLD=0.35

# Hybrid Weights
VECTOR_WEIGHT=0.60
BM25_WEIGHT=0.30
LEXICAL_WEIGHT=0.10

# Optional LangSmith Tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=voyageai
```

---

## 🚀 Running the Application

### 1. Ingest Knowledge & Build Indexes (Initial Setup)
```bash
# Ingest authoritative knowledge documents
python -m data.travel.seed_data

# Build FAISS vector store & BM25 index
python -m app.rag.indexer
```

### 2. Launch the Web Application
```bash
streamlit run app/main.py
```
*Or run using the Python launcher:*
```bash
python run.py
```
Open your browser at **`http://localhost:8501`**.

---

## 🧪 Evaluation & Testing

VoyageAI comes with a **22-test suite** covering guardrails, query understanding, hybrid retrieval, memory isolation, and corrective RAG.

### Run Unit Tests
```bash
pytest -v
```

### Run Test Coverage
```bash
pytest --cov=app --cov-report=term-missing
```

### Run Automated Benchmark Evaluator
```bash
python -m app.evaluation.evaluator
```

---

## 🛡️ Security & Guardrails

- **Zero Secret Exposure**: API keys are loaded via environment variables and never logged, sent to client UI, or committed to Git.
- **Input Guardrails**:
  - Catches instruction injection (`ignore instructions`, `reveal system prompt`).
  - Refuses malicious requests (explosives, weapons, illegal border crossing, fake passports).
  - Tolerates short conversational follow-ups (`"10 days"`, `"tourism"`) when an active trip context exists.
- **Output Guardrails**:
  - Evaluates generated responses for factual grounding.
  - Automatically appends verification disclaimers for valid travel advice while suppressing them on security refusals.

---

## 🗺️ Future Roadmap

- [ ] **Multi-Agent Orchestration**: Integrate LangGraph for complex visa appeal and multi-destination itinerary workflows.
- [ ] **Live Embassy Wait Times**: Real-time integration with VFS/TLS appointment tracking.
- [ ] **Persistent Databases**: PostgreSQL / Redis backend adapters for `BaseSessionMemory`.
- [ ] **Multilingual Support**: Real-time translation of authoritative government notices into 20+ languages.
