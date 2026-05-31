import pandas as pd
import requests

from src.config import (
    ACS_YEAR,
    ACS_VARIABLES,
    CBP_INDUSTRIES,
    CBP_YEARS_TO_TRY,
    CENSUS_API_KEY,
    OPTIONAL_CRIME_RATE_INPUT,
    OPTIONAL_TACTICAL_INPUT,
    PROCESSED_DIR,
    RAW_DIR,
    SOURCE_REGISTER_OUTPUT,
    STATE_FIPS,
)

from src.phase2_inputs import (
    load_optional_fdic_banking_inputs,
    load_optional_ffl_inputs,
)

from src.crime_inputs import (
    load_optional_crime_weapons_inputs,
    load_optional_explosives_activity_inputs,
    load_optional_gang_activity_inputs,
    load_optional_gang_explosives_activity_inputs,
    load_optional_hate_crime_offense_inputs,
    load_optional_law_enforcement_ambush_inputs,
)

from src.disaster_disruption_inputs import load_optional_disaster_disruption_inputs
from src.political_violence_inputs import load_optional_political_violence_inputs


def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_REGISTER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)


def redact_api_key_from_url(url: str) -> str:
    """
    Redact Census API keys before printing URLs to console/logs.
    """

    if "key=" not in url:
        return url

    before_key, after_key = url.split("key=", 1)

    if "&" in after_key:
        remaining_query = after_key.split("&", 1)[1]
        return before_key + "key=REDACTED&" + remaining_query

    return before_key + "key=REDACTED"


def safe_get_json(url: str, params: dict | None = None, timeout: int = 30):
    """
    Defensive API helper.

    Some public APIs return plain text or HTML error messages instead of JSON.
    This function prints the failing URL and response preview, but redacts API keys.
    """

    response = requests.get(url, params=params, timeout=timeout)
    safe_url = redact_api_key_from_url(response.url)

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        print("\nAPI request failed.")
        print(f"URL: {safe_url}")
        print(f"Status code: {response.status_code}")
        print(f"Response preview: {response.text[:1000]}")
        raise exc

    if response.status_code == 204 or not response.text.strip():
        raise ValueError(f"Empty API response from: {safe_url}")

    try:
        return response.json()
    except Exception as exc:
        print("\nAPI did not return valid JSON.")
        print(f"URL: {safe_url}")
        print(f"Status code: {response.status_code}")
        print(f"Response preview: {response.text[:1000]}")
        raise exc


def add_census_key(params: dict) -> dict:
    """
    Add Census API key from .env to Census requests.
    """

    params = params.copy()

    if not CENSUS_API_KEY:
        raise RuntimeError(
            "Missing Census API key. Create a .env file in the project root with:\n\n"
            "CENSUS_API_KEY=PASTE_YOUR_CENSUS_KEY_HERE\n\n"
            "Then rerun: python main.py"
        )

    params["key"] = CENSUS_API_KEY
    return params


