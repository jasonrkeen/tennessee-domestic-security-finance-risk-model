import re

import pandas as pd

from src.config import OPTIONAL_DISASTER_DISRUPTION_INPUT


def _normalize_county_key(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value)

    text = (
        text.replace(" County", "")
        .replace(" county", "")
        .replace(", Tennessee", "")
        .replace(", TN", "")
        .strip()
        .lower()
    )

    text = re.sub(r"[^a-z0-9]", "", text)

    return text


def _build_county_crosswalk(county_base: pd.DataFrame) -> pd.DataFrame:
    if "county" not in county_base.columns:
        raise ValueError("county_base must include a 'county' column.")

    crosswalk = county_base[["county"]].copy()
    crosswalk["county"] = crosswalk["county"].astype(str).str.strip()
    crosswalk["county_key"] = crosswalk["county"].apply(_normalize_county_key)

    return crosswalk.drop_duplicates(subset=["county_key"])


def _apply_county_crosswalk(
    df: pd.DataFrame,
    county_base: pd.DataFrame,
    source_name: str,
) -> pd.DataFrame:
    if "county" not in df.columns:
        raise ValueError(f"{source_name} input must include a 'county' column.")

    crosswalk = _build_county_crosswalk(county_base)

    output = df.copy()
    output["county_original"] = output["county"].astype(str).str.strip()
    output["county_key"] = output["county_original"].apply(_normalize_county_key)

    summary_keys = {
        "total",
        "totals",
        "statewide",
        "tennessee",
        "unknown",
        "nan",
        "",
    }

    output = output[~output["county_key"].isin(summary_keys)].copy()

    output = output.merge(
        crosswalk,
        on="county_key",
        how="left",
        suffixes=("_input", ""),
    )

    unmatched = output[output["county"].isna()][["county_original"]].drop_duplicates()

    if not unmatched.empty:
        print(f"\nWarning: unmatched county names in {source_name} input:")
        for value in unmatched["county_original"].tolist():
            print(f"- {value}")

    output = output[output["county"].notna()].copy()

    output = output.drop(
        columns=["county_original", "county_key"],
        errors="ignore",
    )

    return output


def load_optional_disaster_disruption_inputs(
    county_base: pd.DataFrame,
) -> pd.DataFrame:
    """
    Optional county-level disaster / disruption vulnerability input.

    Expected columns:
    county,
    severe_storm_event_count,
    flood_event_count,
    tornado_event_count,
    winter_weather_event_count,
    wildfire_event_count,
    drought_event_count,
    power_outage_event_count,
    avg_outage_duration_hours,
    hospital_access_stress_score,
    airport_access_stress_score,
    road_access_stress_score,
    communications_disruption_score,
    social_vulnerability_score,
    recovery_strain_score,
    repeat_disruption_exposure_score

    Notes:
    - Use county-level aggregate fields only.
    - Do not include facility addresses, substation locations, hospital addresses,
      airport coordinates, utility maps, road chokepoints, infrastructure diagrams,
      event-level coordinates, exact facility names, or operational vulnerability details.
    - Fields can be manually populated or later automated from public aggregate data.
    """

    expected_cols = [
        "county",
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
    ]

    if OPTIONAL_DISASTER_DISRUPTION_INPUT.exists():
        df = pd.read_csv(OPTIONAL_DISASTER_DISRUPTION_INPUT)

        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0

        df = df[expected_cols].copy()

        df = _apply_county_crosswalk(
            df=df,
            county_base=county_base,
            source_name="Disaster / disruption vulnerability",
        )

    else:
        df = county_base[["county"]].copy()

        for col in expected_cols:
            if col != "county":
                df[col] = 0

        OPTIONAL_DISASTER_DISRUPTION_INPUT.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OPTIONAL_DISASTER_DISRUPTION_INPUT, index=False)

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = (
        df.groupby("county", as_index=False)
        .agg(
            severe_storm_event_count=("severe_storm_event_count", "sum"),
            flood_event_count=("flood_event_count", "sum"),
            tornado_event_count=("tornado_event_count", "sum"),
            winter_weather_event_count=("winter_weather_event_count", "sum"),
            wildfire_event_count=("wildfire_event_count", "sum"),
            drought_event_count=("drought_event_count", "sum"),
            power_outage_event_count=("power_outage_event_count", "sum"),
            avg_outage_duration_hours=("avg_outage_duration_hours", "mean"),
            hospital_access_stress_score=("hospital_access_stress_score", "max"),
            airport_access_stress_score=("airport_access_stress_score", "max"),
            road_access_stress_score=("road_access_stress_score", "max"),
            communications_disruption_score=("communications_disruption_score", "max"),
            social_vulnerability_score=("social_vulnerability_score", "max"),
            recovery_strain_score=("recovery_strain_score", "max"),
            repeat_disruption_exposure_score=("repeat_disruption_exposure_score", "max"),
        )
    )

    # Retain all ACS counties even if the optional input only contains counties
    # with positive activity.
    county_base_clean = county_base[["county"]].copy()
    county_base_clean["county"] = county_base_clean["county"].astype(str).str.strip()

    df = county_base_clean.merge(df, on="county", how="left")

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df
