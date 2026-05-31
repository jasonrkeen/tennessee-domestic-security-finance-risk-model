import csv
import re
from pathlib import Path

import pandas as pd

from src.config import RAW_DIR, TABLES_DIR


LAW_ENFORCEMENT_AMBUSH_RAW_INPUT = RAW_DIR / "tn_law_enforcement_ambush_raw_2024.csv"
LAW_ENFORCEMENT_AMBUSH_OUTPUT = RAW_DIR / "tn_law_enforcement_ambush_inputs.csv"
LAW_ENFORCEMENT_AMBUSH_SUMMARY_OUTPUT = TABLES_DIR / "tn_law_enforcement_ambush_summary.csv"
LAW_ENFORCEMENT_AMBUSH_MAPPING_OUTPUT = TABLES_DIR / "tn_law_enforcement_ambush_mapping_validation.csv"


def _normalize_county_name(value) -> str:
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


def _normalize_label(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _to_int(value) -> int:
    try:
        text = str(value).replace(",", "").strip()
        if not text:
            return 0
        return int(round(float(text)))
    except Exception:
        return 0


def _map_offense_label(label: str) -> str | None:
    """
    Map TBI/TNCrimeOnline Use of Force offense labels into county-level
    law-enforcement ambush fields.

    The source export is filtered to Officer Ambushed = Officer Was Ambushed.
    This is not a terrorism indicator by itself. It is treated as a narrow
    public-safety / tactical-planning proxy that may warrant further review
    when combined with other county-level indicators.
    """

    norm = _normalize_label(label)

    if norm in {
        "murder and nonnegligent manslaughter",
        "murder",
        "justifiable homicide",
    }:
        return "le_ambush_homicide_count"

    if "kidnapping" in norm or "abduction" in norm:
        return "le_ambush_kidnapping_abduction_count"

    if norm == "aggravated assault":
        return "le_ambush_aggravated_assault_count"

    if norm == "simple assault":
        return "le_ambush_simple_assault_count"

    if norm == "intimidation":
        return "le_ambush_intimidation_count"

    if "weapon law" in norm:
        return "le_ambush_weapon_law_violation_count"

    if norm == "arson":
        return "le_ambush_arson_count"

    if (
        "destruction" in norm
        or "damage" in norm
        or "vandalism" in norm
    ):
        return "le_ambush_property_damage_count"

    if any(
        phrase in norm
        for phrase in [
            "robbery",
            "burglary",
            "larceny",
            "theft",
            "motor vehicle theft",
            "stolen property",
        ]
    ):
        return "le_ambush_property_offense_count"

    if "drug" in norm or "narcotic" in norm:
        return "le_ambush_drug_offense_count"

    return None


def _read_raw_export(path: Path) -> list[list[str]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Law-enforcement ambush raw input not found: {path}\n"
            "Place the TBI/TNCrimeOnline Use of Force export at this path."
        )

    with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.reader(f))


