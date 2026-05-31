"""
Prepare county-level healthcare / emergency capacity data for the operational-risk layer.

Input:
    data/raw/tn-health-care-capacity-dashboard-data-download.xlsx

Output:
    data/raw/tn_county_healthcare_capacity.csv

Source workbook structure expected:
    - Hospital sheet
    - Primary Care sheet

Responsible-use boundary:
    - County-level aggregation only
    - No facility names
    - No street addresses
    - No coordinates
    - No target-level or route-level detail

Fields created for operational_risk_features.py:
    county
    hospital_beds_per_100k
    emergency_department_count
    primary_care_rate
    trauma_access_proxy
"""

from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

INPUT_PATH = RAW_DIR / "tn-health-care-capacity-dashboard-data-download.xlsx"
OUTPUT_PATH = RAW_DIR / "tn_county_healthcare_capacity.csv"

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
    value = value.replace(" County", "").replace(" county", "")
    value = value.replace(".", "")
    value = " ".join(value.split())
    return COUNTY_LOOKUP.get(value.lower(), value.title())


def to_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False),
        errors="coerce",
    )


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input workbook: {INPUT_PATH}\n"
            "Save the Sycamore/Tennessee health care capacity workbook to "
            "data/raw/tn-health-care-capacity-dashboard-data-download.xlsx"
        )

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    hospital = pd.read_excel(INPUT_PATH, sheet_name="Hospital")
    primary = pd.read_excel(INPUT_PATH, sheet_name="Primary Care")

    hospital = hospital.loc[:, ~hospital.columns.duplicated()].copy()
    primary = primary.loc[:, ~primary.columns.duplicated()].copy()

    # Remove statewide total rows and preserve only Tennessee counties.
    hospital["county"] = hospital["County"].apply(normalize_county_name)
    primary["county"] = primary["County"].apply(normalize_county_name)
    hospital = hospital[hospital["county"].isin(TN_COUNTIES)].copy()
    primary = primary[primary["county"].isin(TN_COUNTIES)].copy()

    hospital["population_2017"] = to_num(hospital["Population\n(2017)"])
    hospital["staffed_inpatient_beds"] = to_num(hospital["Staffed Inpatient Beds (2017)"])
    hospital["emergency_department_count"] = to_num(hospital["Total Emergency Departments (2019)"])
    hospital["hospital_count"] = to_num(hospital["Hospitals (2019)"])
    hospital["general_surgeons"] = to_num(hospital["General Surgeons (2016)"])

    hospital["hospital_beds_per_100k"] = (
        hospital["staffed_inpatient_beds"] / hospital["population_2017"] * 100000
    )
    hospital["general_surgeons_per_100k"] = (
        hospital["general_surgeons"] / hospital["population_2017"] * 100000
    )
    hospital["emergency_departments_per_100k"] = (
        hospital["emergency_department_count"] / hospital["population_2017"] * 100000
    )

    # This is not a trauma-center locator. It is a county-level proxy combining
    # general-surgeon availability and emergency department presence.
    hospital["trauma_access_proxy"] = (
        hospital["general_surgeons_per_100k"].fillna(0) * 0.70
        + hospital["emergency_departments_per_100k"].fillna(0) * 0.30
    )

    primary["population_2017"] = to_num(primary["Population\n(2017)"])
    primary["primary_care_physicians"] = to_num(primary["Primary Care Physicians\n(2016)"])
    primary["pa_np_count"] = to_num(primary["Physician Assistants/ Nurse Practitioners\n(2017)"])
    primary["primary_care_rate"] = (
        primary["primary_care_physicians"] / primary["population_2017"] * 100000
    )
    primary["pa_np_rate_per_100k"] = primary["pa_np_count"] / primary["population_2017"] * 100000

    out = hospital[
        [
            "county",
            "hospital_beds_per_100k",
            "emergency_department_count",
            "trauma_access_proxy",
            "population_2017",
            "hospital_count",
            "staffed_inpatient_beds",
            "general_surgeons",
            "general_surgeons_per_100k",
        ]
    ].merge(
        primary[
            [
                "county",
                "primary_care_rate",
                "primary_care_physicians",
                "pa_np_count",
                "pa_np_rate_per_100k",
            ]
        ],
        on="county",
        how="left",
    )

    out = out[
        [
            "county",
            "hospital_beds_per_100k",
            "emergency_department_count",
            "primary_care_rate",
            "trauma_access_proxy",
            "population_2017",
            "hospital_count",
            "staffed_inpatient_beds",
            "general_surgeons",
            "general_surgeons_per_100k",
            "primary_care_physicians",
            "pa_np_count",
            "pa_np_rate_per_100k",
        ]
    ].sort_values("county")

    out.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved county healthcare capacity context to: {OUTPUT_PATH}")
    print(f"Rows: {len(out)}")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