def collect_acs_county_data() -> pd.DataFrame:
    """
    Pull Tennessee county socioeconomic data from Census ACS 5-year API.

    Tries multiple years because the newest ACS endpoint or specific variables
    may occasionally fail depending on API availability.
    """

    acs_years_to_try = [ACS_YEAR, 2023, 2022, 2021, 2020]
    variables = ["NAME"] + list(ACS_VARIABLES.keys())

    data = None
    successful_year = None
    last_error = None

    for year in acs_years_to_try:
        print(f"Trying Census ACS {year} county data...")

        url = f"https://api.census.gov/data/{year}/acs/acs5"

        params = {
            "get": ",".join(variables),
            "for": "county:*",
            "in": f"state:{STATE_FIPS}",
        }

        try:
            data = safe_get_json(url, params=add_census_key(params))
            successful_year = year
            print(f"ACS data collected successfully for {year}.")
            break

        except Exception as exc:
            last_error = exc
            print(f"ACS {year} failed. Trying fallback year...")

    if data is None:
        raise RuntimeError(
            "Could not collect ACS county data for any fallback year. "
            "Review the printed Census API response above."
        ) from last_error

    header = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=header)

    rename_map = ACS_VARIABLES.copy()
    rename_map["NAME"] = "county_name"

    df = df.rename(columns=rename_map)

    numeric_cols = list(ACS_VARIABLES.values())
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["state_fips"] = df["state"]
    df["county_fips"] = df["county"]
    df["fips"] = df["state_fips"] + df["county_fips"]

    df["county"] = (
        df["county_name"]
        .str.replace(", Tennessee", "", regex=False)
        .str.replace(" County", "", regex=False)
    )

    df["poverty_rate"] = df["poverty_count"] / df["poverty_universe"]
    df["unemployment_rate"] = df["unemployed"] / df["labor_force"]

    rent_burden_cols = ["rent_30_34", "rent_35_39", "rent_40_49", "rent_50_plus"]
    df["rent_burdened_households"] = df[rent_burden_cols].sum(axis=1)
    df["rent_burden_rate"] = df["rent_burdened_households"] / df["renter_households"]

    keep_cols = [
        "fips",
        "county",
        "county_name",
        "population",
        "median_household_income",
        "poverty_rate",
        "unemployment_rate",
        "rent_burden_rate",
    ]

    output = df[keep_cols].copy()
    output["acs_year"] = successful_year

    output.to_csv(PROCESSED_DIR / "tn_acs_county_data.csv", index=False)
    return output


def _try_cbp_year_industry(year: int, naics_code: str) -> pd.DataFrame | None:
    """
    Pull one CBP industry for all Tennessee counties.

    The 2023 CBP API uses NAICS2017 and expects table filters:
    LFO=001 and EMPSZES=001.
    """

    base_url = f"https://api.census.gov/data/{year}/cbp"

    params = {
        "get": "NAME,NAICS2017_LABEL,ESTAB,PAYANN,PAYQTR1,EMP",
        "for": "county:*",
        "in": f"state:{STATE_FIPS}",
        "NAICS2017": naics_code,
        "LFO": "001",
        "EMPSZES": "001",
    }

    try:
        data = safe_get_json(base_url, params=add_census_key(params))

        if not data or len(data) < 2:
            return None

        header = data[0]
        rows = data[1:]

        df = pd.DataFrame(rows, columns=header)
        df["cbp_year"] = year
        df["naics_code"] = naics_code
        df["naics_param_used"] = "NAICS2017"

        return df

    except Exception as exc:
        print(f"CBP pull failed for {year}, NAICS {naics_code}: {exc}")
        return None


def collect_cbp_business_exposure() -> pd.DataFrame:
    """
    Pull Census County Business Patterns establishment counts for selected
    cash-intensive / regulated retail proxy industries.
    """

    frames = []

    for naics_code, output_col in CBP_INDUSTRIES.items():
        print(f"Trying CBP industry {naics_code} -> {output_col}...")

        industry_df = None

        for year in CBP_YEARS_TO_TRY:
            industry_df = _try_cbp_year_industry(year, naics_code)

            if industry_df is not None and not industry_df.empty:
                print(f"Collected {output_col} from CBP {year}.")
                break

        if industry_df is None or industry_df.empty:
            print(f"Could not collect {output_col}. Filling with zero later.")
            continue

        industry_df = industry_df.rename(columns={"ESTAB": output_col})
        industry_df[output_col] = (
            pd.to_numeric(industry_df[output_col], errors="coerce")
            .fillna(0)
        )

        industry_df["fips"] = industry_df["state"] + industry_df["county"]

        frames.append(
            industry_df[
                [
                    "fips",
                    output_col,
                    "cbp_year",
                    "naics_code",
                    "naics_param_used",
                ]
            ]
        )

    if not frames:
        print(
            "\nWarning: No CBP industry data could be collected. "
            "The pipeline will continue with zero-filled business exposure columns."
        )
        return pd.DataFrame(columns=["fips"] + list(CBP_INDUSTRIES.values()))

    merged = None

    for frame in frames:
        value_cols = [c for c in frame.columns if c.endswith("_establishments")]
        cols = ["fips"] + value_cols

        if merged is None:
            merged = frame[cols].copy()
        else:
            merged = merged.merge(frame[cols], on="fips", how="outer")

    merged = merged.fillna(0)

    for col in CBP_INDUSTRIES.values():
        if col not in merged.columns:
            merged[col] = 0

    merged.to_csv(PROCESSED_DIR / "tn_cbp_business_exposure.csv", index=False)
    return merged