def process_law_enforcement_ambush_file(
    input_path: str | Path = LAW_ENFORCEMENT_AMBUSH_RAW_INPUT,
) -> pd.DataFrame:
    """
    Process a TBI/TNCrimeOnline Use of Force Counts and Percent Change export
    filtered to Officer Ambushed = Officer Was Ambushed.

    Expected raw export structure:
    - Metadata rows at top.
    - Offense Committed row contains offense columns.
    - Officer Ambushed row confirms Officer Was Ambushed across offense columns.
    - Jurisdiction by Geography row appears before county rows.
    - County rows contain ambush-related counts by offense.

    Output is county-level aggregate only. The processor does not retain
    officer names, suspect details, incident IDs, addresses, agency-level
    tactical details, coordinates, narratives, or case-level records.
    """

    input_path = Path(input_path)
    rows = _read_raw_export(input_path)

    offense_row_idx = None
    ambush_row_idx = None
    county_start_idx = None

    for idx, row in enumerate(rows):
        first = row[0].strip() if row else ""

        if first == "Offense Committed":
            offense_row_idx = idx

        if first == "Officer Ambushed":
            ambush_row_idx = idx

        if first == "Jurisdiction by Geography":
            county_start_idx = idx + 1

    if offense_row_idx is None or ambush_row_idx is None or county_start_idx is None:
        raise ValueError(
            "Could not identify required header rows in the law-enforcement ambush export. "
            "Expected rows for Offense Committed, Officer Ambushed, and Jurisdiction by Geography."
        )

    offense_row = rows[offense_row_idx]
    ambush_row = rows[ambush_row_idx]

    offense_cols = []

    for col_idx in range(1, len(offense_row)):
        offense_label = offense_row[col_idx].strip()

        if not offense_label:
            continue

        ambush_flag = ambush_row[col_idx].strip() if col_idx < len(ambush_row) else ""

        if ambush_flag and ambush_flag != "Officer Was Ambushed":
            continue

        offense_cols.append((col_idx, offense_label, _map_offense_label(offense_label)))

    if not offense_cols:
        raise ValueError("No offense columns were found in the ambush export.")

    expected_output_cols = [
        "county",
        "le_ambush_total_count",
        "le_ambush_homicide_count",
        "le_ambush_kidnapping_abduction_count",
        "le_ambush_aggravated_assault_count",
        "le_ambush_simple_assault_count",
        "le_ambush_intimidation_count",
        "le_ambush_weapon_law_violation_count",
        "le_ambush_arson_count",
        "le_ambush_property_damage_count",
        "le_ambush_property_offense_count",
        "le_ambush_drug_offense_count",
        "le_ambush_other_offense_count",
    ]

    records = []
    mapping_records = []

    for row in rows[county_start_idx:]:
        if not row:
            continue

        county = _normalize_county_name(row[0])

        if not county:
            continue

        record = {"county": county}

        for col in expected_output_cols:
            if col != "county":
                record[col] = 0

        for col_idx, offense_label, mapped_field in offense_cols:
            value = _to_int(row[col_idx]) if col_idx < len(row) else 0

            if value == 0:
                continue

            record["le_ambush_total_count"] += value

            if mapped_field is not None:
                record[mapped_field] += value
            else:
                record["le_ambush_other_offense_count"] += value

        records.append(record)

    output = pd.DataFrame(records)

    if output.empty:
        raise ValueError("No county rows were parsed from the law-enforcement ambush file.")

    output = output[expected_output_cols].copy()

    numeric_cols = [col for col in expected_output_cols if col != "county"]

    for col in numeric_cols:
        output[col] = (
            pd.to_numeric(output[col], errors="coerce")
            .fillna(0)
            .round()
            .astype(int)
        )

    output = output.groupby("county", as_index=False)[numeric_cols].sum()
    output = output.sort_values("county")

    for _, offense_label, mapped_field in offense_cols:
        mapping_records.append(
            {
                "source_offense_label": offense_label,
                "normalized_offense_label": _normalize_label(offense_label),
                "mapped_model_field": mapped_field or "le_ambush_other_offense_count",
            }
        )

    mapping_df = (
        pd.DataFrame(mapping_records)
        .drop_duplicates()
        .sort_values(["mapped_model_field", "source_offense_label"])
    )

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    LAW_ENFORCEMENT_AMBUSH_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    output.to_csv(LAW_ENFORCEMENT_AMBUSH_OUTPUT, index=False)

    summary = output.sort_values("le_ambush_total_count", ascending=False).copy()
    summary.to_csv(LAW_ENFORCEMENT_AMBUSH_SUMMARY_OUTPUT, index=False)

    mapping_df.to_csv(LAW_ENFORCEMENT_AMBUSH_MAPPING_OUTPUT, index=False)

    print("\nTBI law-enforcement ambush input created:")
    print(f"- {LAW_ENFORCEMENT_AMBUSH_OUTPUT}")
    print(f"Output shape: {output.shape}")

    print("\nTop 10 counties by law-enforcement ambush count:")
    print(
        summary[
            [
                "county",
                "le_ambush_total_count",
                "le_ambush_aggravated_assault_count",
                "le_ambush_simple_assault_count",
                "le_ambush_intimidation_count",
                "le_ambush_weapon_law_violation_count",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print(f"\nMapping validation saved: {LAW_ENFORCEMENT_AMBUSH_MAPPING_OUTPUT}")

    return output


def main():
    process_law_enforcement_ambush_file()


if __name__ == "__main__":
    main()
