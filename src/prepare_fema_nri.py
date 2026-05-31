"""
Prepare FEMA National Risk Index county data for the Tennessee operational-risk layer.

Input:
    data/raw/fema_nri_counties_original.csv

Output:
    data/raw/fema_nri_counties.csv

Purpose:
    Converts official FEMA National Risk Index county-level data into the
    simplified county-level schema expected by src/operational_risk_features.py.
"""

from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

INPUT_PATH = RAW_DIR / "fema_nri_counties_original.csv"
OUTPUT_PATH = RAW_DIR / "fema_nri_counties.csv"


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Find a column using case-insensitive candidate matching."""
    lower_map = {c.lower(): c for c in df.columns}

    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]

    return None


def normalize_county_name(value: str) -> str:
    """Normalize county name for matching against project county list."""
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.replace(" County", "")
    value = value.replace(" county", "")
    value = value.replace(".", "")
    return value.title()


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing FEMA file: {INPUT_PATH}\n"
            "Download FEMA National Risk Index Dataset All Counties - Table Format, "
            "extract the county CSV if needed, and save it as "
            "data/raw/fema_nri_counties_original.csv"
        )

    df = pd.read_csv(INPUT_PATH, low_memory=False)
    df = df.loc[:, ~df.columns.duplicated()].copy()

    county_col = find_column(df, ["COUNTY", "county", "County", "county_name"])
    state_col = find_column(df, ["STATE", "STATEABBRV", "ST_ABBRV", "state", "State"])

    if county_col is None:
        raise ValueError(
            "Could not find a county column. Expected one of: COUNTY, county, County, county_name."
        )

    if state_col is not None:
        state_values = df[state_col].astype(str).str.upper().str.strip()
        df = df[state_values.isin(["TN", "TENNESSEE"])].copy()

    df["county"] = df[county_col].apply(normalize_county_name)

    field_map = {
        "fema_risk_index_score": [
            "RISK_SCORE",
            "risk_score",
            "Risk Score",
            "National Risk Index - Score - Composite",
        ],
        "fema_social_vulnerability_score": [
            "SOVI_SCORE",
            "sovi_score",
            "Social Vulnerability Score",
            "Social Vulnerability - Score",
        ],
        "fema_community_resilience_score": [
            "RESL_SCORE",
            "resl_score",
            "Community Resilience Score",
            "Community Resilience - Score",
        ],
        "fema_expected_annual_loss_score": [
            "EAL_SCORE",
            "eal_score",
            "Expected Annual Loss Score",
            "Expected Annual Loss - Score",
        ],
    }

    out = pd.DataFrame()
    out["county"] = df["county"]
    out["STATE"] = "TN"

    for output_col, candidates in field_map.items():
        source_col = find_column(df, candidates)

        if source_col is None:
            out[output_col] = pd.NA
            print(f"Warning: Could not find source column for {output_col}")
        else:
            out[output_col] = pd.to_numeric(df[source_col], errors="coerce")
            print(f"Mapped {source_col} -> {output_col}")

    out = out.groupby(["county", "STATE"], as_index=False).mean(numeric_only=True)
    out = out.sort_values("county")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved cleaned FEMA NRI Tennessee county file to: {OUTPUT_PATH}")
    print(f"Rows: {len(out)}")
    print("\nPreview:")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    main()