from src.data_collection import build_master_dataset
from src.risk_scoring import build_scores
from src.visualization import generate_charts
from src.report_generator import generate_report
from src.sensitivity_analysis import run_sensitivity_analysis
from src.crime_trend_analysis import run_crime_trend_analysis
from src.public_group_reference import build_public_group_reference
from src.tbi_hate_crime_report_context import build_tbi_hate_crime_report_context
from src.tdoc_stg_reference_processor import main as build_tdoc_stg_reference_context

# Operational Risk & Protective Planning layer
from src.prepare_county_profile_data import main as prepare_county_profile_data
from src.prepare_tbi_public_safety_context import main as prepare_tbi_public_safety_context
from src.prepare_transport_context import main as prepare_transport_context
from src.prepare_healthcare_capacity import main as prepare_healthcare_capacity
from src.prepare_infrastructure_needs import main as prepare_infrastructure_needs
from src.prepare_law_enforcement_capacity import main as prepare_law_enforcement_capacity
from src.operational_risk_features import build_operational_risk_features


PIPELINE_OUTPUTS = [
    "outputs/tables/tn_county_master_dataset.csv",
    "outputs/tables/tn_county_domestic_security_scores.csv",
    "outputs/tables/tn_county_component_scores.csv",
    "outputs/tables/tn_county_finance_tactical_scores.csv",
    "outputs/tables/tn_county_crime_weapons_scores.csv",
    "outputs/tables/tn_county_organized_violence_scores.csv",
    "outputs/tables/tn_county_targeted_harm_public_safety_scores.csv",
    "outputs/tables/tn_county_disaster_disruption_scores.csv",
    "outputs/tables/tn_county_institutional_enforcement_scores.csv",
    "outputs/tables/tn_county_political_violence_scores.csv",
    "outputs/tables/tn_county_data_quality_flags.csv",
    "outputs/tables/crime_offense_label_mapping_validation.csv",
    "outputs/tables/crime_offense_unmapped_labels.csv",
    "outputs/tables/model_weight_sensitivity_results.csv",
    "outputs/tables/top_county_rank_stability.csv",
    "outputs/tables/scenario_top_county_leaders.csv",
    "outputs/tables/tn_crime_weapons_trend_analysis.csv",
    "outputs/tables/tn_public_group_activity_reference.csv",
    "outputs/tables/tn_public_group_reference_validation.csv",
    "outputs/tables/tn_2024_hate_crime_bias_context.csv",
    "outputs/tables/tn_2024_hate_crime_offense_context.csv",
    "outputs/tables/tn_2024_hate_crime_clearance_context.csv",
    "outputs/tables/tn_2024_hate_crime_location_context.csv",
    "outputs/tables/tn_2024_hate_crime_report_context_summary.csv",
    "outputs/tables/tn_tdoc_stg_reference_context.csv",
    "outputs/tables/tn_tdoc_stg_reference_validation.csv",
    "data/raw/tn_county_profile_data.csv",
    "data/raw/tbi_county_public_safety_context.csv",
    "data/raw/tn_county_transport_context.csv",
    "data/raw/tn_county_healthcare_capacity.csv",
    "data/raw/tn_county_infrastructure_needs.csv",
    "data/raw/tn_county_law_enforcement_capacity.csv",
    "data/processed/tn_operational_risk_features.csv",
    "outputs/charts/",
    "outputs/reports/tennessee_domestic_security_finance_risk_report.pdf",
]


def _print_top_county(
    scores_df,
    score_col: str,
    label: str,
) -> None:
    """
    Print the top county for a selected score column if it exists.

    This keeps the main workflow readable and prevents KeyError issues if an
    optional layer is not active in a given run.
    """

    if score_col not in scores_df.columns or scores_df.empty:
        return

    top_row = scores_df.sort_values(score_col, ascending=False).iloc[0]

    print(f"\nTop county by {label}:")
    print(f"- {top_row['county']}: {top_row[score_col]:.2f}")


def _print_operational_risk_preview(operational_df) -> None:
    """Print a compact preview of the operational-risk layer."""

    if operational_df is None or operational_df.empty:
        print("Operational-risk layer returned no rows.")
        return

    required = [
        "county",
        "final_operational_risk_score",
        "operational_risk_tier",
        "data_quality_flag",
    ]

    missing = [col for col in required if col not in operational_df.columns]
    if missing:
        print(f"Operational-risk preview unavailable. Missing columns: {missing}")
        return

    print("\nTop counties by operational risk / protective-planning score:")
    preview = operational_df.sort_values(
        "final_operational_risk_score",
        ascending=False,
    ).head(10)

    for _, row in preview.iterrows():
        print(
            f"- {row['county']}: "
            f"{row['final_operational_risk_score']:.2f} "
            f"({row['operational_risk_tier']}; data quality: {row['data_quality_flag']})"
        )


