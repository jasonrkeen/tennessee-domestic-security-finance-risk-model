"""
Prepare county-level TDOT transportation pressure data from Traffic Lines CSV.

Input:
    data/raw/Traffic_Lines_-8892729031592288661.csv
    or data/raw/tdot_traffic_lines.csv

Output:
    data/raw/tn_county_transport_context.csv

Responsible-use boundary:
    - County-level aggregation only
    - No route-level vulnerability claims
    - No station-level coordinates
    - No raw route links in processed output
"""

from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

INPUT_CANDIDATES = [
    RAW_DIR / "Traffic_Lines_-8892729031592288661.csv",
    RAW_DIR / "tdot_traffic_lines.csv",
]
OUTPUT_PATH = RAW_DIR / "tn_county_transport_context.csv"

TN_COUNTY_CODE_MAP = {
    1: "Anderson", 2: "Bedford", 3: "Benton", 4: "Bledsoe", 5: "Blount",
    6: "Bradley", 7: "Campbell", 8: "Cannon", 9: "Carroll", 10: "Carter",
    11: "Cheatham", 12: "Chester", 13: "Claiborne", 14: "Clay", 15: "Cocke",
    16: "Coffee", 17: "Crockett", 18: "Cumberland", 19: "Davidson", 20: "Decatur",
    21: "Dekalb", 22: "Dickson", 23: "Dyer", 24: "Fayette", 25: "Fentress",
    26: "Franklin", 27: "Gibson", 28: "Giles", 29: "Grainger", 30: "Greene",
    31: "Grundy", 32: "Hamblen", 33: "Hamilton", 34: "Hancock", 35: "Hardeman",
    36: "Hardin", 37: "Hawkins", 38: "Haywood", 39: "Henderson", 40: "Henry",
    41: "Hickman", 42: "Houston", 43: "Humphreys", 44: "Jackson", 45: "Jefferson",
    46: "Johnson", 47: "Knox", 48: "Lake", 49: "Lauderdale", 50: "Lawrence",
    51: "Lewis", 52: "Lincoln", 53: "Loudon", 54: "Macon", 55: "Madison",
    56: "Marion", 57: "Marshall", 58: "Maury", 59: "Mcminn", 60: "Mcnairy",
    61: "Meigs", 62: "Monroe", 63: "Montgomery", 64: "Moore", 65: "Morgan",
    66: "Obion", 67: "Overton", 68: "Perry", 69: "Pickett", 70: "Polk",
    71: "Putnam", 72: "Rhea", 73: "Roane", 74: "Robertson", 75: "Rutherford",
    76: "Scott", 77: "Sequatchie", 78: "Sevier", 79: "Shelby", 80: "Smith",
    81: "Stewart", 82: "Sullivan", 83: "Sumner", 84: "Tipton", 85: "Trousdale",
    86: "Unicoi", 87: "Union", 88: "Van Buren", 89: "Warren", 90: "Washington",
    91: "Wayne", 92: "Weakley", 93: "White", 94: "Williamson", 95: "Wilson",
}

# Match county capitalization used elsewhere in the project.
CANONICAL_REPLACEMENTS = {
    "Dekalb": "DeKalb",
    "Mcminn": "McMinn",
    "Mcnairy": "McNairy",
}


def find_input_path() -> Path:
    for path in INPUT_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Missing TDOT traffic lines CSV. Save the downloaded file to one of:\n"
        + "\n".join(str(p) for p in INPUT_CANDIDATES)
    )


def clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False),
        errors="coerce",
    )


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    input_path = find_input_path()

    df = pd.read_csv(input_path, low_memory=False)
    df = df.loc[:, ~df.columns.duplicated()].copy()

    required = [
        "County", "AADT", "VMT", "Mileage",
        "Single-Unit Truck %", "Multi-Unit Truck %",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected TDOT Traffic Lines columns: {missing}")

    work = pd.DataFrame()
    work["county_code"] = clean_numeric(df["County"]).astype("Int64")
    work["county"] = work["county_code"].map(TN_COUNTY_CODE_MAP).replace(CANONICAL_REPLACEMENTS)
    work["aadt"] = clean_numeric(df["AADT"])
    work["vmt"] = clean_numeric(df["VMT"])
    work["mileage"] = clean_numeric(df["Mileage"])
    work["single_unit_truck_pct"] = clean_numeric(df["Single-Unit Truck %"])
    work["multi_unit_truck_pct"] = clean_numeric(df["Multi-Unit Truck %"])
    work["truck_percentage"] = work["single_unit_truck_pct"].fillna(0) + work["multi_unit_truck_pct"].fillna(0)

    work = work[work["county"].notna()].copy()
    work = work.dropna(how="all", subset=["aadt", "vmt", "truck_percentage"])

    # County-level only. No route IDs, raw data links, coordinates, or station details.
    county = (
        work.groupby("county", as_index=False)
        .agg(
            avg_aadt=("aadt", "mean"),
            total_vmt=("vmt", "sum"),
            truck_percentage=("truck_percentage", "mean"),
            traffic_station_count=("county", "size"),
            total_traffic_line_mileage=("mileage", "sum"),
        )
        .sort_values("county")
    )

    county["avg_aadt"] = county["avg_aadt"].round(2)
    county["total_vmt"] = county["total_vmt"].round(2)
    county["truck_percentage"] = county["truck_percentage"].round(2)
    county["total_traffic_line_mileage"] = county["total_traffic_line_mileage"].round(2)

    county.to_csv(OUTPUT_PATH, index=False)

    print(f"Loaded TDOT traffic lines from: {input_path}")
    print(f"Saved county transportation context to: {OUTPUT_PATH}")
    print(f"Rows: {len(county)}")
    print(county.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
