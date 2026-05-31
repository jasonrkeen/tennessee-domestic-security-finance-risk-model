from pathlib import Path
import csv
import re

import pandas as pd

from src.config import RAW_DIR, TABLES_DIR


GANG_RAW_INPUT = RAW_DIR / "tn_gang_activity_raw_2024.csv"
GANG_OUTPUT = RAW_DIR / "tn_gang_activity_inputs.csv"

GANG_SUMMARY_OUTPUT = TABLES_DIR / "tn_gang_activity_summary.csv"
GANG_MAPPING_OUTPUT = TABLES_DIR / "tn_gang_activity_mapping_validation.csv"


VIOLENT_OFFENSES = {
    "murder",
    "negligentmanslaughter",
    "kidnappingabduction",
    "allrape",
    "criminalsexualcontact",
    "incest",
    "statutoryrape",
    "aggravatedassault",
    "robbery",
}

SEX_OFFENSES = {
    "allrape",
    "criminalsexualcontact",
    "incest",
    "statutoryrape",
}

PROPERTY_OFFENSES = {
    "arson",
    "burglary",
    "counterfeitingforgery",
    "destructiondamagevandalism",
    "embezzlement",
    "extortionblackmail",
    "fraudfalsepretenses",
    "fraudcreditcardatm",
    "fraudimpersonation",
    "fraudwelfare",
    "fraudwire",
    "fraudidentitytheft",
    "fraudcomputerhackinginvasion",
    "theftpocketpicking",
    "theftpursesnatching",
    "theftshoplifting",
    "theftfrombuilding",
    "theftfromcoinmachine",
    "theftfrommotorvehicle",
    "theftofmotorvehicleparts",
    "theftallotherlarceny",
    "motorvehicletheft",
    "stolenpropertyoffenses",
}

DRUG_OFFENSES = {
    "drugnarcoticviolations",
    "drugnarcoticequipmentviolations",
}