def collect_fema_disaster_data() -> pd.DataFrame:
    """
    Pull FEMA disaster declaration summaries using the OpenFEMA API.

    This produces county-level historical disaster declaration counts
    for Tennessee.
    """

    endpoint = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

    params = {
        "$filter": "state eq 'TN'",
        "$select": (
            "designatedArea,fyDeclared,incidentType,declarationTitle,"
            "state,disasterNumber,declarationDate"
        ),
        "$top": 5000,
    }

    try:
        data = safe_get_json(endpoint, params=params)
        rows = data.get("DisasterDeclarationsSummaries", [])
    except Exception:
        print("Warning: FEMA data could not be collected. Continuing with zero disaster exposure.")
        rows = []

    clean_rows = []

    for item in rows:
        county = item.get("designatedArea")

        if not county:
            continue

        county_clean = (
            str(county)
            .replace(" County", "")
            .replace("(County)", "")
            .strip()
        )

        clean_rows.append(
            {
                "county": county_clean,
                "fy_declared": item.get("fyDeclared"),
                "incident_type": item.get("incidentType"),
                "declaration_title": item.get("declarationTitle"),
                "disaster_number": item.get("disasterNumber"),
                "declaration_date": item.get("declarationDate"),
            }
        )

    df = pd.DataFrame(clean_rows)

    if df.empty:
        county_base = pd.read_csv(PROCESSED_DIR / "tn_acs_county_data.csv")
        agg = county_base[["county"]].copy()
        agg["disaster_declaration_count"] = 0
        agg["unique_disaster_types"] = 0
        agg["recent_disaster_declaration_count"] = 0
    else:
        df["fy_declared"] = pd.to_numeric(df["fy_declared"], errors="coerce")

        max_year = df["fy_declared"].max()
        recent_cutoff = max_year - 10 if pd.notna(max_year) else 2014

        agg = (
            df.groupby("county", as_index=False)
            .agg(
                disaster_declaration_count=("declaration_title", "count"),
                unique_disaster_types=("incident_type", "nunique"),
                recent_disaster_declaration_count=(
                    "fy_declared",
                    lambda x: int((x >= recent_cutoff).sum()),
                ),
            )
        )

    agg.to_csv(PROCESSED_DIR / "tn_fema_disaster_exposure.csv", index=False)
    return agg


