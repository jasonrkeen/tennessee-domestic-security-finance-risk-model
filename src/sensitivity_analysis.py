import pandas as pd
import matplotlib.pyplot as plt

from src.config import TABLES_DIR, CHARTS_DIR


SCENARIOS = {
    "baseline_phase6": {
        "finance_tactical_vulnerability_score": 0.30,
        "organized_violence_pressure_score": 0.20,
        "political_violence_exposure_score": 0.15,
        "household_financial_stress_score": 0.15,
        "disaster_disruption_vulnerability_score": 0.10,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.05,
    },
    "finance_heavy": {
        "finance_tactical_vulnerability_score": 0.45,
        "organized_violence_pressure_score": 0.15,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.10,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.05,
    },
    "organized_violence_heavy": {
        "finance_tactical_vulnerability_score": 0.18,
        "organized_violence_pressure_score": 0.42,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.08,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.07,
    },
    "targeted_harm_public_safety_heavy": {
        "finance_tactical_vulnerability_score": 0.18,
        "organized_violence_pressure_score": 0.22,
        "targeted_harm_public_safety_pressure_score": 0.22,
        "law_enforcement_ambush_pressure_score": 0.10,
        "political_violence_exposure_score": 0.08,
        "household_financial_stress_score": 0.08,
        "disaster_disruption_vulnerability_score": 0.07,
        "institutional_enforcement_pressure_score": 0.05,
    },
    "institutional_enforcement_heavy": {
        "finance_tactical_vulnerability_score": 0.20,
        "organized_violence_pressure_score": 0.18,
        "institutional_enforcement_pressure_score": 0.30,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.07,
        "tactical_access_score": 0.05,
    },
    "gang_explosives_heavy": {
        "finance_tactical_vulnerability_score": 0.18,
        "organized_violence_pressure_score": 0.22,
        "gang_related_crime_pressure_score": 0.15,
        "explosive_related_pressure_score": 0.12,
        "gang_explosive_pressure_score": 0.12,
        "political_violence_exposure_score": 0.08,
        "disaster_disruption_vulnerability_score": 0.06,
        "institutional_enforcement_pressure_score": 0.07,
    },
    "political_violence_heavy": {
        "finance_tactical_vulnerability_score": 0.18,
        "organized_violence_pressure_score": 0.15,
        "political_violence_exposure_score": 0.37,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.08,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.07,
    },
    "disaster_disruption_heavy": {
        "finance_tactical_vulnerability_score": 0.18,
        "organized_violence_pressure_score": 0.15,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.35,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.07,
    },
    "socioeconomic_heavy": {
        "finance_tactical_vulnerability_score": 0.18,
        "organized_violence_pressure_score": 0.15,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.37,
        "disaster_disruption_vulnerability_score": 0.08,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.07,
    },
    "tactical_access_heavy": {
        "finance_tactical_vulnerability_score": 0.23,
        "organized_violence_pressure_score": 0.18,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.07,
        "tactical_access_score": 0.25,
        "institutional_enforcement_pressure_score": 0.07,
    },
}


def _validate_weights(weights: dict) -> None:
    total = sum(weights.values())

    if round(total, 6) != 1.0:
        raise ValueError(f"Scenario weights must sum to 1.0. Current total: {total}")


def _ensure_columns(df: pd.DataFrame, scenario_weights: dict) -> pd.DataFrame:
    output = df.copy()

    for col in scenario_weights:
        if col not in output.columns:
            output[col] = 50.0

        output[col] = pd.to_numeric(output[col], errors="coerce").fillna(50.0)

    return output


def calculate_scenario_score(df: pd.DataFrame, weights: dict) -> pd.Series:
    _validate_weights(weights)

    score = pd.Series(0.0, index=df.index)

    for col, weight in weights.items():
        score += df[col] * weight

    return score


