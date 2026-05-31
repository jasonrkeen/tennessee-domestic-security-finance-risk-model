import csv
import re
from pathlib import Path

import pandas as pd

from src.config import RAW_DIR, TABLES_DIR


HATE_CRIME_RAW_INPUT = RAW_DIR / "tn_hate_crime_offense_raw_2024.csv"
HATE_CRIME_OUTPUT = RAW_DIR / "tn_hate_crime_offense_inputs.csv"
HATE_CRIME_SUMMARY_OUTPUT = TABLES_DIR / "tn_hate_crime_offense_summary.csv"
HATE_CRIME_MAPPING_OUTPUT = TABLES_DIR / "tn_hate_crime_offense_mapping_validation.csv"


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
    Map TBI/TNCrimeOnline offense labels into county-level hate-crime fields.

    Notes:
    - This is an aggregate county-level processor.
    - The raw export is filtered to Bias Motivation = All Hate Crimes.
    - The output does not retain victim, suspect, incident, address, agency,
      bias-detail, narrative, or case-level records.
    """

    norm = _normalize_label(label)

    if norm in {"murder", "murder and nonnegligent manslaughter"}:
        return "hate_crime_homicide_count"

    if "kidnapping" in norm or "abduction" in norm:
        return "hate_crime_kidnapping_abduction_count"

    if norm in {
        "all rape",
        "criminal sexual contact",
        "incest",
        "statutory rape",
    }:
        return "hate_crime_sex_offense_count"

    if norm == "aggravated assault":
        return "hate_crime_aggravated_assault_count"

    if norm == "simple assault":
        return "hate_crime_simple_assault_count"

    if norm == "intimidation":
        return "hate_crime_intimidation_count"

    if norm == "arson":
        return "hate_crime_arson_count"

    if "weapon law" in norm:
        return "hate_crime_weapon_law_violation_count"

    if (
        "destruction" in norm
        or "damage" in norm
        or "vandalism" in norm
    ):
        return "hate_crime_property_damage_count"

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
        return "hate_crime_property_offense_count"

    return None


def _read_raw_export(path: Path) -> list[list[str]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Hate-crime raw input not found: {path}\n"
            "Place the TBI/TNCrimeOnline hate-crime export at this path."
        )

    with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.reader(f))


def process_hate_crime_offense_file(
    input_path: str | Path = HATE_CRIME_RAW_INPUT,
) -> pd.DataFrame:
    """
    Process a TBI/TNCrimeOnline Crimes and Clearances by Offense Type export
    filtered to Bias Motivation = All Hate Crimes.

    Expected raw export structure:
    - Metadata rows at top.
    - Incident Clearance row includes All Clearances and Cleared blocks.
    - Bias Motivation row includes All Hate Crimes.
    - Jurisdiction by Geography row contains county columns.
    - Offense Type rows contain offense counts by county.

    This processor uses the All Clearances block by default because it is the
    broadest count of hate-crime offenses, not just cleared offenses.
    Output is county-level aggregate only. The processor does not retain
    victim details, suspect details, incident IDs, addresses, agency-level
    details, bias-detail notes, coordinates, narratives, or case-level records.
    """

    input_path = Path(input_path)
    rows = _read_raw_export(input_path)

    clearance_row_idx = None
    county_row_idx = None
    offense_header_idx = None

    for idx, row in enumerate(rows):
        first = row[0].strip() if row else ""

        if first == "Incident Clearance":
            clearance_row_idx = idx

        if first == "Jurisdiction by Geography":
            county_row_idx = idx

        if first == "Offense Type":
            offense_header_idx = idx

    if clearance_row_idx is None or county_row_idx is None or offense_header_idx is None:
        raise ValueError(
            "Could not identify required header rows in the hate-crime export. "
            "Expected rows for Incident Clearance, Jurisdiction by Geography, and Offense Type."
        )

    clearance_row = rows[clearance_row_idx]
    county_row = rows[county_row_idx]

    # Use the first county block after "All Clearances".
    # The second block usually begins at the "Cleared" column.
    all_clearances_start = 1
    cleared_start = None

    for col_idx, value in enumerate(clearance_row):
        if str(value).strip().lower() == "cleared":
            cleared_start = col_idx
            break

    if cleared_start is None:
        cleared_start = len(county_row)

    county_cols = []
    for col_idx in range(all_clearances_start, min(cleared_start, len(county_row))):
        county = _normalize_county_name(county_row[col_idx])

        if not county:
            continue

        county_cols.append((col_idx, county))

    if not county_cols:
        raise ValueError("No county columns were found in the All Clearances block.")

    expected_output_cols = [
        "county",
        "hate_crime_total_count",
        "hate_crime_homicide_count",
        "hate_crime_kidnapping_abduction_count",
        "hate_crime_sex_offense_count",
        "hate_crime_aggravated_assault_count",
        "hate_crime_simple_assault_count",
        "hate_crime_intimidation_count",
        "hate_crime_arson_count",
        "hate_crime_weapon_law_violation_count",
        "hate_crime_property_damage_count",
        "hate_crime_property_offense_count",
        "hate_crime_other_offense_count",
    ]

    records_by_county = {
        county: {col: 0 for col in expected_output_cols if col != "county"}
        for _, county in county_cols
    }

    mapping_records = []
    unmapped_records = []

    for row in rows[offense_header_idx + 1:]:
        if not row:
            continue

        offense_label = row[0].strip()

        if not offense_label:
            continue

        mapped_field = _map_offense_label(offense_label)

        row_total = 0

        for col_idx, county in county_cols:
            value = _to_int(row[col_idx]) if col_idx < len(row) else 0

            if value == 0:
                continue

            records_by_county[county]["hate_crime_total_count"] += value
            row_total += value

            if mapped_field is not None:
                records_by_county[county][mapped_field] += value
            else:
                records_by_county[county]["hate_crime_other_offense_count"] += value

        if mapped_field is not None:
            mapping_records.append(
                {
                    "source_offense_label": offense_label,
                    "normalized_offense_label": _normalize_label(offense_label),
                    "mapped_model_field": mapped_field,
                    "total_count": row_total,
                }
            )
        elif row_total > 0:
            unmapped_records.append(
                {
                    "source_offense_label": offense_label,
                    "normalized_offense_label": _normalize_label(offense_label),
                    "mapped_model_field": "hate_crime_other_offense_count",
                    "total_count": row_total,
                }
            )

    output = pd.DataFrame(
        [{"county": county, **values} for county, values in records_by_county.items()]
    )

    output = output[expected_output_cols].copy()

    numeric_cols = [col for col in expected_output_cols if col != "county"]

    for col in numeric_cols:
        output[col] = (
            pd.to_numeric(output[col], errors="coerce")
            .fillna(0)
            .round()
            .astype(int)
        )

    output = output.sort_values("county")

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    HATE_CRIME_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    output.to_csv(HATE_CRIME_OUTPUT, index=False)

    summary = output.sort_values("hate_crime_total_count", ascending=False).copy()
    summary.to_csv(HATE_CRIME_SUMMARY_OUTPUT, index=False)

    mapping_df = pd.DataFrame(mapping_records + unmapped_records)
    if not mapping_df.empty:
        mapping_df = mapping_df.sort_values(
            ["mapped_model_field", "source_offense_label"]
        )
    mapping_df.to_csv(HATE_CRIME_MAPPING_OUTPUT, index=False)

    print("\nTBI hate-crime offense input created:")
    print(f"- {HATE_CRIME_OUTPUT}")
    print(f"Output shape: {output.shape}")

    print("\nTop 10 counties by hate-crime offense count:")
    print(
        summary[
            [
                "county",
                "hate_crime_total_count",
                "hate_crime_intimidation_count",
                "hate_crime_simple_assault_count",
                "hate_crime_aggravated_assault_count",
                "hate_crime_property_damage_count",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print(f"\nMapping validation saved: {HATE_CRIME_MAPPING_OUTPUT}")

    return output


def main():
    process_hate_crime_offense_file()


if __name__ == "__main__":
    main()
