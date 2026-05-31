"""
Build a defensive county-level operational-risk feature layer for Tennessee.

Purpose
-------
This module creates a county-level protective-planning dataset. It is designed
for defensive risk assessment, crisis planning, resilience analysis, and
dashboard context.

It intentionally avoids:
- facility names
- street addresses
- exact coordinates
- individual names
- routes
- schedules
- exploitable security gaps

Expected output
---------------
data/processed/tn_operational_risk_features.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


TN_COUNTIES = [
    "Anderson", "Bedford", "Benton", "Bledsoe", "Blount", "Bradley", "Campbell",
    "Cannon", "Carroll", "Carter", "Cheatham", "Chester", "Claiborne", "Clay",
    "Cocke", "Coffee", "Crockett", "Cumberland", "Davidson", "Decatur", "DeKalb",
    "Dickson", "Dyer", "Fayette", "Fentress", "Franklin", "Gibson", "Giles",
    "Grainger", "Greene", "Grundy", "Hamblen", "Hamilton", "Hancock", "Hardeman",
    "Hardin", "Hawkins", "Haywood", "Henderson", "Henry", "Hickman", "Houston",
    "Humphreys", "Jackson", "Jefferson", "Johnson", "Knox", "Lake", "Lauderdale",
    "Lawrence", "Lewis", "Lincoln", "Loudon", "Macon", "Madison", "Marion",
    "Marshall", "Maury", "McMinn", "McNairy", "Meigs", "Monroe", "Montgomery",
    "Moore", "Morgan", "Obion", "Overton", "Perry", "Pickett", "Polk", "Putnam",
    "Rhea", "Roane", "Robertson", "Rutherford", "Scott", "Sequatchie", "Sevier",
    "Shelby", "Smith", "Stewart", "Sullivan", "Sumner", "Tipton", "Trousdale",
    "Unicoi", "Union", "Van Buren", "Warren", "Washington", "Wayne", "Weakley",
    "White", "Williamson", "Wilson"
]


def normalize_county_name(value: str) -> str:
    """
    Normalize county names for merging while preserving Tennessee-specific
    capitalization and known county spellings.

    This prevents merge failures for counties such as:
    - DeKalb
    - McMinn
    - McNairy
    """
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.replace(" County", "")
    value = value.replace(" county", "")
    value = value.replace(".", "")
    value = " ".join(value.split())

    if not value:
        return ""

    canonical_counties = {county.lower(): county for county in TN_COUNTIES}

    # Most inputs are county names, including all-caps, lowercase, title case,
    # or slightly altered capitalization.
    lookup = value.lower()
    if lookup in canonical_counties:
        return canonical_counties[lookup]

    # Safety aliases for common Tennessee capitalization edge cases.
    aliases = {
        "de kalb": "DeKalb",
        "dekalb": "DeKalb",
        "mc minn": "McMinn",
        "mcminn": "McMinn",
        "mc nairy": "McNairy",
        "mcnairy": "McNairy",
        "vanburen": "Van Buren",
        "van buren": "Van Buren",
    }

    return aliases.get(lookup, value.title())


def as_series(values, index=None) -> pd.Series:
    """
    Convert input to a pandas Series.

    This prevents errors when df.get("missing_column", np.nan) returns
    a scalar instead of a Series.
    """
    if isinstance(values, pd.Series):
        return values

    if index is None:
        return pd.Series(values)

    return pd.Series([values] * len(index), index=index)


def minmax(values, index=None) -> pd.Series:
    """Return 0-100 min-max score."""
    s = as_series(values, index=index)
    s = pd.to_numeric(s, errors="coerce")

    if s.notna().sum() == 0:
        return pd.Series(np.nan, index=s.index)

    low = s.min()
    high = s.max()

    if high == low:
        return pd.Series(50.0, index=s.index)

    return ((s - low) / (high - low) * 100).round(2)


def inverse_minmax(values, index=None) -> pd.Series:
    """Return inverse 0-100 score where lower raw values mean higher risk."""
    return (100 - minmax(values, index=index)).round(2)


def safe_read_csv(path: Path) -> pd.DataFrame:
    """Read CSV if available, otherwise return empty DataFrame."""
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def build_base_county_frame() -> pd.DataFrame:
    """Create a complete 95-county Tennessee frame."""
    df = pd.DataFrame({"county": TN_COUNTIES})
    df["state"] = "Tennessee"
    return df


def load_existing_project_scores() -> pd.DataFrame:
    """
    Load current project risk outputs if available.

    This function is intentionally flexible because project output names may vary.
    It looks for likely county-level files and uses the first available match.
    """

    candidate_files = [
        PROCESSED_DIR / "tn_county_risk_scores.csv",
        PROCESSED_DIR / "county_risk_scores.csv",
        PROCESSED_DIR / "tennessee_county_risk_scores.csv",
        PROCESSED_DIR / "tn_insurgent_risk_scores.csv",
        PROCESSED_DIR / "county_deep_dive_features.csv",
    ]

    for path in candidate_files:
        if path.exists():
            df = pd.read_csv(path)
            county_col = find_column(df, ["county", "county_name", "County"])
            if county_col:
                df["county"] = df[county_col].apply(normalize_county_name)

                score_col = find_column(
                    df,
                    [
                        "final_risk_score",
                        "risk_score",
                        "insurgent_risk_score",
                        "county_risk_score",
                        "scenario_adjusted_risk_score",
                    ],
                )

                if score_col:
                    out = df[["county", score_col]].copy()
                    out = out.rename(columns={score_col: "existing_threat_context_score"})
                    out["existing_threat_context_score"] = pd.to_numeric(
                        out["existing_threat_context_score"], errors="coerce"
                    )
                    return out

    return pd.DataFrame(columns=["county", "existing_threat_context_score"])


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Find the first candidate column that exists, case-insensitive."""
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def load_fema_nri() -> pd.DataFrame:
    """
    Load FEMA National Risk Index county data if user downloads it.

    Expected manual file:
    data/raw/fema_nri_counties.csv

    Useful FEMA-style columns may include:
    - COUNTY
    - STATE
    - RISK_SCORE
    - SOVI_SCORE
    - RESL_SCORE
    - EAL_SCORE
    """

    path = RAW_DIR / "fema_nri_counties.csv"
    df = safe_read_csv(path)

    if df.empty:
        return pd.DataFrame(columns=[
            "county",
            "fema_risk_index_score",
            "fema_social_vulnerability_score",
            "fema_community_resilience_score",
            "fema_expected_annual_loss_score",
        ])

    county_col = find_column(df, ["COUNTY", "county", "County", "county_name"])
    state_col = find_column(df, ["STATE", "state", "State", "ST_ABBRV"])

    if county_col is None:
        return pd.DataFrame()

    if state_col:
        state_values = df[state_col].astype(str).str.upper()
        df = df[state_values.isin(["TENNESSEE", "TN"])]

    df["county"] = df[county_col].apply(normalize_county_name)

    mapping = {
        "fema_risk_index_score": [
            "fema_risk_index_score",
            "RISK_SCORE",
            "risk_score",
            "Risk Score",
        ],
        "fema_social_vulnerability_score": [
            "fema_social_vulnerability_score",
            "SOVI_SCORE",
            "sovi_score",
            "Social Vulnerability Score",
        ],
        "fema_community_resilience_score": [
            "fema_community_resilience_score",
            "RESL_SCORE",
            "resl_score",
            "Community Resilience Score",
        ],
        "fema_expected_annual_loss_score": [
            "fema_expected_annual_loss_score",
            "EAL_SCORE",
            "eal_score",
            "Expected Annual Loss Score",
        ],
    }

    out = df[["county"]].copy()

    for new_col, candidates in mapping.items():
        source_col = find_column(df, candidates)
        if source_col:
            out[new_col] = pd.to_numeric(df[source_col], errors="coerce")
        else:
            out[new_col] = np.nan

    # Optional metadata from the cleaned FEMA file. These are useful for auditing
    # and dashboard context but are not required for scoring.
    optional_meta = {
        "county_fips": ["county_fips", "STCOFIPS", "stcofips"],
        "fema_population": ["fema_population", "POPULATION", "population"],
        "fema_building_value": ["fema_building_value", "BUILDVALUE", "building_value"],
        "fema_area_sq_mi": ["fema_area_sq_mi", "AREA", "area_sq_mi"],
    }

    for new_col, candidates in optional_meta.items():
        source_col = find_column(df, candidates)
        if source_col:
            out[new_col] = pd.to_numeric(df[source_col], errors="coerce")

    grouped = out.groupby("county", as_index=False).mean(numeric_only=True)
    return grouped


