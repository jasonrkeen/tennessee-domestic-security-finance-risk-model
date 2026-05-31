from pathlib import Path
import csv
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import (
    CHARTS_DIR,
    CRIME_TREND_INPUT_2023,
    CRIME_TREND_INPUT_2024,
    TABLES_DIR,
)


INPUT_2023 = CRIME_TREND_INPUT_2023
INPUT_2024 = CRIME_TREND_INPUT_2024

TREND_OUTPUT = TABLES_DIR / "tn_crime_weapons_trend_analysis.csv"


CRIME_COLUMNS = [
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


RAW_OFFENSE_MAPPING = {
    "murder": "homicide_count",
    "kidnappingabduction": "kidnapping_abduction_count",
    "weaponlawviolations": "weapons_law_violation_count",
    "aggravatedassault": "aggravated_assault_count",
    "arson": "arson_count",
    "allrape": "sex_offense_count",
    "criminalsexualcontact": "sex_offense_count",
    "incest": "sex_offense_count",
    "statutoryrape": "sex_offense_count",
}


def _normalize_county(value) -> str:
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


def _normalize_key(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    return re.sub(r"[^a-z0-9]", "", text)


def _normalize_county_key(value) -> str:
    text = _normalize_county(value).lower()
    return re.sub(r"[^a-z0-9]", "", text)


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


def _safe_pct_change(current, previous):
    """
    Calculate percent change safely.

    If previous year is zero:
    - current > 0 returns NaN because the percentage increase is undefined.
    - current == 0 returns 0.
    """

    current = pd.to_numeric(current, errors="coerce").fillna(0)
    previous = pd.to_numeric(previous, errors="coerce").fillna(0)

    pct = np.where(
        previous > 0,
        ((current - previous) / previous) * 100,
        np.where(current > 0, np.nan, 0),
    )

    return pd.Series(pct, index=current.index)


def _looks_like_processed_file(path: Path) -> bool:
    """
    Return True if the file appears to be a processed county-level input.
    """

    try:
        preview = pd.read_csv(path, nrows=2)
    except Exception:
        return False

    lower_cols = {str(col).strip().lower() for col in preview.columns}

    return (
        "county" in lower_cols
        or "jurisdiction" in lower_cols
    ) and any(col in lower_cols for col in ["homicide_count", "violent_crime_count"])


def _load_processed_crime_year(path: Path, year: int) -> pd.DataFrame:
    """
    Load an already processed county-level crime/weapons input file.
    """

    df = pd.read_csv(path)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
    )

    county_candidates = [
        "county",
        "County",
        "COUNTY",
        "jurisdiction",
        "Jurisdiction",
        "JURISDICTION",
    ]

    county_col = None

    for candidate in county_candidates:
        if candidate in df.columns:
            county_col = candidate
            break

    if county_col is None:
        raise ValueError(
            f"{path.name} must include a county or jurisdiction column.\n"
            f"Detected columns: {list(df.columns)}"
        )

    df = df.rename(columns={county_col: "county"})

    df["county"] = df["county"].apply(_normalize_county)
    df["county_key"] = df["county"].apply(_normalize_county_key)

    for col in CRIME_COLUMNS:
        if col not in df.columns:
            df[col] = 0

        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    keep_cols = ["county", "county_key"] + CRIME_COLUMNS
    df = df[keep_cols].copy()

    df = df[
        df["county_key"].notna()
        & df["county_key"].astype(str).str.len().gt(0)
        & ~df["county_key"].isin(
            {
                "total",
                "totals",
                "statewide",
                "tennessee",
                "unknown",
                "nan",
            }
        )
    ].copy()

    df = (
        df.groupby(["county", "county_key"], as_index=False)
        .agg({col: "sum" for col in CRIME_COLUMNS})
    )

    rename_map = {col: f"{col}_{year}" for col in CRIME_COLUMNS}
    df = df.rename(columns=rename_map)

    return df


def _load_raw_crimeinsight_matrix(path: Path, year: int) -> pd.DataFrame:
    """
    Load raw TNCrimeOnline / CrimeInsight matrix export.

    Expected structure:
    - Row contains "Jurisdiction by Geography" followed by counties.
    - Next row contains repeated measures including "Number of Crimes".
    - Offense rows contain one offense label, followed by county measure groups.
    """

    with open(path, "r", encoding="utf-8-sig", errors="ignore", newline="") as file:
        rows = list(csv.reader(file))

    jurisdiction_row_idx = None
    measures_row_idx = None
    offense_start_idx = None

    for idx, row in enumerate(rows):
        if not row:
            continue

        first = str(row[0]).strip().lower()

        if first == "jurisdiction by geography":
            jurisdiction_row_idx = idx

        if first == "measures":
            measures_row_idx = idx

        if first == "offense type":
            offense_start_idx = idx + 1
            break

    if jurisdiction_row_idx is None or measures_row_idx is None or offense_start_idx is None:
        raise ValueError(
            f"Could not identify raw CrimeInsight matrix structure in {path.name}."
        )

    county_row = rows[jurisdiction_row_idx]
    measures_row = rows[measures_row_idx]

    county_measure_positions = []

    current_county = ""

    max_len = max(len(county_row), len(measures_row))

    for col_idx in range(1, max_len):
        county_value = county_row[col_idx] if col_idx < len(county_row) else ""
        measure_value = measures_row[col_idx] if col_idx < len(measures_row) else ""

        if str(county_value).strip():
            current_county = _normalize_county(county_value)

        if (
            current_county
            and str(measure_value).strip().lower() == "number of crimes"
        ):
            county_measure_positions.append((current_county, col_idx))

    if not county_measure_positions:
        raise ValueError(
            f"No county Number of Crimes columns found in {path.name}."
        )

    county_records = {}

    for county, _ in county_measure_positions:
        county_key = _normalize_county_key(county)

        if not county_key:
            continue

        county_records[county_key] = {
            "county": county,
            "county_key": county_key,
            **{col: 0.0 for col in CRIME_COLUMNS},
        }

    for row in rows[offense_start_idx:]:
        if not row:
            continue

        offense_label = str(row[0]).strip()

        if not offense_label:
            continue

        offense_key = _normalize_key(offense_label)
        metric = RAW_OFFENSE_MAPPING.get(offense_key)

        if metric is None:
            continue

        for county, col_idx in county_measure_positions:
            county_key = _normalize_county_key(county)

            if county_key not in county_records:
                continue

            value = row[col_idx] if col_idx < len(row) else 0
            county_records[county_key][metric] += _safe_number(value)

    df = pd.DataFrame(list(county_records.values()))

    if df.empty:
        raise ValueError(f"No mapped crime rows were parsed from {path.name}.")

    # Build violent crime as selected violent offense pressure.
    # Weapon law violations and arson are kept separate and are not included here.
    df["violent_crime_count"] = (
        df["homicide_count"]
        + df["kidnapping_abduction_count"]
        + df["aggravated_assault_count"]
        + df["sex_offense_count"]
    )

    for col in CRIME_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    rename_map = {col: f"{col}_{year}" for col in CRIME_COLUMNS}
    df = df.rename(columns=rename_map)

    return df


def _load_crime_year(path: Path, year: int) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Crime trend input file not found: {path}\n\n"
            "Expected files:\n"
            "- data/raw/tn_crime_weapons_inputs_2023.csv\n"
            "- data/raw/tn_crime_weapons_inputs_2024.csv"
        )

    if _looks_like_processed_file(path):
        print(f"Loading processed county-level crime file for {year}: {path.name}")
        return _load_processed_crime_year(path, year)

    print(f"Loading raw CrimeInsight matrix file for {year}: {path.name}")
    return _load_raw_crimeinsight_matrix(path, year)


