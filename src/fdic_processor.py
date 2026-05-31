from pathlib import Path
import re

import pandas as pd

from src.config import OPTIONAL_FDIC_BANKING_INPUT, PROCESSED_DIR, RAW_DIR


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


def _find_column(df: pd.DataFrame, possible_names: list[str]) -> str | None:
    """
    Find a likely matching column from a list of possible names.
    Matching is case-insensitive and ignores spaces, underscores, hyphens,
    parentheses, and punctuation.
    """

    def normalize_col(value):
        text = str(value).lower()
        text = re.sub(r"[^a-z0-9]", "", text)
        return text

    normalized_cols = {normalize_col(col): col for col in df.columns}

    for name in possible_names:
        key = normalize_col(name)
        if key in normalized_cols:
            return normalized_cols[key]

    return None


def _to_number(value) -> float:
    """
    Convert money/count strings to numeric.
    """

    if pd.isna(value):
        return 0.0

    text = (
        str(value)
        .replace(",", "")
        .replace("$", "")
        .replace("%", "")
        .strip()
    )

    if text == "":
        return 0.0

    try:
        return float(text)
    except Exception:
        return 0.0


def _load_acs_county_crosswalk() -> pd.DataFrame:
    """
    Load the ACS county file and create canonical county names.

    Expected file:
        data/processed/tn_acs_county_data.csv
    """

    acs_path = PROCESSED_DIR / "tn_acs_county_data.csv"

    if not acs_path.exists():
        raise FileNotFoundError(
            "Could not find ACS county crosswalk. Run python main.py once first:\n"
            f"{acs_path}"
        )

    acs = pd.read_csv(acs_path)

    if "county" not in acs.columns:
        raise ValueError("tn_acs_county_data.csv must include a county column.")

    crosswalk = acs[["county"]].copy()
    crosswalk["county"] = crosswalk["county"].astype(str).str.strip()
    crosswalk["county_key"] = crosswalk["county"].apply(_normalize_county_key)

    return crosswalk.drop_duplicates(subset=["county_key"])


def _apply_county_crosswalk(df: pd.DataFrame, county_col: str) -> pd.DataFrame:
    """
    Map FDIC county values to canonical ACS county names.
    """

    crosswalk = _load_acs_county_crosswalk()

    output = df.copy()
    output["county_original"] = output[county_col].astype(str).str.strip()
    output["county_key"] = output["county_original"].apply(_normalize_county_key)

    summary_keys = {
        "",
        "nan",
        "total",
        "totals",
        "uniqueinstitutions",
        "totalsuniqueinstitutions",
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
        print("\nWarning: unmatched FDIC county names:")
        for value in unmatched["county_original"].tolist():
            print(f"- {value}")

    output = output[output["county"].notna()].copy()

    return output


def process_fdic_banking_file(input_path: str | Path) -> pd.DataFrame:
    """
    Process a downloaded FDIC Summary of Deposits / branch-level or county-level CSV
    into county-level banking access inputs.

    Output columns:
        county
        bank_branch_count
        total_deposits_thousands

    Notes:
    - This keeps only aggregate county-level outputs.
    - It does not preserve branch names, branch addresses, routing information,
      institution-level records, customer information, coordinates, or branch-level details.
    - If deposits are supplied in millions, they are converted to thousands.
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"FDIC input file not found: {input_path}")

    df = pd.read_csv(input_path, low_memory=False)

    print(f"Loaded FDIC file: {input_path}")
    print(f"Input shape: {df.shape}")
    print("Detected columns:")
    for col in df.columns:
        print(f"- {col}")

    state_col = _find_column(
        df,
        [
            "STALP",
            "STATE",
            "STATE_ABBR",
            "STATEABBR",
            "BRANCH_STATE",
            "BRST",
            "STNAME",
            "State",
        ],
    )

    county_col = _find_column(
        df,
        [
            "COUNTY",
            "COUNTY_NAME",
            "CNTY",
            "CNTYNAMB",
            "CNTYNM",
            "BRANCH_COUNTY",
            "COUNTYNM",
            "County",
        ],
    )

    # County-summary export column
    offices_col = _find_column(
        df,
        [
            "All Offices",
            "Offices",
            "Office Count",
            "Branch Count",
            "Branches",
            "bank_branch_count",
        ],
    )

    # Raw SOD / branch-level deposit columns and county-summary deposit columns
    deposits_col = _find_column(
        df,
        [
            "All Deposits (Millions USD)",
            "All Deposits Millions USD",
            "All Deposits",
            "DEPSUM",
            "DEPOSITS",
            "DEP",
            "DEPOSIT",
            "TOTAL_DEPOSITS",
            "TOTALDEPOSITS",
            "DEPOSIT_SUM",
            "SOD_DEPOSITS",
            "total_deposits_thousands",
        ],
    )

    if county_col is None:
        raise ValueError(
            "Could not identify a county column in the FDIC file. "
            "Please send me the printed column list and I will map it."
        )

    if deposits_col is None:
        raise ValueError(
            "Could not identify a deposits column in the FDIC file. "
            "Please send me the printed column list and I will map it."
        )

    working = df.copy()

    # Filter to Tennessee if a state column exists.
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
        print("Warning: No state column detected. Assuming input file is already Tennessee-only.")

    if working.empty:
        raise ValueError(
            "No Tennessee rows found after filtering. "
            "Check the state column values or use a Tennessee-only FDIC file."
        )

    working = _apply_county_crosswalk(working, county_col=county_col)

    working["deposits_numeric"] = working[deposits_col].apply(_to_number)

    # Detect whether deposits are in millions or already thousands.
    deposits_col_key = re.sub(r"[^a-z0-9]", "", str(deposits_col).lower())

    if "million" in deposits_col_key:
        working["total_deposits_thousands"] = working["deposits_numeric"] * 1000
    elif deposits_col_key == "totaldepositsthousands":
        working["total_deposits_thousands"] = working["deposits_numeric"]
    else:
        # FDIC raw SOD deposits are commonly already reported in thousands.
        working["total_deposits_thousands"] = working["deposits_numeric"]

    if offices_col is not None:
        working["bank_branch_count"] = working[offices_col].apply(_to_number)
    else:
        # Raw branch-level file: one row represents one office/branch.
        working["bank_branch_count"] = 1

    output = (
        working.groupby("county", as_index=False)
        .agg(
            bank_branch_count=("bank_branch_count", "sum"),
            total_deposits_thousands=("total_deposits_thousands", "sum"),
        )
        .sort_values("county")
    )

    output["bank_branch_count"] = (
        pd.to_numeric(output["bank_branch_count"], errors="coerce")
        .fillna(0)
        .round()
        .astype(int)
    )

    output["total_deposits_thousands"] = (
        pd.to_numeric(output["total_deposits_thousands"], errors="coerce")
        .fillna(0)
        .round()
        .astype(int)
    )

    OPTIONAL_FDIC_BANKING_INPUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OPTIONAL_FDIC_BANKING_INPUT, index=False)

    print("\nFDIC county banking input created:")
    print(f"- {OPTIONAL_FDIC_BANKING_INPUT}")
    print(f"Output shape: {output.shape}")

    print("\nTop 10 counties by deposits:")
    print(
        output.sort_values("total_deposits_thousands", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 counties by bank branch count:")
    print(
        output.sort_values("bank_branch_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    return output


def main():
    """
    Default runner.

    Place your downloaded FDIC file in data/raw and update the filename below.
    """

    input_file = RAW_DIR / "fdic_summary_of_deposits.csv"

    process_fdic_banking_file(input_file)


if __name__ == "__main__":
    main()