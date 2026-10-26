import re

import pandas as pd

from src.source_availability import county_availability, attach_availability

from src.config import OPTIONAL_POLITICAL_VIOLENCE_INPUT


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


def load_optional_political_violence_inputs(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Load optional county-level political violence / civil unrest inputs.

    Expected ACLED-derived columns:
    county,
    protest_event_count,
    violent_unrest_event_count,
    political_violence_event_count,
    strategic_development_count,
    public_disorder_event_count,
    total_acled_event_count,
    acled_fatalities

    Notes:
    - Use county-level aggregate counts only.
    - Do not include event addresses, exact locations, coordinates,
      participant names, actor names, organization names, URLs,
      event notes, or tactical maps.
    """

    expected_cols = [
        "county",
        "protest_event_count",
        "violent_unrest_event_count",
        "political_violence_event_count",
        "strategic_development_count",
        "public_disorder_event_count",
        "total_acled_event_count",
        "acled_fatalities",
    ]

    # Backward-compatible legacy columns from earlier manual-input version.
    legacy_cols = [
        "extremism_related_event_count",
        "threat_incident_count",
    ]

    if OPTIONAL_POLITICAL_VIOLENCE_INPUT.exists():
        df = pd.read_csv(OPTIONAL_POLITICAL_VIOLENCE_INPUT)
        evidence = county_availability(df, expected_cols, "political_violence_data_available")

        # Backward compatibility:
        # If an older file has extremism_related_event_count but not
        # political_violence_event_count, map it forward.
        if (
            "political_violence_event_count" not in df.columns
            and "extremism_related_event_count" in df.columns
        ):
            df["political_violence_event_count"] = df[
                "extremism_related_event_count"
            ]

        # If an older file has threat_incident_count but not
        # strategic_development_count, map it cautiously into strategic developments.
        if (
            "strategic_development_count" not in df.columns
            and "threat_incident_count" in df.columns
        ):
            df["strategic_development_count"] = df["threat_incident_count"]

        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0

        df = df[expected_cols].copy()

        df = _apply_county_crosswalk(
            df=df,
            county_base=county_base,
            source_name="ACLED political violence / civil unrest",
        )

    else:
        evidence = pd.Series(dtype=bool)
        df = county_base[["county"]].copy()

        for col in expected_cols:
            if col != "county":
                df[col] = 0

        OPTIONAL_POLITICAL_VIOLENCE_INPUT.parent.mkdir(parents=True, exist_ok=True)
        df["political_violence_data_available"] = False
        df.to_csv(OPTIONAL_POLITICAL_VIOLENCE_INPUT, index=False)

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = (
        df.groupby("county", as_index=False)
        .agg(
            protest_event_count=("protest_event_count", "sum"),
            violent_unrest_event_count=("violent_unrest_event_count", "sum"),
            political_violence_event_count=("political_violence_event_count", "sum"),
            strategic_development_count=("strategic_development_count", "sum"),
            public_disorder_event_count=("public_disorder_event_count", "sum"),
            total_acled_event_count=("total_acled_event_count", "sum"),
            acled_fatalities=("acled_fatalities", "sum"),
        )
    )

    # Ensure all ACS counties are retained, even if ACLED has no events.
    county_base_clean = county_base[["county"]].copy()
    county_base_clean["county"] = county_base_clean["county"].astype(str).str.strip()

    df = county_base_clean.merge(df, on="county", how="left")

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return attach_availability(df, evidence, "political_violence_data_available")
