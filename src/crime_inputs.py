import re

import pandas as pd

from src.source_availability import county_availability, attach_availability

from src.config import (
    OPTIONAL_CRIME_WEAPONS_INPUT,
    OPTIONAL_GANG_ACTIVITY_INPUT,
    OPTIONAL_EXPLOSIVES_ACTIVITY_INPUT,
    OPTIONAL_GANG_EXPLOSIVES_ACTIVITY_INPUT,
    OPTIONAL_HATE_CRIME_OFFENSE_INPUT,
    OPTIONAL_LAW_ENFORCEMENT_AMBUSH_INPUT,
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

    summary_keys = {
        "total",
        "totals",
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

    unmatched = output[output["county"].isna()][["county_original"]].drop_duplicates()

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


def _load_optional_county_aggregate(
    county_base: pd.DataFrame,
    input_path,
    expected_cols: list[str],
    source_name: str,
    availability_flag: str,
) -> pd.DataFrame:
    """
    Generic loader for optional county-level aggregate inputs.

    If the input file does not exist, the function creates a zero-filled template.
    """

    if "county" not in expected_cols:
        expected_cols = ["county"] + expected_cols

    if input_path.exists():
        df = pd.read_csv(input_path)
        evidence = county_availability(df, expected_cols, availability_flag)

        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0

        df = df[expected_cols].copy()

        df = _apply_county_crosswalk(
            df=df,
            county_base=county_base,
            source_name=source_name,
        )

    else:
        evidence = pd.Series(dtype=bool)
        df = county_base[["county"]].copy()

        for col in expected_cols:
            if col != "county":
                df[col] = 0

        input_path.parent.mkdir(parents=True, exist_ok=True)
        df[availability_flag] = False
        df.to_csv(input_path, index=False)

    for col in expected_cols:
        if col != "county":
            if col not in df.columns:
                df[col] = 0

            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    agg_map = {col: (col, "sum") for col in expected_cols if col != "county"}

    df = df.groupby("county", as_index=False).agg(**agg_map)

    # Retain all ACS counties even if the optional input only contains counties
    # with positive activity.
    county_base_clean = county_base[["county"]].copy()
    county_base_clean["county"] = county_base_clean["county"].astype(str).str.strip()

    df = county_base_clean.merge(df, on="county", how="left")

    for col in expected_cols:
        if col != "county":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return attach_availability(df, evidence, availability_flag)


def load_optional_crime_weapons_inputs(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Optional TBI / CrimeInsight county-level crime-weapons input.

    Notes:
    - Use county-level aggregate counts only.
    - Do not include incident-level details, victim details, suspect details,
      addresses, coordinates, or agency case-level records.
    """

    expected_cols = [
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

    return _load_optional_county_aggregate(
        county_base=county_base,
        input_path=OPTIONAL_CRIME_WEAPONS_INPUT,
        expected_cols=expected_cols,
        source_name="TBI CrimeInsight crime/weapons",
        availability_flag="crime_data_available",
    )


def load_optional_gang_activity_inputs(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Optional TBI gang-related criminal activity input.

    Produced by:
    python -m src.gang_activity_processor

    Notes:
    - County-level aggregate counts only.
    - Do not include gang names, individual names, incident IDs, addresses,
      suspect/victim details, coordinates, or case narratives.
    - Gang-related crime is not a terrorism label. It is treated as an
      organized/group criminal activity pressure indicator.
    """

    expected_cols = [
        "county",
        "gang_related_total_crime_count",
        "gang_related_violent_crime_count",
        "gang_related_weapon_law_violation_count",
        "gang_related_drug_offense_count",
        "gang_related_property_offense_count",
        "gang_related_homicide_count",
        "gang_related_kidnapping_abduction_count",
        "gang_related_aggravated_assault_count",
        "gang_related_robbery_count",
        "gang_related_arson_count",
        "gang_related_sex_offense_count",
    ]

    return _load_optional_county_aggregate(
        county_base=county_base,
        input_path=OPTIONAL_GANG_ACTIVITY_INPUT,
        expected_cols=expected_cols,
        source_name="TBI gang-related criminal activity",
        availability_flag="gang_activity_data_available",
    )


def load_optional_explosives_activity_inputs(county_base: pd.DataFrame) -> pd.DataFrame:
    """
    Optional TBI explosive-use criminal activity input.

    Produced by:
    python -m src.explosives_processor

    Notes:
    - County-level aggregate counts only.
    - Do not include incident-level, address-level, suspect/victim, or case-level detail.
    - Explosive-use activity is not a terrorism label. It is treated as a
      high-severity criminal activity / capability indicator.
    """

    expected_cols = [
        "county",
        "explosive_related_total_offense_count",
        "explosive_related_violent_offense_count",
        "explosive_related_weapon_law_violation_count",
        "explosive_related_drug_offense_count",
        "explosive_related_property_offense_count",
        "explosive_related_homicide_count",
        "explosive_related_kidnapping_abduction_count",
        "explosive_related_aggravated_assault_count",
        "explosive_related_robbery_count",
        "explosive_related_arson_count",
        "explosive_related_sex_offense_count",
        "explosive_related_property_damage_count",
    ]

    return _load_optional_county_aggregate(
        county_base=county_base,
        input_path=OPTIONAL_EXPLOSIVES_ACTIVITY_INPUT,
        expected_cols=expected_cols,
        source_name="TBI explosive-use criminal activity",
        availability_flag="explosives_activity_data_available",
    )


def load_optional_gang_explosives_activity_inputs(
    county_base: pd.DataFrame,
) -> pd.DataFrame:
    """
    Optional TBI gang-related explosive-use criminal activity input.

    Produced by:
    python -m src.gang_explosives_processor

    Notes:
    - County-level aggregate counts only.
    - Do not include gang names, individual names, incident IDs, addresses,
      suspect/victim details, coordinates, organization names, or case narratives.
    - Gang-related explosive-use crime is not a terrorism label. It is treated as
      a high-severity organized/group criminal activity and explosive-use
      intersection indicator.
    """

    expected_cols = [
        "county",
        "gang_explosive_total_offense_count",
        "gang_explosive_violent_offense_count",
        "gang_explosive_weapon_law_violation_count",
        "gang_explosive_drug_offense_count",
        "gang_explosive_property_offense_count",
        "gang_explosive_homicide_count",
        "gang_explosive_kidnapping_abduction_count",
        "gang_explosive_aggravated_assault_count",
        "gang_explosive_robbery_count",
        "gang_explosive_arson_count",
        "gang_explosive_sex_offense_count",
        "gang_explosive_property_damage_count",
    ]

    return _load_optional_county_aggregate(
        county_base=county_base,
        input_path=OPTIONAL_GANG_EXPLOSIVES_ACTIVITY_INPUT,
        expected_cols=expected_cols,
        source_name="TBI gang-related explosive-use criminal activity",
        availability_flag="gang_explosives_activity_data_available",
    )


def load_optional_hate_crime_offense_inputs(
    county_base: pd.DataFrame,
) -> pd.DataFrame:
    """
    Optional TBI hate-crime offense aggregate input.

    Produced by:
    python -m src.hate_crime_processor

    Notes:
    - County-level aggregate counts only.
    - Do not include victim details, suspect details, incident IDs, addresses,
      narratives, bias-detail notes, coordinates, agency case-level records,
      or individual-level data.
    - Hate-crime offense counts are treated as targeted-harm / bias-motivated
      offense pressure indicators, not as terrorism indicators.
    """

    expected_cols = [
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

    return _load_optional_county_aggregate(
        county_base=county_base,
        input_path=OPTIONAL_HATE_CRIME_OFFENSE_INPUT,
        expected_cols=expected_cols,
        source_name="TBI hate-crime offense activity",
        availability_flag="hate_crime_offense_data_available",
    )


def load_optional_law_enforcement_ambush_inputs(
    county_base: pd.DataFrame,
) -> pd.DataFrame:
    """
    Optional TBI law-enforcement ambush aggregate input.

    Produced by:
    python -m src.law_enforcement_ambush_processor

    Notes:
    - County-level aggregate counts only.
    - Do not include officer names, suspect details, incident IDs, addresses,
      agency-level tactical details, coordinates, narratives, or case-level records.
    - Law-enforcement ambush counts are treated as a public-safety personnel
      violence / tactical-planning proxy. They are not terrorism indicators by
      themselves and do not infer motive, ideology, or actor identity.
    """

    expected_cols = [
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

    return _load_optional_county_aggregate(
        county_base=county_base,
        input_path=OPTIONAL_LAW_ENFORCEMENT_AMBUSH_INPUT,
        expected_cols=expected_cols,
        source_name="TBI law-enforcement ambush activity",
        availability_flag="law_enforcement_ambush_data_available",
    )