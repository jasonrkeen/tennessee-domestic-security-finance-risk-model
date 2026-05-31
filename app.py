from pathlib import Path
import math

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = BASE_DIR / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
CHARTS_DIR = OUTPUTS_DIR / "charts"
REPORTS_DIR = OUTPUTS_DIR / "reports"
REPORT_PATH = REPORTS_DIR / "tennessee_domestic_security_finance_risk_report.pdf"


TABLES = {
    "scores": TABLES_DIR / "tn_county_domestic_security_scores.csv",
    "operational_risk": PROCESSED_DIR / "tn_operational_risk_features.csv",
    "components": TABLES_DIR / "tn_county_component_scores.csv",
    "finance": TABLES_DIR / "tn_county_finance_tactical_scores.csv",
    "crime_weapons": TABLES_DIR / "tn_county_crime_weapons_scores.csv",
    "organized": TABLES_DIR / "tn_county_organized_violence_scores.csv",
    "targeted": TABLES_DIR / "tn_county_targeted_harm_public_safety_scores.csv",
    "disruption": TABLES_DIR / "tn_county_disaster_disruption_scores.csv",
    "institutional": TABLES_DIR / "tn_county_institutional_enforcement_scores.csv",
    "political": TABLES_DIR / "tn_county_political_violence_scores.csv",
    "data_quality": TABLES_DIR / "tn_county_data_quality_flags.csv",
    "sensitivity": TABLES_DIR / "model_weight_sensitivity_results.csv",
    "rank_stability": TABLES_DIR / "top_county_rank_stability.csv",
    "scenario_leaders": TABLES_DIR / "scenario_top_county_leaders.csv",
    "crime_trend": TABLES_DIR / "tn_crime_weapons_trend_analysis.csv",
    "public_reference": TABLES_DIR / "tn_public_group_activity_reference.csv",
    "public_reference_validation": TABLES_DIR / "tn_public_group_reference_validation.csv",
    "tbi_hate_bias": TABLES_DIR / "tn_2024_hate_crime_bias_context.csv",
    "tbi_hate_offense": TABLES_DIR / "tn_2024_hate_crime_offense_context.csv",
    "tbi_hate_clearance": TABLES_DIR / "tn_2024_hate_crime_clearance_context.csv",
    "tbi_hate_location": TABLES_DIR / "tn_2024_hate_crime_location_context.csv",
    "tbi_hate_summary": TABLES_DIR / "tn_2024_hate_crime_report_context_summary.csv",
    "tdoc_stg_context": TABLES_DIR / "tn_tdoc_stg_reference_context.csv",
    "tdoc_stg_validation": TABLES_DIR / "tn_tdoc_stg_reference_validation.csv",
    "source_register": TABLES_DIR / "source_register.csv",
}


CHARTS = {
    "Final Risk": "top_15_final_risk_counties.png",
    "Finance / Tactical": "top_15_finance_tactical_risk_counties.png",
    "Organized Violence": "top_15_organized_violence_pressure_counties.png",
    "Institutional / Enforcement": "top_15_institutional_enforcement_pressure_counties.png",
    "Disaster / Disruption": "top_15_disaster_disruption_vulnerability_counties.png",
    "Targeted Harm / Public Safety": "top_15_targeted_harm_public_safety_pressure_counties.png",
    "Crime / Weapons": "top_15_crime_weapons_pressure_counties.png",
    "Overall Crime Rate": "top_15_overall_crime_rate_index_counties.png",
    "Gang Activity": "top_15_gang_related_crime_pressure_counties.png",
    "Explosive Use": "top_15_explosive_related_pressure_counties.png",
    "Gang + Explosive": "top_15_gang_explosive_pressure_counties.png",
    "Political Violence / Civil Unrest": "top_15_political_violence_exposure_counties.png",
    "Rank Stability": "rank_stability_top_counties.png",
    "Average Rank": "average_rank_top_counties.png",
    "Crime Trend YoY": "top_15_crime_pressure_yoy_change.png",

    # Operational Risk & Protective Planning charts
    "Operational Risk": "top_15_operational_risk_counties.png",
    "Operational Exposure": "top_15_operational_exposure_counties.png",
    "Resilience Gap": "top_15_resilience_gap_counties.png",
    "Transport Pressure": "top_15_transport_pressure_counties.png",
    "Infrastructure Pressure": "top_15_infrastructure_pressure_counties.png",
    "Public Safety Context": "top_15_public_safety_context_counties.png",
    "Healthcare Capacity Gap": "top_15_healthcare_capacity_gap_counties.png",
    "Law Enforcement Capacity Gap": "top_15_law_enforcement_capacity_gap_counties.png",
    "Operational Exposure vs Resilience Gap": "operational_exposure_vs_resilience_gap_scatter.png",
    "Transport vs Operational Exposure": "transport_pressure_vs_operational_exposure_scatter.png",
    "Infrastructure vs Operational Exposure": "infrastructure_pressure_vs_operational_exposure_scatter.png",
    "LE Capacity Gap vs Resilience Gap": "law_enforcement_capacity_gap_vs_resilience_gap_scatter.png",
    "Healthcare Gap vs Resilience Gap": "healthcare_capacity_gap_vs_resilience_gap_scatter.png",
}


FINAL_SCORE_WEIGHTS = {
    "finance_tactical_vulnerability_score": 0.30,
    "organized_violence_pressure_score": 0.20,
    "political_violence_exposure_score": 0.15,
    "household_financial_stress_score": 0.15,
    "disaster_disruption_vulnerability_score": 0.10,
    "tactical_access_score": 0.05,
    "institutional_enforcement_pressure_score": 0.05,
}


