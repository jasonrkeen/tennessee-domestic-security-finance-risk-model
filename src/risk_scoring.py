import numpy as np
import pandas as pd

from src.config import TABLES_DIR
from src.data_quality import add_data_quality_flags, save_data_quality_outputs


def minmax_score(series: pd.Series, invert: bool = False) -> pd.Series:
    """
    Convert a numeric series into a 0-100 min-max score.

    If all values are the same, assign a neutral score of 50.
    """

    s = (
        pd.to_numeric(series, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    min_val = s.min()
    max_val = s.max()

    if max_val == min_val:
        score = pd.Series(50, index=s.index, dtype=float)
    else:
        score = 100 * (s - min_val) / (max_val - min_val)

    if invert:
        score = 100 - score

    return score.clip(0, 100)


def per_capita(
    df: pd.DataFrame,
    col: str,
    population_col: str = "population",
    scale: int = 10000,
) -> pd.Series:
    """
    Convert a count column into a per-capita rate.

    Default scale is per 10,000 residents.
    """

    pop = pd.to_numeric(df[population_col], errors="coerce").replace(0, np.nan)

    return (
        pd.to_numeric(df[col], errors="coerce")
        .fillna(0)
        .divide(pop)
        .multiply(scale)
        .fillna(0)
    )


def _ensure_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Ensure required columns exist and are numeric.
    """

    output = df.copy()

    for col in columns:
        if col not in output.columns:
            output[col] = 0

    output[columns] = output[columns].apply(pd.to_numeric, errors="coerce").fillna(0)

    return output


def _add_per_capita_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Add per-10k columns in one concat operation to avoid dataframe fragmentation.
    """

    per_capita_df = pd.DataFrame(index=df.index)

    for col in columns:
        per_capita_df[f"{col}_per_10k"] = per_capita(df, col)

    return pd.concat([df, per_capita_df], axis=1)


def _save_table(df: pd.DataFrame, cols: list[str], filename: str) -> None:
    """
    Save selected columns that exist.
    """

    existing_cols = [col for col in cols if col in df.columns]

    df[existing_cols].to_csv(
        TABLES_DIR / filename,
        index=False,
    )


def _has_positive_signal(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    """
    Return row-level indicator that at least one selected source field is positive.
    """

    existing_cols = [col for col in cols if col in df.columns]

    if not existing_cols:
        return pd.Series(False, index=df.index)

    return df[existing_cols].sum(axis=1) > 0


def build_scores(master_df: pd.DataFrame) -> pd.DataFrame:
    df = master_df.copy()

    establishment_cols = [
        "tobacco_vape_establishments",
        "sporting_goods_establishments",
        "used_merchandise_establishments",
        "gasoline_station_establishments",
        "convenience_store_establishments",
        "consumer_lending_establishments",
        "laundry_service_establishments",
        "used_auto_dealer_establishments",
    ]

    tactical_cols = [
        "ffl_count",
        "dealer_ffl_count",
        "manufacturer_ffl_count",
        "pawnbroker_ffl_count",
        "collector_ffl_count",
        "importer_ffl_count",
        "destructive_device_ffl_count",
        "tactical_training_count",
        "surplus_tactical_retail_count",
        "gun_range_count",
    ]

    banking_cols = [
        "bank_branch_count",
        "total_deposits_thousands",
    ]

    disaster_cols = [
        "disaster_declaration_count",
        "unique_disaster_types",
        "recent_disaster_declaration_count",
    ]

    disaster_disruption_cols = [
        "severe_storm_event_count",
        "flood_event_count",
        "tornado_event_count",
        "winter_weather_event_count",
        "wildfire_event_count",
        "drought_event_count",
        "power_outage_event_count",
        "avg_outage_duration_hours",
        "hospital_access_stress_score",
        "airport_access_stress_score",
        "road_access_stress_score",
        "communications_disruption_score",
        "social_vulnerability_score",
        "recovery_strain_score",
        "repeat_disruption_exposure_score",
    ]

    crime_cols = [
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

    crime_rate_cols = [
        "overall_crime_rate_per_1000_2024",
        "overall_crime_count_2024",
        "crime_population_2024",
    ]

    political_violence_cols = [
        "protest_event_count",
        "violent_unrest_event_count",
        "political_violence_event_count",
        "strategic_development_count",
        "public_disorder_event_count",
        "total_acled_event_count",
        "acled_fatalities",
    ]

    gang_cols = [
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

    explosives_cols = [
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

    gang_explosives_cols = [
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

    hate_crime_cols = [
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

    le_ambush_cols = [
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

    socioeconomic_cols = [
        "population",
        "poverty_rate",
        "unemployment_rate",
        "median_household_income",
        "rent_burden_rate",
    ]

    required_numeric_cols = (
        establishment_cols
        + tactical_cols
        + banking_cols
        + disaster_cols
        + disaster_disruption_cols
        + crime_cols
        + crime_rate_cols
        + political_violence_cols
        + gang_cols
        + explosives_cols
        + gang_explosives_cols
        + hate_crime_cols
        + le_ambush_cols
        + socioeconomic_cols
    )

    df = _ensure_numeric_columns(df, required_numeric_cols)

    # Add per-capita columns in bulk.
    # crime_population_2024 and stress-score fields are intentionally not
    # converted to per-capita.
    df = _add_per_capita_columns(
        df,
        establishment_cols
        + tactical_cols
        + crime_cols
        + political_violence_cols
        + gang_cols
        + explosives_cols
        + gang_explosives_cols
        + hate_crime_cols
        + le_ambush_cols
        + [
            "severe_storm_event_count",
            "flood_event_count",
            "tornado_event_count",
            "winter_weather_event_count",
            "wildfire_event_count",
            "drought_event_count",
            "power_outage_event_count",
        ],
    )

    # ------------------------------------------------------------------
    # Socioeconomic / household financial stress
    # ------------------------------------------------------------------
    socioeconomic_scores = pd.DataFrame(index=df.index)

    socioeconomic_scores["poverty_score"] = minmax_score(df["poverty_rate"])
    socioeconomic_scores["unemployment_score"] = minmax_score(df["unemployment_rate"])
    socioeconomic_scores["income_stress_score"] = minmax_score(
        df["median_household_income"],
        invert=True,
    )
    socioeconomic_scores["rent_burden_score"] = minmax_score(df["rent_burden_rate"])

    socioeconomic_scores["household_financial_stress_score"] = (
        0.35 * socioeconomic_scores["poverty_score"]
        + 0.25 * socioeconomic_scores["unemployment_score"]
        + 0.25 * socioeconomic_scores["income_stress_score"]
        + 0.15 * socioeconomic_scores["rent_burden_score"]
    )

    df = pd.concat([df, socioeconomic_scores], axis=1)

    # ------------------------------------------------------------------
    # Formal banking access / financial system depth
    # ------------------------------------------------------------------
    banking_scores = pd.DataFrame(index=df.index)

    banking_scores["bank_branch_count_per_10k"] = per_capita(
        df,
        "bank_branch_count",
    )

    banking_scores["total_deposits_dollars"] = (
        pd.to_numeric(df["total_deposits_thousands"], errors="coerce").fillna(0)
        * 1000
    )

    population_nonzero = (
        pd.to_numeric(df["population"], errors="coerce")
        .replace(0, np.nan)
    )

    banking_scores["deposits_per_capita"] = (
        banking_scores["total_deposits_dollars"]
        .divide(population_nonzero)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    banking_scores["low_branch_access_score"] = minmax_score(
        banking_scores["bank_branch_count_per_10k"],
        invert=True,
    )

    banking_scores["low_deposit_depth_score"] = minmax_score(
        banking_scores["deposits_per_capita"],
        invert=True,
    )

    banking_scores["banking_access_gap_score"] = (
        0.60 * banking_scores["low_branch_access_score"]
        + 0.40 * banking_scores["low_deposit_depth_score"]
    )

    df = pd.concat([df, banking_scores], axis=1)

    # ------------------------------------------------------------------
    # Cash-intensive retail exposure
    # ------------------------------------------------------------------
    cash_cols = [
        "used_merchandise_establishments_per_10k",
        "gasoline_station_establishments_per_10k",
        "convenience_store_establishments_per_10k",
        "consumer_lending_establishments_per_10k",
        "laundry_service_establishments_per_10k",
        "used_auto_dealer_establishments_per_10k",
    ]

    cash_scores = pd.DataFrame(index=df.index)

    for col in cash_cols:
        cash_scores[f"{col}_score"] = minmax_score(df[col])

    cash_scores["cash_intensive_retail_score"] = cash_scores[
        [f"{col}_score" for col in cash_cols]
    ].mean(axis=1)

    df = pd.concat([df, cash_scores], axis=1)

    # ------------------------------------------------------------------
    # Tobacco / vape regulated retail exposure
    # ------------------------------------------------------------------
    tobacco_scores = pd.DataFrame(index=df.index)

    tobacco_scores["tobacco_vape_density_score"] = minmax_score(
        df["tobacco_vape_establishments_per_10k"]
    )

    tobacco_scores["poverty_adjusted_tobacco_vape_score"] = (
        0.60 * tobacco_scores["tobacco_vape_density_score"]
        + 0.40 * df["poverty_score"]
    )

    df = pd.concat([df, tobacco_scores], axis=1)

    # ------------------------------------------------------------------
    # Tactical access exposure
    # ------------------------------------------------------------------
    tactical_scores = pd.DataFrame(index=df.index)

    tactical_scores["sporting_goods_density_score"] = minmax_score(
        df["sporting_goods_establishments_per_10k"]
    )

    tactical_scores["ffl_density_score"] = minmax_score(df["ffl_count_per_10k"])
    tactical_scores["dealer_ffl_density_score"] = minmax_score(
        df["dealer_ffl_count_per_10k"]
    )
    tactical_scores["manufacturer_ffl_density_score"] = minmax_score(
        df["manufacturer_ffl_count_per_10k"]
    )
    tactical_scores["pawnbroker_ffl_density_score"] = minmax_score(
        df["pawnbroker_ffl_count_per_10k"]
    )
    tactical_scores["collector_ffl_density_score"] = minmax_score(
        df["collector_ffl_count_per_10k"]
    )
    tactical_scores["importer_ffl_density_score"] = minmax_score(
        df["importer_ffl_count_per_10k"]
    )
    tactical_scores["destructive_device_ffl_density_score"] = minmax_score(
        df["destructive_device_ffl_count_per_10k"]
    )

    tactical_scores["training_density_score"] = minmax_score(
        df["tactical_training_count_per_10k"]
    )
    tactical_scores["surplus_tactical_density_score"] = minmax_score(
        df["surplus_tactical_retail_count_per_10k"]
    )
    tactical_scores["gun_range_density_score"] = minmax_score(
        df["gun_range_count_per_10k"]
    )

    tactical_scores["ffl_subtype_score"] = (
        0.35 * tactical_scores["dealer_ffl_density_score"]
        + 0.17 * tactical_scores["manufacturer_ffl_density_score"]
        + 0.17 * tactical_scores["pawnbroker_ffl_density_score"]
        + 0.12 * tactical_scores["collector_ffl_density_score"]
        + 0.09 * tactical_scores["importer_ffl_density_score"]
        + 0.10 * tactical_scores["destructive_device_ffl_density_score"]
    )

    tactical_scores["tactical_access_score"] = (
        0.20 * tactical_scores["sporting_goods_density_score"]
        + 0.25 * tactical_scores["ffl_density_score"]
        + 0.20 * tactical_scores["ffl_subtype_score"]
        + 0.15 * tactical_scores["training_density_score"]
        + 0.10 * tactical_scores["surplus_tactical_density_score"]
        + 0.10 * tactical_scores["gun_range_density_score"]
    )

    df = pd.concat([df, tactical_scores], axis=1)

    # ------------------------------------------------------------------
    # TBI CrimeInsight / crime-weapons pressure
    # ------------------------------------------------------------------
    crime_scores = pd.DataFrame(index=df.index)

    crime_scores["homicide_rate_per_10k"] = df["homicide_count_per_10k"]
    crime_scores["kidnapping_abduction_rate_per_10k"] = df[
        "kidnapping_abduction_count_per_10k"
    ]
    crime_scores["weapons_law_violation_rate_per_10k"] = df[
        "weapons_law_violation_count_per_10k"
    ]
    crime_scores["violent_crime_rate_per_10k"] = df["violent_crime_count_per_10k"]
    crime_scores["aggravated_assault_rate_per_10k"] = df[
        "aggravated_assault_count_per_10k"
    ]
    crime_scores["arson_rate_per_10k"] = df["arson_count_per_10k"]
    crime_scores["sex_offense_rate_per_10k"] = df["sex_offense_count_per_10k"]
    crime_scores["hate_crime_rate_per_10k"] = df["hate_crime_count_per_10k"]
    crime_scores["law_enforcement_assault_rate_per_10k"] = df[
        "law_enforcement_assault_count_per_10k"
    ]

    crime_scores["homicide_pressure_score"] = minmax_score(
        crime_scores["homicide_rate_per_10k"]
    )
    crime_scores["kidnapping_abduction_pressure_score"] = minmax_score(
        crime_scores["kidnapping_abduction_rate_per_10k"]
    )
    crime_scores["weapons_law_violation_pressure_score"] = minmax_score(
        crime_scores["weapons_law_violation_rate_per_10k"]
    )
    crime_scores["violent_crime_pressure_score"] = minmax_score(
        crime_scores["violent_crime_rate_per_10k"]
    )
    crime_scores["aggravated_assault_pressure_score"] = minmax_score(
        crime_scores["aggravated_assault_rate_per_10k"]
    )
    crime_scores["arson_pressure_score"] = minmax_score(
        crime_scores["arson_rate_per_10k"]
    )
    crime_scores["sex_offense_pressure_score"] = minmax_score(
        crime_scores["sex_offense_rate_per_10k"]
    )
    crime_scores["hate_crime_pressure_score"] = minmax_score(
        crime_scores["hate_crime_rate_per_10k"]
    )
    crime_scores["law_enforcement_assault_pressure_score"] = minmax_score(
        crime_scores["law_enforcement_assault_rate_per_10k"]
    )

    crime_scores["violent_crime_weapons_pressure_score"] = (
        0.30 * crime_scores["weapons_law_violation_pressure_score"]
        + 0.20 * crime_scores["violent_crime_pressure_score"]
        + 0.15 * crime_scores["aggravated_assault_pressure_score"]
        + 0.15 * crime_scores["homicide_pressure_score"]
        + 0.10 * crime_scores["kidnapping_abduction_pressure_score"]
        + 0.05 * crime_scores["arson_pressure_score"]
        + 0.03 * crime_scores["sex_offense_pressure_score"]
        + 0.01 * crime_scores["hate_crime_pressure_score"]
        + 0.01 * crime_scores["law_enforcement_assault_pressure_score"]
    )

    df = pd.concat([df, crime_scores], axis=1)

    # ------------------------------------------------------------------
    # TBI overall crime-rate pressure
    # ------------------------------------------------------------------
    crime_rate_scores = pd.DataFrame(index=df.index)

    crime_rate_scores["overall_crime_rate_pressure_score"] = minmax_score(
        df["overall_crime_rate_per_1000_2024"]
    )

    crime_rate_scores["overall_crime_count_pressure_score"] = minmax_score(
        per_capita(df, "overall_crime_count_2024")
    )

    crime_rate_scores["overall_crime_rate_index_score"] = (
        0.70 * crime_rate_scores["overall_crime_rate_pressure_score"]
        + 0.30 * crime_rate_scores["overall_crime_count_pressure_score"]
    )

    df = pd.concat([df, crime_rate_scores], axis=1)

    # ------------------------------------------------------------------
    # TBI gang-related criminal activity pressure
    # ------------------------------------------------------------------
    gang_scores = pd.DataFrame(index=df.index)

    gang_scores["gang_related_total_crime_rate_per_10k"] = df[
        "gang_related_total_crime_count_per_10k"
    ]
    gang_scores["gang_related_violent_crime_rate_per_10k"] = df[
        "gang_related_violent_crime_count_per_10k"
    ]
    gang_scores["gang_related_weapon_law_rate_per_10k"] = df[
        "gang_related_weapon_law_violation_count_per_10k"
    ]
    gang_scores["gang_related_drug_offense_rate_per_10k"] = df[
        "gang_related_drug_offense_count_per_10k"
    ]
    gang_scores["gang_related_homicide_rate_per_10k"] = df[
        "gang_related_homicide_count_per_10k"
    ]
    gang_scores["gang_related_aggravated_assault_rate_per_10k"] = df[
        "gang_related_aggravated_assault_count_per_10k"
    ]
    gang_scores["gang_related_robbery_rate_per_10k"] = df[
        "gang_related_robbery_count_per_10k"
    ]

    gang_scores["gang_related_total_pressure_score"] = minmax_score(
        gang_scores["gang_related_total_crime_rate_per_10k"]
    )
    gang_scores["gang_related_violent_pressure_score"] = minmax_score(
        gang_scores["gang_related_violent_crime_rate_per_10k"]
    )
    gang_scores["gang_related_weapon_law_pressure_score"] = minmax_score(
        gang_scores["gang_related_weapon_law_rate_per_10k"]
    )
    gang_scores["gang_related_drug_pressure_score"] = minmax_score(
        gang_scores["gang_related_drug_offense_rate_per_10k"]
    )
    gang_scores["gang_related_homicide_pressure_score"] = minmax_score(
        gang_scores["gang_related_homicide_rate_per_10k"]
    )
    gang_scores["gang_related_aggravated_assault_pressure_score"] = minmax_score(
        gang_scores["gang_related_aggravated_assault_rate_per_10k"]
    )
    gang_scores["gang_related_robbery_pressure_score"] = minmax_score(
        gang_scores["gang_related_robbery_rate_per_10k"]
    )

    gang_scores["gang_related_crime_pressure_score"] = (
        0.25 * gang_scores["gang_related_total_pressure_score"]
        + 0.25 * gang_scores["gang_related_violent_pressure_score"]
        + 0.20 * gang_scores["gang_related_weapon_law_pressure_score"]
        + 0.10 * gang_scores["gang_related_drug_pressure_score"]
        + 0.10 * gang_scores["gang_related_homicide_pressure_score"]
        + 0.05 * gang_scores["gang_related_aggravated_assault_pressure_score"]
        + 0.05 * gang_scores["gang_related_robbery_pressure_score"]
    )

    df = pd.concat([df, gang_scores], axis=1)

    # ------------------------------------------------------------------
    # TBI explosive-use criminal activity pressure
    # ------------------------------------------------------------------
    explosive_scores = pd.DataFrame(index=df.index)

    explosive_scores["explosive_related_total_rate_per_10k"] = df[
        "explosive_related_total_offense_count_per_10k"
    ]
    explosive_scores["explosive_related_violent_rate_per_10k"] = df[
        "explosive_related_violent_offense_count_per_10k"
    ]
    explosive_scores["explosive_related_weapon_law_rate_per_10k"] = df[
        "explosive_related_weapon_law_violation_count_per_10k"
    ]
    explosive_scores["explosive_related_homicide_rate_per_10k"] = df[
        "explosive_related_homicide_count_per_10k"
    ]
    explosive_scores["explosive_related_arson_rate_per_10k"] = df[
        "explosive_related_arson_count_per_10k"
    ]
    explosive_scores["explosive_related_property_damage_rate_per_10k"] = df[
        "explosive_related_property_damage_count_per_10k"
    ]

    explosive_scores["explosive_related_total_pressure_score"] = minmax_score(
        explosive_scores["explosive_related_total_rate_per_10k"]
    )
    explosive_scores["explosive_related_violent_pressure_score"] = minmax_score(
        explosive_scores["explosive_related_violent_rate_per_10k"]
    )
    explosive_scores["explosive_related_weapon_law_pressure_score"] = minmax_score(
        explosive_scores["explosive_related_weapon_law_rate_per_10k"]
    )
    explosive_scores["explosive_related_homicide_pressure_score"] = minmax_score(
        explosive_scores["explosive_related_homicide_rate_per_10k"]
    )
    explosive_scores["explosive_related_arson_pressure_score"] = minmax_score(
        explosive_scores["explosive_related_arson_rate_per_10k"]
    )
    explosive_scores["explosive_related_property_damage_pressure_score"] = minmax_score(
        explosive_scores["explosive_related_property_damage_rate_per_10k"]
    )

    explosive_scores["explosive_related_pressure_score"] = (
        0.25 * explosive_scores["explosive_related_total_pressure_score"]
        + 0.20 * explosive_scores["explosive_related_violent_pressure_score"]
        + 0.20 * explosive_scores["explosive_related_weapon_law_pressure_score"]
        + 0.15 * explosive_scores["explosive_related_homicide_pressure_score"]
        + 0.10 * explosive_scores["explosive_related_arson_pressure_score"]
        + 0.10 * explosive_scores["explosive_related_property_damage_pressure_score"]
    )

    df = pd.concat([df, explosive_scores], axis=1)

    # ------------------------------------------------------------------
    # TBI gang + explosive-use intersection pressure
    # ------------------------------------------------------------------
    gang_explosive_scores = pd.DataFrame(index=df.index)

    gang_explosive_scores["gang_explosive_total_rate_per_10k"] = df[
        "gang_explosive_total_offense_count_per_10k"
    ]
    gang_explosive_scores["gang_explosive_violent_rate_per_10k"] = df[
        "gang_explosive_violent_offense_count_per_10k"
    ]
    gang_explosive_scores["gang_explosive_weapon_law_rate_per_10k"] = df[
        "gang_explosive_weapon_law_violation_count_per_10k"
    ]
    gang_explosive_scores["gang_explosive_homicide_rate_per_10k"] = df[
        "gang_explosive_homicide_count_per_10k"
    ]
    gang_explosive_scores["gang_explosive_arson_rate_per_10k"] = df[
        "gang_explosive_arson_count_per_10k"
    ]
    gang_explosive_scores["gang_explosive_property_damage_rate_per_10k"] = df[
        "gang_explosive_property_damage_count_per_10k"
    ]

    gang_explosive_scores["gang_explosive_total_pressure_score"] = minmax_score(
        gang_explosive_scores["gang_explosive_total_rate_per_10k"]
    )
    gang_explosive_scores["gang_explosive_violent_pressure_score"] = minmax_score(
        gang_explosive_scores["gang_explosive_violent_rate_per_10k"]
    )
    gang_explosive_scores["gang_explosive_weapon_law_pressure_score"] = minmax_score(
        gang_explosive_scores["gang_explosive_weapon_law_rate_per_10k"]
    )
    gang_explosive_scores["gang_explosive_homicide_pressure_score"] = minmax_score(
        gang_explosive_scores["gang_explosive_homicide_rate_per_10k"]
    )
    gang_explosive_scores["gang_explosive_arson_pressure_score"] = minmax_score(
        gang_explosive_scores["gang_explosive_arson_rate_per_10k"]
    )
    gang_explosive_scores["gang_explosive_property_damage_pressure_score"] = minmax_score(
        gang_explosive_scores["gang_explosive_property_damage_rate_per_10k"]
    )

    gang_explosive_scores["gang_explosive_pressure_score"] = (
        0.25 * gang_explosive_scores["gang_explosive_total_pressure_score"]
        + 0.20 * gang_explosive_scores["gang_explosive_violent_pressure_score"]
        + 0.20 * gang_explosive_scores["gang_explosive_weapon_law_pressure_score"]
        + 0.15 * gang_explosive_scores["gang_explosive_homicide_pressure_score"]
        + 0.10 * gang_explosive_scores["gang_explosive_arson_pressure_score"]
        + 0.10 * gang_explosive_scores["gang_explosive_property_damage_pressure_score"]
    )

    df = pd.concat([df, gang_explosive_scores], axis=1)

    # ------------------------------------------------------------------
    # TBI hate-crime offense / targeted-harm pressure
    # ------------------------------------------------------------------
    hate_scores = pd.DataFrame(index=df.index)

    hate_scores["hate_crime_total_rate_per_10k"] = df[
        "hate_crime_total_count_per_10k"
    ]
    hate_scores["hate_crime_violent_rate_per_10k"] = (
        df["hate_crime_homicide_count_per_10k"]
        + df["hate_crime_kidnapping_abduction_count_per_10k"]
        + df["hate_crime_aggravated_assault_count_per_10k"]
        + df["hate_crime_simple_assault_count_per_10k"]
    )
    hate_scores["hate_crime_intimidation_rate_per_10k"] = df[
        "hate_crime_intimidation_count_per_10k"
    ]
    hate_scores["hate_crime_weapon_law_rate_per_10k"] = df[
        "hate_crime_weapon_law_violation_count_per_10k"
    ]
    hate_scores["hate_crime_property_damage_rate_per_10k"] = df[
        "hate_crime_property_damage_count_per_10k"
    ]

    hate_scores["hate_crime_total_pressure_score"] = minmax_score(
        hate_scores["hate_crime_total_rate_per_10k"]
    )
    hate_scores["hate_crime_violent_pressure_score"] = minmax_score(
        hate_scores["hate_crime_violent_rate_per_10k"]
    )
    hate_scores["hate_crime_intimidation_pressure_score"] = minmax_score(
        hate_scores["hate_crime_intimidation_rate_per_10k"]
    )
    hate_scores["hate_crime_weapon_law_pressure_score"] = minmax_score(
        hate_scores["hate_crime_weapon_law_rate_per_10k"]
    )
    hate_scores["hate_crime_property_damage_pressure_score"] = minmax_score(
        hate_scores["hate_crime_property_damage_rate_per_10k"]
    )

    hate_scores["hate_crime_targeted_harm_pressure_score"] = (
        0.30 * hate_scores["hate_crime_total_pressure_score"]
        + 0.25 * hate_scores["hate_crime_violent_pressure_score"]
        + 0.25 * hate_scores["hate_crime_intimidation_pressure_score"]
        + 0.10 * hate_scores["hate_crime_weapon_law_pressure_score"]
        + 0.10 * hate_scores["hate_crime_property_damage_pressure_score"]
    )

    df = pd.concat([df, hate_scores], axis=1)

    # ------------------------------------------------------------------
    # TBI law-enforcement ambush / public-safety personnel violence proxy
    # ------------------------------------------------------------------
    le_ambush_scores = pd.DataFrame(index=df.index)

    le_ambush_scores["le_ambush_total_rate_per_10k"] = df[
        "le_ambush_total_count_per_10k"
    ]
    le_ambush_scores["le_ambush_violent_rate_per_10k"] = (
        df["le_ambush_homicide_count_per_10k"]
        + df["le_ambush_kidnapping_abduction_count_per_10k"]
        + df["le_ambush_aggravated_assault_count_per_10k"]
        + df["le_ambush_simple_assault_count_per_10k"]
    )
    le_ambush_scores["le_ambush_weapon_law_rate_per_10k"] = df[
        "le_ambush_weapon_law_violation_count_per_10k"
    ]
    le_ambush_scores["le_ambush_intimidation_rate_per_10k"] = df[
        "le_ambush_intimidation_count_per_10k"
    ]
    le_ambush_scores["le_ambush_property_damage_rate_per_10k"] = df[
        "le_ambush_property_damage_count_per_10k"
    ]

    le_ambush_scores["le_ambush_total_pressure_score"] = minmax_score(
        le_ambush_scores["le_ambush_total_rate_per_10k"]
    )
    le_ambush_scores["le_ambush_violent_pressure_score"] = minmax_score(
        le_ambush_scores["le_ambush_violent_rate_per_10k"]
    )
    le_ambush_scores["le_ambush_weapon_law_pressure_score"] = minmax_score(
        le_ambush_scores["le_ambush_weapon_law_rate_per_10k"]
    )
    le_ambush_scores["le_ambush_intimidation_pressure_score"] = minmax_score(
        le_ambush_scores["le_ambush_intimidation_rate_per_10k"]
    )
    le_ambush_scores["le_ambush_property_damage_pressure_score"] = minmax_score(
        le_ambush_scores["le_ambush_property_damage_rate_per_10k"]
    )

    le_ambush_scores["law_enforcement_ambush_pressure_score"] = (
        0.35 * le_ambush_scores["le_ambush_total_pressure_score"]
        + 0.30 * le_ambush_scores["le_ambush_violent_pressure_score"]
        + 0.20 * le_ambush_scores["le_ambush_weapon_law_pressure_score"]
        + 0.10 * le_ambush_scores["le_ambush_intimidation_pressure_score"]
        + 0.05 * le_ambush_scores["le_ambush_property_damage_pressure_score"]
    )

    df = pd.concat([df, le_ambush_scores], axis=1)

    # ------------------------------------------------------------------
    # Targeted harm / public-safety pressure
    # ------------------------------------------------------------------
    targeted_harm_scores = pd.DataFrame(index=df.index)

    targeted_harm_scores["targeted_harm_public_safety_pressure_score"] = (
        0.55 * df["hate_crime_targeted_harm_pressure_score"]
        + 0.45 * df["law_enforcement_ambush_pressure_score"]
    )

    df = pd.concat([df, targeted_harm_scores], axis=1)

    # ------------------------------------------------------------------
    # Organized violence / high-severity crime pressure
    # ------------------------------------------------------------------
    organized_scores = pd.DataFrame(index=df.index)

    organized_scores["organized_violence_pressure_score"] = (
        0.30 * df["violent_crime_weapons_pressure_score"]
        + 0.15 * df["overall_crime_rate_index_score"]
        + 0.18 * df["gang_related_crime_pressure_score"]
        + 0.13 * df["explosive_related_pressure_score"]
        + 0.13 * df["gang_explosive_pressure_score"]
        + 0.11 * df["targeted_harm_public_safety_pressure_score"]
    )

    df = pd.concat([df, organized_scores], axis=1)

    # ------------------------------------------------------------------
    # ACLED political violence / civil unrest exposure
    # ------------------------------------------------------------------
    political_scores = pd.DataFrame(index=df.index)

    political_scores["protest_event_rate_per_10k"] = df[
        "protest_event_count_per_10k"
    ]
    political_scores["violent_unrest_event_rate_per_10k"] = df[
        "violent_unrest_event_count_per_10k"
    ]
    political_scores["political_violence_event_rate_per_10k"] = df[
        "political_violence_event_count_per_10k"
    ]
    political_scores["strategic_development_rate_per_10k"] = df[
        "strategic_development_count_per_10k"
    ]
    political_scores["public_disorder_event_rate_per_10k"] = df[
        "public_disorder_event_count_per_10k"
    ]
    political_scores["total_acled_event_rate_per_10k"] = df[
        "total_acled_event_count_per_10k"
    ]
    political_scores["acled_fatality_rate_per_10k"] = df[
        "acled_fatalities_per_10k"
    ]

    political_scores["protest_event_pressure_score"] = minmax_score(
        political_scores["protest_event_rate_per_10k"]
    )
    political_scores["violent_unrest_event_pressure_score"] = minmax_score(
        political_scores["violent_unrest_event_rate_per_10k"]
    )
    political_scores["political_violence_event_pressure_score"] = minmax_score(
        political_scores["political_violence_event_rate_per_10k"]
    )
    political_scores["strategic_development_pressure_score"] = minmax_score(
        political_scores["strategic_development_rate_per_10k"]
    )
    political_scores["public_disorder_event_pressure_score"] = minmax_score(
        political_scores["public_disorder_event_rate_per_10k"]
    )
    political_scores["total_acled_event_pressure_score"] = minmax_score(
        political_scores["total_acled_event_rate_per_10k"]
    )
    political_scores["acled_fatality_pressure_score"] = minmax_score(
        political_scores["acled_fatality_rate_per_10k"]
    )

    # ACLED layer:
    # - Protest and public disorder are broad civil-unrest exposure indicators.
    # - Violent unrest, political violence, and fatalities are weighted more heavily.
    # - Strategic developments are included cautiously as context, not as a direct threat signal.
    political_scores["political_violence_exposure_score"] = (
        0.20 * political_scores["protest_event_pressure_score"]
        + 0.20 * political_scores["public_disorder_event_pressure_score"]
        + 0.20 * political_scores["total_acled_event_pressure_score"]
        + 0.15 * political_scores["violent_unrest_event_pressure_score"]
        + 0.15 * political_scores["political_violence_event_pressure_score"]
        + 0.05 * political_scores["strategic_development_pressure_score"]
        + 0.05 * political_scores["acled_fatality_pressure_score"]
    )

    df = pd.concat([df, political_scores], axis=1)

    # ------------------------------------------------------------------
    # Disaster / infrastructure disruption exposure
    # ------------------------------------------------------------------
    disaster_scores = pd.DataFrame(index=df.index)

    disaster_scores["disaster_declaration_score"] = minmax_score(
        df["disaster_declaration_count"]
    )
    disaster_scores["disaster_type_diversity_score"] = minmax_score(
        df["unique_disaster_types"]
    )
    disaster_scores["recent_disaster_score"] = minmax_score(
        df["recent_disaster_declaration_count"]
    )

    disaster_scores["infrastructure_disruption_score"] = (
        0.50 * disaster_scores["disaster_declaration_score"]
        + 0.25 * disaster_scores["disaster_type_diversity_score"]
        + 0.25 * disaster_scores["recent_disaster_score"]
    )

    # Optional Phase 6 disaster / disruption vulnerability layer.
    # If the optional Phase 6 fields are all zero, the broader score defaults
    # to the existing FEMA-based infrastructure_disruption_score so the model
    # remains backward compatible.
    weather_event_cols = [
        "severe_storm_event_count",
        "flood_event_count",
        "tornado_event_count",
        "winter_weather_event_count",
        "wildfire_event_count",
        "drought_event_count",
    ]

    disaster_scores["severe_weather_event_rate_per_10k"] = (
        df["severe_storm_event_count_per_10k"]
        + df["flood_event_count_per_10k"]
        + df["tornado_event_count_per_10k"]
        + df["winter_weather_event_count_per_10k"]
        + df["wildfire_event_count_per_10k"]
        + df["drought_event_count_per_10k"]
    )

    disaster_scores["severe_weather_exposure_score"] = minmax_score(
        disaster_scores["severe_weather_event_rate_per_10k"]
    )

    disaster_scores["power_outage_event_rate_per_10k"] = df[
        "power_outage_event_count_per_10k"
    ]
    disaster_scores["power_outage_frequency_score"] = minmax_score(
        disaster_scores["power_outage_event_rate_per_10k"]
    )
    disaster_scores["outage_duration_score"] = minmax_score(
        df["avg_outage_duration_hours"]
    )
    disaster_scores["power_disruption_exposure_score"] = (
        0.60 * disaster_scores["power_outage_frequency_score"]
        + 0.40 * disaster_scores["outage_duration_score"]
    )

    disaster_scores["access_stress_score"] = (
        0.30 * minmax_score(df["hospital_access_stress_score"])
        + 0.25 * minmax_score(df["airport_access_stress_score"])
        + 0.25 * minmax_score(df["road_access_stress_score"])
        + 0.20 * minmax_score(df["communications_disruption_score"])
    )

    disaster_scores["recovery_strain_exposure_score"] = (
        0.45 * minmax_score(df["social_vulnerability_score"])
        + 0.35 * minmax_score(df["recovery_strain_score"])
        + 0.20 * minmax_score(df["repeat_disruption_exposure_score"])
    )

    phase6_positive_signal = (
        _has_positive_signal(df, weather_event_cols)
        | _has_positive_signal(df, ["power_outage_event_count"])
        | _has_positive_signal(
            df,
            [
                "avg_outage_duration_hours",
                "hospital_access_stress_score",
                "airport_access_stress_score",
                "road_access_stress_score",
                "communications_disruption_score",
                "social_vulnerability_score",
                "recovery_strain_score",
                "repeat_disruption_exposure_score",
            ],
        )
    )

    disaster_scores["disaster_disruption_vulnerability_score"] = (
        0.25 * disaster_scores["infrastructure_disruption_score"]
        + 0.20 * disaster_scores["severe_weather_exposure_score"]
        + 0.15 * disaster_scores["recent_disaster_score"]
        + 0.15 * disaster_scores["power_disruption_exposure_score"]
        + 0.15 * disaster_scores["access_stress_score"]
        + 0.10 * disaster_scores["recovery_strain_exposure_score"]
    )

    disaster_scores.loc[
        ~phase6_positive_signal,
        "disaster_disruption_vulnerability_score",
    ] = disaster_scores.loc[
        ~phase6_positive_signal,
        "infrastructure_disruption_score",
    ]

    df = pd.concat([df, disaster_scores], axis=1)

    # Defragment after all derived score blocks are added.
    df = df.copy()

    # ------------------------------------------------------------------
    # Institutional / enforcement pressure
    # ------------------------------------------------------------------
    final_scores = pd.DataFrame(index=df.index)

    final_scores["institutional_enforcement_pressure_score"] = (
        0.25 * df["law_enforcement_ambush_pressure_score"]
        + 0.20 * df["law_enforcement_assault_pressure_score"]
        + 0.20 * df["violent_crime_weapons_pressure_score"]
        + 0.15 * df["overall_crime_rate_index_score"]
        + 0.10 * df["targeted_harm_public_safety_pressure_score"]
        + 0.10 * df["disaster_disruption_vulnerability_score"]
    )

    # ------------------------------------------------------------------
    # Finance / tactical vulnerability score
    # ------------------------------------------------------------------
    final_scores["finance_tactical_vulnerability_score"] = (
        0.24 * df["household_financial_stress_score"]
        + 0.16 * df["banking_access_gap_score"]
        + 0.20 * df["cash_intensive_retail_score"]
        + 0.12 * df["poverty_adjusted_tobacco_vape_score"]
        + 0.20 * df["tactical_access_score"]
        + 0.08 * df["disaster_disruption_vulnerability_score"]
    )

    # ------------------------------------------------------------------
    # Final domestic security risk score
    # ------------------------------------------------------------------
    final_scores["final_domestic_security_risk_score"] = (
        0.30 * final_scores["finance_tactical_vulnerability_score"]
        + 0.20 * df["organized_violence_pressure_score"]
        + 0.15 * df["political_violence_exposure_score"]
        + 0.15 * df["household_financial_stress_score"]
        + 0.10 * df["disaster_disruption_vulnerability_score"]
        + 0.05 * df["tactical_access_score"]
        + 0.05 * final_scores["institutional_enforcement_pressure_score"]
    )

    final_scores["risk_signal"] = pd.cut(
        final_scores["final_domestic_security_risk_score"],
        bins=[-1, 35, 55, 70, 100],
        labels=["Low", "Guarded", "Elevated", "High"],
    ).astype(str)

    df = pd.concat([df, final_scores], axis=1)

    # Defragment before data-quality calculations and output.
    df = df.copy()

    # ------------------------------------------------------------------
    # Data quality / model confidence
    # ------------------------------------------------------------------
    df = add_data_quality_flags(df)
    save_data_quality_outputs(df)

    df = df.sort_values(
        "final_domestic_security_risk_score",
        ascending=False,
    )

    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Save full scored output
    # ------------------------------------------------------------------
    df.to_csv(
        TABLES_DIR / "tn_county_domestic_security_scores.csv",
        index=False,
    )

    # ------------------------------------------------------------------
    # Save component score table
    # ------------------------------------------------------------------
    component_cols = [
        "county",
        "population",
        "household_financial_stress_score",
        "banking_access_gap_score",
        "cash_intensive_retail_score",
        "poverty_adjusted_tobacco_vape_score",
        "tactical_access_score",
        "violent_crime_weapons_pressure_score",
        "overall_crime_rate_index_score",
        "gang_related_crime_pressure_score",
        "explosive_related_pressure_score",
        "gang_explosive_pressure_score",
        "hate_crime_targeted_harm_pressure_score",
        "law_enforcement_ambush_pressure_score",
        "targeted_harm_public_safety_pressure_score",
        "organized_violence_pressure_score",
        "political_violence_exposure_score",
        "disaster_declaration_score",
        "disaster_type_diversity_score",
        "recent_disaster_score",
        "infrastructure_disruption_score",
        "severe_weather_exposure_score",
        "power_disruption_exposure_score",
        "access_stress_score",
        "recovery_strain_exposure_score",
        "disaster_disruption_vulnerability_score",
        "finance_tactical_vulnerability_score",
        "institutional_enforcement_pressure_score",
        "final_domestic_security_risk_score",
        "risk_signal",
        "data_completeness_score",
        "model_confidence",
        "data_quality_note",
    ]

    _save_table(
        df=df,
        cols=component_cols,
        filename="tn_county_component_scores.csv",
    )

    # ------------------------------------------------------------------
    # Save finance / tactical table
    # ------------------------------------------------------------------
    finance_cols = [
        "county",
        "population",
        "poverty_rate",
        "unemployment_rate",
        "median_household_income",
        "rent_burden_rate",
        "bank_branch_count",
        "bank_branch_count_per_10k",
        "total_deposits_thousands",
        "deposits_per_capita",
        "banking_access_gap_score",
        "tobacco_vape_establishments",
        "sporting_goods_establishments",
        "used_merchandise_establishments",
        "gasoline_station_establishments",
        "convenience_store_establishments",
        "consumer_lending_establishments",
        "laundry_service_establishments",
        "used_auto_dealer_establishments",
        "ffl_count",
        "dealer_ffl_count",
        "manufacturer_ffl_count",
        "pawnbroker_ffl_count",
        "collector_ffl_count",
        "importer_ffl_count",
        "destructive_device_ffl_count",
        "tactical_training_count",
        "surplus_tactical_retail_count",
        "gun_range_count",
        "disaster_declaration_count",
        "unique_disaster_types",
        "recent_disaster_declaration_count",
        "disaster_disruption_vulnerability_score",
        "household_financial_stress_score",
        "cash_intensive_retail_score",
        "poverty_adjusted_tobacco_vape_score",
        "tactical_access_score",
        "infrastructure_disruption_score",
        "finance_tactical_vulnerability_score",
        "fdic_data_available",
        "ffl_data_available",
        "cbp_data_available",
        "fema_data_available",
        "crime_data_available",
        "data_completeness_score",
        "model_confidence",
        "data_quality_note",
    ]

    _save_table(
        df=df,
        cols=finance_cols,
        filename="tn_county_finance_tactical_scores.csv",
    )

    # ------------------------------------------------------------------
    # Save crime / weapons table
    # ------------------------------------------------------------------
    crime_cols_output = [
        "county",
        "population",
        "homicide_count",
        "kidnapping_abduction_count",
        "weapons_law_violation_count",
        "violent_crime_count",
        "aggravated_assault_count",
        "arson_count",
        "sex_offense_count",
        "hate_crime_count",
        "law_enforcement_assault_count",
        "homicide_rate_per_10k",
        "kidnapping_abduction_rate_per_10k",
        "weapons_law_violation_rate_per_10k",
        "violent_crime_rate_per_10k",
        "aggravated_assault_rate_per_10k",
        "arson_rate_per_10k",
        "sex_offense_rate_per_10k",
        "homicide_pressure_score",
        "kidnapping_abduction_pressure_score",
        "weapons_law_violation_pressure_score",
        "violent_crime_pressure_score",
        "aggravated_assault_pressure_score",
        "arson_pressure_score",
        "sex_offense_pressure_score",
        "overall_crime_rate_per_1000_2024",
        "overall_crime_count_2024",
        "overall_crime_rate_pressure_score",
        "overall_crime_count_pressure_score",
        "overall_crime_rate_index_score",
        "gang_related_total_crime_count",
        "gang_related_violent_crime_count",
        "gang_related_weapon_law_violation_count",
        "gang_related_crime_pressure_score",
        "explosive_related_total_offense_count",
        "explosive_related_violent_offense_count",
        "explosive_related_weapon_law_violation_count",
        "explosive_related_pressure_score",
        "gang_explosive_total_offense_count",
        "gang_explosive_violent_offense_count",
        "gang_explosive_weapon_law_violation_count",
        "gang_explosive_pressure_score",
        "hate_crime_total_count",
        "hate_crime_aggravated_assault_count",
        "hate_crime_simple_assault_count",
        "hate_crime_intimidation_count",
        "hate_crime_weapon_law_violation_count",
        "hate_crime_property_damage_count",
        "hate_crime_targeted_harm_pressure_score",
        "le_ambush_total_count",
        "le_ambush_aggravated_assault_count",
        "le_ambush_simple_assault_count",
        "le_ambush_intimidation_count",
        "le_ambush_weapon_law_violation_count",
        "law_enforcement_ambush_pressure_score",
        "targeted_harm_public_safety_pressure_score",
        "violent_crime_weapons_pressure_score",
        "organized_violence_pressure_score",
        "crime_data_available",
        "crime_rate_data_available",
        "gang_activity_data_available",
        "explosives_activity_data_available",
        "gang_explosives_activity_data_available",
        "crime_weapons_selected_total",
        "crime_true_zero_selected_categories",
        "data_completeness_score",
        "model_confidence",
        "data_quality_note",
    ]

    _save_table(
        df=df,
        cols=crime_cols_output,
        filename="tn_county_crime_weapons_scores.csv",
    )

    # ------------------------------------------------------------------
    # Save organized violence / explosives table
    # ------------------------------------------------------------------
    organized_cols_output = [
        "county",
        "population",
        "violent_crime_weapons_pressure_score",
        "overall_crime_rate_index_score",
        "gang_related_total_crime_count",
        "gang_related_violent_crime_count",
        "gang_related_weapon_law_violation_count",
        "gang_related_drug_offense_count",
        "gang_related_property_offense_count",
        "gang_related_crime_pressure_score",
        "explosive_related_total_offense_count",
        "explosive_related_violent_offense_count",
        "explosive_related_weapon_law_violation_count",
        "explosive_related_arson_count",
        "explosive_related_property_damage_count",
        "explosive_related_pressure_score",
        "gang_explosive_total_offense_count",
        "gang_explosive_violent_offense_count",
        "gang_explosive_weapon_law_violation_count",
        "gang_explosive_arson_count",
        "gang_explosive_property_damage_count",
        "gang_explosive_pressure_score",
        "hate_crime_total_count",
        "hate_crime_aggravated_assault_count",
        "hate_crime_simple_assault_count",
        "hate_crime_intimidation_count",
        "hate_crime_weapon_law_violation_count",
        "hate_crime_property_damage_count",
        "hate_crime_targeted_harm_pressure_score",
        "le_ambush_total_count",
        "le_ambush_aggravated_assault_count",
        "le_ambush_simple_assault_count",
        "le_ambush_intimidation_count",
        "le_ambush_weapon_law_violation_count",
        "law_enforcement_ambush_pressure_score",
        "targeted_harm_public_safety_pressure_score",
        "organized_violence_pressure_score",
        "gang_activity_data_available",
        "explosives_activity_data_available",
        "gang_explosives_activity_data_available",
        "data_completeness_score",
        "model_confidence",
        "data_quality_note",
    ]

    _save_table(
        df=df,
        cols=organized_cols_output,
        filename="tn_county_organized_violence_scores.csv",
    )

    # ------------------------------------------------------------------
    # Save targeted harm / public-safety personnel pressure table
    # ------------------------------------------------------------------
    targeted_harm_cols_output = [
        "county",
        "population",
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
        "hate_crime_total_rate_per_10k",
        "hate_crime_violent_rate_per_10k",
        "hate_crime_intimidation_rate_per_10k",
        "hate_crime_targeted_harm_pressure_score",
        "le_ambush_total_count",
        "le_ambush_homicide_count",
        "le_ambush_kidnapping_abduction_count",
        "le_ambush_aggravated_assault_count",
        "le_ambush_simple_assault_count",
        "le_ambush_intimidation_count",
        "le_ambush_weapon_law_violation_count",
        "le_ambush_arson_count",
        "le_ambush_property_damage_count",
        "le_ambush_total_rate_per_10k",
        "le_ambush_violent_rate_per_10k",
        "le_ambush_weapon_law_rate_per_10k",
        "law_enforcement_ambush_pressure_score",
        "targeted_harm_public_safety_pressure_score",
        "organized_violence_pressure_score",
        "data_completeness_score",
        "model_confidence",
        "data_quality_note",
    ]

    _save_table(
        df=df,
        cols=targeted_harm_cols_output,
        filename="tn_county_targeted_harm_public_safety_scores.csv",
    )

    # ------------------------------------------------------------------
    # Save disaster / disruption vulnerability table
    # ------------------------------------------------------------------
    disaster_cols_output = [
        "county",
        "population",
        "disaster_declaration_count",
        "unique_disaster_types",
        "recent_disaster_declaration_count",
        "severe_storm_event_count",
        "flood_event_count",
        "tornado_event_count",
        "winter_weather_event_count",
        "wildfire_event_count",
        "drought_event_count",
        "power_outage_event_count",
        "avg_outage_duration_hours",
        "hospital_access_stress_score",
        "airport_access_stress_score",
        "road_access_stress_score",
        "communications_disruption_score",
        "social_vulnerability_score",
        "recovery_strain_score",
        "repeat_disruption_exposure_score",
        "disaster_declaration_score",
        "disaster_type_diversity_score",
        "recent_disaster_score",
        "infrastructure_disruption_score",
        "severe_weather_exposure_score",
        "power_disruption_exposure_score",
        "access_stress_score",
        "recovery_strain_exposure_score",
        "disaster_disruption_vulnerability_score",
        "data_completeness_score",
        "model_confidence",
        "data_quality_note",
    ]

    _save_table(
        df=df,
        cols=disaster_cols_output,
        filename="tn_county_disaster_disruption_scores.csv",
    )

    # ------------------------------------------------------------------
    # Save institutional / enforcement pressure table
    # ------------------------------------------------------------------
    institutional_cols_output = [
        "county",
        "population",
        "law_enforcement_assault_count",
        "law_enforcement_assault_rate_per_10k",
        "law_enforcement_assault_pressure_score",
        "le_ambush_total_count",
        "le_ambush_total_rate_per_10k",
        "law_enforcement_ambush_pressure_score",
        "violent_crime_weapons_pressure_score",
        "overall_crime_rate_index_score",
        "targeted_harm_public_safety_pressure_score",
        "disaster_disruption_vulnerability_score",
        "institutional_enforcement_pressure_score",
        "final_domestic_security_risk_score",
        "risk_signal",
        "data_completeness_score",
        "model_confidence",
        "data_quality_note",
    ]

    _save_table(
        df=df,
        cols=institutional_cols_output,
        filename="tn_county_institutional_enforcement_scores.csv",
    )

    # ------------------------------------------------------------------
    # Save ACLED political violence / civil unrest table
    # ------------------------------------------------------------------
    political_cols_output = [
        "county",
        "population",
        "protest_event_count",
        "violent_unrest_event_count",
        "political_violence_event_count",
        "strategic_development_count",
        "public_disorder_event_count",
        "total_acled_event_count",
        "acled_fatalities",
        "protest_event_rate_per_10k",
        "violent_unrest_event_rate_per_10k",
        "political_violence_event_rate_per_10k",
        "strategic_development_rate_per_10k",
        "public_disorder_event_rate_per_10k",
        "total_acled_event_rate_per_10k",
        "acled_fatality_rate_per_10k",
        "protest_event_pressure_score",
        "violent_unrest_event_pressure_score",
        "political_violence_event_pressure_score",
        "strategic_development_pressure_score",
        "public_disorder_event_pressure_score",
        "total_acled_event_pressure_score",
        "acled_fatality_pressure_score",
        "political_violence_exposure_score",
        "data_completeness_score",
        "model_confidence",
        "data_quality_note",
    ]

    _save_table(
        df=df,
        cols=political_cols_output,
        filename="tn_county_political_violence_scores.csv",
    )

    return df