def load_county_profile_data() -> pd.DataFrame:
    """
    Load county baseline data if user downloads or creates it.

    Expected manual file:
    data/raw/tn_county_profile_data.csv

    Recommended columns:
    county
    population
    population_density
    poverty_rate
    unemployment_rate
    median_household_income
    internet_access_rate
    infrastructure_needs_per_capita
    """

    path = RAW_DIR / "tn_county_profile_data.csv"
    df = safe_read_csv(path)

    if df.empty:
        return pd.DataFrame(columns=[
            "county",
            "population",
            "population_density",
            "poverty_rate",
            "unemployment_rate",
            "median_household_income",
            "internet_access_rate",
            "infrastructure_needs_per_capita",
        ])

    county_col = find_column(df, ["county", "County", "county_name", "County Name"])
    if county_col is None:
        return pd.DataFrame()

    df["county"] = df[county_col].apply(normalize_county_name)

    keep_cols = ["county"]

    optional_cols = {
        "population": ["population", "Population"],
        "population_density": ["population_density", "Population Density", "pop_density"],
        "poverty_rate": ["poverty_rate", "Poverty Rate", "poverty"],
        "unemployment_rate": ["unemployment_rate", "Unemployment Rate", "unemployment"],
        "median_household_income": ["median_household_income", "Median Household Income", "income"],
        "internet_access_rate": ["internet_access_rate", "Internet Access Rate", "internet"],
        "infrastructure_needs_per_capita": [
            "infrastructure_needs_per_capita",
            "Infrastructure Needs Per Capita",
            "infra_needs_pc",
        ],
    }

    out = pd.DataFrame()
    out["county"] = df["county"]

    for new_col, candidates in optional_cols.items():
        source_col = find_column(df, candidates)
        if source_col:
            out[new_col] = pd.to_numeric(df[source_col], errors="coerce")
        else:
            out[new_col] = np.nan

    return out.groupby("county", as_index=False).mean(numeric_only=True)