def load_optional_tactical_inputs(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Optional aggregate CSV.

    Expected columns:
    county, ffl_count, tactical_training_count,
    surplus_tactical_retail_count, gun_range_count

    This file should contain county-level counts only.
    Do not include business names, addresses, owners, coordinates, URLs,
    or site-level/tactical maps.
    """

    expected_cols = [
        "county",
        "ffl_count",
        "tactical_training_count",
        "surplus_tactical_retail_count",
        "gun_range_count",
    ]

    if OPTIONAL_TACTICAL_INPUT.exists():
        df = pd.read_csv(OPTIONAL_TACTICAL_INPUT)

        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0

        df = df[expected_cols].copy()

    else:
        df = county_base[["county"]].copy()

        for col in expected_cols:
            if col != "county":
                df[col] = 0

        df.to_csv(OPTIONAL_TACTICAL_INPUT, index=False)

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def load_optional_crime_rate_inputs(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Optional TBI / TNCrimeOnline county-level overall crime-rate input.

    Produced by:
    python -m src.crime_rate_processor

    Expected columns:
    county,
    overall_crime_rate_per_1000_2024,
    overall_crime_count_2024,
    crime_population_2024
    """

    expected_cols = [
        "county",
        "overall_crime_rate_per_1000_2024",
        "overall_crime_count_2024",
        "crime_population_2024",
    ]

    if OPTIONAL_CRIME_RATE_INPUT.exists():
        df = pd.read_csv(OPTIONAL_CRIME_RATE_INPUT)

        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0

        df = df[expected_cols].copy()

    else:
        df = county_base[["county"]].copy()

        for col in expected_cols:
            if col != "county":
                df[col] = 0

        OPTIONAL_CRIME_RATE_INPUT.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OPTIONAL_CRIME_RATE_INPUT, index=False)

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = (
        df.groupby("county", as_index=False)
        .agg(
            overall_crime_rate_per_1000_2024=("overall_crime_rate_per_1000_2024", "max"),
            overall_crime_count_2024=("overall_crime_count_2024", "sum"),
            crime_population_2024=("crime_population_2024", "max"),
        )
    )

    county_base_clean = county_base[["county"]].copy()
    county_base_clean["county"] = county_base_clean["county"].astype(str).str.strip()

    df = county_base_clean.merge(df, on="county", how="left")

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def build_source_register() -> pd.DataFrame:
    sources = [
        {
            "source": "U.S. Census Bureau ACS 5-Year API",
            "use": "County socioeconomic indicators",
            "url": f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5",
            "notes": (
                "Used for population, poverty, unemployment, income, and rent burden proxies. "
                "Code includes fallback ACS years and .env Census API key support."
            ),
        },
        {
            "source": "U.S. Census Bureau County Business Patterns API",
            "use": "County establishment counts by NAICS industry",
            "url": "https://www.census.gov/data/developers/data-sets/cbp-zbp/cbp-api.html",
            "notes": (
                "Used for tobacco/vape, sporting goods, used merchandise, gas stations, "
                "convenience stores, lending, laundry, and used-auto proxies. "
                "The collector uses NAICS2017 plus LFO=001 and EMPSZES=001."
            ),
        },
        {
            "source": "FEMA OpenFEMA Disaster Declarations Summaries v2",
            "use": "County disaster declaration exposure",
            "url": "https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2",
            "notes": (
                "Used as infrastructure and emergency-disruption vulnerability proxy. "
                "Collector uses the OpenFEMA /api/open/v2/DisasterDeclarationsSummaries endpoint."
            ),
        },
        {
            "source": "Optional local disaster / disruption vulnerability CSV",
            "use": "County-level disaster, infrastructure disruption, access stress, and recovery strain proxy",
            "url": "data/raw/tn_disaster_disruption_inputs.csv",
            "notes": (
                "County-level aggregate fields only. Expected fields include severe storm, flood, tornado, "
                "winter weather, wildfire, drought, power outage, outage duration, hospital access stress, "
                "airport access stress, road access stress, communications disruption, social vulnerability, "
                "recovery strain, and repeat disruption exposure. Do not include facility addresses, "
                "infrastructure maps, coordinates, utility network details, chokepoints, or operational "
                "vulnerability detail."
            ),
        },
        {
            "source": "Optional local tactical-access aggregate CSV",
            "use": "County-level tactical access proxy",
            "url": str(OPTIONAL_TACTICAL_INPUT),
            "notes": (
                "County-level counts only. No business names, addresses, owners, coordinates, URLs, "
                "or tactical site maps."
            ),
        },
        {
            "source": "Optional local FDIC banking aggregate CSV",
            "use": "County-level banking access and deposit-depth proxy",
            "url": "data/raw/tn_fdic_banking_inputs.csv",
            "notes": (
                "County-level aggregates only. Expected fields include bank_branch_count "
                "and total_deposits_thousands. Do not include branch addresses, institution-specific "
                "records, routing information, customer data, coordinates, or branch-level detail."
            ),
        },
        {
            "source": "Optional local ATF FFL aggregate CSV",
            "use": "County-level firearm-license access proxy",
            "url": "data/raw/tn_ffl_county_inputs.csv",
            "notes": (
                "County-level aggregates only. Do not include licensee names, business names, addresses, "
                "coordinates, phone numbers, URLs, license numbers, owner names, or site-level maps. "
                "FFL counts are lawful licensing and access-complexity proxies only, not suspicious-activity indicators."
            ),
        },
        {
            "source": "Optional local TBI CrimeInsight crime/weapons CSV",
            "use": "County-level crime and weapons pressure proxy",
            "url": "data/raw/tn_crime_weapons_inputs.csv",
            "notes": (
                "County-level aggregate counts only. Expected fields include homicide_count, "
                "kidnapping_abduction_count, weapons_law_violation_count, violent_crime_count, "
                "aggravated_assault_count, arson_count, and sex_offense_count. Do not include "
                "incident-level, victim-level, suspect-level, address, coordinate, or case-level records."
            ),
        },
        {
            "source": "Optional local TBI crime-rate aggregate CSV",
            "use": "County-level overall crime rate and total crime count proxy",
            "url": "data/raw/tn_crime_rate_inputs.csv",
            "notes": (
                "County-level aggregate values only. Produced by src/crime_rate_processor.py. "
                "Does not preserve agency-level, incident-level, victim-level, suspect-level, "
                "address, coordinate, or case-level records."
            ),
        },
        {
            "source": "ACLED processed Tennessee aggregate CSV",
            "use": "County-level political violence and civil unrest exposure proxy",
            "url": "data/raw/tn_political_violence_inputs.csv",
            "notes": (
                "Derived from ACLED Tennessee events using county-level aggregation only. "
                "Model output does not preserve event notes, actors, exact coordinates, "
                "event-level locations, URLs, or site-level maps."
            ),
        },
        {
            "source": "Optional local TBI gang-related criminal activity CSV",
            "use": "County-level organized/group criminal activity pressure proxy",
            "url": "data/raw/tn_gang_activity_inputs.csv",
            "notes": (
                "County-level aggregate counts only. Produced by src/gang_activity_processor.py. "
                "Gang-related crime is not a terrorism label. Do not include gang names, "
                "individual names, incident IDs, addresses, coordinates, suspect/victim details, "
                "or case narratives."
            ),
        },
        {
            "source": "Optional local TBI explosive-use criminal activity CSV",
            "use": "County-level explosive-use criminal activity pressure proxy",
            "url": "data/raw/tn_explosives_activity_inputs.csv",
            "notes": (
                "County-level aggregate counts only. Produced by src/explosives_processor.py. "
                "Explosive-use criminal activity is not a terrorism label. Do not include "
                "incident-level, address-level, suspect/victim, organization, coordinates, "
                "incident IDs, narratives, or case-level detail."
            ),
        },
        {
            "source": "Optional local TBI gang-related explosive-use CSV",
            "use": "County-level gang-related explosive-use intersection pressure proxy",
            "url": "data/raw/tn_gang_explosives_activity_inputs.csv",
            "notes": (
                "County-level aggregate counts only. Produced by src/gang_explosives_processor.py. "
                "Gang-related explosive-use activity is not a terrorism label. Do not include "
                "gang names, individual names, incident IDs, addresses, coordinates, "
                "organization names, suspect/victim details, or case narratives."
            ),
        },
        {
            "source": "Optional local TBI hate-crime offense CSV",
            "use": "County-level targeted-harm / bias-motivated offense pressure proxy",
            "url": "data/raw/tn_hate_crime_offense_inputs.csv",
            "notes": (
                "County-level aggregate counts only. Produced by src/hate_crime_processor.py. "
                "Hate-crime offense counts are treated as targeted-harm / bias-motivated offense "
                "pressure indicators, not as terrorism indicators. Do not include victim details, "
                "suspect details, incident IDs, addresses, narratives, bias-detail notes, coordinates, "
                "agency case-level records, or individual-level data."
            ),
        },
        {
            "source": "Optional local TBI law-enforcement ambush CSV",
            "use": "County-level public-safety personnel violence / tactical-planning proxy",
            "url": "data/raw/tn_law_enforcement_ambush_inputs.csv",
            "notes": (
                "County-level aggregate counts only. Produced by src/law_enforcement_ambush_processor.py. "
                "Law-enforcement ambush counts are treated as a public-safety personnel violence and "
                "tactical-planning proxy. They are not terrorism indicators by themselves and do not infer "
                "motive, ideology, or actor identity. Do not include officer names, suspect details, "
                "incident IDs, addresses, agency-level tactical details, coordinates, narratives, or "
                "case-level records."
            ),
        },
                {
            "source": "SPLC Hate Map Tennessee 2024 CSV",
            "use": "Reference-only public group / network context appendix",
            "url": "data/raw/splc_hate_data_2024.csv",
            "notes": (
                "Used only to create a public group / network reference register. "
                "This layer is not included in risk scoring. The model does not independently "
                "verify membership, activity, criminality, motive, ideology, or operational conduct. "
                "Do not include addresses, coordinates, individual names, social handles, meeting "
                "locations, recruitment channels, case narratives, or operational details."
            ),
        },
        {
            "source": "TBI 2024 Hate Crime Report",
            "use": "Statewide targeted-harm / hate-crime context appendix",
            "url": "2024 Hate Crime Final SECURED.pdf",
            "notes": (
                "Used only for statewide hate-crime context tables. This layer does not replace "
                "county-level TBI hate-crime inputs and is not included in risk scoring. "
                "Outputs retain statewide aggregate context only and do not include agency-level, "
                "incident-level, victim-level, suspect-level, address, coordinate, narrative, "
                "or case-level records."
            ),
        },
    ]

    df = pd.DataFrame(sources)
    df.to_csv(SOURCE_REGISTER_OUTPUT, index=False)
    return df


