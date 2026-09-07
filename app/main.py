"""
VoyageAI - Premium Streamlit Web Application.
Travel & Immigration Intelligence Assistant.
"""

import os
import sys
from pathlib import Path

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from typing import Optional
import streamlit as st
from app.config import config
from app.chatbot import TravelImmigrationChatbot, ChatResponse
from app.rag.query_understanding import TripContext
from app.logging_config import configure_logging, get_logger

# Configure logging & Streamlit page settings
configure_logging(config.log_level)
logger = get_logger(__name__)

st.set_page_config(
    page_title="VoyageAI | Travel & Immigration Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Premium CSS Design System
PREMIUM_CSS = """
<style>
    /* Global font & dark navy background theme */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Header hero styling */
    .hero-container {
        padding: 1.8rem 2rem;
        background: linear-gradient(135deg, #161b22 0%, #1a2332 50%, #0e2238 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff 0%, #79c0ff 50%, #56d364 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #8b949e;
        margin-top: 0.4rem;
        margin-bottom: 0;
        font-weight: 400;
    }
    
    /* Trip Context Card */
    .trip-banner {
        background: #161b22;
        border-left: 4px solid #58a6ff;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .trip-route {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f0f6fc;
    }
    
    .trip-badge {
        background: #1f2937;
        color: #79c0ff;
        border: 1px solid #388bfd40;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }

    /* Readiness Cards */
    .readiness-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .readiness-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .readiness-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 0.8rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    
    .card-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #58a6ff;
    }
    
    .card-desc {
        font-size: 0.8rem;
        color: #8b949e;
        margin-top: 0.3rem;
    }
    
    /* Why this answer badge */
    .why-answer-box {
        background: #13233a;
        border: 1px solid #1f4272;
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        margin-top: 0.8rem;
        font-size: 0.85rem;
        color: #a5d6ff;
    }

    /* Quick action buttons */
    .quick-chip {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        color: #c9d1d9;
        font-size: 0.88rem;
        cursor: pointer;
        margin-bottom: 0.5rem;
    }
    
    /* Source pill */
    .source-pill {
        display: inline-block;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 0.4rem 0.7rem;
        margin: 0.3rem 0.3rem 0.3rem 0;
        font-size: 0.8rem;
    }
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


def get_country_flag(country_name: Optional[str]) -> str:
    """Return flag emoji for known destinations."""
    if not country_name:
        return "🌐"
    flags = {
        "india": "🇮🇳",
        "france": "🇫🇷",
        "germany": "🇩🇪",
        "united kingdom": "🇬🇧",
        "united states": "🇺🇸",
        "uae": "🇦🇪",
        "singapore": "🇸🇬",
        "japan": "🇯🇵",
        "australia": "🇦🇺",
    }
    return flags.get(country_name.lower().strip(), "📍")


# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = TravelImmigrationChatbot()

if "trip_context" not in st.session_state:
    st.session_state.trip_context = TripContext()

if "last_response" not in st.session_state:
    st.session_state.last_response = None


# Sidebar: System Controls & Destination Registry
with st.sidebar:
    st.markdown("### ✈️ **VoyageAI Control Center**")
    st.caption("Authoritative Travel & Immigration AI")
    
    st.divider()
    
    st.markdown("#### 🎯 **Active Trip Context**")
    ctx = st.session_state.trip_context
    dest = ctx.destination_country or "Not set"
    orig = ctx.origin_country or "Not set"
    purp = ctx.travel_purpose or "Tourism"
    dur = ctx.duration or "Not set"
    
    st.markdown(f"**Origin**: {get_country_flag(orig)} {orig}")
    st.markdown(f"**Destination**: {get_country_flag(dest)} {dest}")
    st.markdown(f"**Purpose**: 🏷️ {purp}")
    st.markdown(f"**Duration**: ⏱️ {dur}")
    
    if st.button("🔄 Reset Trip Context", use_container_width=True):
        st.session_state.chatbot.memory.clear()
        st.session_state.trip_context = TripContext()
        st.session_state.messages = []
        st.session_state.last_response = None
        st.rerun()

    st.divider()

    st.markdown("#### 🏛️ **Knowledge Base Sources**")
    st.markdown("""
    - 🇫🇷 **France**: France-Visas & Ministère des Affaires Étrangères
    - 🇩🇪 **Germany**: Auswärtiges Amt (Federal Foreign Office)
    - 🇬🇧 **UK**: GOV.UK Visas & Immigration (UKVI)
    - 🇺🇸 **USA**: U.S. Dept of State (Travel.state.gov)
    - 🇦🇪 **UAE**: ICP & GDRFA Dubai Portals
    - 🇸🇬 **Singapore**: ICA Singapore & SG Arrival Card
    - 🇯🇵 **Japan**: MOFA Japan & Japan eVISA
    - 🇦🇺 **Australia**: Dept of Home Affairs Subclass 600
    """)
    
    st.divider()
    
    st.caption("🔒 Verified Official Government Data | Zero Hallucination Mode")


# Main Header Hero
st.markdown("""
<div class="hero-container">
    <div class="hero-title">VoyageAI</div>
    <div class="hero-subtitle">Travel & Immigration Intelligence Assistant • Authoritative Knowledge & Hybrid Grounding</div>
</div>
""", unsafe_allow_html=True)


# Render Trip Context Banner if destination identified
if st.session_state.trip_context.destination_country:
    orig_flag = get_country_flag(st.session_state.trip_context.origin_country)
    dest_flag = get_country_flag(st.session_state.trip_context.destination_country)
    orig_text = st.session_state.trip_context.origin_country or "Global"
    dest_text = st.session_state.trip_context.destination_country
    purpose_text = st.session_state.trip_context.travel_purpose or "Tourism"
    dur_text = st.session_state.trip_context.duration or "Standard Stay"
    date_text = st.session_state.trip_context.travel_date or "Upcoming"

    st.markdown(f"""
    <div class="trip-banner">
        <div>
            <div class="trip-route">{orig_flag} {orig_text} ➔ {dest_flag} {dest_text}</div>
            <div style="margin-top: 0.4rem;">
                <span class="trip-badge">🏷️ {purpose_text}</span>
                <span class="trip-badge">⏱️ {dur_text}</span>
                <span class="trip-badge">📅 {date_text}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Render Travel Readiness Component Cards if response available
if st.session_state.last_response and st.session_state.last_response.readiness:
    readiness = st.session_state.last_response.readiness
    st.markdown("#### 📊 **Travel Readiness Intelligence**")
    
    # Progress Bar
    st.progress(readiness.overall_score / 100.0, text=f"Readiness Score: {readiness.overall_score}% ({readiness.status_label})")
    
    cols = st.columns(len(readiness.components))
    for i, comp in enumerate(readiness.components):
        with cols[i]:
            st.markdown(f"""
            <div class="readiness-card">
                <div class="card-title">{comp.name}</div>
                <div class="card-value">{comp.status}</div>
                <div class="card-desc">{comp.summary}</div>
            </div>
            """, unsafe_allow_html=True)
    st.write("")


# Empty State Quick Actions (shown when no messages yet)
if not st.session_state.messages:
    st.markdown("#### 💡 **Try one of these verified travel queries:**")
    quick_cols = st.columns(2)
    
    example_prompts = [
        "I am an Indian citizen travelling to France for 10 days in December for tourism. What do I need?",
        "What documents are required for a Germany tourist visa?",
        "How much does a UK standard visitor visa cost and how long does it take?",
        "What are the entry rules for Singapore and do I need the SG Arrival Card?",
    ]
    
    for idx, prompt in enumerate(example_prompts):
        col = quick_cols[idx % 2]
        if col.button(f"✈️ {prompt}", key=f"quick_{idx}", use_container_width=True):
            st.session_state.active_prompt = prompt
            st.rerun()


# Handle Quick Prompt Selection
active_query = None
if "active_prompt" in st.session_state and st.session_state.active_prompt:
    active_query = st.session_state.active_prompt
    st.session_state.active_prompt = None


# Render Chat Message History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Render Sources Drawer if available on assistant messages
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            with st.expander(f"📚 Verified Sources ({len(msg['sources'])})"):
                for s in msg["sources"]:
                    st.markdown(
                        f"- **[{s['name']}]({s['url']})** — *{s['document_type']}* (Updated: {s['last_updated']})"
                    )

        # Render Why-This-Answer if available
        if msg["role"] == "assistant" and "why" in msg and msg["why"]:
            why = msg["why"]
            st.markdown(f"""
            <div class="why-answer-box">
                🔍 <b>Why this answer?</b><br>
                • Understood Origin: <b>{why.understood_origin}</b> | Destination: <b>{why.understood_destination}</b><br>
                • Retrieved <b>{why.total_candidate_chunks}</b> chunks (<b>{why.passed_relevance_chunks}</b> passed relevance validation)<br>
                • Supported by <b>{why.authoritative_sources_used}</b> authoritative sources with <b>{why.confidence_level}</b> confidence.<br>
                • <i>{why.grounding_summary}</i>
            </div>
            """, unsafe_allow_html=True)


# Chat Input Box
user_prompt = st.chat_input("Ask about visa requirements, documents, processing fees, or entry rules...") or active_query

if user_prompt:
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Stream Assistant Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_streamed_text = ""

        # Stream response
        final_chat_response: Optional[ChatResponse] = None
        for chunk, response_obj in st.session_state.chatbot.stream_query(user_prompt):
            if chunk:
                full_streamed_text += chunk
                response_placeholder.markdown(full_streamed_text + "▌")
            if response_obj:
                final_chat_response = response_obj

        response_placeholder.markdown(full_streamed_text)

        # Update Session State with Response details
        if final_chat_response:
            st.session_state.trip_context = final_chat_response.trip_context
            st.session_state.last_response = final_chat_response

            st.session_state.messages.append({
                "role": "assistant",
                "content": final_chat_response.answer,
                "sources": final_chat_response.sources,
                "why": final_chat_response.why_this_answer,
            })

            # Render Sources Expander
            if final_chat_response.sources:
                with st.expander(f"📚 Verified Sources ({len(final_chat_response.sources)})"):
                    for s in final_chat_response.sources:
                        st.markdown(
                            f"- **[{s['name']}]({s['url']})** — *{s['document_type']}* (Updated: {s['last_updated']})"
                        )

            # Render Why-This-Answer
            why = final_chat_response.why_this_answer
            st.markdown(f"""
            <div class="why-answer-box">
                🔍 <b>Why this answer?</b><br>
                • Understood Origin: <b>{why.understood_origin}</b> | Destination: <b>{why.understood_destination}</b><br>
                • Retrieved <b>{why.total_candidate_chunks}</b> chunks (<b>{why.passed_relevance_chunks}</b> passed relevance validation)<br>
                • Supported by <b>{why.authoritative_sources_used}</b> authoritative sources with <b>{why.confidence_level}</b> confidence.<br>
                • <i>{why.grounding_summary}</i>
            </div>
            """, unsafe_allow_html=True)

            st.rerun()
