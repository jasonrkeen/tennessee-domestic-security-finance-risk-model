from pathlib import Path
import csv
import re

import pandas as pd

from src.config import RAW_DIR, TABLES_DIR


GANG_EXPLOSIVES_RAW_INPUT = RAW_DIR / "tn_gang_explosives_activity_raw_2024.csv"
GANG_EXPLOSIVES_OUTPUT = RAW_DIR / "tn_gang_explosives_activity_inputs.csv"

GANG_EXPLOSIVES_SUMMARY_OUTPUT = TABLES_DIR / "tn_gang_explosives_activity_summary.csv"
GANG_EXPLOSIVES_MAPPING_OUTPUT = (
    TABLES_DIR / "tn_gang_explosives_activity_mapping_validation.csv"
)


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


def _find_required_rows(rows: list[list[str]]) -> tuple[int, int, int, int, int, int]:
    """
    Locate key rows in a raw TNCrimeOnline matrix export.

    Expected structure may include:
    - Measures row
    - Gang Activity row
    - Incident Date row
    - Offense Type row
    - Type of Weapon/Force Involved row
    - Jurisdiction by Geography row
    """

    measures_idx = None
    gang_idx = None
    incident_idx = None
    offense_idx = None
    weapon_idx = None
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

        elif first == "type of weapon/force involved":
            weapon_idx = idx

        elif first == "jurisdiction by geography":
            jurisdiction_idx = idx

    if (
        measures_idx is None
        or offense_idx is None
        or weapon_idx is None
        or jurisdiction_idx is None
    ):
        raise ValueError(
            "Could not identify the raw TNCrimeOnline gang + explosives matrix "
            "structure. Expected rows for Measures, Offense Type, "
            "Type of Weapon/Force Involved, and Jurisdiction by Geography."
        )

    return (
        measures_idx,
        gang_idx,
        incident_idx,
        offense_idx,
        weapon_idx,
        jurisdiction_idx,
    )


def _identify_gang_explosive_number_of_crimes_columns(
    measures_row: list[str],
    offense_row: list[str],
    weapon_row: list[str],
) -> list[tuple[int, str, str]]:
    """
    Identify offense columns where:
    - Measure block is Number of Crimes
    - Weapon/force type is Explosives

    The file itself should already be filtered to Gang Activity = All Gang Activities.
    """

    columns = []
    current_measure = ""

    max_len = max(len(measures_row), len(offense_row), len(weapon_row))

    for idx in range(1, max_len):
        measure_value = measures_row[idx] if idx < len(measures_row) else ""
        offense_value = offense_row[idx] if idx < len(offense_row) else ""
        weapon_value = weapon_row[idx] if idx < len(weapon_row) else ""

        if str(measure_value).strip():
            current_measure = str(measure_value).strip()

        if current_measure.lower() != "number of crimes":
            continue

        if str(weapon_value).strip().lower() != "explosives":
            continue

        offense_label = str(offense_value).strip()

        if not offense_label:
            continue

        offense_key = _normalize_key(offense_label)
        columns.append((idx, offense_label, offense_key))

    if not columns:
        raise ValueError(
            "No gang-related explosive-use Number of Crimes columns were found."
        )

    return columns


