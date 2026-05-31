from pathlib import Path
import re

import pandas as pd

from src.config import OPTIONAL_FFL_INPUT, PROCESSED_DIR, RAW_DIR


def _normalize_county_key(value) -> str:
    """
    Create a merge-safe county key.

    Examples:
    - DeKalb, Dekalb, dekalb -> dekalb
    - McMinn, Mcminn, mcminn -> mcminn
    - McNairy, Mcnairy, mcnairy -> mcnairy
    """

    if pd.isna(value):
        return ""

    text = str(value)

    text = (
        text.replace(" County", "")
        .replace(" county", "")
        .replace(", Tennessee", "")
        .replace(", TN", "")
        .strip()
        .lower()
    )

    text = re.sub(r"[^a-z0-9]", "", text)

    return text


def _clean_county_text(value):
    """
    Light county-name cleaning without forcing title case.
    Canonical capitalization is applied later through the ACS crosswalk.
    """

    if pd.isna(value):
        return ""

    return (
        str(value)
        .replace(" County", "")
        .replace(" county", "")
        .replace(", Tennessee", "")
        .replace(", TN", "")
        .strip()
    )


def _normalize_col(value):
    """
    Normalize column names for flexible matching.
    """

    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _find_column(df: pd.DataFrame, possible_names: list[str]) -> str | None:
    """
    Find a likely matching column from a list of possible names.
    Matching is case-insensitive and ignores spaces, underscores, punctuation,
    hyphens, slashes, and periods.
    """

    normalized_cols = {_normalize_col(col): col for col in df.columns}

    for name in possible_names:
        key = _normalize_col(name)
        if key in normalized_cols:
            return normalized_cols[key]

    return None


def _read_input_file(input_path: Path) -> pd.DataFrame:
    """
    Read CSV, TXT, or Excel ATF FFL file.
    """

    suffix = input_path.suffix.lower()

    if suffix in [".csv", ".txt"]:
        return pd.read_csv(input_path, low_memory=False)

    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(input_path)

    raise ValueError(
        f"Unsupported file type: {suffix}. Use CSV, TXT, XLSX, or XLS."
    )


def _normalize_license_type(value) -> str:
    """
    Normalize ATF FFL license type into a two-digit string when possible.

    Examples:
    - 1 -> 01
    - 01 -> 01
    - 7 -> 07
    - Type 10 -> 10
    """

    if pd.isna(value):
        return ""

    text = str(value).strip().lower()

    # Pull first one- or two-digit number from strings like "Type 01 - Dealer".
    match = re.search(r"\b(\d{1,2})\b", text)

    if match:
        return match.group(1).zfill(2)

    return text


def _classify_ffl_type(value) -> str:
    """
    Classify FFL license type into broad aggregate categories.

    Common ATF FFL type mappings:
    01 = Dealer in firearms other than destructive devices
    02 = Pawnbroker in firearms other than destructive devices
    03 = Collector of curios and relics
    06 = Manufacturer of ammunition
    07 = Manufacturer of firearms other than destructive devices
    08 = Importer of firearms other than destructive devices
    09 = Dealer in destructive devices
    10 = Manufacturer of destructive devices
    11 = Importer of destructive devices

    The model outputs dealer, manufacturer, pawnbroker, collector, importer,
    and destructive-device-related aggregate counts.
    """

    type_code = _normalize_license_type(value)
    text = str(value).strip().lower() if not pd.isna(value) else ""

    if type_code == "01" or "dealer" in text:
        return "dealer"

    if type_code == "02" or "pawn" in text:
        return "pawnbroker"

    if type_code == "03" or "collector" in text or "curio" in text:
        return "collector"

    if type_code in {"06", "07", "10"} or "manufacturer" in text:
        return "manufacturer"

    if type_code in {"08", "11"} or "importer" in text:
        return "importer"

    return "other"


def _is_destructive_device_ffl(value) -> int:
    """
    Flag destructive-device-related FFL types.

    ATF destructive-device-related license types:
    09 = Dealer in destructive devices
    10 = Manufacturer of destructive devices
    11 = Importer of destructive devices

    This is a subtype indicator and can overlap with importer/manufacturer
    categories. It should not be summed with the other subtype counts to
    reconcile to total FFL count.
    """

    type_code = _normalize_license_type(value)
    text = str(value).strip().lower() if not pd.isna(value) else ""

    if type_code in {"09", "10", "11"}:
        return 1

    if "destructive" in text and "device" in text:
        return 1

    return 0


