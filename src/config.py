import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_NAME = "Tennessee Domestic Security & Illicit Finance Risk Intelligence Model"
REPORT_TITLE = "Tennessee Domestic Security & Illicit Finance Risk Intelligence Assessment"
REPORT_SUBTITLE = (
    "County-level OSINT model for illicit-finance vulnerability, "
    "cash-economy exposure, tactical-access indicators, organized/group "
    "criminal activity, explosive-use indicators, targeted-harm indicators, "
    "public-safety personnel pressure, disaster/disruption vulnerability, "
    "institutional/enforcement pressure, public group/network reference context, "
    "TDOC correctional-system STG context, "
    "law-enforcement response-capacity context, operational-risk exposure, "
    "protective-planning resilience, and domestic security risk"
)

BASE_DIR = Path(__file__).resolve().parents[1]

# Load environment variables from project-level .env file
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = BASE_DIR / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
CHARTS_DIR = OUTPUTS_DIR / "charts"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# ---------------------------------------------------------------------
# Operational Risk & Protective Planning Layer
# ---------------------------------------------------------------------
# County-level aggregate inputs only. These files support defensive
# protective-planning, resilience, exposure, and response-capacity analysis.
# Do not include facility names, street addresses, exact coordinates, routes,
# schedules, individual names, agency identifiers, ORI identifiers, case-level
# narratives, or exploitable vulnerability details.

FEMA_NRI_COUNTIES_INPUT = RAW_DIR / "fema_nri_counties.csv"
COUNTY_PROFILE_INPUT = RAW_DIR / "tn_county_profile_data.csv"
TBI_PUBLIC_SAFETY_CONTEXT_INPUT = RAW_DIR / "tbi_county_public_safety_context.csv"
TDOT_TRANSPORT_CONTEXT_INPUT = RAW_DIR / "tn_county_transport_context.csv"
HEALTHCARE_CAPACITY_INPUT = RAW_DIR / "tn_county_healthcare_capacity.csv"
INFRASTRUCTURE_NEEDS_INPUT = RAW_DIR / "tn_county_infrastructure_needs.csv"
LAW_ENFORCEMENT_CAPACITY_INPUT = RAW_DIR / "tn_county_law_enforcement_capacity.csv"

# Raw source files used by preparation scripts.
FEMA_NRI_ORIGINAL_INPUT = RAW_DIR / "fema_nri_counties_original.csv"
TBI_OFFENSE_TYPE_2024_INPUT = RAW_DIR / "crimes_clearances_by_offense_type_2024.csv"
TDOT_TRAFFIC_LINES_INPUT = RAW_DIR / "Traffic_Lines_-8892729031592288661.csv"
SYCAMORE_HEALTHCARE_CAPACITY_WORKBOOK = (
    RAW_DIR / "tn-health-care-capacity-dashboard-data-download.xlsx"
)
TACIR_INFRASTRUCTURE_APPENDIX_D_PDF = RAW_DIR / "2026_Infrastructure_AppendixD.pdf"
CSLLEA_ICPSR_ZIP_INPUT = RAW_DIR / "ICPSR_38771-V1 (2).zip"
CSLLEA_TSV_INPUT = RAW_DIR / "38771-0001-Data.tsv"
CSLLEA_CSV_INPUT = RAW_DIR / "38771-0001-Data.csv"

OPERATIONAL_RISK_FEATURES_OUTPUT = (
    PROCESSED_DIR / "tn_operational_risk_features.csv"
)

ACS_YEAR = 2024

# CBP table family: CBP2023.CB2300CBP
# The data collection module will try these years in order.
CBP_YEARS_TO_TRY = [2023, 2022, 2021]

STATE_FIPS = "47"  # Tennessee
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "").strip()

# ---------------------------------------------------------------------
# ACLED credentials and date range
# ---------------------------------------------------------------------
# Add these to your project-level .env file:
#
# ACLED_USERNAME=your_acled_username_or_email
# ACLED_PASSWORD=your_acled_password
# ACLED_START_DATE=2023-01-01
# ACLED_END_DATE=2024-12-31
#
# Optional:
# ACLED_SAVE_FULL_RAW=false
#
# Do not hard-code credentials directly in this file.
ACLED_USERNAME = os.getenv("ACLED_USERNAME", "").strip()
ACLED_PASSWORD = os.getenv("ACLED_PASSWORD", "").strip()
ACLED_START_DATE = os.getenv("ACLED_START_DATE", "2023-01-01").strip()
ACLED_END_DATE = os.getenv("ACLED_END_DATE", "2024-12-31").strip()

