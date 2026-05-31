import pandas as pd

from src.config import TABLES_DIR


def _has_positive_value(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """
    Return True if any supplied column has a positive numeric value.

    Useful for sources where zero generally means missing or zero-filled input.
    """

    existing_cols = [col for col in columns if col in df.columns]

    if not existing_cols:
        return pd.Series(False, index=df.index)

    numeric = df[existing_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    return numeric.gt(0).any(axis=1)


def _has_columns_present(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """
    Return True if at least one expected source column exists.

    This is useful for sources where a valid county can have true zero values
    in selected categories. In that case, zero is not necessarily missing data.
    """

    existing_cols = [col for col in columns if col in df.columns]

    if not existing_cols:
        return pd.Series(False, index=df.index)

    return pd.Series(True, index=df.index)


def _selected_total(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """
    Sum selected numeric source columns that exist.
    """

    existing_cols = [col for col in columns if col in df.columns]

    if not existing_cols:
        return pd.Series(0, index=df.index, dtype=float)

    return (
        df[existing_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .sum(axis=1)
    )


def add_data_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add county-level data availability and completeness indicators.

    These flags do not change the underlying raw values. They help interpret
    whether a county's score is based on complete data or if some source layers
    are missing/zero-filled.

    Notes:
    - Data completeness measures source coverage, not risk.
    - Many TBI and ACLED layers can be valid true-zero layers.
    - Institutional / enforcement pressure is now an active derived layer.
    """

    output = df.copy()

    # ------------------------------------------------------------------
    # Expected source-layer columns
    # ------------------------------------------------------------------
    acs_cols = [
        "population",
        "median_household_income",
        "poverty_rate",
        "unemployment_rate",
        "rent_burden_rate",
    ]

    cbp_cols = [
        "tobacco_vape_establishments",
        "sporting_goods_establishments",
        "used_merchandise_establishments",
        "gasoline_station_establishments",
        "convenience_store_establishments",
        "consumer_lending_establishments",
        "laundry_service_establishments",
        "used_auto_dealer_establishments",
    ]

    fdic_cols = [
        "bank_branch_count",
        "total_deposits_thousands",
    ]

    ffl_cols = [
        "ffl_count",
        "dealer_ffl_count",
        "manufacturer_ffl_count",
        "pawnbroker_ffl_count",
        "collector_ffl_count",
        "importer_ffl_count",
        "destructive_device_ffl_count",
    ]

    fema_cols = [
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

    hate_crime_offense_cols = [
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

    law_enforcement_ambush_cols = [
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

    targeted_harm_public_safety_cols = [
        "hate_crime_targeted_harm_pressure_score",
        "law_enforcement_ambush_pressure_score",
        "targeted_harm_public_safety_pressure_score",
    ]

    institutional_cols = [
        "law_enforcement_assault_pressure_score",
        "law_enforcement_ambush_pressure_score",
        "violent_crime_weapons_pressure_score",
        "overall_crime_rate_index_score",
        "targeted_harm_public_safety_pressure_score",
        "disaster_disruption_vulnerability_score",
        "institutional_enforcement_pressure_score",
    ]

    # ------------------------------------------------------------------
    # Source availability flags
    # ------------------------------------------------------------------
    output["acs_data_available"] = _has_positive_value(output, acs_cols)

    # CBP can legitimately be zero in smaller counties for selected NAICS.
    output["cbp_data_available"] = _has_columns_present(output, cbp_cols)

    output["fdic_data_available"] = _has_positive_value(output, fdic_cols)
    output["ffl_data_available"] = _has_positive_value(output, ffl_cols)
    output["fema_data_available"] = _has_positive_value(output, fema_cols)

    # Phase 6 optional disaster/disruption fields may be valid true-zero fields.
    output["disaster_disruption_data_available"] = _has_columns_present(
        output,
        disaster_disruption_cols,
    )

    # TBI / ACLED layers can legitimately be zero for some counties/categories.
    # Treat as available if expected columns exist, then use true-zero diagnostics.
    output["crime_data_available"] = _has_columns_present(output, crime_cols)
    output["crime_rate_data_available"] = _has_columns_present(output, crime_rate_cols)
    output["political_violence_data_available"] = _has_columns_present(
        output,
        political_violence_cols,
    )
    output["gang_activity_data_available"] = _has_columns_present(output, gang_cols)
    output["explosives_activity_data_available"] = _has_columns_present(
        output,
        explosives_cols,
    )
    output["gang_explosives_activity_data_available"] = _has_columns_present(
        output,
        gang_explosives_cols,
    )
    output["hate_crime_offense_data_available"] = _has_columns_present(
        output,
        hate_crime_offense_cols,
    )
    output["law_enforcement_ambush_data_available"] = _has_columns_present(
        output,
        law_enforcement_ambush_cols,
    )
    output["targeted_harm_public_safety_data_available"] = (
        _has_columns_present(output, targeted_harm_public_safety_cols)
        | output["hate_crime_offense_data_available"]
        | output["law_enforcement_ambush_data_available"]
    )

    # Institutional / enforcement pressure is now an active derived layer.
    output["institutional_data_available"] = _has_columns_present(
        output,
        institutional_cols,
    )

    # ------------------------------------------------------------------
    # Additional diagnostic fields
    # ------------------------------------------------------------------
    output["cbp_selected_establishment_total"] = _selected_total(output, cbp_cols)
    output["cbp_true_zero_selected_categories"] = (
        output["cbp_data_available"]
        & output["cbp_selected_establishment_total"].eq(0)
    )

    output["ffl_selected_total"] = _selected_total(output, ffl_cols)
    output["ffl_true_zero_selected_categories"] = (
        output["ffl_data_available"]
        & output["ffl_selected_total"].eq(0)
    )

    output["fema_selected_total"] = _selected_total(output, fema_cols)
    output["fema_true_zero_selected_categories"] = (
        output["fema_data_available"]
        & output["fema_selected_total"].eq(0)
    )

    output["disaster_disruption_selected_total"] = _selected_total(
        output,
        disaster_disruption_cols,
    )
    output["disaster_disruption_true_zero_selected_categories"] = (
        output["disaster_disruption_data_available"]
        & output["disaster_disruption_selected_total"].eq(0)
    )

    output["crime_weapons_selected_total"] = _selected_total(output, crime_cols)
    output["crime_true_zero_selected_categories"] = (
        output["crime_data_available"]
        & output["crime_weapons_selected_total"].eq(0)
    )

    output["crime_rate_selected_total"] = _selected_total(output, crime_rate_cols)
    output["crime_rate_true_zero_selected_categories"] = (
        output["crime_rate_data_available"]
        & output["crime_rate_selected_total"].eq(0)
    )

    output["political_violence_selected_total"] = _selected_total(
        output,
        political_violence_cols,
    )
    output["political_violence_true_zero_selected_categories"] = (
        output["political_violence_data_available"]
        & output["political_violence_selected_total"].eq(0)
    )

    output["gang_activity_selected_total"] = _selected_total(output, gang_cols)
    output["gang_activity_true_zero_selected_categories"] = (
        output["gang_activity_data_available"]
        & output["gang_activity_selected_total"].eq(0)
    )

    output["explosives_activity_selected_total"] = _selected_total(
        output,
        explosives_cols,
    )
    output["explosives_activity_true_zero_selected_categories"] = (
        output["explosives_activity_data_available"]
        & output["explosives_activity_selected_total"].eq(0)
    )

    output["gang_explosives_activity_selected_total"] = _selected_total(
        output,
        gang_explosives_cols,
    )
    output["gang_explosives_activity_true_zero_selected_categories"] = (
        output["gang_explosives_activity_data_available"]
        & output["gang_explosives_activity_selected_total"].eq(0)
    )

    output["hate_crime_offense_selected_total"] = _selected_total(
        output,
        hate_crime_offense_cols,
    )
    output["hate_crime_offense_true_zero_selected_categories"] = (
        output["hate_crime_offense_data_available"]
        & output["hate_crime_offense_selected_total"].eq(0)
    )

    output["law_enforcement_ambush_selected_total"] = _selected_total(
        output,
        law_enforcement_ambush_cols,
    )
    output["law_enforcement_ambush_true_zero_selected_categories"] = (
        output["law_enforcement_ambush_data_available"]
        & output["law_enforcement_ambush_selected_total"].eq(0)
    )

    output["targeted_harm_public_safety_selected_total"] = _selected_total(
        output,
        targeted_harm_public_safety_cols,
    )
    output["targeted_harm_public_safety_true_zero_selected_categories"] = (
        output["targeted_harm_public_safety_data_available"]
        & output["targeted_harm_public_safety_selected_total"].eq(0)
    )

    output["institutional_selected_total"] = _selected_total(
        output,
        institutional_cols,
    )
    output["institutional_true_zero_selected_categories"] = (
        output["institutional_data_available"]
        & output["institutional_selected_total"].eq(0)
    )

    # ------------------------------------------------------------------
    # Data completeness score
    # ------------------------------------------------------------------
    # Active Phase 6 sources:
    # ACS, CBP, FDIC, FFL, FEMA, disaster/disruption, TBI crime/weapons,
    # TBI crime rate, ACLED, TBI gang activity, TBI explosives,
    # TBI gang + explosives intersection, TBI hate crime, TBI law-enforcement
    # ambush, targeted harm/public-safety, and institutional/enforcement.
    active_flags = [
        "acs_data_available",
        "cbp_data_available",
        "fdic_data_available",
        "ffl_data_available",
        "fema_data_available",
        "disaster_disruption_data_available",
        "crime_data_available",
        "crime_rate_data_available",
        "political_violence_data_available",
        "gang_activity_data_available",
        "explosives_activity_data_available",
        "gang_explosives_activity_data_available",
        "hate_crime_offense_data_available",
        "law_enforcement_ambush_data_available",
        "targeted_harm_public_safety_data_available",
        "institutional_data_available",
    ]

    output["active_source_count"] = output[active_flags].sum(axis=1)

    output["data_completeness_score"] = (
        output["active_source_count"] / len(active_flags) * 100
    )

    output["model_confidence"] = pd.cut(
        output["data_completeness_score"],
        bins=[-1, 40, 60, 80, 100],
        labels=["Low", "Moderate", "Good", "High"],
    ).astype(str)

    # ------------------------------------------------------------------
    # Specific diagnostic flags
    # ------------------------------------------------------------------
    output["possible_fdic_gap_flag"] = (
        output["acs_data_available"]
        & ~output["fdic_data_available"]
    )

    output["possible_cbp_gap_flag"] = (
        output["acs_data_available"]
        & ~output["cbp_data_available"]
    )

    output["possible_ffl_gap_flag"] = (
        output["acs_data_available"]
        & ~output["ffl_data_available"]
    )

    output["possible_fema_gap_flag"] = (
        output["acs_data_available"]
        & ~output["fema_data_available"]
    )

    output["possible_disaster_disruption_gap_flag"] = (
        output["acs_data_available"]
        & ~output["disaster_disruption_data_available"]
    )

    output["possible_crime_gap_flag"] = (
        output["acs_data_available"]
        & ~output["crime_data_available"]
    )

    output["possible_crime_rate_gap_flag"] = (
        output["acs_data_available"]
        & ~output["crime_rate_data_available"]
    )

    output["possible_political_violence_gap_flag"] = (
        output["acs_data_available"]
        & ~output["political_violence_data_available"]
    )

    output["possible_gang_activity_gap_flag"] = (
        output["acs_data_available"]
        & ~output["gang_activity_data_available"]
    )

    output["possible_explosives_activity_gap_flag"] = (
        output["acs_data_available"]
        & ~output["explosives_activity_data_available"]
    )

    output["possible_gang_explosives_activity_gap_flag"] = (
        output["acs_data_available"]
        & ~output["gang_explosives_activity_data_available"]
    )

    output["possible_hate_crime_offense_gap_flag"] = (
        output["acs_data_available"]
        & ~output["hate_crime_offense_data_available"]
    )

    output["possible_law_enforcement_ambush_gap_flag"] = (
        output["acs_data_available"]
        & ~output["law_enforcement_ambush_data_available"]
    )

    output["possible_targeted_harm_public_safety_gap_flag"] = (
        output["acs_data_available"]
        & ~output["targeted_harm_public_safety_data_available"]
    )

    output["possible_institutional_gap_flag"] = (
        output["acs_data_available"]
        & ~output["institutional_data_available"]
    )

    # ------------------------------------------------------------------
    # Human-readable data-quality notes
    # ------------------------------------------------------------------
    output["data_quality_note"] = ""

    output.loc[
        output["possible_fdic_gap_flag"],
        "data_quality_note",
    ] += "FDIC banking data missing or zero-filled. "

    output.loc[
        output["possible_cbp_gap_flag"],
        "data_quality_note",
    ] += "CBP business exposure columns missing. "

    output.loc[
        output["cbp_true_zero_selected_categories"],
        "data_quality_note",
    ] += "CBP selected categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_ffl_gap_flag"],
        "data_quality_note",
    ] += "FFL aggregate data missing or zero-filled. "

    output.loc[
        output["ffl_true_zero_selected_categories"],
        "data_quality_note",
    ] += "FFL aggregate categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_fema_gap_flag"],
        "data_quality_note",
    ] += "FEMA disaster data missing or zero-filled. "

    output.loc[
        output["fema_true_zero_selected_categories"],
        "data_quality_note",
    ] += "FEMA disaster categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_disaster_disruption_gap_flag"],
        "data_quality_note",
    ] += "Phase 6 disaster/disruption columns missing. "

    output.loc[
        output["disaster_disruption_true_zero_selected_categories"],
        "data_quality_note",
    ] += "Phase 6 disaster/disruption categories are zero; treated as true zero exposure or unpopulated optional input depending on source review. "

    output.loc[
        output["possible_crime_gap_flag"],
        "data_quality_note",
    ] += "TBI CrimeInsight crime/weapons columns missing. "

    output.loc[
        output["crime_true_zero_selected_categories"],
        "data_quality_note",
    ] += "TBI CrimeInsight selected crime/weapons categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_crime_rate_gap_flag"],
        "data_quality_note",
    ] += "TBI overall crime-rate columns missing. "

    output.loc[
        output["crime_rate_true_zero_selected_categories"],
        "data_quality_note",
    ] += "TBI overall crime-rate values are zero; treated as true zero or export-filter issue depending on source review. "

    output.loc[
        output["possible_political_violence_gap_flag"],
        "data_quality_note",
    ] += "ACLED political violence / civil unrest columns missing. "

    output.loc[
        output["political_violence_true_zero_selected_categories"],
        "data_quality_note",
    ] += "ACLED selected political violence / civil unrest categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_gang_activity_gap_flag"],
        "data_quality_note",
    ] += "TBI gang-related criminal activity columns missing. "

    output.loc[
        output["gang_activity_true_zero_selected_categories"],
        "data_quality_note",
    ] += "TBI gang-related criminal activity categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_explosives_activity_gap_flag"],
        "data_quality_note",
    ] += "TBI explosive-use criminal activity columns missing. "

    output.loc[
        output["explosives_activity_true_zero_selected_categories"],
        "data_quality_note",
    ] += "TBI explosive-use criminal activity categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_gang_explosives_activity_gap_flag"],
        "data_quality_note",
    ] += "TBI gang-related explosive-use criminal activity columns missing. "

    output.loc[
        output["gang_explosives_activity_true_zero_selected_categories"],
        "data_quality_note",
    ] += "TBI gang-related explosive-use categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_hate_crime_offense_gap_flag"],
        "data_quality_note",
    ] += "TBI hate-crime offense columns missing. "

    output.loc[
        output["hate_crime_offense_true_zero_selected_categories"],
        "data_quality_note",
    ] += "TBI hate-crime offense categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_law_enforcement_ambush_gap_flag"],
        "data_quality_note",
    ] += "TBI law-enforcement ambush columns missing. "

    output.loc[
        output["law_enforcement_ambush_true_zero_selected_categories"],
        "data_quality_note",
    ] += "TBI law-enforcement ambush categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_targeted_harm_public_safety_gap_flag"],
        "data_quality_note",
    ] += "Targeted harm / public-safety derived columns missing. "

    output.loc[
        output["targeted_harm_public_safety_true_zero_selected_categories"],
        "data_quality_note",
    ] += "Targeted harm / public-safety categories are zero; treated as true zero exposure, not missing data. "

    output.loc[
        output["possible_institutional_gap_flag"],
        "data_quality_note",
    ] += "Institutional / enforcement pressure columns missing. "

    output.loc[
        output["institutional_true_zero_selected_categories"],
        "data_quality_note",
    ] += "Institutional / enforcement pressure fields are zero; review upstream derived scoring inputs. "

    output["data_quality_note"] = output["data_quality_note"].str.strip()

    return output


def save_data_quality_outputs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Save a dedicated data-quality table.
    """

    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    quality_cols = [
        "county",
        "population",
        "acs_data_available",
        "cbp_data_available",
        "fdic_data_available",
        "ffl_data_available",
        "fema_data_available",
        "disaster_disruption_data_available",
        "crime_data_available",
        "crime_rate_data_available",
        "political_violence_data_available",
        "gang_activity_data_available",
        "explosives_activity_data_available",
        "gang_explosives_activity_data_available",
        "hate_crime_offense_data_available",
        "law_enforcement_ambush_data_available",
        "targeted_harm_public_safety_data_available",
        "institutional_data_available",
        "active_source_count",
        "data_completeness_score",
        "model_confidence",
        "possible_fdic_gap_flag",
        "possible_cbp_gap_flag",
        "possible_ffl_gap_flag",
        "possible_fema_gap_flag",
        "possible_disaster_disruption_gap_flag",
        "possible_crime_gap_flag",
        "possible_crime_rate_gap_flag",
        "possible_political_violence_gap_flag",
        "possible_gang_activity_gap_flag",
        "possible_explosives_activity_gap_flag",
        "possible_gang_explosives_activity_gap_flag",
        "possible_hate_crime_offense_gap_flag",
        "possible_law_enforcement_ambush_gap_flag",
        "possible_targeted_harm_public_safety_gap_flag",
        "possible_institutional_gap_flag",
        "cbp_selected_establishment_total",
        "cbp_true_zero_selected_categories",
        "ffl_selected_total",
        "ffl_true_zero_selected_categories",
        "fema_selected_total",
        "fema_true_zero_selected_categories",
        "disaster_disruption_selected_total",
        "disaster_disruption_true_zero_selected_categories",
        "crime_weapons_selected_total",
        "crime_true_zero_selected_categories",
        "crime_rate_selected_total",
        "crime_rate_true_zero_selected_categories",
        "political_violence_selected_total",
        "political_violence_true_zero_selected_categories",
        "gang_activity_selected_total",
        "gang_activity_true_zero_selected_categories",
        "explosives_activity_selected_total",
        "explosives_activity_true_zero_selected_categories",
        "gang_explosives_activity_selected_total",
        "gang_explosives_activity_true_zero_selected_categories",
        "hate_crime_offense_selected_total",
        "hate_crime_offense_true_zero_selected_categories",
        "law_enforcement_ambush_selected_total",
        "law_enforcement_ambush_true_zero_selected_categories",
        "targeted_harm_public_safety_selected_total",
        "targeted_harm_public_safety_true_zero_selected_categories",
        "institutional_selected_total",
        "institutional_true_zero_selected_categories",
        "data_quality_note",
    ]

    existing_cols = [col for col in quality_cols if col in df.columns]

    quality_df = df[existing_cols].copy()

    quality_df = quality_df.sort_values(
        ["data_completeness_score", "county"],
        ascending=[True, True],
    )

    output_path = TABLES_DIR / "tn_county_data_quality_flags.csv"
    quality_df.to_csv(output_path, index=False)

    return quality_df
