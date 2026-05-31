"""
Prepare TBI county-level public-safety context from CrimeInsight export.

Input:
    data/raw/crimes_clearances_by_offense_type_2024.csv

Output:
    data/raw/tbi_county_public_safety_context.csv

Responsible-use boundary:
    - County-level only
    - No incident IDs
    - No names
    - No addresses
    - No coordinates
    - No facility-level or target-level data
"""

from pathlib import Path
import csv
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

INPUT_PATH = RAW_DIR / "crimes_clearances_by_offense_type_2024.csv"
OUTPUT_PATH = RAW_DIR / "tbi_county_public_safety_context.csv"

# Violent-crime/public-safety proxy fields from available offense categories.
# These are broad county-level rates, not incident-level investigative findings.
VIOLENT_OFFENSES = [
    "Murder",
    "Negligent Manslaughter",
    "Negligent Vehicular Manslaughter",
    "Kidnapping/Abduction",
    "All Rape",
    "Aggravated Assault",
    "Robbery",
]

# Public-disorder proxy from offense categories available in this export.
# This is a proxy only; it should be documented as such.
PUBLIC_DISORDER_PROXY_OFFENSES = [
    "Intimidation",
    "Stalking",
    "Arson",
    "Destruction/Damage/Vandalism",
]

WEAPON_OFFENSE = "Weapon Law Violations"


def normalize_county_name(value: str) -> str:
    if pd.isna(value):
        return ""
    value = str(value).strip()
    value = value.replace(" County", "")
    value = value.replace(" county", "")
    value = value.replace(".", "")
    return value.title()


def to_number(value) -> float:
    if value is None:
        return 0.0
    text = str(value).replace(",", "").strip()
    if text == "":
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def find_all_clearances_county_groups(rows: list[list[str]]) -> list[tuple[str, int]]:
    """
    The CrimeInsight export has a multi-row header:
    - row 4: Incident Clearance section labels
    - row 5: county labels repeated every 4 columns
    - row 6: measures repeated every 4 columns

    We use the All Clearances section only. The Cleared section begins where
    row 4 contains "Cleared".
    """
    clearance_row = rows[4]
    county_row = rows[5]

    start_col = 1
    end_col = len(county_row)

    for idx, value in enumerate(clearance_row):
        if str(value).strip().lower() == "cleared":
            end_col = idx
            break

    groups = []
    for col_idx in range(start_col, end_col, 4):
        if col_idx < len(county_row):
            county = normalize_county_name(county_row[col_idx])
            if county:
                groups.append((county, col_idx))

    return groups


def build_offense_row_lookup(rows: list[list[str]]) -> dict[str, list[str]]:
    lookup = {}
    for row in rows[8:]:
        if row and str(row[0]).strip():
            lookup[str(row[0]).strip()] = row
    return lookup


def get_offense_value(offense_rows: dict[str, list[str]], offense: str, col_idx: int) -> float:
    row = offense_rows.get(offense)
    if row is None or col_idx >= len(row):
        return 0.0
    return to_number(row[col_idx])


def sum_offense_measure(
    offense_rows: dict[str, list[str]],
    offenses: list[str],
    base_col_idx: int,
    measure_offset: int,
) -> float:
    """
    In each county group:
    offset 0 = Number of Crimes
    offset 1 = Crime Rate per 100,000
    offset 2 = Offense Rate per 100,000
    offset 3 = Incident Rate per 100,000
    """
    col_idx = base_col_idx + measure_offset
    return sum(get_offense_value(offense_rows, offense, col_idx) for offense in offenses)


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_PATH}\n"
            "Place crimes_clearances_by_offense_type_2024.csv in data/raw/."
        )

    rows = read_rows(INPUT_PATH)
    county_groups = find_all_clearances_county_groups(rows)
    offense_rows = build_offense_row_lookup(rows)

    if not county_groups:
        raise ValueError("Could not identify county groups in the CrimeInsight CSV header.")

    records = []

    for county, col_idx in county_groups:
        violent_count = sum_offense_measure(offense_rows, VIOLENT_OFFENSES, col_idx, 0)
        violent_rate = sum_offense_measure(offense_rows, VIOLENT_OFFENSES, col_idx, 1)

        weapon_count = get_offense_value(offense_rows, WEAPON_OFFENSE, col_idx)
        weapon_rate = get_offense_value(offense_rows, WEAPON_OFFENSE, col_idx + 1)

        public_disorder_count = sum_offense_measure(
            offense_rows,
            PUBLIC_DISORDER_PROXY_OFFENSES,
            col_idx,
            0,
        )
        public_disorder_rate = sum_offense_measure(
            offense_rows,
            PUBLIC_DISORDER_PROXY_OFFENSES,
            col_idx,
            1,
        )

        records.append(
            {
                "county": county,
                "violent_crime_count": round(violent_count, 2),
                "violent_crime_rate": round(violent_rate, 2),
                # This export is offense-type data, not a hate-crime dataset.
                # Keep these blank until a dedicated hate-crime county file is added.
                "hate_crime_count": pd.NA,
                "hate_crime_rate": pd.NA,
                "weapon_law_violation_count": round(weapon_count, 2),
                "weapon_law_violation_rate": round(weapon_rate, 2),
                "public_disorder_count": round(public_disorder_count, 2),
                "public_disorder_rate": round(public_disorder_rate, 2),
                "source_file": INPUT_PATH.name,
                "source_scope": "TIBRS offense data; incident date 2024; all clearances",
            }
        )

    out = pd.DataFrame(records).sort_values("county")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved TBI public-safety context to: {OUTPUT_PATH}")
    print(f"Rows: {len(out)}")
    print("\nPreview:")
    print(out.head(10).to_string(index=False))

    missing_hate = out["hate_crime_count"].isna().sum()
    print(
        f"\nNote: hate_crime_count and hate_crime_rate are blank for {missing_hate} counties "
        "because this input file is offense-type data, not a hate-crime file."
    )


if __name__ == "__main__":
    main()
