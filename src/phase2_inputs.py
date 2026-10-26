import re

import pandas as pd

from src.source_availability import county_availability, attach_availability

from src.config import (
    OPTIONAL_FDIC_BANKING_INPUT,
    OPTIONAL_FFL_INPUT,
)


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


def _build_county_crosswalk(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Build a canonical county-name crosswalk from the ACS county base.

    This lets external files use imperfect county capitalization while the
    model keeps ACS county names as the canonical naming standard.
    """

    if "county" not in county_base.columns:
        raise ValueError("county_base must include a 'county' column.")

    crosswalk = county_base[["county"]].copy()
    crosswalk["county"] = crosswalk["county"].astype(str).str.strip()
    crosswalk["county_key"] = crosswalk["county"].apply(_normalize_county_key)

    crosswalk = crosswalk.drop_duplicates(subset=["county_key"])

    return crosswalk


def _apply_county_crosswalk(
    df: pd.DataFrame,
    county_base: pd.DataFrame,
    source_name: str,
) -> pd.DataFrame:
    """
    Map county names from an input file to canonical ACS county names.
    """

    if "county" not in df.columns:
        raise ValueError(f"{source_name} input must include a 'county' column.")

    crosswalk = _build_county_crosswalk(county_base)

    output = df.copy()

    output["county_original"] = output["county"].astype(str).str.strip()
    output["county_key"] = output["county_original"].apply(_normalize_county_key)

    # Remove known non-county summary rows.
    summary_keys = {
        "total",
        "totals",
        "uniqueinstitutions",
        "totalsuniqueinstitutions",
        "statewide",
        "tennessee",
        "unknown",
        "nan",
        "",
    }

    output = output[~output["county_key"].isin(summary_keys)].copy()

    output = output.merge(
        crosswalk,
        on="county_key",
        how="left",
        suffixes=("_input", ""),
    )

    unmatched = output[
        output["county"].isna()
    ][["county_original"]].drop_duplicates()

    if not unmatched.empty:
        print(f"\nWarning: unmatched county names in {source_name} input:")
        for value in unmatched["county_original"].tolist():
            print(f"- {value}")

    output = output[output["county"].notna()].copy()

    output = output.drop(
        columns=["county_original", "county_key"],
        errors="ignore",
    )

    return output


def load_optional_fdic_banking_inputs(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Optional FDIC banking input.

    Expected columns:
    county, bank_branch_count, total_deposits_thousands

    Notes:
    - total_deposits_thousands should be county-level deposits in thousands of dollars.
    - This file should contain county-level aggregates only.
    - Do not include branch addresses, institution-specific details,
      routing information, coordinates, customer information, or branch-level records
      in model outputs.
    """

    expected_cols = [
        "county",
        "bank_branch_count",
        "total_deposits_thousands",
    ]

    if OPTIONAL_FDIC_BANKING_INPUT.exists():
        df = pd.read_csv(OPTIONAL_FDIC_BANKING_INPUT)
        evidence = county_availability(df, expected_cols, "fdic_data_available")

        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0

        df = df[expected_cols].copy()

        df = _apply_county_crosswalk(
            df=df,
            county_base=county_base,
            source_name="FDIC banking",
        )

    else:
        evidence = pd.Series(dtype=bool)
        df = county_base[["county"]].copy()

        for col in expected_cols:
            if col != "county":
                df[col] = 0

        OPTIONAL_FDIC_BANKING_INPUT.parent.mkdir(parents=True, exist_ok=True)
        df["fdic_data_available"] = False
        df.to_csv(OPTIONAL_FDIC_BANKING_INPUT, index=False)

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # If duplicate counties exist after canonical mapping, aggregate them.
    df = (
        df.groupby("county", as_index=False)
        .agg(
            bank_branch_count=("bank_branch_count", "sum"),
            total_deposits_thousands=("total_deposits_thousands", "sum"),
        )
    )

    df["bank_branch_count"] = (
        pd.to_numeric(df["bank_branch_count"], errors="coerce")
        .fillna(0)
        .round()
        .astype(int)
    )

    df["total_deposits_thousands"] = (
        pd.to_numeric(df["total_deposits_thousands"], errors="coerce")
        .fillna(0)
        .round()
        .astype(int)
    )

    return attach_availability(df, evidence, "fdic_data_available")


def load_optional_ffl_inputs(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Optional ATF FFL county-level input.

    Expected columns:
    county,
    ffl_count,
    dealer_ffl_count,
    manufacturer_ffl_count,
    pawnbroker_ffl_count,
    collector_ffl_count,
    importer_ffl_count,
    destructive_device_ffl_count

        Notes:
    - Use county-level aggregate counts only.
    - Do not include licensee names, business names, addresses, coordinates,
      phone numbers, URLs, license numbers, owner names, or site-level maps.
    - destructive_device_ffl_count is a subtype indicator for ATF FFL Types 09, 10, and 11.
      It can overlap with importer/manufacturer classifications and should not be summed
      with other subtype counts to reconcile to total FFL count.
    - FFL counts are lawful licensing and access-complexity proxies only.
      They are not suspicious-activity indicators.
    """

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

    if OPTIONAL_FFL_INPUT.exists():
        df = pd.read_csv(OPTIONAL_FFL_INPUT)
        evidence = county_availability(df, expected_cols, "ffl_data_available")

        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0

        df = df[expected_cols].copy()

        df = _apply_county_crosswalk(
            df=df,
            county_base=county_base,
            source_name="FFL aggregate",
        )

    else:
        evidence = pd.Series(dtype=bool)
        df = county_base[["county"]].copy()

        for col in expected_cols:
            if col != "county":
                df[col] = 0

        OPTIONAL_FFL_INPUT.parent.mkdir(parents=True, exist_ok=True)
        df["ffl_data_available"] = False
        df.to_csv(OPTIONAL_FFL_INPUT, index=False)

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # If duplicate counties exist after canonical mapping, aggregate them.
    df = (
        df.groupby("county", as_index=False)
        .agg(
            ffl_count=("ffl_count", "sum"),
            dealer_ffl_count=("dealer_ffl_count", "sum"),
            manufacturer_ffl_count=("manufacturer_ffl_count", "sum"),
            pawnbroker_ffl_count=("pawnbroker_ffl_count", "sum"),
            collector_ffl_count=("collector_ffl_count", "sum"),
            importer_ffl_count=("importer_ffl_count", "sum"),
            destructive_device_ffl_count=("destructive_device_ffl_count", "sum"),
        )
    )

    numeric_cols = [
        "ffl_count",
        "dealer_ffl_count",
        "manufacturer_ffl_count",
        "pawnbroker_ffl_count",
        "collector_ffl_count",
        "importer_ffl_count",
        "destructive_device_ffl_count",
    ]

    for col in numeric_cols:
        df[col] = (
            pd.to_numeric(df[col], errors="coerce")
            .fillna(0)
            .round()
            .astype(int)
        )

    return attach_availability(df, evidence, "ffl_data_available")
