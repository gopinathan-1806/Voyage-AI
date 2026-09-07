"""
Script to populate authoritative travel knowledge base with structured, verified travel & immigration data
for core destination countries: France, Germany, UK, US, UAE, Singapore, Japan, and Australia.
"""

from pathlib import Path
from app.config import config
from app.ingestion.models import TravelDocument
from app.ingestion.pipeline import IngestionPipeline

SEED_DOCUMENTS = [
    # 1. FRANCE - Tourist Visa & Entry Rules
    TravelDocument(
        doc_id="france-schengen-tourism-general",
        title="France Short-Stay Schengen Tourist Visa (Type C) Guide",
        destination_country="France",
        origin_country="All",
        travel_purpose="Tourism",
        document_type="visa_information",
        content="""
# France Short-Stay Schengen Visa (Type C) Official Information

### Visa Overview
Citizens of non-EU/EEA countries who are not visa-exempt (such as citizens of India, China, South Africa, etc.) require a Short-Stay Schengen Visa (Uniform Schengen Visa, Type C) to enter France and the Schengen Area for tourism, visiting family, or short business stays. A Type C visa allows stays of up to 90 days in any 180-day period.

### Eligibility & General Criteria
- The main travel destination or the point of first longest stay in the Schengen Area must be France.
- Intended stay must not exceed 90 days in any 180-day window.
- Applicants must prove financial sufficiency, intention to return to home country, and genuine travel purpose.

### Required Documents
1. **Valid Passport**: Issued within the last 10 years, with at least 3 months validity beyond the scheduled departure date from the Schengen area, and at least 2 blank pages.
2. **Completed Application Form**: Filled online on the official France-Visas portal and signed.
3. **Photographs**: Two recent standard ICAO/ISO-compliant passport photos (35x45mm, light grey or plain background).
4. **Travel Medical Insurance**: Minimum medical coverage of €30,000 covering emergency medical care, hospitalization, and repatriation across the entire Schengen zone.
5. **Proof of Accommodation**: Hotel bookings, rental contract, or an official 'Attestation d'accueil' issued by the French town hall if staying with a resident.
6. **Round-Trip Itinerary**: Flight reservations or itinerary showing entry and exit dates from Schengen territory.
7. **Proof of Financial Means**: Bank statements for the last 3-6 months showing adequate funds (€120/day if no hotel booking, €65/day with hotel booking, €32.50/day with attestation d'accueil), pay slips, or employment proof.
8. **Employment/Student Proof**: Letter from employer granting leave or enrollment certificate.

### Fees & Charges
- Standard Adult Visa Fee: €90 (updated Schengen standard fee).
- Children aged 6–12: €45.
- Children under 6: Free.
- Additional external visa service provider fees (e.g., VFS Global) apply (typically €30–€40).

### Processing Time
- Standard processing time: 15 calendar days from the date of submission at the visa centre.
- During peak travel seasons (May-August, December), applications can take up to 30 to 45 days.
- Applications can be lodged up to 6 months before the intended travel date.

### Entry & Border Requirements
- Valid passport and Schengen visa.
- Boarding officers and French border police (Police aux Frontières) may request to inspect the travel insurance certificate, return ticket, and proof of funds upon arrival at French ports of entry.
        """,
        source_name="France-Visas (Official French Visa Portal)",
        source_url="https://france-visas.gouv.fr/",
        source_type="government",
        visa_type="Short-Stay Schengen Type C",
        eligibility="Non-visa-exempt foreign nationals visiting France for tourism up to 90 days.",
        required_documents=[
            "Passport (valid 3+ months post-departure)",
            "France-Visas application form",
            "Schengen Travel Insurance (€30,000 coverage)",
            "Proof of Accommodation / Hotel reservation",
            "Round-trip flight itinerary",
            "Bank statements (last 3-6 months)",
            "Employment / Leave certificate"
        ],
        application_process="1. Register on France-Visas portal. 2. Complete online application. 3. Book appointment at VFS Global centre. 4. Submit biometrics and documents. 5. Track passport return.",
        fees="€90 for adults; €45 for children 6-12; free for under 6.",
        processing_time="15 to 45 calendar days depending on season.",
        entry_requirements="Valid passport, Schengen Type C visa, travel insurance, proof of accommodation, and financial means.",
        passport_requirements="Issued within 10 years, minimum 3 months validity beyond Schengen departure, 2 blank pages.",
        last_updated="2024-11-15",
    ),

    # 2. GERMANY - Tourist Visa & Entry Rules
    TravelDocument(
        doc_id="germany-schengen-tourism",
        title="Germany Schengen Tourist Visa & Entry Requirements",
        destination_country="Germany",
        origin_country="All",
        travel_purpose="Tourism",
        document_type="visa_information",
        content="""
# Germany Schengen Visitor / Tourist Visa (Category C)

### Visa Summary
For citizens of third countries requiring a visa (including India, China, Philippines, Nigeria), a German Schengen visa is mandatory for tourist, recreational, or private visits for stays up to 90 days within any 180-day period.

### Core Eligibility
- Germany must be the sole or main destination (longest duration of stay) in the Schengen area.
- Applicant must demonstrate stable socio-economic ties to their country of residence.

### Required Application Documents
1. **National Passport**: Valid for at least 3 months after intended departure from Germany, issued within the last 10 years, with at least 2 consecutive blank pages.
2. **VIDEX Application Form**: Completed and signed VIDEX electronic visa application form with declaration section.
3. **Biometric Photos**: 2 identical recent biometric passport photos (35x45mm) meeting German consular biometric criteria.
4. **Travel Health Insurance**: Minimum €30,000 coverage for emergency hospital treatments and repatriation, valid in all 29 Schengen states.
5. **Proof of Financial Resources**: Recent bank statements (last 3 months with official bank seal/stamp), income tax returns (ITR/Form 16), or a formal obligation letter ('Verpflichtungserklärung') if sponsored by a German resident.
6. **Proof of Accommodation & Flight Plan**: Confirmed round-trip flight booking and hotel reservation across entire stay.
7. **Cover Letter & Detailed Itinerary**: Outlining day-by-day travel plan inside Germany.
8. **Proof of Employment**: Leave approval letter from employer, salary slips, or business registration if self-employed.

### Fees
- Regular Visa Fee: €90 for adults.
- Minors (6-12 years): €45.
- Minors under 6: Free.
- Third-party service fee (VFS Global / TLScontact): around €30.

### Processing Timelines
- Standard decision time: Approximately 15 calendar days after biometric capture.
- Early applications: Can be submitted up to 6 months prior to trip. Recommended minimum 3-4 weeks in advance.

### Border Formalities
- Present passport with valid Schengen visa.
- Border authorities (Bundespolizei) at Frankfurt, Munich, Berlin or other points of entry may request proof of health insurance and return ticket.
        """,
        source_name="Federal Foreign Office - Germany (Auswärtiges Amt)",
        source_url="https://www.auswaertiges-amt.de/en/visa-service",
        source_type="government",
        visa_type="Schengen Visa Category C (Tourist)",
        eligibility="Foreign nationals requiring visa whose primary Schengen destination is Germany.",
        required_documents=[
            "Valid Passport with 3+ months validity post-trip",
            "Signed VIDEX visa application form",
            "2 Biometric photographs",
            "Travel Medical Insurance (€30,000 minimum)",
            "Bank statements (3 months with bank stamp)",
            "Confirmed hotel reservations and flight itinerary",
            "Cover letter with daily itinerary",
            "Employer leave sanction letter"
        ],
        application_process="1. Fill VIDEX form. 2. Book appointment at German Visa Application Centre. 3. Submit biometric data and documents. 4. Collection upon decision.",
        fees="€90 (Adults), €45 (Children 6-12)",
        processing_time="15 calendar days (can extend to 45 in peak periods)",
        entry_requirements="Valid passport, Schengen visa, travel insurance, proof of accommodation.",
        passport_requirements="Valid at least 3 months beyond intended departure date, 2 blank pages, issued within 10 years.",
        last_updated="2024-10-20",
    ),

    # 3. UNITED KINGDOM - Standard Visitor Visa
    TravelDocument(
        doc_id="uk-standard-visitor-visa",
        title="UK Standard Visitor Visa Official Guide",
        destination_country="United Kingdom",
        origin_country="All",
        travel_purpose="Tourism",
        document_type="visa_information",
        content="""
# UK Standard Visitor Visa (Tourism, Family, Short Business)

### Visa Overview
Non-visa nationals (EU, US, Australia, Canada, Japan) can enter the UK for tourism without a visa for up to 6 months (subject to ETA requirements). Visa-national citizens (India, China, Pakistan, South Africa, etc.) must apply for a UK Standard Visitor Visa before travelling. A Standard Visitor visa permits stays of up to 6 months for leisure, holiday, visiting friends/family, or participating in permitted business activities.

### Eligibility Criteria
- You must show that you will leave the UK at the end of your visit.
- You are able to support yourself and any dependents without working or accessing public funds.
- You can pay for your return or onward journey.
- You cannot do paid work, live in the UK through frequent visits, or marry (without a Marriage Visitor visa).

### Mandatory Documents
1. **Current Valid Passport**: Must have at least one blank page for the visa sticker (vignette). Must be valid for the duration of the stay in the UK.
2. **Online Application**: Submitted via the official GOV.UK portal.
3. **Financial Evidence**: Bank statements, payslips, or financial sponsor evidence demonstrating sufficient funds to cover all costs during the visit.
4. **Employment & Status**: Letter from employer specifying job title, salary, length of employment, and approved leave of absence.
5. **Accommodation & Travel Details**: Details of where you intend to stay (hotel bookings or invitation letter and proof of address from UK host).
6. **Tuberculosis (TB) Test**: Required only if residing in specific listed countries and applying for a stay longer than 6 months (not required for 6-month standard tourist visitor).

### Fees
- 6-Month Standard Visitor Visa: £115.
- 2-Year Long-Term Visitor Visa: £432.
- 5-Year Long-Term Visitor Visa: £771.
- 10-Year Long-Term Visitor Visa: £963.
- Priority Service (5 working days): £500 additional.
- Super Priority Service (next working day): £1,000 additional.

### Processing Times
- Standard processing: 3 weeks (15 working days) from biometric appointment date at VFS Global / TLScontact.

### Entry Notes
- Passports must be valid for the whole of your stay in the UK.
- Electronic Travel Authorisation (ETA): UK is phasing in ETA for visa-free travellers starting 2024-2025.
        """,
        source_name="GOV.UK Visas and Immigration (UKVI)",
        source_url="https://www.gov.uk/standard-visitor",
        source_type="government",
        visa_type="Standard Visitor Visa (6 Months)",
        eligibility="Nationals requiring entry clearance for tourism, family visits, or permitted activities in the UK.",
        required_documents=[
            "Valid passport with at least 1 blank page",
            "Online GOV.UK application form",
            "Bank statements (last 6 months recommended)",
            "Proof of employment and leave permission",
            "Accommodation details / UK host letter",
            "Travel itinerary"
        ],
        application_process="1. Apply on GOV.UK. 2. Pay visa fee. 3. Book biometric appointment at visa centre. 4. Attend biometrics & submit documents. 5. Receive decision & passport.",
        fees="£115 for 6-month visa.",
        processing_time="3 weeks (15 working days).",
        entry_requirements="Valid passport and UK entry clearance vignette / visa.",
        passport_requirements="Valid for the whole of your stay in the UK.",
        last_updated="2024-12-01",
    ),

    # 4. UNITED STATES - B1/B2 Visitor Visa
    TravelDocument(
        doc_id="us-b1-b2-tourist-visa",
        title="United States B1/B2 Nonimmigrant Visitor Visa",
        destination_country="United States",
        origin_country="All",
        travel_purpose="Tourism",
        document_type="visa_information",
        content="""
# United States B1/B2 Visitor Visa for Tourism & Business

### Visa Overview
Citizens of foreign countries traveling to the United States for tourism, vacation, visiting family, or medical treatment require a B-2 visa (or combined B-1/B-2 visitor visa), unless eligible for the Visa Waiver Program (ESTA). Stays are granted up to 6 months per entry by U.S. Customs and Border Protection (CBP) at the port of entry.

### Eligibility Criteria
Under Section 214(b) of the Immigration and Nationality Act (INA), every applicant is presumed to be an intending immigrant until overcoming this presumption by proving:
- The purpose of trip is a temporary visit for pleasure or medical treatment.
- They intend to remain for a specific, limited period.
- Residence outside the U.S. and binding social/economic ties ensuring their return home.
- Sufficient financial funds to cover all expenses.

### Required Application Documents
1. **Valid Passport**: Valid for travel to the U.S. with validity date at least 6 months beyond intended stay (unless country is exempt via Six-Month Club).
2. **Form DS-160 Confirmation Page**: Online Nonimmigrant Visa Application confirmation barcode.
3. **Application Fee Payment Receipt**: Machine Readable Visa (MRV) fee receipt.
4. **Photo**: 2x2 inches (51x51mm) color photo taken within the last 6 months complying with Department of State specs.
5. **Interview Appointment Confirmation**: Form showing scheduled VAC (biometrics) and Consular interview appointments.
6. **Supporting Documentation** (brought to interview):
   - Proof of income, tax payments, property ownership, or business assets.
   - Travel itinerary and/or explanation of planned trip.
   - Letter from employer detailing position, salary, and authorized leave.

### Visa Fee
- Nonimmigrant Visa Application Fee (MRV): $185 USD (non-refundable).

### Processing & Appointment Times
- Wait times for consular interview appointments vary heavily by location and season (ranging from several weeks to several months).
- Passport return following approved interview: 3 to 7 business days.

### Port of Entry Requirements
- A visa does not guarantee entry into the U.S. CBP officers at port of entry determine eligibility and length of authorized stay (Form I-94).
        """,
        source_name="U.S. Department of State - Bureau of Consular Affairs",
        source_url="https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html",
        source_type="government",
        visa_type="B1/B2 Visitor Visa",
        eligibility="Non-U.S. citizens seeking temporary entry for tourism, family visits, or business.",
        required_documents=[
            "Valid Passport (6+ months validity beyond stay)",
            "DS-160 confirmation page with barcode",
            "MRV fee receipt ($185 USD)",
            "2x2 inch compliant photograph",
            "Interview appointment letter",
            "Financial statements, employment verification, ties to home country"
        ],
        application_process="1. Complete DS-160. 2. Pay $185 fee on appointment portal. 3. Schedule biometrics (OFC/VAC) and Consular interview. 4. Attend interviews. 5. Collect stamped passport.",
        fees="$185 USD.",
        processing_time="Interview wait times vary by embassy; passport issuance 3-7 days post-approval.",
        entry_requirements="Valid US visa, passport, Form I-94 issued at border.",
        passport_requirements="Valid at least 6 months beyond intended stay period in the US.",
        last_updated="2024-10-01",
    ),

    # 5. UNITED ARAB EMIRATES (UAE) - Tourist Visas & Entry
    TravelDocument(
        doc_id="uae-tourist-visa-entry",
        title="United Arab Emirates (UAE/Dubai) Tourist Visa & Entry Regulations",
        destination_country="UAE",
        origin_country="All",
        travel_purpose="Tourism",
        document_type="visa_information",
        content="""
# UAE (Dubai, Abu Dhabi) Tourist Visa & Entry Regulations

### Visa Framework
- **Visa on Arrival / Visa Free**: GCC nationals, EU citizens, UK, US, Australia, and select countries receive free 30-day or 90-day visa on arrival.
- **Pre-Arranged Tourist Visa**: Indian citizens with normal passports (unless holding a valid US visa/green card or UK/EU residency) and citizens of non-exempt countries must obtain a pre-arranged tourist visa before arrival through airlines (Emirates, flydubai, Etihad), hotels, travel agencies, or the GDRFA / ICP portals.
- **Special Rule for Indian Citizens**: Indian citizens with a normal passport valid for at least 6 months holding a US visa/green card or UK/EU residence permit (valid for minimum 6 months) are eligible for a 14-day Visa on Arrival (extendable) at all UAE ports of entry for an issuance fee of approximately AED 120-140.

### Pre-Arranged Visa Types
1. **30-Day Single / Multiple Entry Tourist Visa**: For short leisure visits.
2. **60-Day Single / Multiple Entry Tourist Visa**: Standard tourist stay.
3. **5-Year Multiple Entry Tourist Visa**: Allows stays up to 90 days per visit, extendable up to 180 days total per year.

### Required Documents
1. **Passport Copy**: Clear color copy of passport bio-pages (minimum 6 months validity from date of arrival).
2. **Passport Photo**: White background color photograph.
3. **Confirmed Return Ticket**: Round-trip flight with onward travel proof.
4. **Hotel Booking or Host Details**: Confirmed hotel reservation or address of host resident in UAE.
5. **Financial Capacity**: For 5-year visa: bank balance proof of $4,000 USD (or equivalent) in the last 6 months.

### Fees
- 30-Day Tourist Visa: Approx. AED 250 - AED 350 (~$70 - $95 USD) plus service fees.
- 60-Day Tourist Visa: Approx. AED 500 - AED 650 (~$135 - $175 USD).
- 14-Day VoA for qualifying Indian passport holders: ~AED 120-140.

### Processing Time
- Pre-arranged eVisa: 24 to 72 hours (1 to 3 working days). Express processing available within 24 hours.

### Passport & Entry Requirements
- Passport must be valid for at least 6 months from the date of entry into the UAE.
        """,
        source_name="Federal Authority for Identity, Citizenship, Customs and Port Security (ICP)",
        source_url="https://icp.gov.ae/en/",
        source_type="government",
        visa_type="Pre-arranged Tourist Visa / Visa on Arrival",
        eligibility="International tourists entering Dubai, Abu Dhabi, or other UAE emirates.",
        required_documents=[
            "Passport copy (valid 6+ months)",
            "White background passport photo",
            "Confirmed return flight ticket",
            "Hotel accommodation confirmation",
            "Valid US/UK/EU visa copy (if applying for VoA facility)"
        ],
        application_process="Apply online via GDRFA Dubai / ICP portal or through airline (Emirates/Etihad) / authorized travel provider.",
        fees="30-day: ~AED 250-350; 60-day: ~AED 500-650; VoA facility: ~AED 140.",
        processing_time="24 to 72 hours (1 to 3 business days).",
        entry_requirements="Valid passport (6 months validity), eVisa approval printout or VoA eligibility, return ticket.",
        passport_requirements="Minimum 6 months validity from date of arrival.",
        last_updated="2024-11-01",
    ),

    # 6. SINGAPORE - Entry & SG Arrival Card
    TravelDocument(
        doc_id="singapore-entry-visa-rules",
        title="Singapore Entry Requirements, Visa & SG Arrival Card",
        destination_country="Singapore",
        origin_country="All",
        travel_purpose="Tourism",
        document_type="visa_information",
        content="""
# Singapore Tourist Visa, Entry Rules & SG Arrival Card (SGAC)

### Entry Framework
- **Visa-Exempt Nationals**: Citizens of the United States, European Union, UK, Australia, Japan, and many ASEAN nations do not require an entry visa for tourist stays up to 30 or 90 days.
- **Assessment Level I & II Countries**: Nationals of India, China, Russia, Nigeria, etc. require an entry visa before departing for Singapore.
- **SG Arrival Card with Electronic Health Declaration**: ALL travellers (including Singapore citizens, PRs, and tourists) MUST submit the online SG Arrival Card within 3 days prior to arrival. The SG Arrival Card is 100% FREE of charge on the official ICA website.

### Required Documents for Tourist Visa
1. **Valid Passport**: Valid for at least 6 months beyond the date of arrival in Singapore.
2. **Form 14A**: Completed and signed application form.
3. **Passport Photo**: Recent passport-sized color photograph with white background taken within last 3 months.
4. **Flight & Hotel Bookings**: Confirmed round-trip tickets and hotel reservations.
5. **Letter of Introduction (LOI)**: Form V39A issued by a Singapore citizen or Permanent Resident (or applied through an authorized visa agent).
6. **Processing Fee**: SGD $30 (non-refundable) + authorized agent service fee.

### Visa Processing Time
- Processing Time: 1 to 3 working days via the Immigration & Checkpoints Authority (ICA) e-Services.

### SG Arrival Card (Mandatory for All)
- Submission Window: Within 3 days before arriving in Singapore (including arrival day).
- Cost: Free. Beware of commercial scam sites charging fees for SGAC.
- Portal: Official ICA website (eservices.ica.gov.sg/sgarrivalcard) or MyICA Mobile App.

### Border Requirements
- Minimum 6 months passport validity.
- Approved Singapore eVisa (if applicable).
- SG Arrival Card acknowledgement email/barcode.
- Proof of sufficient funds and confirmed return/onward tickets.
        """,
        source_name="Immigration & Checkpoints Authority (ICA Singapore)",
        source_url="https://www.ica.gov.sg/enter-transit-depart/entering-singapore",
        source_type="government",
        visa_type="Entry Visa (e-Visa) & SG Arrival Card",
        eligibility="Foreign travellers visiting Singapore for tourism or social visits.",
        required_documents=[
            "Passport (valid 6+ months)",
            "Completed Form 14A",
            "Passport photograph (white background)",
            "Round-trip flight booking",
            "Hotel reservation",
            "SG Arrival Card submission (within 3 days of arrival)"
        ],
        application_process="1. Apply via ICA Authorized Visa Agent or Singapore Citizen sponsor on SAVE portal. 2. Submit SG Arrival Card 3 days before flight. 3. Enter via automated lanes or passport control.",
        fees="SGD $30 ICA official fee + agent fee.",
        processing_time="1 to 3 business days.",
        entry_requirements="Valid passport (6 months), eVisa (if required), SG Arrival Card submission, return ticket.",
        passport_requirements="Minimum 6 months validity from entry date.",
        last_updated="2024-11-20",
    ),

    # 7. JAPAN - Tourist eVisa & Visit Japan Web
    TravelDocument(
        doc_id="japan-tourist-evisa-rules",
        title="Japan Short-Term Tourist Visa & Visit Japan Web Requirements",
        destination_country="Japan",
        origin_country="All",
        travel_purpose="Tourism",
        document_type="visa_information",
        content="""
# Japan Tourist Visa & Short-Term Stay Guidelines

### Visa Overview
- **Visa Exemption**: Citizens of 71 countries (including US, UK, Canada, Australia, Singapore, EU member states) can enter Japan visa-free for tourism stays up to 90 days.
- **eVisa Eligibility**: Nationals of select countries (including India, Brazil, UAE, Saudi Arabia, Taiwan, etc. residing in eligible jurisdictions) can apply for a single-entry electronic visa (eVisa) for tourism stays up to 90 days via the JAPAN eVISA website.
- **Paper Application**: Other applicants submit physical applications via Japanese embassies/consulates or accredited agencies (VFS Global).

### Required Documents for Japan Tourist Visa
1. **Valid Passport**: Valid for duration of stay with at least 2 blank pages.
2. **Visa Application Form**: With 2x2 inch photo attached.
3. **Detailed Travel Schedule / Itinerary**: Daily plan of activities in Japan including hotel contact details.
4. **Proof of Financial Standing**: Recent bank statements (3-6 months), income tax certificate / returns.
5. **Employment / Leave Letter**: Proof of occupation and approved vacation leave.
6. **Flight Reservations**: Confirmed flight itinerary to and from Japan.
7. **Accommodation Proof**: Confirmed hotel vouchers.

### Fees
- Single Entry Visa: JPY 3,000 (or equivalent in local currency, approx. $20-25 USD).
- Double/Multiple Entry: JPY 6,000.
- Transit Visa: JPY 700.
- Agency processing fees may apply.

### Processing Times
- Standard processing: 5 working days from submission of all required documents.

### Visit Japan Web
- Highly recommended online digital service (vjw-lp.digital.go.jp) to complete Immigration clearance (Disembarkation Card) and Customs Declaration QR code prior to boarding.
        """,
        source_name="Ministry of Foreign Affairs of Japan (MOFA)",
        source_url="https://www.mofa.go.jp/j_info/visit/visa/index.html",
        source_type="government",
        visa_type="Short-Term Tourist Visa (Single/Multiple) / JAPAN eVISA",
        eligibility="Foreign tourists traveling to Japan for recreational and sightseeing purposes.",
        required_documents=[
            "Valid passport with 2 blank pages",
            "Visa Application form with photo (45x35mm or 2x2 in)",
            "Day-by-day Itinerary in Japan (Form Schedule of Stay)",
            "Bank statements (last 3-6 months)",
            "Income tax certificates",
            "Flight reservations and hotel vouchers"
        ],
        application_process="1. Apply online via JAPAN eVISA or via accredited agency (VFS). 2. Submit documents and pay visa fee. 3. Receive digital visa issuance notice. 4. Complete Visit Japan Web QR.",
        fees="JPY 3,000 (~$22 USD) for single entry visa.",
        processing_time="5 working days.",
        entry_requirements="Valid passport, valid visa / eVisa, customs declaration via Visit Japan Web QR.",
        passport_requirements="Valid for intended duration of stay.",
        last_updated="2024-10-15",
    ),

    # 8. AUSTRALIA - Visitor Visa (Subclass 600)
    TravelDocument(
        doc_id="australia-visitor-subclass-600",
        title="Australia Visitor Visa Subclass 600 Tourist Stream Guide",
        destination_country="Australia",
        origin_country="All",
        travel_purpose="Tourism",
        document_type="visa_information",
        content="""
# Australia Visitor Visa (Subclass 600) - Tourist Stream

### Visa Summary
The Visitor Visa Subclass 600 (Tourist stream applied outside Australia) is for individuals wishing to visit Australia for holidays, sightseeing, social or recreational reasons, or to visit friends and family for up to 3, 6, or 12 months.

### Eligibility Requirements
- **Genuine Temporary Entrant (GTE)**: Must satisfy the Department of Home Affairs that you genuinely intend to stay temporarily and will abide by visa conditions.
- **Financial Stability**: Have access to sufficient funds to support your stay in Australia.
- **Health & Character**: Meet Australia's strict health (chest x-ray/medical exam if required) and character requirements (police clearance if requested).

### Required Documents
1. **Valid Passport**: Clear color copy of passport identification pages. Minimum 6 months validity recommended.
2. **Financial Evidence**: Bank statements (last 3 months), savings history, tax returns, pay slips.
3. **Employment Evidence**: Letter from employer confirming position, salary, leave approval, and return to employment.
4. **Travel Plan**: Planned itinerary, tourist activities, and accommodation details.
5. **Ties to Home Country**: Evidence of immediate family, property ownership, business ownership, or ongoing studies.
6. **Biometrics**: Required in certain countries (including India) - applicant receives a Biometric Requirement Letter to attend a collection centre (VFS).

### Application Fee
- Subclass 600 Base Fee: AUD $190.
- Biometric collection fee at VFS (if applicable): ~AUD $25-35.

### Processing Times
- 25% of applications: within 7 days.
- 50% of applications: within 15 days.
- 75% of applications: within 26 days.
- 90% of applications: within 37 days.

### Entry Conditions
- Visa Condition 8101: No work allowed.
- Visa Condition 8201: Maximum 3 months study allowed.
- Mandatory Incoming Passenger Card (IPC) declaration on arrival.
        """,
        source_name="Department of Home Affairs - Australian Government",
        source_url="https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600",
        source_type="government",
        visa_type="Visitor Visa Subclass 600 (Tourist Stream)",
        eligibility="Foreign nationals wishing to visit Australia for tourism, recreation, or family visits.",
        required_documents=[
            "Passport bio-page color scan",
            "Bank statements and financial evidence",
            "Employer leave approval letter and salary slips",
            "Proof of assets/ties to home country",
            "Detailed trip itinerary and accommodation",
            "Biometric collection appointment"
        ],
        application_process="1. Create ImmiAccount online. 2. Complete Subclass 600 form and attach documents. 3. Pay AUD $190. 4. Complete biometrics if requested. 5. Receive digital grant notice.",
        fees="AUD $190.",
        processing_time="15 to 37 calendar days.",
        entry_requirements="Valid passport, granted electronic Subclass 600 visa, completed Incoming Passenger Card.",
        passport_requirements="Valid for duration of stay, recommended 6 months validity.",
        last_updated="2024-11-10",
    ),
]


def seed_knowledge_base():
    """Seed the processed knowledge base with authoritative travel documents."""
    pipeline = IngestionPipeline()
    for doc in SEED_DOCUMENTS:
        pipeline.ingest_document(doc)
    print(f"Successfully seeded {len(SEED_DOCUMENTS)} authoritative travel documents!")


if __name__ == "__main__":
    seed_knowledge_base()
