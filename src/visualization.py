from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.config import CHARTS_DIR


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OPERATIONAL_RISK_PATH = PROJECT_ROOT / "data" / "processed" / "tn_operational_risk_features.csv"


def load_operational_risk_features() -> pd.DataFrame:
    """Load the defensive operational-risk feature layer if it exists."""
    if not OPERATIONAL_RISK_PATH.exists():
        print(f"Operational risk feature file not found: {OPERATIONAL_RISK_PATH}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(OPERATIONAL_RISK_PATH)
        df = df.loc[:, ~df.columns.duplicated()].copy()
        return df
    except Exception as exc:
        print(f"Could not load operational risk feature file: {exc}")
        return pd.DataFrame()



def _remove_stale_chart(filename: str) -> None:
    """
    Remove an older chart file when a chart is intentionally skipped.

    This prevents the PDF/report layer from picking up stale PNGs from a prior
    run when the current data has no meaningful variation.
    """
    path = CHARTS_DIR / filename
    if path.exists():
        try:
            path.unlink()
            print(f"Removed stale chart: {path}")
        except Exception as exc:
            print(f"Could not remove stale chart {path}: {exc}")


def save_bar_chart(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    filename: str,
    top_n: int = 15,
    xlabel: str = "Score",
    skip_zero_only: bool = True,
):
    """
    Save a horizontal bar chart for the top counties by a selected value.

    Returns:
        pathlib.Path or None
    """

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    if value_col not in df.columns:
        print(f"Skipping chart. Missing column: {value_col}")
        _remove_stale_chart(filename)
        return None

    plot_df = df.copy()
    plot_df[value_col] = pd.to_numeric(plot_df[value_col], errors="coerce").fillna(0)

    if "county" not in plot_df.columns:
        print("Skipping chart. Missing column: county")
        _remove_stale_chart(filename)
        return None

    usable_values = plot_df[value_col].dropna()

    if usable_values.empty:
        print(f"Skipping chart. No usable values for: {value_col}")
        _remove_stale_chart(filename)
        return None

    if skip_zero_only and usable_values.max() <= 0:
        print(f"Skipping chart. All values are zero for: {value_col}")
        _remove_stale_chart(filename)
        return None

    if usable_values.nunique(dropna=True) <= 1:
        print(f"Skipping chart. No meaningful variation for: {value_col}")
        _remove_stale_chart(filename)
        return None

    plot_df = plot_df.sort_values(value_col, ascending=False).head(top_n).copy()
    plot_df = plot_df.sort_values(value_col, ascending=True)

    if plot_df.empty:
        print(f"Skipping chart. No data available for: {value_col}")
        _remove_stale_chart(filename)
        return None

    plt.figure(figsize=(10, 7))
    plt.barh(plot_df["county"], plot_df[value_col])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("County")
    plt.tight_layout()

    path = CHARTS_DIR / filename
    plt.savefig(path, dpi=200)
    plt.close()

    return path


def save_scatter_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
    filename: str,
    label_top_n: int = 12,
    skip_zero_only: bool = True,
):
    """
    Save a scatter chart comparing two model scores.

    Returns:
        pathlib.Path or None
    """

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    required_cols = ["county", x_col, y_col]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"Skipping scatter chart. Missing columns: {missing_cols}")
        _remove_stale_chart(filename)
        return None

    plot_df = df.copy()
    plot_df[x_col] = pd.to_numeric(plot_df[x_col], errors="coerce")
    plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors="coerce")
    plot_df = plot_df.dropna(subset=[x_col, y_col])

    if plot_df.empty:
        print(f"Skipping scatter chart. No usable data for: {x_col}, {y_col}")
        _remove_stale_chart(filename)
        return None

    if skip_zero_only and plot_df[x_col].max() <= 0 and plot_df[y_col].max() <= 0:
        print(f"Skipping scatter chart. All values are zero for: {x_col}, {y_col}")
        _remove_stale_chart(filename)
        return None

    if plot_df[x_col].nunique(dropna=True) <= 1 and plot_df[y_col].nunique(dropna=True) <= 1:
        print(f"Skipping scatter chart. No meaningful variation for: {x_col}, {y_col}")
        _remove_stale_chart(filename)
        return None

    plt.figure(figsize=(9, 6))
    plt.scatter(plot_df[x_col], plot_df[y_col])

    label_df = plot_df.sort_values(y_col, ascending=False).head(label_top_n)

    for _, row in label_df.iterrows():
        plt.annotate(
            row["county"],
            (row[x_col], row[y_col]),
            fontsize=8,
        )

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()

    path = CHARTS_DIR / filename
    plt.savefig(path, dpi=200)
    plt.close()

    return path