def load_tbi_public_safety_context() -> pd.DataFrame:
    """
    Load public-safety context from user-prepared TBI county summary.

    Expected manual file:
    data/raw/tbi_county_public_safety_context.csv

    Recommended columns:
    county
    violent_crime_rate
    hate_crime_count
    hate_crime_rate
    weapon_law_violation_rate
    public_disorder_rate

    Keep this county-level only.
    """

    path = RAW_DIR / "tbi_county_public_safety_context.csv"
    df = safe_read_csv(path)

    if df.empty:
        return pd.DataFrame(columns=[
            "county",
            "violent_crime_rate",
            "hate_crime_count",
            "hate_crime_rate",
            "weapon_law_violation_rate",
            "public_disorder_rate",
        ])

    county_col = find_column(df, ["county", "County", "county_name", "County Name"])
    if county_col is None:
        return pd.DataFrame()

    df["county"] = df[county_col].apply(normalize_county_name)

    out = pd.DataFrame()
    out["county"] = df["county"]

    optional_cols = {
        "violent_crime_rate": ["violent_crime_rate", "Violent Crime Rate"],
        "hate_crime_count": ["hate_crime_count", "Hate Crime Count"],
        "hate_crime_rate": ["hate_crime_rate", "Hate Crime Rate"],
        "weapon_law_violation_rate": ["weapon_law_violation_rate", "Weapon Law Violation Rate"],
        "public_disorder_rate": ["public_disorder_rate", "Public Disorder Rate"],
    }

    for new_col, candidates in optional_cols.items():
        source_col = find_column(df, candidates)
        if source_col:
            out[new_col] = pd.to_numeric(df[source_col], errors="coerce")
        else:
            out[new_col] = np.nan

    return out.groupby("county", as_index=False).mean(numeric_only=True)