def _load_acs_county_crosswalk() -> pd.DataFrame:
    """
    Load ACS county file and build Tennessee county crosswalks.

    Expected ACS file:
        data/processed/tn_acs_county_data.csv

    Required fields:
        fips
        county
    """

    acs_path = PROCESSED_DIR / "tn_acs_county_data.csv"

    if not acs_path.exists():
        raise FileNotFoundError(
            "County crosswalk not found. Run the main pipeline once first so this file exists:\n"
            f"{acs_path}"
        )

    acs = pd.read_csv(acs_path, dtype={"fips": str})

    if "fips" not in acs.columns or "county" not in acs.columns:
        raise ValueError(
            "ACS county file must include 'fips' and 'county' columns."
        )

    crosswalk = acs[["fips", "county"]].copy()
    crosswalk["county"] = crosswalk["county"].astype(str).str.strip()
    crosswalk["county_fips_3"] = (
        crosswalk["fips"].astype(str).str[-3:].str.zfill(3)
    )
    crosswalk["county_key"] = crosswalk["county"].apply(_normalize_county_key)

    return crosswalk[["county_fips_3", "county_key", "county"]].drop_duplicates()


def _apply_county_name_crosswalk(
    working: pd.DataFrame,
    county_col: str,
) -> pd.DataFrame:
    """
    Map a county-name column to canonical ACS county names.
    """

    crosswalk = _load_acs_county_crosswalk()[["county_key", "county"]].drop_duplicates()

    output = working.copy()
    output["county_original"] = output[county_col].apply(_clean_county_text)
    output["county_key"] = output["county_original"].apply(_normalize_county_key)

    summary_keys = {
        "",
        "nan",
        "total",
        "totals",
        "statewide",
        "tennessee",
        "unknown",
    }

    output = output[~output["county_key"].isin(summary_keys)].copy()

    output = output.merge(
        crosswalk,
        on="county_key",
        how="left",
        suffixes=("_input", ""),
    )

    unmatched = (
        output.loc[output["county"].isna(), ["county_original"]]
        .drop_duplicates()
        .sort_values("county_original")
    )

    if not unmatched.empty:
        print("\nWarning: unmatched FFL county names:")
        for value in unmatched["county_original"].tolist():
            print(f"- {value}")

    output["county"] = output["county"].fillna("")

    return output


def _apply_county_code_crosswalk(
    working: pd.DataFrame,
    county_code_col: str,
) -> pd.DataFrame:
    """
    Map a county-code column such as LIC_CNTY to canonical ACS county names.
    """

    crosswalk = _load_acs_county_crosswalk()[["county_fips_3", "county"]].drop_duplicates()

    output = working.copy()

    output["county_fips_3"] = (
        pd.to_numeric(output[county_code_col], errors="coerce")
        .fillna(-1)
        .astype(int)
        .astype(str)
        .str.zfill(3)
    )

    output = output.merge(crosswalk, on="county_fips_3", how="left")

    unmatched = output["county"].isna().sum()
    if unmatched:
        print(f"Warning: {unmatched} FFL rows could not be matched to a Tennessee county.")

    output["county"] = output["county"].fillna("")

    return output


def _prepare_county_field(working: pd.DataFrame) -> pd.DataFrame:
    """
    Add standardized county names to the FFL dataframe.

    Priority:
    1. Use a plain county name column if present.
    2. Use LIC_CNTY / county code and map it through ACS county FIPS crosswalk.
    """

    county_col = _find_column(
        working,
        [
            "county",
            "premise county",
            "premises county",
            "premise_county",
            "premises_county",
            "business county",
            "license county",
        ],
    )

    if county_col is not None:
        return _apply_county_name_crosswalk(working, county_col)

    county_code_col = _find_column(
        working,
        [
            "LIC_CNTY",
            "lic_cnty",
            "license county code",
            "county code",
            "county_fips",
            "cnty",
        ],
    )

    if county_code_col is None:
        raise ValueError(
            "Could not identify either a county-name column or county-code column. "
            "For the current ATF file, expected something like LIC_CNTY."
        )

    return _apply_county_code_crosswalk(working, county_code_col)