ACS_VARIABLES = {
    "B01003_001E": "population",
    "B19013_001E": "median_household_income",
    "B17001_001E": "poverty_universe",
    "B17001_002E": "poverty_count",
    "B23025_003E": "labor_force",
    "B23025_005E": "unemployed",
    "B25070_001E": "renter_households",
    "B25070_007E": "rent_30_34",
    "B25070_008E": "rent_35_39",
    "B25070_009E": "rent_40_49",
    "B25070_010E": "rent_50_plus",
}

CBP_INDUSTRIES = {
    # 2023 CBP API uses NAICS2017 industry codes.
    # Table family: CBP2023.CB2300CBP
    #
    # Important:
    # These are aggregate county-level establishment counts only.
    # They are used as exposure proxies, not as indicators of wrongdoing.

    # Regulated / cash-intensive retail proxies
    "453991": "tobacco_vape_establishments",          # Tobacco Stores
    "451110": "sporting_goods_establishments",        # Sporting Goods Stores
    "453310": "used_merchandise_establishments",      # Used Merchandise Stores

    # Broader cash-economy proxies
    "447110": "gasoline_station_establishments",      # Gasoline Stations with Convenience Stores
    "445120": "convenience_store_establishments",     # Convenience Stores
    "522291": "consumer_lending_establishments",      # Consumer Lending
    "812310": "laundry_service_establishments",       # Coin-Operated Laundries and Drycleaners
    "441120": "used_auto_dealer_establishments",      # Used Car Dealers
}

# ---------------------------------------------------------------------
# Optional aggregate input files
# ---------------------------------------------------------------------
# These should contain county-level counts only.
# Do not include individual business names, addresses, owners, URLs,
# coordinates, event-level notes, participant names, suspect/victim details,
# gang names, organization names, or site-level maps.

OPTIONAL_TACTICAL_INPUT = RAW_DIR / "tn_tactical_access_inputs.csv"
OPTIONAL_FDIC_BANKING_INPUT = RAW_DIR / "tn_fdic_banking_inputs.csv"
OPTIONAL_FFL_INPUT = RAW_DIR / "tn_ffl_county_inputs.csv"

# TBI / CrimeInsight aggregate input.
# This should contain county-level counts only.
OPTIONAL_CRIME_WEAPONS_INPUT = RAW_DIR / "tn_crime_weapons_inputs.csv"

# TBI / CrimeInsight county-level overall crime-rate input.
# Produced by src/crime_rate_processor.py.
# This should contain county-level aggregate values only.
OPTIONAL_CRIME_RATE_INPUT = RAW_DIR / "tn_crime_rate_inputs.csv"

# ACLED / political violence / civil unrest aggregate input.
# This should contain county-level counts only.
OPTIONAL_POLITICAL_VIOLENCE_INPUT = RAW_DIR / "tn_political_violence_inputs.csv"

# TBI gang-related criminal activity aggregate input.
# Produced by src/gang_activity_processor.py.
# This should contain county-level counts only.
OPTIONAL_GANG_ACTIVITY_INPUT = RAW_DIR / "tn_gang_activity_inputs.csv"

# TBI explosive-use criminal activity aggregate input.
# Produced by src/explosives_processor.py.
# This should contain county-level counts only.
OPTIONAL_EXPLOSIVES_ACTIVITY_INPUT = RAW_DIR / "tn_explosives_activity_inputs.csv"

# TBI gang-related explosive-use criminal activity aggregate input.
# Produced by src/gang_explosives_processor.py.
# This should contain county-level counts only.
OPTIONAL_GANG_EXPLOSIVES_ACTIVITY_INPUT = (
    RAW_DIR / "tn_gang_explosives_activity_inputs.csv"
)

# ---------------------------------------------------------------------
# Phase 6 disaster / disruption vulnerability aggregate input
# ---------------------------------------------------------------------
# County-level aggregate fields only.
# Do not include site-level infrastructure details, facility addresses,
# utility-specific vulnerabilities, exact locations, coordinates,
# road chokepoints, infrastructure maps, or operational disruption details.
OPTIONAL_DISASTER_DISRUPTION_INPUT = RAW_DIR / "tn_disaster_disruption_inputs.csv"


# ---------------------------------------------------------------------
# Final TBI public-safety / targeted-harm aggregate inputs
# ---------------------------------------------------------------------
# TBI hate-crime offense aggregate input.
# Produced by src/hate_crime_processor.py.
# This should contain county-level counts only.
# Do not include victim details, suspect details, incident IDs,
# addresses, narratives, bias-detail notes, coordinates, or case-level records.
OPTIONAL_HATE_CRIME_OFFENSE_INPUT = RAW_DIR / "tn_hate_crime_offense_inputs.csv"