def load_transport_context() -> pd.DataFrame:
    """
    Load county-level transportation pressure.

    Expected manual file:
    data/raw/tn_county_transport_context.csv

    Recommended columns:
    county
    avg_aadt
    total_vmt
    truck_percentage
    traffic_station_count

    Do not include exact station coordinates in the processed model output.
    """

    path = RAW_DIR / "tn_county_transport_context.csv"
    df = safe_read_csv(path)

    if df.empty:
        return pd.DataFrame(columns=[
            "county",
            "avg_aadt",
            "total_vmt",
            "truck_percentage",
            "traffic_station_count",
        ])

    county_col = find_column(df, ["county", "County", "county_name", "County Name"])
    if county_col is None:
        return pd.DataFrame()

    df["county"] = df[county_col].apply(normalize_county_name)

    out = pd.DataFrame()
    out["county"] = df["county"]

    optional_cols = {
        "avg_aadt": ["avg_aadt", "AADT", "aadt", "Average AADT"],
        "total_vmt": ["total_vmt", "VMT", "vmt", "Total VMT"],
        "truck_percentage": ["truck_percentage", "Truck Percentage", "truck_pct"],
        "traffic_station_count": ["traffic_station_count", "Traffic Station Count", "station_count"],
    }

    for new_col, candidates in optional_cols.items():
        source_col = find_column(df, candidates)
        if source_col:
            out[new_col] = pd.to_numeric(df[source_col], errors="coerce")
        else:
            out[new_col] = np.nan

    return out.groupby("county", as_index=False).mean(numeric_only=True)


def load_healthcare_capacity() -> pd.DataFrame:
    """
    Load county-level healthcare / emergency capacity.

    Expected manual file:
    data/raw/tn_county_healthcare_capacity.csv

    Recommended columns:
    county
    hospital_beds_per_100k
    emergency_department_count
    primary_care_rate
    trauma_access_proxy

    Keep this aggregated by county.
    """

    path = RAW_DIR / "tn_county_healthcare_capacity.csv"
    df = safe_read_csv(path)

    if df.empty:
        return pd.DataFrame(columns=[
            "county",
            "hospital_beds_per_100k",
            "emergency_department_count",
            "primary_care_rate",
            "trauma_access_proxy",
        ])

    county_col = find_column(df, ["county", "County", "county_name", "County Name"])
    if county_col is None:
        return pd.DataFrame()

    df["county"] = df[county_col].apply(normalize_county_name)

    out = pd.DataFrame()
    out["county"] = df["county"]

    optional_cols = {
        "hospital_beds_per_100k": ["hospital_beds_per_100k", "Hospital Beds Per 100k"],
        "emergency_department_count": ["emergency_department_count", "Emergency Department Count"],
        "primary_care_rate": ["primary_care_rate", "Primary Care Rate"],
        "trauma_access_proxy": ["trauma_access_proxy", "Trauma Access Proxy"],
    }

    for new_col, candidates in optional_cols.items():
        source_col = find_column(df, candidates)
        if source_col:
            out[new_col] = pd.to_numeric(df[source_col], errors="coerce")
        else:
            out[new_col] = np.nan

    return out.groupby("county", as_index=False).mean(numeric_only=True)