SCENARIO_PRESETS = {
    "Baseline Phase 6": FINAL_SCORE_WEIGHTS,
    "Finance Heavy": {
        "finance_tactical_vulnerability_score": 0.45,
        "organized_violence_pressure_score": 0.15,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.15,
        "disaster_disruption_vulnerability_score": 0.07,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.03,
    },
    "Organized Violence Heavy": {
        "finance_tactical_vulnerability_score": 0.20,
        "organized_violence_pressure_score": 0.40,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.08,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.07,
    },
    "Targeted Harm / Public Safety Heavy": {
        "finance_tactical_vulnerability_score": 0.20,
        "organized_violence_pressure_score": 0.25,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.10,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.20,
    },
    "Disaster / Disruption Heavy": {
        "finance_tactical_vulnerability_score": 0.20,
        "organized_violence_pressure_score": 0.15,
        "political_violence_exposure_score": 0.10,
        "household_financial_stress_score": 0.10,
        "disaster_disruption_vulnerability_score": 0.35,
        "tactical_access_score": 0.05,
        "institutional_enforcement_pressure_score": 0.05,
    },
}


def page_config() -> None:
    st.set_page_config(
        page_title="TN Domestic Security & Illicit Finance Risk Dashboard",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    path_obj = Path(path)
    if not path_obj.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(path_obj)
        df = df.loc[:, ~df.columns.duplicated()].copy()
        return df
    except Exception as exc:
        st.warning(f"Could not load {path_obj.name}: {exc}")
        return pd.DataFrame()


def load_tables() -> dict[str, pd.DataFrame]:
    return {name: load_csv(str(path)) for name, path in TABLES.items()}


def cols(df: pd.DataFrame, desired: list[str]) -> list[str]:
    present = []
    seen = set()

    for col in desired:
        if col in df.columns and col not in seen:
            present.append(col)
            seen.add(col)

    return present


def make_arrow_safe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Streamlit displays dataframes through Arrow. Object columns with mixed
    strings/numbers can produce Arrow conversion errors. This function is used
    for display only and does not modify source outputs.
    """

    out = df.copy()
    out = out.loc[:, ~out.columns.duplicated()].copy()

    for col in out.columns:
        if out[col].dtype == "object":
            out[col] = out[col].astype(str)

    return out


def show_df(df: pd.DataFrame, desired: list[str] | None = None, height: int = 420) -> None:
    if df.empty:
        st.info("No data available for this section.")
        return

    out = df.copy()

    if desired:
        present = cols(out, desired)
        if present:
            out = out[present]

    out = make_arrow_safe(out)
    st.dataframe(out, width="stretch", hide_index=True, height=height)


def score(value) -> str:
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):.1f}"
    except Exception:
        return "N/A"


def show_chart(key: str) -> None:
    filename = CHARTS.get(key, key)
    path = CHARTS_DIR / filename

    if path.exists():
        st.image(str(path), width="stretch")
        return

    stem_terms = [
        term
        for term in Path(filename).stem.split("_")
        if term not in {"top", "15", "county", "counties", "score"}
    ]

    candidates = []
    if CHARTS_DIR.exists() and stem_terms:
        for candidate in CHARTS_DIR.glob("*.png"):
            candidate_name = candidate.stem.lower()
            match_count = sum(term.lower() in candidate_name for term in stem_terms)
            if match_count >= max(2, min(3, len(stem_terms))):
                candidates.append((match_count, candidate))

    if candidates:
        candidates = sorted(candidates, key=lambda item: item[0], reverse=True)
        st.image(str(candidates[0][1]), width="stretch")
        st.caption(f"Loaded closest matching chart: {candidates[0][1].name}")
    else:
        st.info(f"Chart not found: outputs/charts/{filename}")


def sidebar(scores_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    st.sidebar.title("County-Level Dashboard Filters")
    st.sidebar.markdown(
        "These filters apply across county-level tabs. Public group, TBI hate-crime, and TDOC STG context layers remain non-scoring."
    )

    if scores_df.empty:
        return scores_df, [], []

    filtered = scores_df.copy()

    county_values = (
        sorted(filtered["county"].dropna().astype(str).unique())
        if "county" in filtered.columns
        else []
    )

    selected_counties = st.sidebar.multiselect(
        "Filter counties",
        county_values,
        default=[],
        key="sidebar_filter_counties_unique",
        placeholder="All counties",
    )

    if selected_counties:
        filtered = filtered[filtered["county"].astype(str).isin(selected_counties)]

    selected_signals: list[str] = []

    if "risk_signal" in filtered.columns:
        signals = sorted(scores_df["risk_signal"].dropna().astype(str).unique())

        selected_signals = st.sidebar.multiselect(
            "Filter risk signals",
            signals,
            default=[],
            key="sidebar_filter_risk_signals_unique",
            placeholder="All signals",
        )

        if selected_signals:
            filtered = filtered[filtered["risk_signal"].astype(str).isin(selected_signals)]

    st.sidebar.divider()
    st.sidebar.caption("Empty selections mean all counties / all signals.")
    st.sidebar.caption("Run `python main.py` before opening the dashboard.")
    return filtered, selected_counties, selected_signals


def apply_county_filter(df: pd.DataFrame, selected_counties: list[str]) -> pd.DataFrame:
    """
    Apply the sidebar county filter to any county-level output table.
    Non-county reference/context tables should not use this helper.
    """

    if df.empty or not selected_counties or "county" not in df.columns:
        return df

    return df[df["county"].astype(str).isin(selected_counties)].copy()


def filter_scores_by_signal(df: pd.DataFrame, selected_signals: list[str]) -> pd.DataFrame:
    """
    Apply the sidebar risk-signal filter to score-like tables that include risk_signal.
    Most component output tables do not include risk_signal, so county filtering is the
    primary cross-tab control for component tabs.
    """

    if df.empty or not selected_signals or "risk_signal" not in df.columns:
        return df

    return df[df["risk_signal"].astype(str).isin(selected_signals)].copy()


def metrics(scores_df: pd.DataFrame) -> None:
    if scores_df.empty:
        return

    if "final_domestic_security_risk_score" in scores_df.columns:
        top = scores_df.sort_values("final_domestic_security_risk_score", ascending=False).iloc[0]
    else:
        top = scores_df.iloc[0]

    avg_comp = (
        scores_df["data_completeness_score"].mean()
        if "data_completeness_score" in scores_df.columns
        else math.nan
    )

    elevated = 0
    if "risk_signal" in scores_df.columns:
        elevated = scores_df["risk_signal"].astype(str).str.contains(
            "Elevated|High",
            case=False,
            regex=True,
        ).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Top County",
        str(top.get("county", "N/A")),
        f"Score {score(top.get('final_domestic_security_risk_score'))}",
    )
    c2.metric("Top Signal", str(top.get("risk_signal", "N/A")))
    c3.metric("Avg. Source Completeness", f"{avg_comp:.1f}%" if not pd.isna(avg_comp) else "N/A")
    c4.metric("Elevated / High Counties", f"{int(elevated):,}")


def overview(scores_df: pd.DataFrame) -> None:
    st.header("Executive Overview")
    st.info(
        "This dashboard does not predict attacks, identify suspects, assess individual businesses or licensees, "
        "or label lawful activity as suspicious. Reference/context layers are non-scoring appendices only."
    )

    metrics(scores_df)

    st.subheader("Top County Risk Rankings")

    rank = (
        scores_df.sort_values("final_domestic_security_risk_score", ascending=False)
        if "final_domestic_security_risk_score" in scores_df.columns
        else scores_df
    )

    show_df(
        rank.head(15),
        [
            "county",
            "finance_tactical_vulnerability_score",
            "organized_violence_pressure_score",
            "political_violence_exposure_score",
            "disaster_disruption_vulnerability_score",
            "institutional_enforcement_pressure_score",
            "final_domestic_security_risk_score",
            "risk_signal",
            "model_confidence",
        ],
    )

    c1, c2 = st.columns(2)
    with c1:
        show_chart("Final Risk")
    with c2:
        show_chart("Finance / Tactical")


def rankings(scores_df: pd.DataFrame) -> None:
    st.header("County Risk Rankings")

    if scores_df.empty:
        st.info("No score data available.")
        return

    score_cols = [
        c
        for c in [
            "final_domestic_security_risk_score",
            "finance_tactical_vulnerability_score",
            "organized_violence_pressure_score",
            "violent_crime_weapons_pressure_score",
            "overall_crime_rate_index_score",
            "targeted_harm_public_safety_pressure_score",
            "disaster_disruption_vulnerability_score",
            "institutional_enforcement_pressure_score",
            "political_violence_exposure_score",
            "tactical_access_score",
            "household_financial_stress_score",
        ]
        if c in scores_df.columns
    ]

    if not score_cols:
        st.warning("No score columns found.")
        return

    selected = st.selectbox("Ranking score", score_cols, key="ranking_score_select")

    ranked = scores_df.sort_values(selected, ascending=False).copy()
    ranked.insert(0, "rank", range(1, len(ranked) + 1))

    show_df(
        ranked,
        ["rank", "county", selected, "final_domestic_security_risk_score", "risk_signal", "model_confidence"],
        600,
    )

    st.download_button(
        "Download ranked table",
        ranked.to_csv(index=False).encode("utf-8"),
        file_name=f"tn_county_rankings_{selected}.csv",
        mime="text/csv",
        key="download_ranked_table",
    )


def county_deep_dive(scores_df: pd.DataFrame) -> None:
    st.header("County Deep Dive")

    if scores_df.empty or "county" not in scores_df.columns:
        st.info("No score data available.")
        return

    selected = st.selectbox(
        "Select county",
        sorted(scores_df["county"].dropna().astype(str).unique()),
        key="county_deep_dive_select",
    )

    row_df = scores_df[scores_df["county"].astype(str).eq(selected)]

    if row_df.empty:
        return

    row = row_df.iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final Score", score(row.get("final_domestic_security_risk_score")))
    c2.metric("Signal", str(row.get("risk_signal", "N/A")))
    c3.metric("Confidence", str(row.get("model_confidence", "N/A")))
    c4.metric("Completeness", f"{score(row.get('data_completeness_score'))}%")

    detail = row_df.T.reset_index()
    detail.columns = ["metric", "value"]
    detail["value"] = detail["value"].astype(str)

    show_df(detail, height=650)


def layer(
    title: str,
    df: pd.DataFrame,
    score_col: str,
    table_cols: list[str],
    chart_key: str | None = None,
) -> None:
    st.header(title)

    if df.empty:
        st.info("No data available for this layer.")
        return

    ranked = df.sort_values(score_col, ascending=False) if score_col in df.columns else df

    show_df(ranked.head(25), table_cols, 520)

    if chart_key:
        st.subheader("Chart")
        show_chart(chart_key)


def scenarios(
    scores_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
    rank_stability_df: pd.DataFrame,
) -> None:
    st.header("Scenario Controls & Sensitivity Analysis")

    if scores_df.empty:
        st.info("No score data available.")
        return

    name = st.selectbox("Scenario preset", list(SCENARIO_PRESETS.keys()), key="scenario_preset_select")

    weights = {k: v for k, v in SCENARIO_PRESETS[name].items() if k in scores_df.columns}
    total = sum(weights.values())

    if total <= 0:
        st.warning("No scenario weight columns are available in the score output.")
        return

    scenario_df = scores_df.copy()
    scenario_df["dashboard_scenario_score"] = 0.0

    for col, weight in weights.items():
        scenario_df["dashboard_scenario_score"] += (
            pd.to_numeric(scenario_df[col], errors="coerce").fillna(0) * (weight / total)
        )

    scenario_df = scenario_df.sort_values("dashboard_scenario_score", ascending=False)
    scenario_df.insert(0, "dashboard_scenario_rank", range(1, len(scenario_df) + 1))

    show_df(
        scenario_df.head(20),
        [
            "dashboard_scenario_rank",
            "county",
            "dashboard_scenario_score",
            "final_domestic_security_risk_score",
            "risk_signal",
            "model_confidence",
        ],
        520,
    )

    with st.expander("Scenario weights"):
        show_df(pd.DataFrame([{"component": k, "weight": v} for k, v in weights.items()]), height=260)

    c1, c2 = st.columns(2)
    with c1:
        show_chart("Rank Stability")
    with c2:
        show_chart("Average Rank")

    st.subheader("Rank Stability Table")
    show_df(rank_stability_df, height=460)

    with st.expander("Full sensitivity output"):
        show_df(sensitivity_df, height=520)


def public_references(ref_df: pd.DataFrame, validation_df: pd.DataFrame) -> None:
    st.header("Public Group / Network Reference Register")
    st.warning(
        "Non-scoring reference layer. Not a terrorism, criminality, operational-presence, or county-risk label."
    )

    if ref_df.empty:
        st.info("No public reference output available.")
        return

    display = ref_df.copy()

    if "is_valid_reference" in display.columns:
        display = display[display["is_valid_reference"].astype(str).str.lower().isin(["true", "1", "yes"])]

    if "include_in_report" in display.columns:
        display = display[display["include_in_report"].astype(str).str.lower().isin(["true", "1", "yes"])]

    c1, c2, c3 = st.columns(3)
    c1.metric("Valid References", f"{len(display):,}")
    c2.metric("Categories", f"{display['category'].nunique():,}" if "category" in display.columns else "N/A")
    c3.metric("Sources", f"{display['source_name'].nunique():,}" if "source_name" in display.columns else "N/A")

    show_df(
        display,
        [
            "reference_id",
            "group_or_network_name",
            "category",
            "source_type",
            "source_name",
            "geographic_reference",
            "geo_level",
            "confidence_level",
            "responsible_use_flag",
        ],
        560,
    )

    with st.expander("Validation output"):
        show_df(validation_df, height=420)


def tbi_context(tables: dict[str, pd.DataFrame]) -> None:
    st.header("TBI 2024 Hate Crime Context")
    st.warning("Statewide context only. Non-scoring and not a replacement for the county-level hate-crime processor.")

    st.subheader("Summary")
    show_df(tables["tbi_hate_summary"], height=300)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Bias Context")
        show_df(tables["tbi_hate_bias"], height=360)
    with c2:
        st.subheader("Offense Context")
        show_df(tables["tbi_hate_offense"], height=360)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Clearance Context")
        show_df(tables["tbi_hate_clearance"], height=300)
    with c4:
        st.subheader("Location Context")
        show_df(tables["tbi_hate_location"], height=300)





def tdoc_stg_context(context_df: pd.DataFrame, validation_df: pd.DataFrame) -> None:
    st.header("TDOC Security Threat Group Context")

    st.warning(
        "Non-scoring correctional-system reference layer. This tab does not indicate current "
        "community presence, county-level activity, terrorism, ideology, or criminal conduct by "
        "any person, group, facility, business, or place."
    )

    st.markdown(
        """
This layer is intended to preserve carefully worded TDOC Security Threat Group context from public or historical
correctional-system sources. It is separate from the TBI county-level gang-related crime scoring layer.

Use boundaries:
- Treat 2010 TDOC threat-assessment entries as historical correctional-system context only.
- Treat FY2025 Statistical Abstract rows as facility-level aggregate correctional context only.
- Do not infer current street-level activity, county risk, terrorism, motive, ideology, or operational presence.
- Do not add symbols, tattoos, identifiers, ranks, phrases, addresses, individual names, or operational notes.
"""
    )

    if context_df.empty:
        st.info(
            "TDOC STG context output not found. Run `python src/tdoc_stg_reference_processor.py` "
            "or `python main.py` after adding the processor."
        )
        st.code("python src/tdoc_stg_reference_processor.py", language="powershell")
        return

    display = context_df.copy()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Context Rows", f"{len(display):,}")
    c2.metric(
        "Unique References",
        f"{display['group_or_network_name'].nunique():,}"
        if "group_or_network_name" in display.columns
        else "N/A",
    )
    c3.metric(
        "Source Years",
        f"{display['source_year'].nunique():,}" if "source_year" in display.columns else "N/A",
    )
    c4.metric(
        "Sources",
        f"{display['source_name'].nunique():,}" if "source_name" in display.columns else "N/A",
    )

    if "source_year" in display.columns:
        year_options = sorted(display["source_year"].dropna().astype(str).unique())
        selected_years = st.multiselect(
            "Filter by source year",
            year_options,
            default=[],
            placeholder="All years",
            key="tdoc_stg_year_filter",
        )
        if selected_years:
            display = display[display["source_year"].astype(str).isin(selected_years)]

    if "source_name" in display.columns:
        source_options = sorted(display["source_name"].dropna().astype(str).unique())
        selected_sources = st.multiselect(
            "Filter by source",
            source_options,
            default=[],
            placeholder="All sources",
            key="tdoc_stg_source_filter",
        )
        if selected_sources:
            display = display[display["source_name"].astype(str).isin(selected_sources)]

    st.subheader("TDOC STG Context Table")

    preferred_cols = [
        "reference_id",
        "group_or_network_name",
        "category",
        "source_type",
        "source_name",
        "source_year",
        "geographic_reference",
        "geo_level",
        "correctional_context_flag",
        "confirmed_member_count",
        "suspected_member_count",
        "total_member_count",
        "facility_context",
        "include_in_score",
        "responsible_use_flag",
    ]

    show_df(display, preferred_cols, height=620)

    st.download_button(
        "Download TDOC STG context table",
        display.to_csv(index=False).encode("utf-8"),
        file_name="tn_tdoc_stg_reference_context_filtered.csv",
        mime="text/csv",
        key="download_tdoc_stg_context",
    )

    with st.expander("Validation output"):
        show_df(validation_df, height=420)

def operational_risk_context(operational_df: pd.DataFrame, selected_counties: list[str]) -> None:
    st.header("Operational Risk & Protective Planning")

    st.info(
        "This layer is a defensive county-level planning aid. It uses aggregate indicators only and does not "
        "publish facility names, addresses, routes, schedules, coordinates, individual names, agency-level "
        "tactical details, or exploitable security details."
    )

    operational_df = apply_county_filter(operational_df, selected_counties)

    if operational_df.empty:
        st.warning(
            "Operational-risk output not found. Run `python src/operational_risk_features.py` "
            "or `python main.py` after integrating the operational-risk builder."
        )
        st.code("python src/operational_risk_features.py", language="powershell")
        return

    rank_col = (
        "final_operational_risk_score"
        if "final_operational_risk_score" in operational_df.columns
        else None
    )

    if rank_col:
        ranked = operational_df.sort_values(rank_col, ascending=False).copy()
        top = ranked.iloc[0]
    else:
        ranked = operational_df.copy()
        top = ranked.iloc[0]

    avg_score = (
        pd.to_numeric(operational_df.get("final_operational_risk_score"), errors="coerce").mean()
        if "final_operational_risk_score" in operational_df.columns
        else math.nan
    )

    limited_count = 0
    if "data_quality_flag" in operational_df.columns:
        limited_count = operational_df["data_quality_flag"].astype(str).str.contains(
            "Limited",
            case=False,
            na=False,
        ).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Top Operational-Risk County", str(top.get("county", "N/A")))
    c2.metric("Top Score", score(top.get("final_operational_risk_score")))
    c3.metric("Avg. Operational Score", f"{avg_score:.1f}" if not pd.isna(avg_score) else "N/A")
    c4.metric("Limited Data Rows", f"{int(limited_count):,}")

    st.subheader("County Operational-Risk Ranking")

    ranking_cols = [
        "county",
        "existing_threat_context_score",
        "operational_exposure_score",
        "resilience_gap_score",
        "final_operational_risk_score",
        "operational_risk_tier",
        "data_quality_flag",
    ]

    show_df(ranked.head(25), ranking_cols, 540)

    st.subheader("Operational-Risk Charts")

    chart_tabs = st.tabs(
        [
            "Risk",
            "Exposure",
            "Resilience",
            "Infrastructure",
            "Healthcare",
            "Law Enforcement",
            "Scatter",
        ]
    )

    with chart_tabs[0]:
        show_chart("Operational Risk")
    with chart_tabs[1]:
        show_chart("Operational Exposure")
        show_chart("Transport Pressure")
    with chart_tabs[2]:
        show_chart("Resilience Gap")
    with chart_tabs[3]:
        show_chart("Infrastructure Pressure")
    with chart_tabs[4]:
        show_chart("Healthcare Capacity Gap")
        show_chart("Healthcare Gap vs Resilience Gap")
    with chart_tabs[5]:
        show_chart("Law Enforcement Capacity Gap")
        show_chart("LE Capacity Gap vs Resilience Gap")
    with chart_tabs[6]:
        show_chart("Operational Exposure vs Resilience Gap")
        show_chart("Transport vs Operational Exposure")
        show_chart("Infrastructure vs Operational Exposure")

    st.subheader("Component View")

    component_cols = [
        "population_exposure_score",
        "density_exposure_score",
        "socioeconomic_pressure_score",
        "transport_pressure_score",
        "infrastructure_pressure_score",
        "public_safety_context_score",
        "healthcare_capacity_gap_score",
        "law_enforcement_capacity_score",
        "law_enforcement_capacity_gap_score",
        "fema_vulnerability_score",
        "fema_resilience_gap_score",
    ]

    available_components = [c for c in component_cols if c in operational_df.columns]

    if available_components:
        selected_component = st.selectbox(
            "Operational-risk component",
            available_components,
            key="operational_component_select",
        )

        component_rank = operational_df.sort_values(selected_component, ascending=False).copy()

        show_df(
            component_rank.head(25),
            [
                "county",
                selected_component,
                "operational_exposure_score",
                "resilience_gap_score",
                "final_operational_risk_score",
                "data_quality_flag",
            ],
            460,
        )
    else:
        st.info("No operational-risk component columns are available yet.")

    st.subheader("Law-Enforcement Capacity Baseline")
    st.caption(
        "CSLLEA 2018 is treated as a structural response-capacity baseline. It is not a threat indicator "
        "and should not be used to evaluate individual agencies."
    )

    le_cols = [
        "county",
        "law_enforcement_agency_count",
        "sheriff_office_count",
        "local_police_agency_count",
        "law_enforcement_sworn_personnel",
        "law_enforcement_sworn_per_100k",
        "law_enforcement_full_time_employees_per_100k",
        "patrol_response_agency_count",
        "dispatch_agency_count",
        "criminal_investigation_agency_count",
        "special_event_response_agency_count",
        "law_enforcement_capacity_score",
        "law_enforcement_capacity_gap_score",
        "law_enforcement_data_year",
    ]

    show_df(
        ranked.head(25),
        le_cols,
        420,
    )

    st.subheader("Exposure vs. Resilience Gap")

    scatter_cols = [
        "county",
        "operational_exposure_score",
        "resilience_gap_score",
        "final_operational_risk_score",
        "operational_risk_tier",
        "data_quality_flag",
    ]
    present_scatter_cols = cols(operational_df, scatter_cols)

    if {"operational_exposure_score", "resilience_gap_score"}.issubset(set(operational_df.columns)):
        chart_df = operational_df[present_scatter_cols].copy()

        numeric_cols = [
            "operational_exposure_score",
            "resilience_gap_score",
            "final_operational_risk_score",
        ]

        for col in numeric_cols:
            if col in chart_df.columns:
                chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

        chart_df = chart_df.dropna(
            subset=["operational_exposure_score", "resilience_gap_score"]
        ).copy()

        if chart_df.empty:
            st.info("No usable exposure/resilience rows are available for the scatter plot.")
        else:
            county_options = (
                sorted(chart_df["county"].dropna().astype(str).unique())
                if "county" in chart_df.columns
                else []
            )

            default_label_counties: list[str] = []

            if (
                "final_operational_risk_score" in chart_df.columns
                and "county" in chart_df.columns
            ):
                default_label_counties = (
                    chart_df.sort_values(
                        "final_operational_risk_score",
                        ascending=False,
                    )
                    .head(10)["county"]
                    .dropna()
                    .astype(str)
                    .tolist()
                )

            label_counties = st.multiselect(
                "Label counties on scatter",
                county_options,
                default=default_label_counties,
                key="operational_scatter_label_counties",
                help=(
                    "Select counties to display as text labels. Hover over any point "
                    "to see county name and component values."
                ),
            )

            if "county" in chart_df.columns:
                chart_df["county_label"] = chart_df["county"].astype(str).where(
                    chart_df["county"].astype(str).isin(label_counties),
                    "",
                )
            else:
                chart_df["county_label"] = ""

            hover_data = {
                "operational_exposure_score": ":.1f",
                "resilience_gap_score": ":.1f",
            }

            if "final_operational_risk_score" in chart_df.columns:
                hover_data["final_operational_risk_score"] = ":.1f"

            if "operational_risk_tier" in chart_df.columns:
                hover_data["operational_risk_tier"] = True

            if "data_quality_flag" in chart_df.columns:
                hover_data["data_quality_flag"] = True

            fig = px.scatter(
                chart_df,
                x="operational_exposure_score",
                y="resilience_gap_score",
                size=(
                    "final_operational_risk_score"
                    if "final_operational_risk_score" in chart_df.columns
                    else None
                ),
                color=(
                    "operational_risk_tier"
                    if "operational_risk_tier" in chart_df.columns
                    else None
                ),
                hover_name="county" if "county" in chart_df.columns else None,
                hover_data=hover_data,
                text="county_label",
                title="Operational Exposure vs. Resilience Gap",
            )

            fig.update_traces(
                textposition="top center",
                marker={"opacity": 0.72},
            )

            fig.update_layout(
                height=620,
                xaxis_title="Operational Exposure Score",
                yaxis_title="Resilience Gap Score",
                legend_title_text="Operational Risk Tier",
                margin={"l": 20, "r": 20, "t": 55, "b": 20},
            )

            fig.update_xaxes(range=[0, 100])
            fig.update_yaxes(range=[0, 100])

            st.plotly_chart(fig, width="stretch")

            st.caption(
                "Hover over any dot to identify the county. The default labels show the "
                "top 10 counties by final operational-risk score; use the selector above "
                "to label different counties."
            )

    show_df(operational_df[present_scatter_cols] if present_scatter_cols else operational_df, height=420)

    st.subheader("Data-Quality Notes")
    st.markdown(
        """
- `Strong`, `Partial`, and `Limited` describe source coverage, not threat level.
- Law-enforcement capacity is a CSLLEA 2018 response-capacity baseline, not a current staffing audit.
- Healthcare capacity, FEMA resilience, and law-enforcement capacity reduce the resilience-gap score when capacity is stronger.
- Transportation, infrastructure, population, socioeconomic, and public-safety indicators increase exposure context.
- This tab is for resilience planning and monitoring-priority context, not target identification.
"""
    )

    st.download_button(
        "Download operational-risk table",
        operational_df.to_csv(index=False).encode("utf-8"),
        file_name="tn_operational_risk_features_filtered.csv",
        mime="text/csv",
        key="download_operational_risk_table",
    )

def county_brief(scores_df: pd.DataFrame) -> None:
    st.header("County Intelligence Brief Generator")

    st.info(
        "This brief is generated from aggregate county-level model outputs only. "
        "It is not a prediction, investigative finding, or operational assessment."
    )

    if scores_df.empty or "county" not in scores_df.columns:
        st.info("No score data available.")
        return

    county_options = sorted(scores_df["county"].dropna().astype(str).unique())

    selected = st.selectbox(
        "Select county for brief",
        county_options,
        key="county_brief_select",
    )

    row_df = scores_df[scores_df["county"].astype(str).eq(selected)]

    if row_df.empty:
        st.warning("Selected county not found.")
        return

    row = row_df.iloc[0]

    score_fields = [
        ("Finance / Tactical Vulnerability", "finance_tactical_vulnerability_score"),
        ("Organized Violence / High-Severity Crime", "organized_violence_pressure_score"),
        ("Political Violence / Civil Unrest", "political_violence_exposure_score"),
        ("Household Financial Stress", "household_financial_stress_score"),
        ("Tactical Access Exposure", "tactical_access_score"),
        ("Disaster / Disruption Vulnerability", "disaster_disruption_vulnerability_score"),
        ("Targeted Harm / Public-Safety Pressure", "targeted_harm_public_safety_pressure_score"),
        ("Institutional / Enforcement Pressure", "institutional_enforcement_pressure_score"),
        ("Crime / Weapons Pressure", "violent_crime_weapons_pressure_score"),
        ("Overall Crime-Rate Index", "overall_crime_rate_index_score"),
        ("Gang-Related Criminal Activity Pressure", "gang_related_crime_pressure_score"),
        ("Explosive-Use Criminal Activity Pressure", "explosive_related_pressure_score"),
        ("Gang + Explosive Intersection Pressure", "gang_explosive_pressure_score"),
        ("Hate-Crime / Targeted-Harm Pressure", "hate_crime_targeted_harm_pressure_score"),
        ("Law-Enforcement Ambush Pressure", "law_enforcement_ambush_pressure_score"),
    ]

    available_scores = []

    for label, col in score_fields:
        if col in row_df.columns:
            try:
                value = float(row.get(col))
                if not pd.isna(value):
                    available_scores.append((label, col, value))
            except Exception:
                pass

    available_scores = sorted(available_scores, key=lambda item: item[2], reverse=True)
    top_drivers = available_scores[:5]

    final_score = score(row.get("final_domestic_security_risk_score"))
    signal = str(row.get("risk_signal", "N/A"))
    confidence = str(row.get("model_confidence", "N/A"))
    completeness = score(row.get("data_completeness_score"))
    population = row.get("population", "N/A")

    try:
        population_display = f"{int(float(population)):,}"
    except Exception:
        population_display = "N/A"

    driver_lines = "\n".join(
        f"- {label}: {value:.1f}" for label, _, value in top_drivers
    )

    if not driver_lines:
        driver_lines = "- No component scores available."

    brief_text = f"""# {selected} County Intelligence Brief

## Executive Snapshot

- **Final Model Score:** {final_score}
- **Risk Signal:** {signal}
- **Model Confidence:** {confidence}
- **Data Completeness:** {completeness}%
- **Population:** {population_display}

## Top Contributing Model Layers

{driver_lines}

## Analytical Interpretation

{selected} County's current model position reflects the relative overlap of aggregate county-level indicators across the Phase 6 framework. Higher component scores indicate stronger relative exposure within Tennessee counties, not proof of criminal activity, terrorism, extremism, illicit finance, or operational threat activity.

The most important interpretation is whether multiple independent indicator families reinforce the same monitoring-priority signal. For example, overlap among finance/tactical vulnerability, organized violence / high-severity crime pressure, disaster/disruption vulnerability, institutional/enforcement pressure, or political violence / civil unrest exposure may support further qualitative review.

## Responsible-Use Notes

This brief is generated from county-level aggregate public-source indicators only. It does not identify suspects, groups, businesses, licensees, agencies, addresses, facilities, or event locations. Public group / network references and statewide TBI hate-crime context are non-scoring appendix layers and are not used to calculate this county score.

## Recommended Analyst Next Steps

1. Review the county's top component scores against the data-quality flags.
2. Check whether high scores are driven by broad source coverage, true-zero conditions, or a small number of high per-capita indicators.
3. Compare the county's baseline rank with sensitivity-analysis rankings.
4. Use the PDF report and source register for source context before drawing any qualitative conclusion.
"""

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final Score", final_score)
    c2.metric("Signal", signal)
    c3.metric("Confidence", confidence)
    c4.metric("Completeness", f"{completeness}%")

    st.markdown(brief_text)

    st.download_button(
        "Download County Brief as Markdown",
        brief_text.encode("utf-8"),
        file_name=f"{selected.lower().replace(' ', '_')}_county_intelligence_brief.md",
        mime="text/markdown",
        key="download_county_brief_md",
    )

    with st.expander("Top driver table"):
        driver_df = pd.DataFrame(
            [
                {
                    "driver": label,
                    "field": col,
                    "score": round(value, 2),
                }
                for label, col, value in top_drivers
            ]
        )
        show_df(driver_df, height=260)

def model_card() -> None:
    st.header("Responsible Use / Model Card")
    st.markdown(
        """
### What this model does
- Compares Tennessee counties using aggregate public-source indicators.
- Supports relative monitoring-priority analysis.
- Documents source coverage, assumptions, and sensitivity.
- Provides non-scoring reference/context appendices.

### What this model does not do
- It does not predict attacks.
- It does not identify suspects, threat actors, members, victims, officers, or organizations.
- It does not assess individual businesses, licensees, addresses, agencies, or facilities.
- It does not label counties as having terrorism, extremism, or illicit-finance activity.
- It does not use public group / network references in scoring.

### Red lines
Do not add addresses, coordinates, social handles, recruitment channels, meeting locations, facility-level details,
case narratives, incident IDs, individual names, or operational notes to this project.
"""
    )


def pdf_tab() -> None:
    st.header("PDF Report")

    if REPORT_PATH.exists():
        st.success("PDF report found.")
        st.download_button(
            "Download PDF Report",
            REPORT_PATH.read_bytes(),
            file_name=REPORT_PATH.name,
            mime="application/pdf",
            key="download_pdf_report",
        )
    else:
        st.info("PDF report not found. Run `python main.py` first.")
        st.code("python main.py", language="powershell")


def main() -> None:
    page_config()
    tables = load_tables()
    scores_df = tables["scores"]

    if scores_df.empty:
        st.error("Main score output not found. Run `python main.py` first.")
        st.code("python main.py", language="powershell")

    filtered_scores, selected_counties, selected_signals = sidebar(scores_df)

    st.title("Tennessee Domestic Security & Illicit Finance Risk Intelligence Dashboard")
    st.caption(
        "County-level OSINT indicators only | Reference/context layers, including TDOC STG context, are non-scoring | "
        "Operational-risk layer is defensive protective-planning context | Portfolio decision-support product"
    )

    if selected_counties or selected_signals:
        county_label = ", ".join(selected_counties) if selected_counties else "All counties"
        signal_label = ", ".join(selected_signals) if selected_signals else "All signals"
        st.info(f"Active filters — Counties: {county_label} | Signals: {signal_label}")

    tabs = st.tabs(
        [
            "Overview",
            "Rankings",
            "County Deep Dive",
            "County Brief",
            "Operational Risk",
            "Finance / Tactical",
            "Organized Violence",
            "Targeted Harm",
            "Disaster / Disruption",
            "Institutional",
            "Political Violence",
            "Scenarios",
            "Data Quality",
            "Public References",
            "TBI Hate-Crime Context",
            "TDOC STG Context",
            "Sources",
            "Model Card",
            "PDF",
        ]
    )

    with tabs[0]:
        overview(filtered_scores)

    with tabs[1]:
        rankings(filtered_scores)

    with tabs[2]:
        county_deep_dive(filtered_scores)

    with tabs[3]:
        county_brief(filtered_scores)

    with tabs[4]:
        operational_risk_context(tables["operational_risk"], selected_counties)

    with tabs[5]:
        layer(
            "Finance / Tactical Vulnerability",
            apply_county_filter(tables["finance"], selected_counties),
            "finance_tactical_vulnerability_score",
            [
                "county",
                "bank_branch_count",
                "deposits_per_capita",
                "banking_access_gap_score",
                "cash_intensive_retail_score",
                "ffl_count",
                "dealer_ffl_count",
                "manufacturer_ffl_count",
                "importer_ffl_count",
                "destructive_device_ffl_count",
                "tactical_access_score",
                "finance_tactical_vulnerability_score",
            ],
            "Finance / Tactical",
        )

    with tabs[6]:
        layer(
            "Organized Violence / High-Severity Crime Pressure",
            apply_county_filter(tables["organized"], selected_counties),
            "organized_violence_pressure_score",
            [
                "county",
                "violent_crime_weapons_pressure_score",
                "overall_crime_rate_index_score",
                "gang_related_crime_pressure_score",
                "explosive_related_pressure_score",
                "gang_explosive_pressure_score",
                "targeted_harm_public_safety_pressure_score",
                "organized_violence_pressure_score",
            ],
            "Organized Violence",
        )

    with tabs[7]:
        layer(
            "Targeted Harm / Public-Safety Pressure",
            apply_county_filter(tables["targeted"], selected_counties),
            "targeted_harm_public_safety_pressure_score",
            [
                "county",
                "hate_crime_total_count",
                "hate_crime_intimidation_count",
                "hate_crime_aggravated_assault_count",
                "hate_crime_weapon_law_violation_count",
                "le_ambush_total_count",
                "le_ambush_aggravated_assault_count",
                "law_enforcement_assault_count",
                "hate_crime_targeted_harm_pressure_score",
                "law_enforcement_ambush_pressure_score",
                "targeted_harm_public_safety_pressure_score",
            ],
            "Targeted Harm / Public Safety",
        )

    with tabs[8]:
        layer(
            "Disaster / Disruption Vulnerability",
            apply_county_filter(tables["disruption"], selected_counties),
            "disaster_disruption_vulnerability_score",
            [
                "county",
                "disaster_declaration_count",
                "recent_disaster_declaration_count",
                "severe_weather_exposure_score",
                "power_disruption_exposure_score",
                "access_stress_score",
                "recovery_strain_exposure_score",
                "disaster_disruption_vulnerability_score",
            ],
            "Disaster / Disruption",
        )

    with tabs[9]:
        layer(
            "Institutional / Enforcement Pressure",
            apply_county_filter(tables["institutional"], selected_counties),
            "institutional_enforcement_pressure_score",
            [
                "county",
                "law_enforcement_assault_pressure_score",
                "law_enforcement_ambush_pressure_score",
                "violent_crime_weapons_pressure_score",
                "overall_crime_rate_index_score",
                "targeted_harm_public_safety_pressure_score",
                "disaster_disruption_vulnerability_score",
                "institutional_enforcement_pressure_score",
            ],
            "Institutional / Enforcement",
        )

    with tabs[10]:
        layer(
            "ACLED Political Violence / Civil Unrest",
            apply_county_filter(tables["political"], selected_counties),
            "political_violence_exposure_score",
            [
                "county",
                "protest_event_count",
                "violent_unrest_event_count",
                "political_violence_event_count",
                "strategic_development_count",
                "public_disorder_event_count",
                "total_acled_event_count",
                "acled_fatalities",
                "political_violence_exposure_score",
            ],
            "Political Violence / Civil Unrest",
        )

    with tabs[11]:
        scenarios(filtered_scores, tables["sensitivity"], tables["rank_stability"])

    with tabs[12]:
        st.header("Data Quality & Model Confidence")
        st.info("Data completeness measures source coverage, not risk.")
        show_df(apply_county_filter(tables["data_quality"], selected_counties), height=650)

    with tabs[13]:
        public_references(tables["public_reference"], tables["public_reference_validation"])

    with tabs[14]:
        tbi_context(tables)

    with tabs[15]:
        tdoc_stg_context(tables["tdoc_stg_context"], tables["tdoc_stg_validation"])

    with tabs[16]:
        st.header("Source Register")
        show_df(tables["source_register"], height=650)

    with tabs[17]:
        model_card()

    with tabs[18]:
        pdf_tab()

if __name__ == "__main__":
    main()
