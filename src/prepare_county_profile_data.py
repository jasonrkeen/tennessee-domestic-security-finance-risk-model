"""
Prepare Tennessee county baseline data for the operational-risk layer.

Output:
    data/raw/tn_county_profile_data.csv

Fields created:
    county
    population
    population_density
    poverty_rate
    unemployment_rate
    median_household_income
    internet_access_rate
    infrastructure_needs_per_capita

Notes:
    - Uses Census ACS 5-year Data Profile API for county-level baseline indicators.
    - Keeps everything county-level.
    - Does not collect addresses, facilities, routes, or target-level data.
"""

from pathlib import Path
import os

import requests
import pandas as pd
from dotenv import load_dotenv


load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = RAW_DIR / "tn_county_profile_data.csv"

ACS_YEAR = 2024
STATE_FIPS_TN = "47"

# ACS 5-Year Data Profile variables.
# Do not request invalid placeholder variables; the Census API returns a plain-text
# error page for bad variables, which then causes JSONDecodeError.
VARIABLES = {
    "NAME": "NAME",
    "population": "DP05_0001E",                 # Total population
    "poverty_rate": "DP03_0128PE",             # Percent below poverty level
    "unemployment_rate": "DP03_0009PE",        # Unemployment rate
    "median_household_income": "DP03_0062E",   # Median household income
    "internet_access_rate": "DP02_0154PE",     # Broadband internet subscription
}


def normalize_county_name(value: str) -> str:
    if pd.isna(value):
        return ""

    value = str(value)
    value = value.replace(" County, Tennessee", "")
    value = value.replace(" County", "")
    value = value.strip()
    return value.title()


def fetch_acs_profile(year: int = ACS_YEAR) -> pd.DataFrame:
    """Fetch Tennessee county profile fields from Census ACS 5-year profile API."""
    base_url = f"https://api.census.gov/data/{year}/acs/acs5/profile"

    get_vars = ",".join(VARIABLES.values())

    api_key = os.getenv("CENSUS_API_KEY") or os.getenv("CENSUS_KEY")

    if not api_key:
        raise RuntimeError(
            "Missing Census API key. Add CENSUS_API_KEY=your_key_here "
            "or CENSUS_KEY=your_key_here to your .env file."
        )

    params = {
        "get": get_vars,
        "for": "county:*",
        "in": f"state:{STATE_FIPS_TN}",
        "key": api_key,
    }

    response = requests.get(base_url, params=params, timeout=45)

    if not response.ok:
        raise RuntimeError(
            f"Census API request failed with status {response.status_code}.\n"
            f"URL: {response.url}\n"
            f"Response preview:\n{response.text[:1000]}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "Census API returned a non-JSON response. This usually means one of the "
            "requested ACS variables is invalid for the selected year/dataset.\n"
            f"URL: {response.url}\n"
            f"Response preview:\n{response.text[:1000]}"
        ) from exc

    header = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=header)

    # Preserve the Census county FIPS suffix before creating the readable county name.
    county_fips_suffix = df["county"].astype(str).str.zfill(3) if "county" in df.columns else pd.Series(pd.NA, index=df.index)

    reverse_map = {v: k for k, v in VARIABLES.items()}
    df = df.rename(columns=reverse_map)

    df["county"] = df["NAME"].apply(normalize_county_name)
    df["county_fips_suffix"] = county_fips_suffix

    numeric_cols = [
        "population",
        "poverty_rate",
        "unemployment_rate",
        "median_household_income",
        "internet_access_rate",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # county_fips_suffix is the county FIPS suffix from the API response.
    df["county_fips"] = df["state"].astype(str).str.zfill(2) + df["county_fips_suffix"].astype(str).str.zfill(3)

    return df


def add_density_from_fema_if_available(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use FEMA population and area if available to create population density.

    This avoids adding geometry or coordinates and keeps the feature county-level.
    """

    fema_path = RAW_DIR / "fema_nri_counties.csv"

    if not fema_path.exists():
        df["population_density"] = pd.NA
        return df

    fema = pd.read_csv(fema_path)

    needed = {"county", "fema_population", "fema_area_sq_mi"}

    if not needed.issubset(set(fema.columns)):
        df["population_density"] = pd.NA
        return df

    fema["county"] = fema["county"].astype(str).str.title()
    fema["fema_population"] = pd.to_numeric(fema["fema_population"], errors="coerce")
    fema["fema_area_sq_mi"] = pd.to_numeric(fema["fema_area_sq_mi"], errors="coerce")

    fema["population_density"] = fema["fema_population"] / fema["fema_area_sq_mi"]

    density = fema[["county", "population_density"]].copy()

    df = df.merge(density, on="county", how="left")

    return df


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    df = fetch_acs_profile()
    df = add_density_from_fema_if_available(df)

    # Infrastructure needs will come from TACIR later.
    df["infrastructure_needs_per_capita"] = pd.NA

    out = df[
        [
            "county",
            "population",
            "population_density",
            "poverty_rate",
            "unemployment_rate",
            "median_household_income",
            "internet_access_rate",
            "infrastructure_needs_per_capita",
        ]
    ].copy()

    out = out.sort_values("county")
    out.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved Tennessee county profile data to: {OUTPUT_PATH}")
    print(f"Rows: {len(out)}")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
