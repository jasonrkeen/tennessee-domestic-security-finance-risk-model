from pathlib import Path
import csv
import re

import pandas as pd

from src.config import OPTIONAL_CRIME_RATE_INPUT, RAW_DIR


OUTPUT_FILE = OPTIONAL_CRIME_RATE_INPUT


def _to_float(value):
    if value is None:
        return 0.0

    text = str(value).replace(",", "").replace("%", "").strip()

    if text == "":
        return 0.0

    try:
        return float(text)
    except Exception:
        return 0.0


def _to_int(value):
    return int(round(_to_float(value)))


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


def _find_header_row(rows: list[list[str]]) -> int:
    """
    Find the row containing the expected CrimeInsight export headers.
    """

    expected_terms = {
        "measures",
        "crime rate (per 1,000)",
        "estimated population",
        "number of crimes",
    }

    for idx, row in enumerate(rows[:30]):
        normalized = {str(cell).strip().lower() for cell in row}
        matches = len(expected_terms.intersection(normalized))

        if matches >= 2:
            return idx

    raise ValueError(
        "Could not find the expected header row. Expected columns like "
        "'Measures', 'Crime Rate (per 1,000)', 'Estimated Population', "
        "and 'Number of Crimes'."
    )


def _clean_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize numeric columns from the CrimeInsight crime-rate export.
    """

    output = df.copy()

    numeric_map = {
        "Crime Rate (per 1,000)": "overall_crime_rate_per_1000_2024",
        "Estimated Population": "crime_population_2024",
        "Number of Crimes": "overall_crime_count_2024",
    }

    for source_col, output_col in numeric_map.items():
        if source_col not in output.columns:
            output[output_col] = 0
        else:
            if output_col == "overall_crime_rate_per_1000_2024":
                output[output_col] = output[source_col].apply(_to_float)
            else:
                output[output_col] = output[source_col].apply(_to_int)

    return output


def process_crime_rate_file(input_path: str | Path) -> pd.DataFrame:
    """
    Process TBI CrimeInsight / TNCrimeOnline Crime Rates by Jurisdiction CSV.

    The raw export may include statewide, regional, county, and agency rows.
    This processor keeps only rows that match Tennessee counties from the ACS
    county base.

    Output:
        data/raw/tn_crime_rate_inputs.csv

    Output columns:
        county
        overall_crime_rate_per_1000_2024
        overall_crime_count_2024
        crime_population_2024

    Notes:
    - Keeps county-level aggregate values only.
    - Does not preserve agency-level, incident-level, victim-level,
      suspect-level, address, coordinate, narrative, or case-level records.
    - Overall crime rate is a broad public-safety pressure proxy and should
      not be interpreted as a terrorism, extremism, or illicit-finance indicator
      by itself.
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Crime rate input file not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8-sig", errors="replace") as f:
        rows = list(csv.reader(f))

    if len(rows) < 5:
        raise ValueError("Crime rate file does not have the expected row structure.")

    header_idx = _find_header_row(rows)

    header = rows[header_idx]
    data_rows = rows[header_idx + 1 :]

    raw_df = pd.DataFrame(data_rows, columns=header)

    raw_df = raw_df.dropna(how="all")

    if "Measures" not in raw_df.columns:
        raise ValueError(
            "Crime rate export must include a 'Measures' column containing county or jurisdiction names."
        )

    raw_df = raw_df.loc[
        raw_df["Measures"].astype(str).str.strip().ne("")
    ].copy()

    raw_df["jurisdiction_original"] = raw_df["Measures"].astype(str).str.strip()
    raw_df["county_key"] = raw_df["jurisdiction_original"].apply(_normalize_key)

    county_base = _load_acs_county_base()

    merged = county_base.merge(
        raw_df,
        on="county_key",
        how="left",
        suffixes=("", "_crime_export"),
    )

    merged = _clean_numeric_columns(merged)

    output = merged[
        [
            "county",
            "overall_crime_rate_per_1000_2024",
            "overall_crime_count_2024",
            "crime_population_2024",
        ]
    ].copy()

    for col in [
        "overall_crime_rate_per_1000_2024",
        "overall_crime_count_2024",
        "crime_population_2024",
    ]:
        output[col] = pd.to_numeric(output[col], errors="coerce").fillna(0)

    output["overall_crime_count_2024"] = output["overall_crime_count_2024"].astype(int)
    output["crime_population_2024"] = output["crime_population_2024"].astype(int)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False)

    all_zero_rows = output[
        (output["overall_crime_rate_per_1000_2024"] == 0)
        & (output["overall_crime_count_2024"] == 0)
    ]

    print("\nCrime rate input created:")
    print(f"- {OUTPUT_FILE}")
    print(f"Output shape: {output.shape}")

    print("\nTop 10 counties by overall crime rate per 1,000:")
    print(
        output.sort_values("overall_crime_rate_per_1000_2024", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 counties by number of crimes:")
    print(
        output.sort_values("overall_crime_count_2024", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print(
        "\nNote: Counties with all-zero values may represent true zero exposure, "
        "a county-name mismatch, or an export filter issue."
    )
    print(f"All-zero county rows: {len(all_zero_rows)}")

    return output


def main():
    input_file = RAW_DIR / "crime_rates_by_jurisdiction_2024.csv"
    process_crime_rate_file(input_file)


if __name__ == "__main__":
    main()