def load_law_enforcement_capacity() -> pd.DataFrame:
    """
    Load county-level law-enforcement capacity / response-capability context.

    Expected manual/prepared file:
    data/raw/tn_county_law_enforcement_capacity.csv

    This is a defensive resilience/capacity layer, not a threat indicator.
    Keep output county-level only.
    """

    path = RAW_DIR / "tn_county_law_enforcement_capacity.csv"
    df = safe_read_csv(path)

    if df.empty:
        return pd.DataFrame(columns=[
            "county",
            "law_enforcement_agency_count",
            "law_enforcement_complete_agency_count",
            "law_enforcement_full_time_employees",
            "law_enforcement_sworn_personnel",
            "law_enforcement_sworn_per_100k",
            "law_enforcement_full_time_employees_per_100k",
            "law_enforcement_capacity_score",
            "law_enforcement_capacity_gap_score",
        ])

    county_col = find_column(df, ["county", "County", "county_name", "County Name"])
    if county_col is None:
        return pd.DataFrame()

    df["county"] = df[county_col].apply(normalize_county_name)

    optional_cols = {
        "law_enforcement_agency_count": ["law_enforcement_agency_count"],
        "law_enforcement_complete_agency_count": ["law_enforcement_complete_agency_count"],
        "sheriff_office_count": ["sheriff_office_count"],
        "local_police_agency_count": ["local_police_agency_count"],
        "law_enforcement_full_time_employees": ["law_enforcement_full_time_employees"],
        "law_enforcement_part_time_employees": ["law_enforcement_part_time_employees"],
        "law_enforcement_sworn_personnel": ["law_enforcement_sworn_personnel"],
        "law_enforcement_civilian_personnel": ["law_enforcement_civilian_personnel"],
        "law_enforcement_sworn_per_100k": ["law_enforcement_sworn_per_100k"],
        "law_enforcement_full_time_employees_per_100k": ["law_enforcement_full_time_employees_per_100k"],
        "law_enforcement_agencies_per_100k": ["law_enforcement_agencies_per_100k"],
        "patrol_response_agency_count": ["patrol_response_agency_count"],
        "dispatch_agency_count": ["dispatch_agency_count"],
        "special_event_response_agency_count": ["special_event_response_agency_count"],
        "criminal_investigation_agency_count": ["criminal_investigation_agency_count"],
        "traffic_enforcement_agency_count": ["traffic_enforcement_agency_count"],
        "specialized_response_agency_count": ["specialized_response_agency_count"],
        "law_enforcement_capacity_score": ["law_enforcement_capacity_score"],
        "law_enforcement_capacity_gap_score": ["law_enforcement_capacity_gap_score"],
        "law_enforcement_data_year": ["law_enforcement_data_year"],
    }

    out = pd.DataFrame()
    out["county"] = df["county"]

    for new_col, candidates in optional_cols.items():
        source_col = find_column(df, candidates)
        if source_col:
            out[new_col] = pd.to_numeric(df[source_col], errors="coerce")
        else:
            out[new_col] = np.nan

    return out.groupby("county", as_index=False).mean(numeric_only=True)

