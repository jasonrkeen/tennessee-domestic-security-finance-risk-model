from pathlib import Path
import csv
import re

import pandas as pd

from src.config import RAW_DIR, TABLES_DIR


OUTPUT_FILE = RAW_DIR / "tn_crime_weapons_inputs.csv"
VALIDATION_OUTPUT_FILE = TABLES_DIR / "crime_offense_label_mapping_validation.csv"
UNMAPPED_OUTPUT_FILE = TABLES_DIR / "crime_offense_unmapped_labels.csv"


def _to_number(value):
    if value is None:
        return 0

    text = str(value).replace(",", "").strip()

    if text == "":
        return 0

    try:
        return int(float(text))
    except Exception:
        return 0


def _normalize_county(value):
    if pd.isna(value):
        return ""

    text = str(value)
    text = (
        text.replace(" County", "")
        .replace(" county", "")
        .replace(", Tennessee", "")
        .replace(", TN", "")
        .strip()
    )

    return text


def _normalize_key(value):
    text = _normalize_county(value).lower()
    return re.sub(r"[^a-z0-9]", "", text)


def _normalize_label(value):
    """
    Normalize offense labels from CrimeInsight / TNCrimeOnline exports.
    """

    if value is None:
        return ""

    text = str(value).strip().lower()
    text = text.replace("&", "and")
    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = text.replace(",", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _load_acs_county_base() -> pd.DataFrame:
    """
    Use the ACS county file as the canonical Tennessee county list.
    """

    acs_path = RAW_DIR.parent / "processed" / "tn_acs_county_data.csv"

    if not acs_path.exists():
        raise FileNotFoundError(
            "Could not find processed ACS county file. Run python main.py once first:\n"
            f"{acs_path}"
        )

    county_base = pd.read_csv(acs_path)

    if "county" not in county_base.columns:
        raise ValueError("tn_acs_county_data.csv must include a county column.")

    county_base = county_base[["county"]].copy()
    county_base["county"] = county_base["county"].astype(str).str.strip()
    county_base["county_key"] = county_base["county"].apply(_normalize_key)

    return county_base.drop_duplicates(subset=["county_key"])


def _find_matrix_rows(rows: list[list[str]]) -> tuple[int, int | None, int]:
    """
    Locate key rows in a TNCrimeOnline / CrimeInsight matrix export.

    Returns:
        geography_idx, measures_idx, offense_type_idx

    Expected rows may include:
    - Jurisdiction by Geography
    - Measures
    - Offense Type

    This is more defensive than assuming fixed row positions.
    """

    geography_idx = None
    measures_idx = None
    offense_type_idx = None

    for idx, row in enumerate(rows[:50]):
        if not row:
            continue

        first = str(row[0]).strip().lower()

        if first == "jurisdiction by geography":
            geography_idx = idx

        elif first == "measures":
            measures_idx = idx

        elif first == "offense type":
            offense_type_idx = idx

    if geography_idx is None:
        geography_idx = _find_geography_row_by_county_matches(rows)

    if offense_type_idx is None:
        raise ValueError(
            "Could not identify the Offense Type row. "
            "Open the CSV and confirm the export includes offense rows."
        )

    return geography_idx, measures_idx, offense_type_idx


def _find_geography_row_by_county_matches(rows: list[list[str]]) -> int:
    """
    Fallback geography row detector.

    Looks for the row containing the greatest number of Tennessee county names.
    """

    county_base = _load_acs_county_base()
    county_keys = set(county_base["county_key"].tolist())

    best_idx = None
    best_matches = 0

    for idx, row in enumerate(rows[:50]):
        normalized_values = {_normalize_key(cell) for cell in row if str(cell).strip()}
        matches = len(normalized_values.intersection(county_keys))

        if matches > best_matches:
            best_matches = matches
            best_idx = idx

    if best_idx is None or best_matches < 5:
        raise ValueError(
            "Could not automatically identify the geography/header row. "
            "Open the CSV and confirm which row contains county names."
        )

    return best_idx


def _identify_county_value_columns(
    geography_row: list[str],
    measures_row: list[str] | None,
) -> list[tuple[str, int]]:
    """
    Identify county columns to read.

    If a Measures row exists, use only columns where the active measure is
    Number of Crimes. This avoids accidentally reading crime rates or clearance
    percentages if those are included in the export.

    If no Measures row exists, fall back to the first visible county column.
    """

    county_base = _load_acs_county_base()
    valid_county_keys = set(county_base["county_key"].tolist())

    columns = []
    current_county = ""
    current_measure = ""

    max_len = len(geography_row)

    if measures_row is not None:
        max_len = max(max_len, len(measures_row))

    for idx in range(1, max_len):
        geography_value = geography_row[idx] if idx < len(geography_row) else ""
        measure_value = measures_row[idx] if measures_row is not None and idx < len(measures_row) else ""

        if str(geography_value).strip():
            possible_county = _normalize_county(geography_value)
            possible_key = _normalize_key(possible_county)

            if possible_key in valid_county_keys:
                current_county = possible_county

        if str(measure_value).strip():
            current_measure = str(measure_value).strip().lower()

        if not current_county:
            continue

        if measures_row is not None:
            if current_measure == "number of crimes":
                columns.append((current_county, idx))
        else:
            if str(geography_value).strip():
                columns.append((current_county, idx))

    if not columns:
        raise ValueError(
            "No county Number of Crimes columns were found. "
            "Check whether the export includes a Measures row and county headers."
        )

    return columns


def _offense_map() -> dict[str, str]:
    """
    Map normalized CrimeInsight offense labels to model input columns.

    Supports exact labels and common TIBRS / CrimeInsight naming variations.
    """

    return {
        # Homicide / murder
        "murder": "homicide_count",
        "homicide": "homicide_count",
        "murder and nonnegligent manslaughter": "homicide_count",
        "murder nonnegligent manslaughter": "homicide_count",
        "murder non negligent manslaughter": "homicide_count",

        # Kidnapping
        "kidnapping abduction": "kidnapping_abduction_count",
        "kidnapping": "kidnapping_abduction_count",
        "abduction": "kidnapping_abduction_count",

        # Weapon law violations
        "weapon law violations": "weapons_law_violation_count",
        "weapons law violations": "weapons_law_violation_count",
        "weapon law violation": "weapons_law_violation_count",

        # Violent crime / assault
        "violent crime": "violent_crime_count",
        "aggravated assault": "aggravated_assault_count",

        # Arson
        "arson": "arson_count",

        # Sex offense naming variations
        "sex offenses": "sex_offense_count",
        "sex offense": "sex_offense_count",
        "sex offenses non consensual": "sex_offense_count",
        "sex offenses nonconsensual": "sex_offense_count",
        "non consensual sex offenses": "sex_offense_count",
        "nonconsensual sex offenses": "sex_offense_count",
        "all rape": "sex_offense_count",
        "rape": "sex_offense_count",
        "forcible rape": "sex_offense_count",
        "sodomy": "sex_offense_count",
        "forcible sodomy": "sex_offense_count",
        "sexual assault w object": "sex_offense_count",
        "sexual assault with object": "sex_offense_count",
        "forcible fondling": "sex_offense_count",
        "fondling": "sex_offense_count",
        "statutory rape": "sex_offense_count",
        "incest": "sex_offense_count",
        "criminal sexual contact": "sex_offense_count",

        # Future / optional categories
        "hate crime": "hate_crime_count",
        "law enforcement assault": "law_enforcement_assault_count",
        "assault on law enforcement": "law_enforcement_assault_count",
    }


def _map_offense_label(label: str) -> str | None:
    """
    Map exact and partial CrimeInsight offense labels to model columns.
    """

    normalized = _normalize_label(label)
    label_map = _offense_map()

    if normalized in label_map:
        return label_map[normalized]

    sex_keywords = [
        "sex offense",
        "sex offenses",
        "non consensual",
        "nonconsensual",
        "rape",
        "sodomy",
        "fondling",
        "sexual assault",
        "sexual contact",
        "incest",
    ]

    if any(keyword in normalized for keyword in sex_keywords):
        return "sex_offense_count"

    if "weapon" in normalized and "law" in normalized:
        return "weapons_law_violation_count"

    if "aggravated" in normalized and "assault" in normalized:
        return "aggravated_assault_count"

    if "kidnapping" in normalized or "abduction" in normalized:
        return "kidnapping_abduction_count"

    if "murder" in normalized or "homicide" in normalized:
        return "homicide_count"

    if "arson" in normalized:
        return "arson_count"

    if "hate" in normalized and "crime" in normalized:
        return "hate_crime_count"

    if "law enforcement" in normalized and "assault" in normalized:
        return "law_enforcement_assault_count"

    return None


def _save_label_validation_outputs(
    long_df: pd.DataFrame,
    unmapped_labels: set[str],
) -> None:
    """
    Save mapping-validation outputs for report transparency.
    """

    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    mapping_validation = (
        long_df.groupby(["source_offense_label", "metric"], as_index=False)
        .agg(total_count=("value", "sum"))
        .sort_values(["metric", "source_offense_label"])
    )

    mapping_validation["normalized_offense_label"] = mapping_validation[
        "source_offense_label"
    ].apply(_normalize_label)

    mapping_validation = mapping_validation[
        [
            "source_offense_label",
            "normalized_offense_label",
            "metric",
            "total_count",
        ]
    ].copy()

    mapping_validation.to_csv(VALIDATION_OUTPUT_FILE, index=False)

    unmapped_output = pd.DataFrame(
        {
            "unmapped_offense_label": sorted(unmapped_labels),
            "normalized_unmapped_label": [
                _normalize_label(label) for label in sorted(unmapped_labels)
            ],
        }
    )

    unmapped_output.to_csv(UNMAPPED_OUTPUT_FILE, index=False)


def process_crime_offense_file(input_path: str | Path) -> pd.DataFrame:
    """
    Process a TBI CrimeInsight / TNCrimeOnline Crimes and Clearances by Offense Type CSV.

    Output:
        data/raw/tn_crime_weapons_inputs.csv
        outputs/tables/crime_offense_label_mapping_validation.csv
        outputs/tables/crime_offense_unmapped_labels.csv

    Notes:
    - Keeps county-level aggregate values only.
    - Does not preserve agency-level, incident-level, victim-level,
      suspect-level, address, coordinate, narrative, or case-level records.
    - Crime/weapons counts are public-safety pressure proxies and should not be
      interpreted as terrorism, extremism, or illicit-finance indicators by themselves.
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Crime offense input file not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8-sig", errors="replace") as f:
        rows = list(csv.reader(f))

    if len(rows) < 5:
        raise ValueError("Crime offense file does not have the expected row structure.")

    geography_idx, measures_idx, offense_type_idx = _find_matrix_rows(rows)

    geography_row = rows[geography_idx]
    measures_row = rows[measures_idx] if measures_idx is not None else None
    offense_rows = rows[offense_type_idx + 1 :]

    county_value_columns = _identify_county_value_columns(
        geography_row=geography_row,
        measures_row=measures_row,
    )

    records = []
    mapped_labels = {}
    unmapped_labels = set()

    for row in offense_rows:
        if not row:
            continue

        raw_offense_name = row[0].strip()

        if raw_offense_name == "":
            continue

        output_col = _map_offense_label(raw_offense_name)

        if output_col is None:
            unmapped_labels.add(raw_offense_name)
            continue

        mapped_labels[raw_offense_name] = output_col

        for county, col_idx in county_value_columns:
            county_key = _normalize_key(county)

            if county_key == "":
                continue

            value = row[col_idx] if col_idx < len(row) else 0

            records.append(
                {
                    "county": county,
                    "county_key": county_key,
                    "metric": output_col,
                    "value": _to_number(value),
                    "source_offense_label": raw_offense_name,
                }
            )

    if not records:
        raise ValueError(
            "No supported offense rows were found. Expected at least one of: "
            "Murder, Kidnapping/Abduction, Weapon Law Violations, "
            "Aggravated Assault, Arson, or Sex Offenses."
        )

    long_df = pd.DataFrame(records)

    _save_label_validation_outputs(long_df, unmapped_labels)

    county_metric = (
        long_df.groupby(["county_key", "metric"], as_index=False)
        .agg(value=("value", "sum"))
    )

    wide = (
        county_metric.pivot_table(
            index="county_key",
            columns="metric",
            values="value",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    county_base = _load_acs_county_base()

    output = county_base.merge(wide, on="county_key", how="left")

    expected_cols = [
        "homicide_count",
        "kidnapping_abduction_count",
        "weapons_law_violation_count",
        "violent_crime_count",
        "aggravated_assault_count",
        "arson_count",
        "sex_offense_count",
        "hate_crime_count",
        "law_enforcement_assault_count",
    ]

    for col in expected_cols:
        if col not in output.columns:
            output[col] = 0

        output[col] = (
            pd.to_numeric(output[col], errors="coerce")
            .fillna(0)
            .astype(int)
        )

    # If violent crime was not separately exported, create a partial violent-crime count.
    # This avoids double counting if a future export already provides violent_crime_count.
    if output["violent_crime_count"].sum() == 0:
        output["violent_crime_count"] = (
            output["homicide_count"]
            + output["kidnapping_abduction_count"]
            + output["aggravated_assault_count"]
            + output["sex_offense_count"]
        )

    output = output[
        [
            "county",
            "homicide_count",
            "kidnapping_abduction_count",
            "weapons_law_violation_count",
            "violent_crime_count",
            "aggravated_assault_count",
            "arson_count",
            "sex_offense_count",
            "hate_crime_count",
            "law_enforcement_assault_count",
        ]
    ].copy()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False)

    all_zero_rows = output[
        (output["homicide_count"] == 0)
        & (output["kidnapping_abduction_count"] == 0)
        & (output["weapons_law_violation_count"] == 0)
        & (output["violent_crime_count"] == 0)
        & (output["aggravated_assault_count"] == 0)
        & (output["arson_count"] == 0)
        & (output["sex_offense_count"] == 0)
    ]

    print("\nCrime/weapons input created:")
    print(f"- {OUTPUT_FILE}")
    print(f"Output shape: {output.shape}")

    print("\nCrimeInsight offense-label validation saved:")
    print(f"- {VALIDATION_OUTPUT_FILE}")
    print(f"- {UNMAPPED_OUTPUT_FILE}")

    print("\nMapped CrimeInsight offense labels:")
    for label, output_col in sorted(mapped_labels.items()):
        print(f"- {label} -> {output_col}")

    print("\nCrime/weapons totals by category:")
    totals = output[
        [
            "homicide_count",
            "kidnapping_abduction_count",
            "weapons_law_violation_count",
            "violent_crime_count",
            "aggravated_assault_count",
            "arson_count",
            "sex_offense_count",
            "hate_crime_count",
            "law_enforcement_assault_count",
        ]
    ].sum()

    print(totals.to_string())

    if unmapped_labels:
        print("\nUnmapped offense labels found in export:")
        for label in sorted(unmapped_labels):
            print(f"- {label}")

    print("\nTop 10 counties by weapon law violations:")
    print(
        output.sort_values("weapons_law_violation_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 counties by sex offenses:")
    print(
        output.sort_values("sex_offense_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 counties by partial violent-crime count:")
    print(
        output.sort_values("violent_crime_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print(
        "\nNote: Counties with all-zero values may represent true zero exposure or may be absent "
        "from the exported CrimeInsight file. Review the export filters if this count is high."
    )
    print(f"All-zero county rows: {len(all_zero_rows)}")

    return output


def main():
    input_file = RAW_DIR / "crimes_clearances_by_offense_type_2024.csv"
    process_crime_offense_file(input_file)


if __name__ == "__main__":
    main()