def _add_trend_columns(df: pd.DataFrame) -> pd.DataFrame:
    output = df.copy()

    for col in CRIME_COLUMNS:
        col_2023 = f"{col}_2023"
        col_2024 = f"{col}_2024"

        abs_change_col = f"{col}_abs_change"
        pct_change_col = f"{col}_pct_change"

        output[abs_change_col] = output[col_2024] - output[col_2023]
        output[pct_change_col] = _safe_pct_change(
            output[col_2024],
            output[col_2023],
        )

    output["total_selected_crime_count_2023"] = output[
        [f"{col}_2023" for col in CRIME_COLUMNS]
    ].sum(axis=1)

    output["total_selected_crime_count_2024"] = output[
        [f"{col}_2024" for col in CRIME_COLUMNS]
    ].sum(axis=1)

    output["total_selected_crime_abs_change"] = (
        output["total_selected_crime_count_2024"]
        - output["total_selected_crime_count_2023"]
    )

    output["total_selected_crime_pct_change"] = _safe_pct_change(
        output["total_selected_crime_count_2024"],
        output["total_selected_crime_count_2023"],
    )

    output["weapon_law_violation_yoy_change"] = output[
        "weapons_law_violation_count_abs_change"
    ]

    output["violent_crime_yoy_change"] = output[
        "violent_crime_count_abs_change"
    ]

    output["crime_pressure_yoy_change"] = output[
        "total_selected_crime_abs_change"
    ]

    output["trend_signal"] = pd.cut(
        output["total_selected_crime_pct_change"].fillna(999),
        bins=[-999999, -10, 10, 25, 999999],
        labels=[
            "Declining",
            "Stable / Mixed",
            "Increasing",
            "Sharp Increase",
        ],
    ).astype(str)

    output.loc[
        output["total_selected_crime_count_2023"].eq(0)
        & output["total_selected_crime_count_2024"].gt(0),
        "trend_signal",
    ] = "New / Previously Zero"

    output.loc[
        output["total_selected_crime_count_2023"].eq(0)
        & output["total_selected_crime_count_2024"].eq(0),
        "trend_signal",
    ] = "No Selected Activity"

    return output