def add_proxy_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Create defensive operational-risk component scores."""

    df = df.copy()

    # Exposure components
    df["population_exposure_score"] = minmax(df.get("population", np.nan), index=df.index)
    df["density_exposure_score"] = minmax(df.get("population_density", np.nan), index=df.index)

    df["socioeconomic_pressure_score"] = (
        minmax(df.get("poverty_rate", np.nan), index=df.index).fillna(50) * 0.45
        + minmax(df.get("unemployment_rate", np.nan), index=df.index).fillna(50) * 0.35
        + inverse_minmax(df.get("median_household_income", np.nan), index=df.index).fillna(50) * 0.20
    ).round(2)

    df["infrastructure_pressure_score"] = minmax(
        df.get("infrastructure_needs_per_capita", np.nan),
        index=df.index,
    ).fillna(50).round(2)

    df["transport_pressure_score"] = (
        minmax(df.get("avg_aadt", np.nan), index=df.index).fillna(50) * 0.40
        + minmax(df.get("total_vmt", np.nan), index=df.index).fillna(50) * 0.40
        + minmax(df.get("truck_percentage", np.nan), index=df.index).fillna(50) * 0.20
    ).round(2)

    df["public_safety_context_score"] = (
        minmax(df.get("violent_crime_rate", np.nan), index=df.index).fillna(50) * 0.35
        + minmax(df.get("hate_crime_rate", np.nan), index=df.index).fillna(50) * 0.25
        + minmax(df.get("weapon_law_violation_rate", np.nan), index=df.index).fillna(50) * 0.25
        + minmax(df.get("public_disorder_rate", np.nan), index=df.index).fillna(50) * 0.15
    ).round(2)

    # Higher healthcare capacity should lower operational risk.
    df["healthcare_capacity_score"] = (
        minmax(df.get("hospital_beds_per_100k", np.nan), index=df.index).fillna(50) * 0.40
        + minmax(df.get("emergency_department_count", np.nan), index=df.index).fillna(50) * 0.25
        + minmax(df.get("primary_care_rate", np.nan), index=df.index).fillna(50) * 0.20
        + minmax(df.get("trauma_access_proxy", np.nan), index=df.index).fillna(50) * 0.15
    ).round(2)

    df["healthcare_capacity_gap_score"] = (100 - df["healthcare_capacity_score"]).round(2)

    # FEMA resilience: higher resilience is treated as lowering risk.
    df["fema_resilience_gap_score"] = (
        100 - minmax(df.get("fema_community_resilience_score", np.nan), index=df.index).fillna(50)
    ).round(2)

    df["fema_vulnerability_score"] = minmax(
        df.get("fema_social_vulnerability_score", np.nan),
        index=df.index,
    ).fillna(50).round(2)

    # Existing project threat context. If absent, neutral value so model still runs.
    if "existing_threat_context_score" not in df.columns:
        df["existing_threat_context_score"] = 50.0

    df["existing_threat_context_score"] = df["existing_threat_context_score"].fillna(50)

    df["operational_exposure_score"] = (
        df["population_exposure_score"].fillna(50) * 0.20
        + df["density_exposure_score"].fillna(50) * 0.15
        + df["transport_pressure_score"].fillna(50) * 0.20
        + df["infrastructure_pressure_score"].fillna(50) * 0.20
        + df["public_safety_context_score"].fillna(50) * 0.15
        + df["socioeconomic_pressure_score"].fillna(50) * 0.10
    ).round(2)

    # Law enforcement capacity is treated as a defensive response-capability layer.
    # If the CSLLEA source has not been added yet, use a neutral value so the
    # model remains runnable.
    if "law_enforcement_capacity_score" not in df.columns:
        df["law_enforcement_capacity_score"] = 50.0

    df["law_enforcement_capacity_score"] = df["law_enforcement_capacity_score"].fillna(50)
    df["law_enforcement_capacity_gap_score"] = (
        100 - df["law_enforcement_capacity_score"]
    ).round(2)

    df["resilience_gap_score"] = (
        df["healthcare_capacity_gap_score"].fillna(50) * 0.30
        + df["fema_resilience_gap_score"].fillna(50) * 0.25
        + df["fema_vulnerability_score"].fillna(50) * 0.25
        + df["law_enforcement_capacity_gap_score"].fillna(50) * 0.20
    ).round(2)

    df["final_operational_risk_score"] = (
        df["existing_threat_context_score"].fillna(50) * 0.40
        + df["operational_exposure_score"].fillna(50) * 0.35
        + df["resilience_gap_score"].fillna(50) * 0.25
    ).round(2)

    df["operational_risk_tier"] = pd.cut(
        df["final_operational_risk_score"],
        bins=[-1, 25, 50, 75, 100],
        labels=["Low", "Moderate", "Elevated", "High"],
    ).astype(str)

    return df


def add_data_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add data-quality flags based on source coverage."""

    df = df.copy()

    required_cols = [
        "population",
        "population_density",
        "poverty_rate",
        "unemployment_rate",
        "median_household_income",
        "avg_aadt",
        "violent_crime_rate",
        "fema_social_vulnerability_score",
        "fema_community_resilience_score",
        "hospital_beds_per_100k",
        "law_enforcement_sworn_per_100k",
    ]

    # Count both blank values and source columns that have not been added yet.
    missing_source_columns = [c for c in required_cols if c not in df.columns]
    existing_required_cols = [c for c in required_cols if c in df.columns]

    if existing_required_cols:
        blank_required_values = df[existing_required_cols].isna().sum(axis=1)
    else:
        blank_required_values = pd.Series(0, index=df.index)

    df["missing_required_fields"] = blank_required_values + len(missing_source_columns)

    df["data_quality_flag"] = np.select(
        [
            df["missing_required_fields"] <= 2,
            df["missing_required_fields"].between(3, 5),
            df["missing_required_fields"] > 5,
        ],
        ["Strong", "Partial", "Limited"],
        default="Limited",
    )

    return df


