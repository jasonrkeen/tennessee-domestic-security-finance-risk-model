"""Coverage evidence captured before loaders/scoring fill missing numeric values."""

import re

import numpy as np
import pandas as pd


def observed_values(
    df: pd.DataFrame, columns: list[str], flag: str
) -> pd.Series:
    """Require complete finite nonnegative inputs, respecting explicit evidence.

    Legacy all-zero rows are ambiguous: previous loaders wrote zero templates.
    A reviewed zero row must carry its layer's *_data_available=True marker.
    Explicit false/blank/unrecognized markers never count as observed.
    """
    if not all(col in df.columns for col in columns):
        return pd.Series(False, index=df.index)
    numeric = df[columns].apply(pd.to_numeric, errors="coerce")
    valid = (np.isfinite(numeric) & numeric.ge(0)).all(axis=1)
    if flag in df.columns:
        evidence = df[flag].astype("string").str.strip().str.lower().isin(
            ["true", "1", "1.0"]
        )
    else:
        evidence = numeric.gt(0).any(axis=1)
    return valid & evidence


def county_key(value: object) -> str:
    """Match the optional loaders' canonical county crosswalk convention."""
    if pd.isna(value):
        return ""
    text = str(value).lower().replace(", tennessee", "").replace(", tn", "")
    return re.sub(r"[^a-z0-9]", "", text.replace(" county", ""))


def county_availability(
    source: pd.DataFrame, columns: list[str], flag: str
) -> pd.Series:
    """Snapshot row evidence before coercion; all duplicate rows must be valid."""
    if "county" not in source.columns:
        return pd.Series(dtype=bool)
    available = observed_values(source, [c for c in columns if c != "county"], flag)
    return available.groupby(source["county"].map(county_key)).all()


def attach_availability(
    output: pd.DataFrame, evidence: pd.Series, flag: str
) -> pd.DataFrame:
    """Carry evidence through aggregation and left joins without changing values."""
    output[flag] = output["county"].map(county_key).map(evidence).eq(True)
    return output