def _append_existing_chart(chart_paths: list[Path], filename: str) -> list[Path]:
    """
    Append an already-created chart to chart_paths if it exists.

    This is useful for charts generated by other modules, such as:
    - sensitivity_analysis.py
    - crime_trend_analysis.py
    """

    path = CHARTS_DIR / filename

    if path.exists():
        chart_paths.append(path)

    return chart_paths


def _append_existing_charts(chart_paths: list[Path], filenames: list[str]) -> list[Path]:
    for filename in filenames:
        chart_paths = _append_existing_chart(chart_paths, filename)

    return chart_paths



def generate_operational_risk_charts() -> list[Path]:
    """
    Generate charts for the defensive county-level operational-risk layer.

    These charts use data/processed/tn_operational_risk_features.csv and stay
    county-level only. They do not include facility names, addresses,
    coordinates, routes, schedules, or agency-level operational details.
    """

    operational_df = load_operational_risk_features()
    chart_paths: list[Path] = []

    if operational_df.empty:
        return chart_paths

    chart_specs = [
        (
            "final_operational_risk_score",
            "Top 15 Tennessee Counties by Operational Risk & Protective Planning Score",
            "top_15_operational_risk_counties.png",
            "Score",
        ),
        (
            "operational_exposure_score",
            "Top 15 Tennessee Counties by Operational Exposure Score",
            "top_15_operational_exposure_counties.png",
            "Score",
        ),
        (
            "resilience_gap_score",
            "Top 15 Tennessee Counties by Resilience Gap Score",
            "top_15_resilience_gap_counties.png",
            "Score",
        ),
        (
            "transport_pressure_score",
            "Top 15 Tennessee Counties by Transportation Pressure Score",
            "top_15_transport_pressure_counties.png",
            "Score",
        ),
        (
            "infrastructure_pressure_score",
            "Top 15 Tennessee Counties by Infrastructure Pressure Score",
            "top_15_infrastructure_pressure_counties.png",
            "Score",
        ),
        (
            "public_safety_context_score",
            "Top 15 Tennessee Counties by Public-Safety Context Score",
            "top_15_public_safety_context_counties.png",
            "Score",
        ),
        (
            "healthcare_capacity_gap_score",
            "Top 15 Tennessee Counties by Healthcare Capacity Gap Score",
            "top_15_healthcare_capacity_gap_counties.png",
            "Score",
        ),
        (
            "law_enforcement_capacity_gap_score",
            "Top 15 Tennessee Counties by Law-Enforcement Capacity Gap Score",
            "top_15_law_enforcement_capacity_gap_counties.png",
            "Score",
        ),
    ]

    for value_col, title, filename, xlabel in chart_specs:
        path = save_bar_chart(
            operational_df,
            value_col,
            title,
            filename,
            xlabel=xlabel,
        )

        if path is not None:
            chart_paths.append(path)

    scatter_specs = [
        (
            "operational_exposure_score",
            "resilience_gap_score",
            "Operational Exposure vs. Resilience Gap",
            "Operational Exposure Score",
            "Resilience Gap Score",
            "operational_exposure_vs_resilience_gap_scatter.png",
        ),
        (
            "transport_pressure_score",
            "operational_exposure_score",
            "Transportation Pressure vs. Operational Exposure",
            "Transportation Pressure Score",
            "Operational Exposure Score",
            "transport_pressure_vs_operational_exposure_scatter.png",
        ),
        (
            "infrastructure_pressure_score",
            "operational_exposure_score",
            "Infrastructure Pressure vs. Operational Exposure",
            "Infrastructure Pressure Score",
            "Operational Exposure Score",
            "infrastructure_pressure_vs_operational_exposure_scatter.png",
        ),
        (
            "law_enforcement_capacity_gap_score",
            "resilience_gap_score",
            "Law-Enforcement Capacity Gap vs. Resilience Gap",
            "Law-Enforcement Capacity Gap Score",
            "Resilience Gap Score",
            "law_enforcement_capacity_gap_vs_resilience_gap_scatter.png",
        ),
        (
            "healthcare_capacity_gap_score",
            "resilience_gap_score",
            "Healthcare Capacity Gap vs. Resilience Gap",
            "Healthcare Capacity Gap Score",
            "Resilience Gap Score",
            "healthcare_capacity_gap_vs_resilience_gap_scatter.png",
        ),
    ]

    for x_col, y_col, title, xlabel, ylabel, filename in scatter_specs:
        path = save_scatter_chart(
            operational_df,
            x_col,
            y_col,
            title,
            xlabel,
            ylabel,
            filename,
        )

        if path is not None:
            chart_paths.append(path)

    return chart_paths