def build_master_dataset() -> pd.DataFrame:
    ensure_dirs()

    acs = collect_acs_county_data()
    cbp = collect_cbp_business_exposure()
    fema = collect_fema_disaster_data()
    tactical = load_optional_tactical_inputs(acs)
    fdic_banking = load_optional_fdic_banking_inputs(acs)
    ffl_inputs = load_optional_ffl_inputs(acs)
    crime_weapons = load_optional_crime_weapons_inputs(acs)
    crime_rate = load_optional_crime_rate_inputs(acs)
    political_violence = load_optional_political_violence_inputs(acs)
    gang_activity = load_optional_gang_activity_inputs(acs)
    explosives_activity = load_optional_explosives_activity_inputs(acs)
    gang_explosives_activity = load_optional_gang_explosives_activity_inputs(acs)
    hate_crime_offense = load_optional_hate_crime_offense_inputs(acs)
    law_enforcement_ambush = load_optional_law_enforcement_ambush_inputs(acs)
    disaster_disruption = load_optional_disaster_disruption_inputs(acs)

    df = acs.merge(cbp, on="fips", how="left")
    df = df.merge(fema, on="county", how="left")
    df = df.merge(tactical, on="county", how="left")
    df = df.merge(fdic_banking, on="county", how="left")
    df = df.merge(ffl_inputs, on="county", how="left", suffixes=("", "_ffl_input"))
    df = df.merge(crime_weapons, on="county", how="left")
    df = df.merge(crime_rate, on="county", how="left")
    df = df.merge(political_violence, on="county", how="left")
    df = df.merge(gang_activity, on="county", how="left")
    df = df.merge(explosives_activity, on="county", how="left")
    df = df.merge(gang_explosives_activity, on="county", how="left")
    df = df.merge(hate_crime_offense, on="county", how="left")
    df = df.merge(law_enforcement_ambush, on="county", how="left")
    df = df.merge(disaster_disruption, on="county", how="left")

    if "ffl_count_ffl_input" in df.columns:
        df["ffl_count"] = df["ffl_count_ffl_input"].fillna(df["ffl_count"])
        df = df.drop(columns=["ffl_count_ffl_input"])

    for col in CBP_INDUSTRIES.values():
        if col not in df.columns:
            df[col] = 0

    fill_cols = [
        "ffl_count",
        "tactical_training_count",
        "surplus_tactical_retail_count",
        "gun_range_count",
        "dealer_ffl_count",
        "manufacturer_ffl_count",
        "pawnbroker_ffl_count",
        "collector_ffl_count",
        "importer_ffl_count",
        "destructive_device_ffl_count",
        "bank_branch_count",
        "total_deposits_thousands",
        "disaster_declaration_count",
        "unique_disaster_types",
        "recent_disaster_declaration_count",
        "severe_storm_event_count",
        "flood_event_count",
        "tornado_event_count",
        "winter_weather_event_count",
        "wildfire_event_count",
        "drought_event_count",
        "power_outage_event_count",
        "avg_outage_duration_hours",
        "hospital_access_stress_score",
        "airport_access_stress_score",
        "road_access_stress_score",
        "communications_disruption_score",
        "social_vulnerability_score",
        "recovery_strain_score",
        "repeat_disruption_exposure_score",
        "homicide_count",
        "kidnapping_abduction_count",
        "weapons_law_violation_count",
        "violent_crime_count",
        "aggravated_assault_count",
        "arson_count",
        "sex_offense_count",
        "hate_crime_count",
        "law_enforcement_assault_count",
        "overall_crime_rate_per_1000_2024",
        "overall_crime_count_2024",
        "crime_population_2024",
        "protest_event_count",
        "violent_unrest_event_count",
        "political_violence_event_count",
        "strategic_development_count",
        "public_disorder_event_count",
        "total_acled_event_count",
        "acled_fatalities",
        "gang_related_total_crime_count",
        "gang_related_violent_crime_count",
        "gang_related_weapon_law_violation_count",
        "gang_related_drug_offense_count",
        "gang_related_property_offense_count",
        "gang_related_homicide_count",
        "gang_related_kidnapping_abduction_count",
        "gang_related_aggravated_assault_count",
        "gang_related_robbery_count",
        "gang_related_arson_count",
        "gang_related_sex_offense_count",
        "explosive_related_total_offense_count",
        "explosive_related_violent_offense_count",
        "explosive_related_weapon_law_violation_count",
        "explosive_related_drug_offense_count",
        "explosive_related_property_offense_count",
        "explosive_related_homicide_count",
        "explosive_related_kidnapping_abduction_count",
        "explosive_related_aggravated_assault_count",
        "explosive_related_robbery_count",
        "explosive_related_arson_count",
        "explosive_related_sex_offense_count",
        "explosive_related_property_damage_count",
        "gang_explosive_total_offense_count",
        "gang_explosive_violent_offense_count",
        "gang_explosive_weapon_law_violation_count",
        "gang_explosive_drug_offense_count",
        "gang_explosive_property_offense_count",
        "gang_explosive_homicide_count",
        "gang_explosive_kidnapping_abduction_count",
        "gang_explosive_aggravated_assault_count",
        "gang_explosive_robbery_count",
        "gang_explosive_arson_count",
        "gang_explosive_sex_offense_count",
        "gang_explosive_property_damage_count",
        "hate_crime_total_count",
        "hate_crime_homicide_count",
        "hate_crime_kidnapping_abduction_count",
        "hate_crime_sex_offense_count",
        "hate_crime_aggravated_assault_count",
        "hate_crime_simple_assault_count",
        "hate_crime_intimidation_count",
        "hate_crime_arson_count",
        "hate_crime_weapon_law_violation_count",
        "hate_crime_property_damage_count",
        "hate_crime_property_offense_count",
        "hate_crime_other_offense_count",
        "le_ambush_total_count",
        "le_ambush_homicide_count",
        "le_ambush_kidnapping_abduction_count",
        "le_ambush_aggravated_assault_count",
        "le_ambush_simple_assault_count",
        "le_ambush_intimidation_count",
        "le_ambush_weapon_law_violation_count",
        "le_ambush_arson_count",
        "le_ambush_property_damage_count",
        "le_ambush_property_offense_count",
        "le_ambush_drug_offense_count",
        "le_ambush_other_offense_count",
    ]

    for col in fill_cols:
        if col not in df.columns:
            df[col] = 0

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    for col in fill_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df.to_csv(PROCESSED_DIR / "tn_county_master_dataset.csv", index=False)

    build_source_register()

    return df