# TBI law-enforcement ambush aggregate input.
# Produced by src/law_enforcement_ambush_processor.py.
# This should contain county-level counts only.
# Do not include officer names, suspect details, incident IDs,
# addresses, narratives, agency-level tactical details, coordinates,
# or case-level records.
OPTIONAL_LAW_ENFORCEMENT_AMBUSH_INPUT = (
    RAW_DIR / "tn_law_enforcement_ambush_inputs.csv"
)


# ---------------------------------------------------------------------
# CrimeInsight trend-analysis inputs
# ---------------------------------------------------------------------
# These are used by src/crime_trend_analysis.py.
# The 2023 file may be a raw TNCrimeOnline matrix export.
# The 2024 file may be the processed county-level crime/weapons input.
CRIME_TREND_INPUT_2023 = RAW_DIR / "tn_crime_weapons_inputs_2023.csv"
CRIME_TREND_INPUT_2024 = RAW_DIR / "tn_crime_weapons_inputs_2024.csv"


# ---------------------------------------------------------------------
# Public group / network reference and statewide hate-crime context
# ---------------------------------------------------------------------
# These are reference/context layers only.
# They are not included in risk scoring.
# Do not include addresses, coordinates, individual names, social handles,
# meeting locations, recruitment channels, operational notes, or case narratives.

# SPLC Tennessee Hate Map CSV input.
# Produced manually by downloading/exporting the SPLC Hate Map CSV for Tennessee.
# Used by src/splc_group_reference_processor.py.
SPLC_HATE_MAP_INPUT = RAW_DIR / "splc_hate_data_2024.csv"

# Safe manually reviewed public group / network reference input.
# Created or updated by src/public_group_reference.py and/or
# src/splc_group_reference_processor.py.
PUBLIC_GROUP_REFERENCE_INPUT = RAW_DIR / "tn_public_group_reference_inputs.csv"

# Validated public group / network reference register.
PUBLIC_GROUP_REFERENCE_OUTPUT = (
    TABLES_DIR / "tn_public_group_activity_reference.csv"
)

# Validation report for public group / network reference register.
PUBLIC_GROUP_REFERENCE_VALIDATION_OUTPUT = (
    TABLES_DIR / "tn_public_group_reference_validation.csv"
)

# SPLC-derived candidate table. This is a source-assisted candidate output,
# not a scoring table and not an independent model finding.
SPLC_PUBLIC_GROUP_REFERENCE_CANDIDATES_OUTPUT = (
    TABLES_DIR / "tn_splc_public_group_reference_candidates_2024.csv"
)

# TBI 2024 Hate Crime Report statewide context outputs.
# These are context-only outputs and do not replace county-level inputs from
# src/hate_crime_processor.py.
TBI_HATE_CRIME_BIAS_CONTEXT_OUTPUT = (
    TABLES_DIR / "tn_2024_hate_crime_bias_context.csv"
)

TBI_HATE_CRIME_OFFENSE_CONTEXT_OUTPUT = (
    TABLES_DIR / "tn_2024_hate_crime_offense_context.csv"
)

TBI_HATE_CRIME_CLEARANCE_CONTEXT_OUTPUT = (
    TABLES_DIR / "tn_2024_hate_crime_clearance_context.csv"
)

TBI_HATE_CRIME_LOCATION_CONTEXT_OUTPUT = (
    TABLES_DIR / "tn_2024_hate_crime_location_context.csv"
)

TBI_HATE_CRIME_REPORT_CONTEXT_SUMMARY_OUTPUT = (
    TABLES_DIR / "tn_2024_hate_crime_report_context_summary.csv"
)


# ---------------------------------------------------------------------
# TDOC correctional-system STG reference context
# ---------------------------------------------------------------------
# These are non-scoring reference/context outputs only. They are used to
# document broad correctional-system Security Threat Group context from TDOC
# source documents. They are not county-risk, street-presence, terrorism,
# extremism, illicit-finance, or criminality indicators.
#
# Do not publish or retain identifiers, tattoos, symbols, phrases, rank
# structures, individual names, facility security details, staff contact details,
# operational notes, case narratives, addresses, coordinates, or tactical details.

TDOC_STG_THREAT_ASSESSMENT_2010_PDF = (
    RAW_DIR / "stg_threat_assessment__tn_major_groups__apr_2010__les_.pdf"
)

TDOC_STATISTICAL_ABSTRACT_2025_PDF = RAW_DIR / "2025 Statistical Abstract.pdf"

TDOC_STG_REFERENCE_CONTEXT_OUTPUT = (
    TABLES_DIR / "tn_tdoc_stg_reference_context.csv"
)

TDOC_STG_REFERENCE_VALIDATION_OUTPUT = (
    TABLES_DIR / "tn_tdoc_stg_reference_validation.csv"
)


# ---------------------------------------------------------------------
# Source register
# ---------------------------------------------------------------------
SOURCE_REGISTER_OUTPUT = TABLES_DIR / "source_register.csv"