def generate_charts(scores_df: pd.DataFrame):
    """
    Generate core model charts.

    Notes:
    - The rank-stability chart is generated by src/sensitivity_analysis.py.
    - Crime trend charts are generated by src/crime_trend_analysis.py.
    - This function appends those externally generated charts if they already exist.
    """

    chart_paths = []

    chart_specs = [
        (
            "final_domestic_security_risk_score",
            "Top 15 Tennessee Counties by Final Domestic Security Risk Score",
            "top_15_final_risk_counties.png",
            "Score",
        ),
        (
            "finance_tactical_vulnerability_score",
            "Top 15 Tennessee Counties by Finance & Tactical Vulnerability Score",
            "top_15_finance_tactical_risk_counties.png",
            "Score",
        ),
        (
            "institutional_enforcement_pressure_score",
            "Top 15 Tennessee Counties by Institutional / Enforcement Pressure Score",
            "top_15_institutional_enforcement_pressure_counties.png",
            "Score",
        ),
        (
            "disaster_disruption_vulnerability_score",
            "Top 15 Tennessee Counties by Disaster / Disruption Vulnerability Score",
            "top_15_disaster_disruption_vulnerability_counties.png",
            "Score",
        ),
        (
            "infrastructure_disruption_score",
            "Top 15 Tennessee Counties by FEMA-Based Infrastructure Disruption Score",
            "top_15_infrastructure_disruption_counties.png",
            "Score",
        ),
        (
            "severe_weather_exposure_score",
            "Top 15 Tennessee Counties by Severe Weather Exposure Score",
            "top_15_severe_weather_exposure_counties.png",
            "Score",
        ),
        (
            "power_disruption_exposure_score",
            "Top 15 Tennessee Counties by Power Disruption Exposure Score",
            "top_15_power_disruption_exposure_counties.png",
            "Score",
        ),
        (
            "access_stress_score",
            "Top 15 Tennessee Counties by Infrastructure / Access Stress Score",
            "top_15_access_stress_counties.png",
            "Score",
        ),
        (
            "recovery_strain_exposure_score",
            "Top 15 Tennessee Counties by Recovery Strain Exposure Score",
            "top_15_recovery_strain_exposure_counties.png",
            "Score",
        ),
        (
            "violent_crime_weapons_pressure_score",
            "Top 15 Tennessee Counties by Crime & Weapons Pressure Score",
            "top_15_crime_weapons_pressure_counties.png",
            "Score",
        ),
        (
            "organized_violence_pressure_score",
            "Top 15 Tennessee Counties by Organized Violence / High-Severity Crime Pressure Score",
            "top_15_organized_violence_pressure_counties.png",
            "Score",
        ),
        (
            "overall_crime_rate_index_score",
            "Top 15 Tennessee Counties by Overall Crime Rate Index Score",
            "top_15_overall_crime_rate_index_counties.png",
            "Score",
        ),
        (
            "weapons_law_violation_pressure_score",
            "Top 15 Tennessee Counties by Weapon Law Violation Pressure Score",
            "top_15_weapon_law_violation_pressure_counties.png",
            "Score",
        ),
        (
            "targeted_harm_public_safety_pressure_score",
            "Top 15 Tennessee Counties by Targeted Harm / Public-Safety Pressure Score",
            "top_15_targeted_harm_public_safety_pressure_counties.png",
            "Score",
        ),
        (
            "hate_crime_targeted_harm_pressure_score",
            "Top 15 Tennessee Counties by Hate-Crime / Targeted-Harm Pressure Score",
            "top_15_hate_crime_targeted_harm_pressure_counties.png",
            "Score",
        ),
        (
            "hate_crime_total_count",
            "Top 15 Tennessee Counties by Hate-Crime Offense Count",
            "top_15_hate_crime_total_counties.png",
            "Offense Count",
        ),
        (
            "hate_crime_intimidation_count",
            "Top 15 Tennessee Counties by Hate-Crime Intimidation Count",
            "top_15_hate_crime_intimidation_counties.png",
            "Offense Count",
        ),
        (
            "law_enforcement_ambush_pressure_score",
            "Top 15 Tennessee Counties by Law-Enforcement Ambush Pressure Score",
            "top_15_law_enforcement_ambush_pressure_counties.png",
            "Score",
        ),
        (
            "le_ambush_total_count",
            "Top 15 Tennessee Counties by Law-Enforcement Ambush Count",
            "top_15_law_enforcement_ambush_counties.png",
            "Offense Count",
        ),
        (
            "law_enforcement_assault_pressure_score",
            "Top 15 Tennessee Counties by Law-Enforcement Assault Pressure Score",
            "top_15_law_enforcement_assault_pressure_counties.png",
            "Score",
        ),
        (
            "law_enforcement_assault_count",
            "Top 15 Tennessee Counties by Law-Enforcement Assault Count",
            "top_15_law_enforcement_assault_counties.png",
            "Offense Count",
        ),
        (
            "political_violence_exposure_score",
            "Top 15 Tennessee Counties by ACLED Political Violence / Civil Unrest Exposure Score",
            "top_15_political_violence_exposure_counties.png",
            "Score",
        ),
        (
            "total_acled_event_count",
            "Top 15 Tennessee Counties by Total ACLED Event Count",
            "top_15_total_acled_event_counties.png",
            "Event Count",
        ),
        (
            "protest_event_count",
            "Top 15 Tennessee Counties by ACLED Protest Event Count",
            "top_15_acled_protest_event_counties.png",
            "Event Count",
        ),
        (
            "public_disorder_event_count",
            "Top 15 Tennessee Counties by ACLED Public Disorder Event Count",
            "top_15_acled_public_disorder_counties.png",
            "Event Count",
        ),
        (
            "gang_related_crime_pressure_score",
            "Top 15 Tennessee Counties by Gang-Related Criminal Activity Pressure Score",
            "top_15_gang_related_crime_pressure_counties.png",
            "Score",
        ),
        (
            "gang_related_total_crime_count",
            "Top 15 Tennessee Counties by Gang-Related Total Crime Count",
            "top_15_gang_related_total_crime_counties.png",
            "Offense Count",
        ),
        (
            "gang_related_weapon_law_violation_count",
            "Top 15 Tennessee Counties by Gang-Related Weapon Law Violation Count",
            "top_15_gang_related_weapon_law_counties.png",
            "Offense Count",
        ),
        (
            "explosive_related_pressure_score",
            "Top 15 Tennessee Counties by Explosive-Use Criminal Activity Pressure Score",
            "top_15_explosive_related_pressure_counties.png",
            "Score",
        ),
        (
            "explosive_related_total_offense_count",
            "Top 15 Tennessee Counties by Explosive-Related Total Offense Count",
            "top_15_explosive_related_total_offense_counties.png",
            "Offense Count",
        ),
        (
            "explosive_related_weapon_law_violation_count",
            "Top 15 Tennessee Counties by Explosive-Related Weapon Law Violation Count",
            "top_15_explosive_related_weapon_law_counties.png",
            "Offense Count",
        ),
        (
            "gang_explosive_pressure_score",
            "Top 15 Tennessee Counties by Gang + Explosive Intersection Pressure Score",
            "top_15_gang_explosive_pressure_counties.png",
            "Score",
        ),
        (
            "gang_explosive_total_offense_count",
            "Top 15 Tennessee Counties by Gang-Related Explosive-Use Total Offense Count",
            "top_15_gang_explosive_total_offense_counties.png",
            "Offense Count",
        ),
        (
            "gang_explosive_weapon_law_violation_count",
            "Top 15 Tennessee Counties by Gang-Related Explosive Weapon Law Violation Count",
            "top_15_gang_explosive_weapon_law_counties.png",
            "Offense Count",
        ),
        (
            "tactical_access_score",
            "Top 15 Tennessee Counties by Tactical Access Exposure Score",
            "top_15_tactical_access_counties.png",
            "Score",
        ),
        (
            "importer_ffl_count",
            "Top 15 Tennessee Counties by Importer FFL Count",
            "top_15_importer_ffl_counties.png",
            "FFL Count",
        ),
        (
            "destructive_device_ffl_count",
            "Top 15 Tennessee Counties by Destructive-Device-Related FFL Count",
            "top_15_destructive_device_ffl_counties.png",
            "FFL Count",
        ),
        (
            "banking_access_gap_score",
            "Top 15 Tennessee Counties by Banking Access Gap Score",
            "top_15_banking_access_gap_counties.png",
            "Score",
        ),
        (
            "poverty_adjusted_tobacco_vape_score",
            "Top 15 Tennessee Counties by Tobacco/Vape Retail Exposure Score",
            "top_15_tobacco_vape_exposure_counties.png",
            "Score",
        ),
    ]

    for value_col, title, filename, xlabel in chart_specs:
        path = save_bar_chart(
            scores_df,
            value_col,
            title,
            filename,
            xlabel=xlabel,
        )

        if path is not None:
            chart_paths.append(path)

    scatter_specs = [
        (
            "finance_tactical_vulnerability_score",
            "final_domestic_security_risk_score",
            "Finance & Tactical Vulnerability vs. Final Domestic Security Risk",
            "Finance & Tactical Vulnerability Score",
            "Final Domestic Security Risk Score",
            "finance_vs_final_risk_scatter.png",
        ),
        (
            "institutional_enforcement_pressure_score",
            "final_domestic_security_risk_score",
            "Institutional / Enforcement Pressure vs. Final Domestic Security Risk",
            "Institutional / Enforcement Pressure Score",
            "Final Domestic Security Risk Score",
            "institutional_enforcement_vs_final_risk_scatter.png",
        ),
        (
            "institutional_enforcement_pressure_score",
            "organized_violence_pressure_score",
            "Institutional / Enforcement Pressure vs. Organized Violence / High-Severity Crime Pressure",
            "Institutional / Enforcement Pressure Score",
            "Organized Violence / High-Severity Crime Pressure Score",
            "institutional_enforcement_vs_organized_violence_scatter.png",
        ),
        (
            "disaster_disruption_vulnerability_score",
            "final_domestic_security_risk_score",
            "Disaster / Disruption Vulnerability vs. Final Domestic Security Risk",
            "Disaster / Disruption Vulnerability Score",
            "Final Domestic Security Risk Score",
            "disaster_disruption_vs_final_risk_scatter.png",
        ),
        (
            "disaster_disruption_vulnerability_score",
            "institutional_enforcement_pressure_score",
            "Disaster / Disruption Vulnerability vs. Institutional / Enforcement Pressure",
            "Disaster / Disruption Vulnerability Score",
            "Institutional / Enforcement Pressure Score",
            "disaster_disruption_vs_institutional_enforcement_scatter.png",
        ),
        (
            "violent_crime_weapons_pressure_score",
            "final_domestic_security_risk_score",
            "Crime & Weapons Pressure vs. Final Domestic Security Risk",
            "Crime & Weapons Pressure Score",
            "Final Domestic Security Risk Score",
            "crime_weapons_vs_final_risk_scatter.png",
        ),
        (
            "organized_violence_pressure_score",
            "final_domestic_security_risk_score",
            "Organized Violence / High-Severity Crime Pressure vs. Final Domestic Security Risk",
            "Organized Violence / High-Severity Crime Pressure Score",
            "Final Domestic Security Risk Score",
            "organized_violence_vs_final_risk_scatter.png",
        ),
        (
            "organized_violence_pressure_score",
            "finance_tactical_vulnerability_score",
            "Organized Violence / High-Severity Crime Pressure vs. Finance & Tactical Vulnerability",
            "Organized Violence / High-Severity Crime Pressure Score",
            "Finance & Tactical Vulnerability Score",
            "organized_violence_vs_finance_tactical_scatter.png",
        ),
        (
            "overall_crime_rate_index_score",
            "organized_violence_pressure_score",
            "Overall Crime Rate Index vs. Organized Violence / High-Severity Crime Pressure",
            "Overall Crime Rate Index Score",
            "Organized Violence / High-Severity Crime Pressure Score",
            "overall_crime_rate_vs_organized_violence_scatter.png",
        ),
        (
            "targeted_harm_public_safety_pressure_score",
            "organized_violence_pressure_score",
            "Targeted Harm / Public-Safety Pressure vs. Organized Violence / High-Severity Crime Pressure",
            "Targeted Harm / Public-Safety Pressure Score",
            "Organized Violence / High-Severity Crime Pressure Score",
            "targeted_harm_vs_organized_violence_scatter.png",
        ),
        (
            "targeted_harm_public_safety_pressure_score",
            "institutional_enforcement_pressure_score",
            "Targeted Harm / Public-Safety Pressure vs. Institutional / Enforcement Pressure",
            "Targeted Harm / Public-Safety Pressure Score",
            "Institutional / Enforcement Pressure Score",
            "targeted_harm_vs_institutional_enforcement_scatter.png",
        ),
        (
            "hate_crime_targeted_harm_pressure_score",
            "targeted_harm_public_safety_pressure_score",
            "Hate-Crime / Targeted-Harm Pressure vs. Targeted Harm / Public-Safety Pressure",
            "Hate-Crime / Targeted-Harm Pressure Score",
            "Targeted Harm / Public-Safety Pressure Score",
            "hate_crime_vs_targeted_harm_scatter.png",
        ),
        (
            "law_enforcement_ambush_pressure_score",
            "targeted_harm_public_safety_pressure_score",
            "Law-Enforcement Ambush Pressure vs. Targeted Harm / Public-Safety Pressure",
            "Law-Enforcement Ambush Pressure Score",
            "Targeted Harm / Public-Safety Pressure Score",
            "law_enforcement_ambush_vs_targeted_harm_scatter.png",
        ),
        (
            "law_enforcement_assault_pressure_score",
            "institutional_enforcement_pressure_score",
            "Law-Enforcement Assault Pressure vs. Institutional / Enforcement Pressure",
            "Law-Enforcement Assault Pressure Score",
            "Institutional / Enforcement Pressure Score",
            "law_enforcement_assault_vs_institutional_enforcement_scatter.png",
        ),
        (
            "political_violence_exposure_score",
            "final_domestic_security_risk_score",
            "ACLED Political Violence / Civil Unrest Exposure vs. Final Domestic Security Risk",
            "Political Violence / Civil Unrest Exposure Score",
            "Final Domestic Security Risk Score",
            "political_violence_vs_final_risk_scatter.png",
        ),
        (
            "political_violence_exposure_score",
            "violent_crime_weapons_pressure_score",
            "ACLED Political Violence / Civil Unrest Exposure vs. Crime & Weapons Pressure",
            "Political Violence / Civil Unrest Exposure Score",
            "Crime & Weapons Pressure Score",
            "political_violence_vs_crime_weapons_scatter.png",
        ),
        (
            "gang_related_crime_pressure_score",
            "violent_crime_weapons_pressure_score",
            "Gang-Related Criminal Activity Pressure vs. Crime & Weapons Pressure",
            "Gang-Related Criminal Activity Pressure Score",
            "Crime & Weapons Pressure Score",
            "gang_pressure_vs_crime_weapons_scatter.png",
        ),
        (
            "gang_related_crime_pressure_score",
            "final_domestic_security_risk_score",
            "Gang-Related Criminal Activity Pressure vs. Final Domestic Security Risk",
            "Gang-Related Criminal Activity Pressure Score",
            "Final Domestic Security Risk Score",
            "gang_pressure_vs_final_risk_scatter.png",
        ),
        (
            "explosive_related_pressure_score",
            "violent_crime_weapons_pressure_score",
            "Explosive-Use Pressure vs. Crime & Weapons Pressure",
            "Explosive-Use Pressure Score",
            "Crime & Weapons Pressure Score",
            "explosive_pressure_vs_crime_weapons_scatter.png",
        ),
        (
            "explosive_related_pressure_score",
            "final_domestic_security_risk_score",
            "Explosive-Use Pressure vs. Final Domestic Security Risk",
            "Explosive-Use Pressure Score",
            "Final Domestic Security Risk Score",
            "explosive_pressure_vs_final_risk_scatter.png",
        ),
        (
            "gang_explosive_pressure_score",
            "violent_crime_weapons_pressure_score",
            "Gang + Explosive Intersection Pressure vs. Crime & Weapons Pressure",
            "Gang + Explosive Intersection Pressure Score",
            "Crime & Weapons Pressure Score",
            "gang_explosive_vs_crime_weapons_scatter.png",
        ),
        (
            "gang_explosive_pressure_score",
            "final_domestic_security_risk_score",
            "Gang + Explosive Intersection Pressure vs. Final Domestic Security Risk",
            "Gang + Explosive Intersection Pressure Score",
            "Final Domestic Security Risk Score",
            "gang_explosive_vs_final_risk_scatter.png",
        ),
        (
            "tactical_access_score",
            "political_violence_exposure_score",
            "Tactical Access vs. ACLED Political Violence / Civil Unrest Exposure",
            "Tactical Access Score",
            "Political Violence / Civil Unrest Exposure Score",
            "tactical_access_vs_political_violence_scatter.png",
        ),
        (
            "tactical_access_score",
            "violent_crime_weapons_pressure_score",
            "Tactical Access vs. Crime & Weapons Pressure",
            "Tactical Access Score",
            "Crime & Weapons Pressure Score",
            "tactical_access_vs_crime_weapons_scatter.png",
        ),
        (
            "destructive_device_ffl_count",
            "tactical_access_score",
            "Destructive-Device-Related FFL Count vs. Tactical Access Score",
            "Destructive-Device-Related FFL Count",
            "Tactical Access Score",
            "destructive_device_ffl_vs_tactical_access_scatter.png",
        ),
        (
            "banking_access_gap_score",
            "finance_tactical_vulnerability_score",
            "Banking Access Gap vs. Finance & Tactical Vulnerability",
            "Banking Access Gap Score",
            "Finance & Tactical Vulnerability Score",
            "banking_gap_vs_finance_tactical_scatter.png",
        ),
    ]

    for x_col, y_col, title, xlabel, ylabel, filename in scatter_specs:
        path = save_scatter_chart(
            scores_df,
            x_col,
            y_col,
            title,
            xlabel,
            ylabel,
            filename,
        )

        if path is not None:
            chart_paths.append(path)

    # Operational Risk & Protective Planning charts use the separate
    # data/processed/tn_operational_risk_features.csv output.
    chart_paths.extend(generate_operational_risk_charts())

    # Charts created outside visualization.py.
    chart_paths = _append_existing_charts(
        chart_paths,
        [
            # Sensitivity analysis
            "rank_stability_top_counties.png",
            "average_rank_top_counties.png",

            # Crime trend analysis
            "top_15_weapon_law_violation_yoy_change.png",
            "top_15_violent_crime_yoy_change.png",
            "top_15_crime_pressure_yoy_change.png",
        ],
    )

    return chart_paths