def main():
    print("=" * 80)
    print("Tennessee Domestic Security & Illicit Finance Risk Intelligence Model")
    print("=" * 80)

    print("\n[1/9] Building reference/context layers...")
    build_public_group_reference()
    build_tbi_hate_crime_report_context()
    build_tdoc_stg_reference_context()

    print("Reference/context layers complete.")
    print("- outputs/tables/tn_public_group_activity_reference.csv")
    print("- outputs/tables/tn_public_group_reference_validation.csv")
    print("- outputs/tables/tn_2024_hate_crime_bias_context.csv")
    print("- outputs/tables/tn_2024_hate_crime_offense_context.csv")
    print("- outputs/tables/tn_2024_hate_crime_clearance_context.csv")
    print("- outputs/tables/tn_2024_hate_crime_location_context.csv")
    print("- outputs/tables/tn_2024_hate_crime_report_context_summary.csv")
    print("- outputs/tables/tn_tdoc_stg_reference_context.csv")
    print("- outputs/tables/tn_tdoc_stg_reference_validation.csv")
    print(
        "Note: Reference/context layers are not included in risk scoring. "
        "They support the PDF/dashboard appendices only."
    )

    print("\n[2/9] Collecting public-source county data...")
    master_df = build_master_dataset()
    print(f"Master dataset shape: {master_df.shape}")

    print("\n[3/9] Building Phase 6 risk scores...")
    scores_df = build_scores(master_df)

    if scores_df.empty:
        raise ValueError(
            "Risk scoring returned an empty dataset. Review upstream source files "
            "and data_collection.py outputs."
        )

    top = scores_df.iloc[0]
    print("\nTop county by current model score:")
    print(
        f"- {top['county']}: "
        f"{top['final_domestic_security_risk_score']:.2f} "
        f"({top['risk_signal']})"
    )

    _print_top_county(
        scores_df,
        "finance_tactical_vulnerability_score",
        "finance / tactical vulnerability",
    )

    _print_top_county(
        scores_df,
        "organized_violence_pressure_score",
        "organized violence / high-severity crime pressure",
    )

    _print_top_county(
        scores_df,
        "violent_crime_weapons_pressure_score",
        "crime / weapons pressure",
    )

    _print_top_county(
        scores_df,
        "gang_related_crime_pressure_score",
        "gang-related criminal activity pressure",
    )

    _print_top_county(
        scores_df,
        "explosive_related_pressure_score",
        "explosive-use criminal activity pressure",
    )

    _print_top_county(
        scores_df,
        "gang_explosive_pressure_score",
        "gang + explosive intersection pressure",
    )

    _print_top_county(
        scores_df,
        "targeted_harm_public_safety_pressure_score",
        "targeted harm / public-safety pressure",
    )

    _print_top_county(
        scores_df,
        "hate_crime_targeted_harm_pressure_score",
        "hate-crime / targeted-harm pressure",
    )

    _print_top_county(
        scores_df,
        "law_enforcement_ambush_pressure_score",
        "law-enforcement ambush pressure",
    )

    _print_top_county(
        scores_df,
        "disaster_disruption_vulnerability_score",
        "disaster / disruption vulnerability",
    )

    _print_top_county(
        scores_df,
        "institutional_enforcement_pressure_score",
        "institutional / enforcement pressure",
    )

    if "data_completeness_score" in scores_df.columns:
        avg_confidence = scores_df["data_completeness_score"].mean()

        print("\nAverage active-source completeness:")
        print(f"- {avg_confidence:.2f}%")

    print("\n[4/9] Running Phase 6 sensitivity analysis...")
    sensitivity_df, rank_stability_df, sensitivity_chart = run_sensitivity_analysis(
        scores_df
    )

    print("Sensitivity analysis complete.")
    print("- outputs/tables/model_weight_sensitivity_results.csv")
    print("- outputs/tables/top_county_rank_stability.csv")
    print("- outputs/tables/scenario_top_county_leaders.csv")
    print(f"- {sensitivity_chart}")
    print("- outputs/charts/average_rank_top_counties.png")

    if not rank_stability_df.empty:
        print("\nMost stable top-ranked counties across sensitivity scenarios:")
        stable_preview = rank_stability_df.head(10)

        for _, row in stable_preview.iterrows():
            print(
                f"- {row['county']}: "
                f"Top-10 scenarios={row['top_10_scenario_count']}, "
                f"Avg rank={row['average_rank']:.1f}, "
                f"Stability={row['rank_stability_signal']}"
            )

    print("\n[5/9] Running CrimeInsight trend analysis...")
    trend_df, trend_chart_paths = run_crime_trend_analysis()

    print("CrimeInsight trend analysis complete.")
    print("- outputs/tables/tn_crime_weapons_trend_analysis.csv")

    for path in trend_chart_paths:
        print(f"- {path}")

    print("\n[6/9] Building Operational Risk & Protective Planning layer...")
    print("[Operational Risk] Preparing Census / ACS county profile data...")
    prepare_county_profile_data()

    print("[Operational Risk] Preparing TBI public-safety context...")
    prepare_tbi_public_safety_context()

    print("[Operational Risk] Preparing TDOT transportation context...")
    prepare_transport_context()

    print("[Operational Risk] Preparing healthcare capacity context...")
    prepare_healthcare_capacity()

    print("[Operational Risk] Preparing TACIR infrastructure needs context...")
    prepare_infrastructure_needs()

    print("[Operational Risk] Preparing CSLLEA law-enforcement capacity context...")
    prepare_law_enforcement_capacity()

    print("[Operational Risk] Building operational-risk feature layer...")
    operational_df = build_operational_risk_features()
    _print_operational_risk_preview(operational_df)

    print("\n[7/9] Generating charts...")
    chart_paths = generate_charts(scores_df)

    for path in chart_paths:
        print(f"- {path}")

    print("\n[8/9] Generating PDF report...")
    report_path = generate_report(scores_df)
    print(f"PDF report created: {report_path}")

    print("\n[9/9] Pipeline summary.")
    print("\nPipeline complete.")

    for output in PIPELINE_OUTPUTS:
        print(f"- {output}")


if __name__ == "__main__":
    main()
