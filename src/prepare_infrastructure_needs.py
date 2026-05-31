"""
Prepare county-level TACIR public infrastructure needs data.

Input:
    data/raw/2026_Infrastructure_AppendixD.pdf

Outputs:
    data/raw/tn_county_infrastructure_needs.csv
    data/raw/tn_county_profile_data.csv  (updated with infrastructure_needs_per_capita)

Purpose:
    Extracts Table D-1a, All Needs by County, from TACIR Appendix D and
    creates a county-level infrastructure pressure feature for the operational
    risk model.

Responsible-use boundary:
    - County-level totals only
    - No project names
    - No facility addresses
    - No exact locations
    - No vulnerability descriptions
"""

from pathlib import Path
import re
import pandas as pd

try:
    import pdfplumber
except ImportError as exc:
    raise ImportError(
        "Missing dependency: pdfplumber. Install with: pip install pdfplumber"
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

INPUT_PATH = RAW_DIR / "2026_Infrastructure_AppendixD.pdf"
OUTPUT_PATH = RAW_DIR / "tn_county_infrastructure_needs.csv"
COUNTY_PROFILE_PATH = RAW_DIR / "tn_county_profile_data.csv"

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

COUNTY_LOOKUP = {county.lower(): county for county in TN_COUNTIES}


def normalize_county_name(value: str) -> str:
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.replace(" County", "")
    value = value.replace(" county", "")
    value = value.replace(".", "")
    value = " ".join(value.split())
    return COUNTY_LOOKUP.get(value.lower(), value.title())


def money_to_int(value: str) -> int | None:
    if value is None:
        return None
    cleaned = str(value).replace("$", "").replace(",", "").strip()
    if cleaned == "":
        return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def extract_table_d1a() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_PATH}\n"
            "Copy 2026_Infrastructure_AppendixD.pdf into data/raw first."
        )

    # Table D-1a is on PDF pages 145-147, which are file page indexes 4-6.
    rows = []
    row_pattern = re.compile(
        r"^(?P<county>[A-Za-z]+(?:\s+Buren)?)\s+"
        r"(?P<population>[\d,]+)\s+"
        r"\$?\s*(?P<regional>[\d,]+)\s+"
        r"\$?\s*(?P<local>[\d,]+)\s+"
        r"\$(?P<local_per_capita>[\d,]+)\s+"
        r"(?P<projects>[\d,]+)\s+"
        r"\$?\s*(?P<total>[\d,]+)\s+"
        r"\$(?P<total_per_capita>[\d,]+)$"
    )

    with pdfplumber.open(INPUT_PATH) as pdf:
        for page_index in [4, 5, 6]:
            text = pdf.pages[page_index].extract_text(x_tolerance=1, y_tolerance=3) or ""
            for line in text.splitlines():
                line = " ".join(line.strip().split())
                match = row_pattern.match(line)
                if not match:
                    continue

                county = normalize_county_name(match.group("county"))

                # Exclude non-county summary rows.
                if county not in TN_COUNTIES:
                    continue

                rows.append(
                    {
                        "county": county,
                        "tacir_2024_population": money_to_int(match.group("population")),
                        "regional_infrastructure_needs": money_to_int(match.group("regional")),
                        "local_infrastructure_needs": money_to_int(match.group("local")),
                        "local_infrastructure_needs_per_capita": money_to_int(match.group("local_per_capita")),
                        "infrastructure_project_count": money_to_int(match.group("projects")),
                        "total_infrastructure_needs": money_to_int(match.group("total")),
                        "infrastructure_needs_per_capita": money_to_int(match.group("total_per_capita")),
                    }
                )

    out = pd.DataFrame(rows)

    if out.empty:
        raise RuntimeError("No county rows were extracted from Table D-1a.")

    out = out.drop_duplicates(subset=["county"]).sort_values("county")

    missing = sorted(set(TN_COUNTIES) - set(out["county"]))
    if missing:
        raise RuntimeError(
            "Extracted table is missing counties: " + ", ".join(missing)
        )

    return out


def update_county_profile(infra: pd.DataFrame) -> None:
    if not COUNTY_PROFILE_PATH.exists():
        print(
            f"County profile file not found, so only wrote {OUTPUT_PATH}. "
            "Run prepare_county_profile_data.py first, then rerun this script to update it."
        )
        return

    profile = pd.read_csv(COUNTY_PROFILE_PATH)

    if "county" not in profile.columns:
        raise ValueError(f"{COUNTY_PROFILE_PATH} does not include a county column.")

    profile["county"] = profile["county"].apply(normalize_county_name)

    infra_cols = [
        "county",
        "total_infrastructure_needs",
        "infrastructure_needs_per_capita",
        "infrastructure_project_count",
        "regional_infrastructure_needs",
        "local_infrastructure_needs",
    ]

    profile = profile.drop(
        columns=[c for c in infra_cols if c != "county" and c in profile.columns],
        errors="ignore",
    )

    merged = profile.merge(infra[infra_cols], on="county", how="left")
    merged.to_csv(COUNTY_PROFILE_PATH, index=False)

    print(f"Updated county profile data with infrastructure fields: {COUNTY_PROFILE_PATH}")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    infra = extract_table_d1a()
    infra.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved TACIR infrastructure needs data to: {OUTPUT_PATH}")
    print(f"Rows: {len(infra)}")
    print(infra.head(10).to_string(index=False))

    update_county_profile(infra)


if __name__ == "__main__":
    main()