def _normalize_key(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    return re.sub(r"[^a-z0-9]", "", text)


def _normalize_county(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()

    text = (
        text.replace(" County", "")
        .replace(" county", "")
        .replace(", Tennessee", "")
        .replace(", TN", "")
        .strip()
    )

    return text


def _safe_number(value) -> float:
    if pd.isna(value):
        return 0.0

    text = str(value).strip().replace(",", "")

    if text == "":
        return 0.0

    try:
        return float(text)
    except Exception:
        return 0.0


def _find_required_rows(rows: list[list[str]]) -> tuple[int, int | None, int | None, int, int]:
    """
    Locate key rows in a raw TNCrimeOnline matrix export.

    Expected structure:
    - Measures row
    - Gang Activity row
    - Incident Date row
    - Offense Type row
    - Jurisdiction by Geography row

    The Gang Activity and Incident Date rows are useful for validation but are not
    required for parsing the county-level aggregate output.
    """

    measures_idx = None
    gang_idx = None
    incident_idx = None
    offense_idx = None
    jurisdiction_idx = None

    for idx, row in enumerate(rows):
        if not row:
            continue

        first = str(row[0]).strip().lower()

        if first == "measures":
            measures_idx = idx

        elif first == "gang activity":
            gang_idx = idx

        elif first == "incident date":
            incident_idx = idx

        elif first == "offense type":
            offense_idx = idx

        elif first == "jurisdiction by geography":
            jurisdiction_idx = idx

    if measures_idx is None or offense_idx is None or jurisdiction_idx is None:
        raise ValueError(
            "Could not identify the raw TNCrimeOnline matrix structure. "
            "Expected rows for Measures, Offense Type, and Jurisdiction by Geography."
        )

    return measures_idx, gang_idx, incident_idx, offense_idx, jurisdiction_idx


def _identify_number_of_crimes_columns(
    measures_row: list[str],
    offense_row: list[str],
) -> list[tuple[int, str, str]]:
    """
    Identify the offense columns that belong to the Number of Crimes measure block.

    The export includes repeated offense columns for Number of Crimes and Number of Offenses.
    This model uses Number of Crimes for county-level aggregate scoring.
    """

    columns = []
    current_measure = ""

    max_len = max(len(measures_row), len(offense_row))

    for idx in range(1, max_len):
        measure_value = measures_row[idx] if idx < len(measures_row) else ""
        offense_value = offense_row[idx] if idx < len(offense_row) else ""

        if str(measure_value).strip():
            current_measure = str(measure_value).strip()

        if current_measure.lower() != "number of crimes":
            continue

        offense_label = str(offense_value).strip()

        if not offense_label:
            continue

        offense_key = _normalize_key(offense_label)
        columns.append((idx, offense_label, offense_key))

    if not columns:
        raise ValueError("No Number of Crimes offense columns were found.")

    return columns


def process_gang_activity_file(input_path: Path = GANG_RAW_INPUT) -> pd.DataFrame:
    """
    Process raw TBI/TNCrimeOnline gang activity export into county-level aggregates.

    The output is county-level only and does not include individual, event-level,
    address-level, gang-name, organization-name, suspect, victim, coordinates,
    incident IDs, narratives, or case-level detail.

    Gang-related criminal activity is not a terrorism label. It is treated as an
    organized/group criminal activity pressure indicator that may warrant further
    review when combined with other model layers.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Gang activity raw input file not found: {input_path}\n\n"
            "Save the TBI/TNCrimeOnline export as:\n"
            "data/raw/tn_gang_activity_raw_2024.csv"
        )

    with open(input_path, "r", encoding="utf-8-sig", errors="ignore", newline="") as file:
        rows = list(csv.reader(file))

    measures_idx, gang_idx, incident_idx, offense_idx, jurisdiction_idx = (
        _find_required_rows(rows)
    )

    measures_row = rows[measures_idx]
    offense_row = rows[offense_idx]

    number_of_crimes_cols = _identify_number_of_crimes_columns(
        measures_row=measures_row,
        offense_row=offense_row,
    )

    county_rows = rows[jurisdiction_idx + 1:]

    records = []
    mapping_records = []

    for county_row in county_rows:
        if not county_row:
            continue

        county = _normalize_county(county_row[0])
        county_key = _normalize_key(county)

        if county_key in {
            "",
            "total",
            "totals",
            "statewide",
            "tennessee",
            "unknown",
            "nan",
        }:
            continue

        record = {
            "county": county,
            "gang_related_total_crime_count": 0.0,
            "gang_related_violent_crime_count": 0.0,
            "gang_related_weapon_law_violation_count": 0.0,
            "gang_related_drug_offense_count": 0.0,
            "gang_related_property_offense_count": 0.0,
            "gang_related_homicide_count": 0.0,
            "gang_related_kidnapping_abduction_count": 0.0,
            "gang_related_aggravated_assault_count": 0.0,
            "gang_related_robbery_count": 0.0,
            "gang_related_arson_count": 0.0,
            "gang_related_sex_offense_count": 0.0,
        }

        for col_idx, offense_label, offense_key in number_of_crimes_cols:
            value = county_row[col_idx] if col_idx < len(county_row) else 0
            count = _safe_number(value)

            record["gang_related_total_crime_count"] += count

            if offense_key in VIOLENT_OFFENSES:
                record["gang_related_violent_crime_count"] += count

            if offense_key == "weaponlawviolations":
                record["gang_related_weapon_law_violation_count"] += count

            if offense_key in DRUG_OFFENSES:
                record["gang_related_drug_offense_count"] += count

            if offense_key in PROPERTY_OFFENSES:
                record["gang_related_property_offense_count"] += count

            if offense_key == "murder":
                record["gang_related_homicide_count"] += count

            if offense_key == "kidnappingabduction":
                record["gang_related_kidnapping_abduction_count"] += count

            if offense_key == "aggravatedassault":
                record["gang_related_aggravated_assault_count"] += count

            if offense_key == "robbery":
                record["gang_related_robbery_count"] += count

            if offense_key == "arson":
                record["gang_related_arson_count"] += count

            if offense_key in SEX_OFFENSES:
                record["gang_related_sex_offense_count"] += count

        records.append(record)

    output = pd.DataFrame(records)

    if output.empty:
        raise ValueError(
            "No county records were parsed from the gang activity file. "
            "Check that the export includes county rows below the "
            "'Jurisdiction by Geography' row."
        )

    numeric_cols = [col for col in output.columns if col != "county"]

    for col in numeric_cols:
        output[col] = pd.to_numeric(output[col], errors="coerce").fillna(0)

    output = (
        output.groupby("county", as_index=False)[numeric_cols]
        .sum()
        .sort_values("county")
        .copy()
    )

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    output.to_csv(GANG_OUTPUT, index=False)

    summary = output.sort_values(
        "gang_related_total_crime_count",
        ascending=False,
    ).copy()

    summary.to_csv(GANG_SUMMARY_OUTPUT, index=False)

    for col_idx, offense_label, offense_key in number_of_crimes_cols:
        mapping_records.append(
            {
                "source_offense_label": offense_label,
                "normalized_offense_label": offense_key,
                "gang_activity_filter": "All Gang Activities",
                "used_in_total_gang_crime": True,
                "violent_offense_bucket": offense_key in VIOLENT_OFFENSES,
                "weapon_offense_bucket": offense_key == "weaponlawviolations",
                "drug_offense_bucket": offense_key in DRUG_OFFENSES,
                "property_offense_bucket": offense_key in PROPERTY_OFFENSES,
                "sex_offense_bucket": offense_key in SEX_OFFENSES,
            }
        )

    mapping_df = pd.DataFrame(mapping_records).drop_duplicates()
    mapping_df.to_csv(GANG_MAPPING_OUTPUT, index=False)

    print("\nGang activity county input created:")
    print(f"- {GANG_OUTPUT}")
    print(f"- {GANG_SUMMARY_OUTPUT}")
    print(f"- {GANG_MAPPING_OUTPUT}")

    print("\nTop 10 counties by gang-related total crime count:")
    print(
        output.sort_values("gang_related_total_crime_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    return output


def main():
    process_gang_activity_file()


if __name__ == "__main__":
    main()