def build_sensitivity_results(scores_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build county-level sensitivity results across alternative weighting scenarios.

    Phase 6 scenarios include:
    - Baseline Phase 6
    - Finance-heavy
    - Organized-violence-heavy
    - Targeted-harm / public-safety-heavy
    - Institutional / enforcement-heavy
    - Gang / explosives-heavy
    - Political-violence-heavy
    - Disaster / disruption-heavy
    - Socioeconomic-heavy
    - Tactical-access-heavy
    """

    results = []

    for scenario_name, weights in SCENARIOS.items():
        working = _ensure_columns(scores_df, weights).copy()

        working["scenario"] = scenario_name
        working["scenario_score"] = calculate_scenario_score(working, weights)

        working = working.sort_values("scenario_score", ascending=False).copy()
        working["scenario_rank"] = range(1, len(working) + 1)

        keep_cols = [
            "scenario",
            "county",
            "scenario_score",
            "scenario_rank",
            "finance_tactical_vulnerability_score",
            "organized_violence_pressure_score",
            "violent_crime_weapons_pressure_score",
            "overall_crime_rate_index_score",
            "gang_related_crime_pressure_score",
            "explosive_related_pressure_score",
            "gang_explosive_pressure_score",
            "hate_crime_targeted_harm_pressure_score",
            "law_enforcement_ambush_pressure_score",
            "targeted_harm_public_safety_pressure_score",
            "political_violence_exposure_score",
            "household_financial_stress_score",
            "infrastructure_disruption_score",
            "disaster_disruption_vulnerability_score",
            "severe_weather_exposure_score",
            "power_disruption_exposure_score",
            "access_stress_score",
            "recovery_strain_exposure_score",
            "tactical_access_score",
            "institutional_enforcement_pressure_score",
            "final_domestic_security_risk_score",
            "risk_signal",
            "model_confidence",
        ]

        existing_cols = [col for col in keep_cols if col in working.columns]

        results.append(working[existing_cols])

    sensitivity_df = pd.concat(results, ignore_index=True)

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    sensitivity_df.to_csv(
        TABLES_DIR / "model_weight_sensitivity_results.csv",
        index=False,
    )

    return sensitivity_df


def build_rank_stability_table(sensitivity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize how stable county rankings are across weighting scenarios.
    """

    pivot = sensitivity_df.pivot_table(
        index="county",
        columns="scenario",
        values="scenario_rank",
        aggfunc="first",
    ).reset_index()

    scenario_cols = [col for col in pivot.columns if col != "county"]

    pivot["best_rank"] = pivot[scenario_cols].min(axis=1)
    pivot["worst_rank"] = pivot[scenario_cols].max(axis=1)
    pivot["average_rank"] = pivot[scenario_cols].mean(axis=1)
    pivot["rank_range"] = pivot["worst_rank"] - pivot["best_rank"]

    top10_counts = (
        sensitivity_df[sensitivity_df["scenario_rank"] <= 10]
        .groupby("county")
        .size()
        .reset_index(name="top_10_scenario_count")
    )

    pivot = pivot.merge(top10_counts, on="county", how="left")
    pivot["top_10_scenario_count"] = (
        pivot["top_10_scenario_count"]
        .fillna(0)
        .astype(int)
    )

    pivot["rank_stability_signal"] = pd.cut(
        pivot["rank_range"],
        bins=[-1, 5, 15, 30, 100],
        labels=[
            "Very Stable",
            "Stable",
            "Moderately Sensitive",
            "Highly Sensitive",
        ],
    ).astype(str)

    output = pivot.sort_values(
        ["top_10_scenario_count", "average_rank"],
        ascending=[False, True],
    )

    output.to_csv(
        TABLES_DIR / "top_county_rank_stability.csv",
        index=False,
    )

    return output


def build_scenario_leader_table(sensitivity_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Save the top counties under each scenario in a readable long-form table.
    """

    leaders = (
        sensitivity_df[sensitivity_df["scenario_rank"] <= top_n]
        .sort_values(["scenario", "scenario_rank"])
        .copy()
    )

    leaders.to_csv(
        TABLES_DIR / "scenario_top_county_leaders.csv",
        index=False,
    )

    return leaders


def save_rank_stability_chart(rank_stability_df: pd.DataFrame, top_n: int = 20):
    """
    Save a chart showing how often counties appear in the top 10 across scenarios.
    """

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    plot_df = rank_stability_df.sort_values(
        ["top_10_scenario_count", "average_rank"],
        ascending=[False, True],
    ).head(top_n)

    plot_df = plot_df.sort_values("top_10_scenario_count", ascending=True)

    plt.figure(figsize=(10, 7))
    plt.barh(plot_df["county"], plot_df["top_10_scenario_count"])
    plt.title("Top-10 Rank Stability Across Phase 6 Weighting Scenarios")
    plt.xlabel("Number of Scenarios Where County Appears in Top 10")
    plt.ylabel("County")
    plt.tight_layout()

    path = CHARTS_DIR / "rank_stability_top_counties.png"
    plt.savefig(path, dpi=200)
    plt.close()

    return path


def save_average_rank_chart(rank_stability_df: pd.DataFrame, top_n: int = 20):
    """
    Save a chart of counties with the strongest average rank across scenarios.
    """

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    plot_df = rank_stability_df.sort_values(
        "average_rank",
        ascending=True,
    ).head(top_n)

    plot_df = plot_df.sort_values("average_rank", ascending=False)

    plt.figure(figsize=(10, 7))
    plt.barh(plot_df["county"], plot_df["average_rank"])
    plt.title("Best Average Rank Across Phase 6 Weighting Scenarios")
    plt.xlabel("Average Rank Across Scenarios")
    plt.ylabel("County")
    plt.tight_layout()

    path = CHARTS_DIR / "average_rank_top_counties.png"
    plt.savefig(path, dpi=200)
    plt.close()

    return path


def run_sensitivity_analysis(scores_df: pd.DataFrame):
    """
    Run full sensitivity analysis workflow.
    """

    sensitivity_df = build_sensitivity_results(scores_df)
    rank_stability_df = build_rank_stability_table(sensitivity_df)
    scenario_leaders_df = build_scenario_leader_table(sensitivity_df)

    rank_chart_path = save_rank_stability_chart(rank_stability_df)
    average_rank_chart_path = save_average_rank_chart(rank_stability_df)

    return sensitivity_df, rank_stability_df, rank_chart_path
