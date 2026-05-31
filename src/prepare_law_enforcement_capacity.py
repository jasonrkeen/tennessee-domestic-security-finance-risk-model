"""
Prepare county-level law-enforcement capacity context from BJS/ICPSR CSLLEA 2018.

Preferred input:
    data/raw/38771-0001-Data.tsv
or:
    data/raw/38771-0001-Data.csv

Output:
    data/raw/tn_county_law_enforcement_capacity.csv

Responsible-use boundary:
    - Aggregates to county level only
    - Does not publish agency names, ORI identifiers, ZIP codes, or locations
    - Treats law-enforcement staffing as response-capacity context, not a threat indicator
"""

from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

INPUT_CANDIDATES = [
    RAW_DIR / "38771-0001-Data.tsv",
    RAW_DIR / "38771-0001-Data.csv",
    RAW_DIR / "csllea_2018_agency_data.tsv",
    RAW_DIR / "csllea_2018_agency_data.csv",
]

COUNTY_PROFILE_PATH = RAW_DIR / "tn_county_profile_data.csv"
OUTPUT_PATH = RAW_DIR / "tn_county_law_enforcement_capacity.csv"


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
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.replace(" County", "")
    value = value.replace(" county", "")
    value = value.replace(".", "")
    value = " ".join(value.split())

    canonical = {county.lower(): county for county in TN_COUNTIES}
    return canonical.get(value.lower(), value.title())


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def minmax(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if s.notna().sum() == 0:
        return pd.Series(np.nan, index=series.index)
    low = s.min()
    high = s.max()
    if high == low:
        return pd.Series(50.0, index=series.index)
    return ((s - low) / (high - low) * 100).round(2)


def inverse_minmax(series: pd.Series) -> pd.Series:
    return (100 - minmax(series)).round(2)


def read_input() -> pd.DataFrame:
    for path in INPUT_CANDIDATES:
        if path.exists():
            if path.suffix.lower() == ".tsv":
                return pd.read_csv(path, sep="\t", low_memory=False)
            if path.suffix.lower() == ".csv":
                return pd.read_csv(path, low_memory=False)

    raise FileNotFoundError(
        "Missing CSLLEA agency data. Download the ICPSR 38771 DS0001 delimited "
        "data file and save it as data/raw/38771-0001-Data.tsv or "
        "data/raw/38771-0001-Data.csv."
    )


def clean_numeric(series: pd.Series) -> pd.Series:
    out = pd.to_numeric(series, errors="coerce")
    out = out.mask(out.isin([-9, -8, -1]))
    return out


def load_population() -> pd.DataFrame:
    if not COUNTY_PROFILE_PATH.exists():
        return pd.DataFrame({"county": TN_COUNTIES, "population": np.nan})

    df = pd.read_csv(COUNTY_PROFILE_PATH)
    county_col = find_column(df, ["county", "County"])
    pop_col = find_column(df, ["population", "Population"])

    if county_col is None or pop_col is None:
        return pd.DataFrame({"county": TN_COUNTIES, "population": np.nan})

    out = df[[county_col, pop_col]].copy()
    out.columns = ["county", "population"]
    out["county"] = out["county"].apply(normalize_county_name)
    out["population"] = pd.to_numeric(out["population"], errors="coerce")
    return out


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    df = read_input()
    df = df.loc[:, ~df.columns.duplicated()].copy()

    state_col = find_column(df, ["STATE", "state"])
    county_col = find_column(df, ["COUNTY", "county"])

    if state_col is None or county_col is None:
        raise ValueError("Could not find STATE and COUNTY columns in CSLLEA data.")

    # Tennessee only
    df = df[df[state_col].astype(str).str.upper().str.strip().isin(["TN", "TENNESSEE"])].copy()
    df["county"] = df[county_col].apply(normalize_county_name)

    # Keep local/county law-enforcement agencies by default.
    # 1 = Sheriff, 3 = Local Police, 4 = County/Regional Police in the ICPSR codebook.
    agency_type_col = find_column(df, ["AGENCYSAMPTYPE", "AgencySampleType"])
    if agency_type_col:
        df[agency_type_col] = pd.to_numeric(df[agency_type_col], errors="coerce")
        df = df[df[agency_type_col].isin([1, 3, 4])].copy()

    complete_col = find_column(df, ["COMPLETE", "Complete"])
    if complete_col:
        # Keep complete records where coded; leave rows when coding is unclear.
        comp = pd.to_numeric(df[complete_col], errors="coerce")
        if comp.notna().sum() > 0:
            df = df[comp.eq(1) | comp.isna()].copy()

    sworn_col = find_column(df, ["FTSWORN", "FTSWORN_TOTAL"])
    pt_sworn_col = find_column(df, ["PTSWORN"])
    limited_col = find_column(df, ["FTLIM", "FTLIM_TOTAL"])
    non_col = find_column(df, ["FTNON"])
    total_ft_col = find_column(df, ["TOTFTEMP"])
    total_pt_col = find_column(df, ["TOTPTEMP"])

    for new_col, source_col in {
        "full_time_sworn": sworn_col,
        "part_time_sworn": pt_sworn_col,
        "full_time_limited": limited_col,
        "full_time_non_sworn": non_col,
        "total_full_time_employees": total_ft_col,
        "total_part_time_employees": total_pt_col,
    }.items():
        if source_col:
            df[new_col] = clean_numeric(df[source_col])
        else:
            df[new_col] = np.nan

    function_cols = {
        "patrol_response_agency_count": ["PAT_RESP_CRIM_INC", "PAT_RESP_ROUTINE", "PAT_RESP_DISPATCH"],
        "criminal_investigation_agency_count": ["CRIM_HOMICIDE", "CRIM_ARSON", "CRIM_CYBER"],
        "traffic_response_agency_count": ["TRAF_ENFORCE", "TRAF_DIRECT", "TRAF_ACC_INV"],
        "court_detention_agency_count": ["COURT_SEC", "COURT_SERVE", "DET_JAIL", "DET_BOOK"],
        "special_events_agency_count": ["PAT_RESP_SPEC_EVT"],
    }

    for output_col, candidates in function_cols.items():
        present = [find_column(df, [c]) for c in candidates]
        present = [c for c in present if c]
        if present:
            # Count agencies that report yes (=1) to at least one related function.
            yes_any = pd.DataFrame(
                {c: pd.to_numeric(df[c], errors="coerce").eq(1) for c in present}
            ).any(axis=1)
            df[output_col] = yes_any.astype(int)
        else:
            df[output_col] = 0

    grouped = (
        df.groupby("county", as_index=False)
        .agg(
            law_enforcement_agency_count=("county", "size"),
            law_enforcement_full_time_employees=("total_full_time_employees", "sum"),
            law_enforcement_part_time_employees=("total_part_time_employees", "sum"),
            law_enforcement_sworn_personnel=("full_time_sworn", "sum"),
            law_enforcement_part_time_sworn_personnel=("part_time_sworn", "sum"),
            law_enforcement_limited_authority_personnel=("full_time_limited", "sum"),
            law_enforcement_non_sworn_personnel=("full_time_non_sworn", "sum"),
            patrol_response_agency_count=("patrol_response_agency_count", "sum"),
            criminal_investigation_agency_count=("criminal_investigation_agency_count", "sum"),
            traffic_response_agency_count=("traffic_response_agency_count", "sum"),
            court_detention_agency_count=("court_detention_agency_count", "sum"),
            special_events_agency_count=("special_events_agency_count", "sum"),
        )
    )

    base = pd.DataFrame({"county": TN_COUNTIES})
    grouped = base.merge(grouped, on="county", how="left")

    numeric_cols = [c for c in grouped.columns if c != "county"]
    grouped[numeric_cols] = grouped[numeric_cols].fillna(0)

    pop = load_population()
    grouped = grouped.merge(pop, on="county", how="left")

    grouped["law_enforcement_sworn_per_100k"] = (
        grouped["law_enforcement_sworn_personnel"] / grouped["population"] * 100000
    ).round(2)

    grouped["law_enforcement_employee_per_100k"] = (
        grouped["law_enforcement_full_time_employees"] / grouped["population"] * 100000
    ).round(2)

    grouped["law_enforcement_capacity_score"] = (
        minmax(grouped["law_enforcement_sworn_per_100k"]).fillna(50) * 0.45
        + minmax(grouped["law_enforcement_employee_per_100k"]).fillna(50) * 0.35
        + minmax(grouped["patrol_response_agency_count"]).fillna(50) * 0.10
        + minmax(grouped["criminal_investigation_agency_count"]).fillna(50) * 0.10
    ).round(2)

    grouped["law_enforcement_capacity_gap_score"] = (
        100 - grouped["law_enforcement_capacity_score"]
    ).round(2)

    # Do not include agency names, ORI identifiers, ZIP codes, or addresses.
    output_cols = [
        "county",
        "population",
        "law_enforcement_agency_count",
        "law_enforcement_full_time_employees",
        "law_enforcement_part_time_employees",
        "law_enforcement_sworn_personnel",
        "law_enforcement_part_time_sworn_personnel",
        "law_enforcement_limited_authority_personnel",
        "law_enforcement_non_sworn_personnel",
        "law_enforcement_sworn_per_100k",
        "law_enforcement_employee_per_100k",
        "patrol_response_agency_count",
        "criminal_investigation_agency_count",
        "traffic_response_agency_count",
        "court_detention_agency_count",
        "special_events_agency_count",
        "law_enforcement_capacity_score",
        "law_enforcement_capacity_gap_score",
    ]

    out = grouped[output_cols].sort_values("county")
    out.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved county law-enforcement capacity context to: {OUTPUT_PATH}")
    print(f"Rows: {len(out)}")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