def build_operational_risk_features() -> pd.DataFrame:
    """Build and save county-level operational-risk feature dataset."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = build_base_county_frame()

    datasets = [
        load_existing_project_scores(),
        load_county_profile_data(),
        load_fema_nri(),
        load_tbi_public_safety_context(),
        load_transport_context(),
        load_healthcare_capacity(),
        load_law_enforcement_capacity(),
    ]

    for source_df in datasets:
        if not source_df.empty and "county" in source_df.columns:
            source_df["county"] = source_df["county"].apply(normalize_county_name)
            df = df.merge(source_df, on="county", how="left")

    df = add_proxy_scores(df)
    df = add_data_quality_flags(df)

    # Output only county-level fields. No names, addresses, routes, or coordinates.
    output_cols = [
        "county",
        "state",
        "existing_threat_context_score",
        "population",
        "population_density",
        "poverty_rate",
        "unemployment_rate",
        "median_household_income",
        "internet_access_rate",
        "infrastructure_needs_per_capita",
        "avg_aadt",
        "total_vmt",
        "truck_percentage",
        "violent_crime_rate",
        "hate_crime_count",
        "hate_crime_rate",
        "weapon_law_violation_rate",
        "public_disorder_rate",
        "fema_risk_index_score",
        "fema_social_vulnerability_score",
        "fema_community_resilience_score",
        "fema_expected_annual_loss_score",
        "county_fips",
        "fema_population",
        "fema_building_value",
        "fema_area_sq_mi",
        "hospital_beds_per_100k",
        "emergency_department_count",
        "primary_care_rate",
        "trauma_access_proxy",
        "law_enforcement_agency_count",
        "law_enforcement_complete_agency_count",
        "sheriff_office_count",
        "local_police_agency_count",
        "law_enforcement_full_time_employees",
        "law_enforcement_sworn_personnel",
        "law_enforcement_civilian_personnel",
        "law_enforcement_sworn_per_100k",
        "law_enforcement_full_time_employees_per_100k",
        "law_enforcement_agencies_per_100k",
        "patrol_response_agency_count",
        "dispatch_agency_count",
        "special_event_response_agency_count",
        "criminal_investigation_agency_count",
        "traffic_enforcement_agency_count",
        "specialized_response_agency_count",
        "law_enforcement_capacity_score",
        "law_enforcement_capacity_gap_score",
        "law_enforcement_data_year",
        "population_exposure_score",
        "density_exposure_score",
        "socioeconomic_pressure_score",
        "transport_pressure_score",
        "infrastructure_pressure_score",
        "public_safety_context_score",
        "healthcare_capacity_score",
        "healthcare_capacity_gap_score",
        "fema_vulnerability_score",
        "fema_resilience_gap_score",
        "operational_exposure_score",
        "resilience_gap_score",
        "final_operational_risk_score",
        "operational_risk_tier",
        "missing_required_fields",
        "data_quality_flag",
    ]

    output_cols = [c for c in output_cols if c in df.columns]
    df = df[output_cols].sort_values("final_operational_risk_score", ascending=False)

    output_path = PROCESSED_DIR / "tn_operational_risk_features.csv"
    df.to_csv(output_path, index=False)

    print(f"Operational risk features saved to: {output_path}")
    print(f"Rows: {len(df)}")
    print("\nTop 10 counties by final operational risk score:")
    print(
        df[
            [
                "county",
                "final_operational_risk_score",
                "operational_risk_tier",
                "data_quality_flag",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    return df


if __name__ == "__main__":
    build_operational_risk_features()