def process_gang_explosives_activity_file(
    input_path: Path = GANG_EXPLOSIVES_RAW_INPUT,
) -> pd.DataFrame:
    """
    Process raw TBI/TNCrimeOnline gang + explosives export into county-level aggregates.

    The output is county-level only and does not include individual, event-level,
    address-level, suspect, victim, gang-name, organization, coordinates,
    incident IDs, narratives, or case-level details.

    Important:
    Gang-related explosive-use criminal activity is not a terrorism label. It is a
    high-severity organized/group criminal activity and explosive-use indicator that
    may justify further analysis when combined with other model layers.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Gang + explosives raw input file not found: {input_path}\n\n"
            "Save the TBI/TNCrimeOnline export as:\n"
            "data/raw/tn_gang_explosives_activity_raw_2024.csv"
        )

    with open(input_path, "r", encoding="utf-8-sig", errors="ignore", newline="") as file:
        rows = list(csv.reader(file))

    (
        measures_idx,
        gang_idx,
        incident_idx,
        offense_idx,
        weapon_idx,
        jurisdiction_idx,
    ) = _find_required_rows(rows)

    measures_row = rows[measures_idx]
    offense_row = rows[offense_idx]
    weapon_row = rows[weapon_idx]

    gang_explosive_cols = _identify_gang_explosive_number_of_crimes_columns(
        measures_row=measures_row,
        offense_row=offense_row,
        weapon_row=weapon_row,
    )

    county_rows = rows[jurisdiction_idx + 1 :]

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
            "gang_explosive_total_offense_count": 0.0,
            "gang_explosive_violent_offense_count": 0.0,
            "gang_explosive_weapon_law_violation_count": 0.0,
            "gang_explosive_drug_offense_count": 0.0,
            "gang_explosive_property_offense_count": 0.0,
            "gang_explosive_homicide_count": 0.0,
            "gang_explosive_kidnapping_abduction_count": 0.0,
            "gang_explosive_aggravated_assault_count": 0.0,
            "gang_explosive_robbery_count": 0.0,
            "gang_explosive_arson_count": 0.0,
            "gang_explosive_sex_offense_count": 0.0,
            "gang_explosive_property_damage_count": 0.0,
        }

        for col_idx, offense_label, offense_key in gang_explosive_cols:
            value = county_row[col_idx] if col_idx < len(county_row) else 0
            count = _safe_number(value)

            record["gang_explosive_total_offense_count"] += count

            if offense_key in VIOLENT_OFFENSES:
                record["gang_explosive_violent_offense_count"] += count

            if offense_key == "weaponlawviolations":
                record["gang_explosive_weapon_law_violation_count"] += count

            if offense_key in DRUG_OFFENSES:
                record["gang_explosive_drug_offense_count"] += count

            if offense_key in PROPERTY_OFFENSES:
                record["gang_explosive_property_offense_count"] += count

            if offense_key == "murder":
                record["gang_explosive_homicide_count"] += count

            if offense_key == "kidnappingabduction":
                record["gang_explosive_kidnapping_abduction_count"] += count

            if offense_key == "aggravatedassault":
                record["gang_explosive_aggravated_assault_count"] += count

            if offense_key == "robbery":
                record["gang_explosive_robbery_count"] += count

            if offense_key == "arson":
                record["gang_explosive_arson_count"] += count

            if offense_key in SEX_OFFENSES:
                record["gang_explosive_sex_offense_count"] += count

            if offense_key == "destructiondamagevandalism":
                record["gang_explosive_property_damage_count"] += count

        records.append(record)

    output = pd.DataFrame(records)

    if output.empty:
        raise ValueError("No county records were parsed from the gang + explosives file.")

    numeric_cols = [col for col in output.columns if col != "county"]

    for col in numeric_cols:
        output[col] = pd.to_numeric(output[col], errors="coerce").fillna(0)

    output = output.sort_values("county").copy()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    output.to_csv(GANG_EXPLOSIVES_OUTPUT, index=False)

    summary = output.sort_values(
        "gang_explosive_total_offense_count",
        ascending=False,
    ).copy()

    summary.to_csv(GANG_EXPLOSIVES_SUMMARY_OUTPUT, index=False)

    for col_idx, offense_label, offense_key in gang_explosive_cols:
        mapping_records.append(
            {
                "source_offense_label": offense_label,
                "normalized_offense_label": offense_key,
                "gang_activity_filter": "All Gang Activities",
                "weapon_force_filter": "Explosives",
                "used_in_total_gang_explosive_offenses": True,
                "violent_offense_bucket": offense_key in VIOLENT_OFFENSES,
                "weapon_offense_bucket": offense_key == "weaponlawviolations",
                "drug_offense_bucket": offense_key in DRUG_OFFENSES,
                "property_offense_bucket": offense_key in PROPERTY_OFFENSES,
                "sex_offense_bucket": offense_key in SEX_OFFENSES,
                "property_damage_bucket": offense_key == "destructiondamagevandalism",
            }
        )

    mapping_df = pd.DataFrame(mapping_records).drop_duplicates()
    mapping_df.to_csv(GANG_EXPLOSIVES_MAPPING_OUTPUT, index=False)

    print("\nGang + explosives activity county input created:")
    print(f"- {GANG_EXPLOSIVES_OUTPUT}")
    print(f"- {GANG_EXPLOSIVES_SUMMARY_OUTPUT}")
    print(f"- {GANG_EXPLOSIVES_MAPPING_OUTPUT}")

    print("\nTop 10 counties by gang-related explosive-use total offense count:")
    print(
        output.sort_values("gang_explosive_total_offense_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    return output


def main():
    process_gang_explosives_activity_file()


if __name__ == "__main__":
    main()