def process_ffl_file(input_path: str | Path) -> pd.DataFrame:
    """
    Process a downloaded ATF FFL listing file into county-level aggregate inputs.

    Output columns:
        county
        ffl_count
        dealer_ffl_count
        manufacturer_ffl_count
        pawnbroker_ffl_count
        collector_ffl_count
        importer_ffl_count
        destructive_device_ffl_count

    Important:
    - This function does not preserve licensee names, business names, addresses,
      phone numbers, coordinates, URLs, license numbers, owner names,
      or business-level / site-level details.
    - FFL counts are lawful licensing and access-complexity proxies only.
      They are not suspicious-activity indicators.
    - destructive_device_ffl_count is a subtype flag count for Types 09, 10, and 11.
      It can overlap with importer/manufacturer classifications and should be
      interpreted as a high-sensitivity subtype indicator, not as an additive
      component that reconciles to total FFL count.
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"ATF FFL input file not found: {input_path}")

    df = _read_input_file(input_path)

    print(f"Loaded ATF FFL file: {input_path}")
    print(f"Input shape: {df.shape}")
    print("Detected columns:")
    for col in df.columns:
        print(f"- {col}")

    state_col = _find_column(
        df,
        [
            "state",
            "lic state",
            "license state",
            "premise state",
            "premises state",
            "premise_state",
            "premises_state",
            "business state",
            "mailing state",
            "PREMISE_STATE",
            "MAIL_STATE",
        ],
    )

    type_col = _find_column(
        df,
        [
            "license type",
            "license_type",
            "lic type",
            "lic_type",
            "type",
            "ffl type",
            "ffl_type",
            "LIC_TYPE",
        ],
    )

    if type_col is None:
        raise ValueError(
            "Could not identify a license type column in the ATF FFL file. "
            "For the current ATF file, expected something like LIC_TYPE."
        )

    working = df.copy()

    if state_col is not None:
        state_values = working[state_col].astype(str).str.upper().str.strip()

        tn_mask = (
            state_values.eq("TN")
            | state_values.eq("TENNESSEE")
            | state_values.str.contains("TENNESSEE", na=False)
        )

        working = working.loc[tn_mask].copy()

        print(f"Filtered to Tennessee using state column: {state_col}")
        print(f"Tennessee rows: {len(working)}")
    else:
        print("Warning: No state column detected. Assuming file is Tennessee-only.")

    if working.empty:
        raise ValueError(
            "No Tennessee rows found after filtering. "
            "Check the state column values or use a Tennessee-only FFL file."
        )

    working = _prepare_county_field(working)
    working["ffl_category"] = working[type_col].apply(_classify_ffl_type)
    working["destructive_device_flag"] = working[type_col].apply(_is_destructive_device_ffl)

    working = working[working["county"].astype(str).str.len() > 0].copy()

    grouped = (
        working.groupby("county", as_index=False)
        .agg(
            ffl_count=("county", "count"),
            destructive_device_ffl_count=("destructive_device_flag", "sum"),
        )
    )

    category_counts = (
        working.pivot_table(
            index="county",
            columns="ffl_category",
            values=type_col,
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    output = grouped.merge(category_counts, on="county", how="left")

    rename_map = {
        "dealer": "dealer_ffl_count",
        "manufacturer": "manufacturer_ffl_count",
        "pawnbroker": "pawnbroker_ffl_count",
        "collector": "collector_ffl_count",
        "importer": "importer_ffl_count",
    }

    output = output.rename(columns=rename_map)

    expected_cols = [
        "county",
        "ffl_count",
        "dealer_ffl_count",
        "manufacturer_ffl_count",
        "pawnbroker_ffl_count",
        "collector_ffl_count",
        "importer_ffl_count",
        "destructive_device_ffl_count",
    ]

    for col in expected_cols:
        if col not in output.columns:
            output[col] = 0

    output = output[expected_cols].copy()

    numeric_cols = [col for col in expected_cols if col != "county"]
    for col in numeric_cols:
        output[col] = (
            pd.to_numeric(output[col], errors="coerce")
            .fillna(0)
            .round()
            .astype(int)
        )

    output = output.sort_values("county")

    OPTIONAL_FFL_INPUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OPTIONAL_FFL_INPUT, index=False)

    print("\nATF FFL county input created:")
    print(f"- {OPTIONAL_FFL_INPUT}")
    print(f"Output shape: {output.shape}")

    print("\nTop 10 counties by FFL count:")
    print(
        output.sort_values("ffl_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 counties by dealer FFL count:")
    print(
        output.sort_values("dealer_ffl_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 counties by importer FFL count:")
    print(
        output.sort_values("importer_ffl_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 counties by destructive-device-related FFL count:")
    print(
        output.sort_values("destructive_device_ffl_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    return output


def main():
    """
    Default runner.

    Place the ATF Tennessee FFL CSV in data/raw and name it:
        atf_ffl_listing.csv

    Or update the filename below.
    """

    input_file = RAW_DIR / "atf_ffl_listing.csv"

    process_ffl_file(input_file)


if __name__ == "__main__":
    main()