def build_crime_trend_analysis() -> pd.DataFrame:
    """
    Build 2023-to-2024 county-level crime/weapons trend table.
    """

    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    df_2023 = _load_crime_year(INPUT_2023, 2023)
    df_2024 = _load_crime_year(INPUT_2024, 2024)

    trend_df = df_2024.merge(
        df_2023.drop(columns=["county"]),
        on="county_key",
        how="outer",
    )

    if "county" not in trend_df.columns:
        trend_df["county"] = ""

    trend_df["county"] = trend_df["county"].fillna("")

    for col in CRIME_COLUMNS:
        for year in [2023, 2024]:
            year_col = f"{col}_{year}"
            if year_col not in trend_df.columns:
                trend_df[year_col] = 0

            trend_df[year_col] = pd.to_numeric(
                trend_df[year_col],
                errors="coerce",
            ).fillna(0)

    trend_df = _add_trend_columns(trend_df)

    trend_df = trend_df.sort_values(
        "crime_pressure_yoy_change",
        ascending=False,
    )

    trend_df.to_csv(TREND_OUTPUT, index=False)

    return trend_df


def _save_yoy_bar_chart(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    filename: str,
    top_n: int = 15,
):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    if value_col not in df.columns:
        print(f"Skipping trend chart. Missing column: {value_col}")
        return None

    plot_df = df.copy()
    plot_df[value_col] = pd.to_numeric(plot_df[value_col], errors="coerce").fillna(0)

    plot_df = plot_df.sort_values(value_col, ascending=False).head(top_n)
    plot_df = plot_df.sort_values(value_col, ascending=True)

    if plot_df.empty:
        print(f"Skipping trend chart. No data for: {value_col}")
        return None

    plt.figure(figsize=(10, 7))
    plt.barh(plot_df["county"], plot_df[value_col])
    plt.title(title)
    plt.xlabel("YoY Absolute Change, 2024 minus 2023")
    plt.ylabel("County")
    plt.tight_layout()

    path = CHARTS_DIR / filename
    plt.savefig(path, dpi=200)
    plt.close()

    return path


def generate_crime_trend_charts(trend_df: pd.DataFrame):
    chart_paths = []

    specs = [
        (
            "weapon_law_violation_yoy_change",
            "Top 15 Counties by Weapon Law Violation YoY Increase",
            "top_15_weapon_law_violation_yoy_change.png",
        ),
        (
            "violent_crime_yoy_change",
            "Top 15 Counties by Violent Crime YoY Increase",
            "top_15_violent_crime_yoy_change.png",
        ),
        (
            "crime_pressure_yoy_change",
            "Top 15 Counties by Selected Crime / Weapons YoY Increase",
            "top_15_crime_pressure_yoy_change.png",
        ),
    ]

    for value_col, title, filename in specs:
        path = _save_yoy_bar_chart(
            trend_df,
            value_col=value_col,
            title=title,
            filename=filename,
        )

        if path is not None:
            chart_paths.append(path)

    return chart_paths


def run_crime_trend_analysis():
    """
    Run full CrimeInsight trend-analysis workflow.
    """

    trend_df = build_crime_trend_analysis()
    chart_paths = generate_crime_trend_charts(trend_df)

    print("\nCrimeInsight trend analysis created:")
    print(f"- {TREND_OUTPUT}")

    for path in chart_paths:
        print(f"- {path}")

    print("\nTop 10 counties by selected crime/weapons YoY increase:")

    preview_cols = [
        "county",
        "total_selected_crime_count_2023",
        "total_selected_crime_count_2024",
        "total_selected_crime_abs_change",
        "total_selected_crime_pct_change",
        "trend_signal",
    ]

    print(
        trend_df[preview_cols]
        .head(10)
        .to_string(index=False)
    )

    return trend_df, chart_paths


def main():
    run_crime_trend_analysis()


if __name__ == "__main__":
    main()