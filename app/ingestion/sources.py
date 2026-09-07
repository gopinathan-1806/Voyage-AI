"""
Source Registry containing authoritative travel and immigration portals.
"""

from typing import List
from app.ingestion.models import TravelSource

# Comprehensive registry of verified official government & embassy portals
AUTHORITATIVE_SOURCES: List[TravelSource] = [
    # France / Schengen
    TravelSource(
        source_id="france-visas-gov",
        destination_country="France",
        origin_country="All",
        source_name="France-Visas (Official French Visa Portal)",
        source_url="https://france-visas.gouv.fr/",
        source_type="government",
        document_type="visa_information",
        authority_score=1.0,
        description="Official portal for visa applications to France and Schengen area.",
    ),
    TravelSource(
        source_id="france-diplomatie",
        destination_country="France",
        origin_country="All",
        source_name="Ministry for Europe and Foreign Affairs - France",
        source_url="https://www.diplomatie.gouv.fr/en/coming-to-france/",
        source_type="government",
        document_type="entry_rules",
        authority_score=1.0,
        description="Official French foreign affairs entry guidelines, passport validity and customs.",
    ),

    # Germany / Schengen
    TravelSource(
        source_id="germany-diplo",
        destination_country="Germany",
        origin_country="All",
        source_name="Federal Foreign Office - Germany (Auswärtiges Amt)",
        source_url="https://www.auswaertiges-amt.de/en/visa-service",
        source_type="government",
        document_type="visa_information",
        authority_score=1.0,
        description="Official visa requirements, national visas, and Schengen tourist visa procedures.",
    ),

    # United Kingdom
    TravelSource(
        source_id="uk-gov-visas",
        destination_country="United Kingdom",
        origin_country="All",
        source_name="GOV.UK Visas and Immigration (UKVI)",
        source_url="https://www.gov.uk/standard-visitor",
        source_type="government",
        document_type="visa_information",
        authority_score=1.0,
        description="Official UK Standard Visitor Visa rules, processing fees, biometric requirements.",
    ),

    # United States
    TravelSource(
        source_id="us-travel-state",
        destination_country="United States",
        origin_country="All",
        source_name="U.S. Department of State - Bureau of Consular Affairs",
        source_url="https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html",
        source_type="government",
        document_type="visa_information",
        authority_score=1.0,
        description="B1/B2 Visitor visa requirements, DS-160 application, SEVIS, interview wait times.",
    ),

    # United Arab Emirates (UAE)
    TravelSource(
        source_id="uae-icp-gov",
        destination_country="UAE",
        origin_country="All",
        source_name="Federal Authority for Identity, Citizenship, Customs and Port Security (ICP)",
        source_url="https://icp.gov.ae/en/",
        source_type="government",
        document_type="visa_information",
        authority_score=1.0,
        description="Official tourist visa, visa on arrival guidelines, and GCC entry requirements.",
    ),

    # Singapore
    TravelSource(
        source_id="singapore-ica",
        destination_country="Singapore",
        origin_country="All",
        source_name="Immigration & Checkpoints Authority (ICA Singapore)",
        source_url="https://www.ica.gov.sg/enter-transit-depart/entering-singapore",
        source_type="government",
        document_type="entry_rules",
        authority_score=1.0,
        description="SG Arrival Card, visa requirements, assessment level 1 and 2 countries.",
    ),

    # Japan
    TravelSource(
        source_id="japan-mofa",
        destination_country="Japan",
        origin_country="All",
        source_name="Ministry of Foreign Affairs of Japan (MOFA)",
        source_url="https://www.mofa.go.jp/j_info/visit/visa/index.html",
        source_type="government",
        document_type="visa_information",
        authority_score=1.0,
        description="Short-term stay visas, eVisa eligible countries, and Visit Japan Web customs declarations.",
    ),

    # Australia
    TravelSource(
        source_id="australia-homeaffairs",
        destination_country="Australia",
        origin_country="All",
        source_name="Department of Home Affairs - Australian Government",
        source_url="https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600",
        source_type="government",
        document_type="visa_information",
        authority_score=1.0,
        description="Visitor visa (subclass 600) tourist stream, biometric collections, and processing times.",
    ),
]


def get_all_sources() -> List[TravelSource]:
    """Retrieve active sources."""
    return [s for s in AUTHORITATIVE_SOURCES if s.is_active]


def get_sources_by_destination(destination_country: str) -> List[TravelSource]:
    """Filter sources by destination country."""
    dest_lower = destination_country.strip().lower()
    return [
        s for s in AUTHORITATIVE_SOURCES 
        if s.is_active and s.destination_country.lower() == dest_lower
    ]
