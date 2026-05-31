from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.config import (
    CHARTS_DIR,
    PROCESSED_DIR,
    PUBLIC_GROUP_REFERENCE_OUTPUT,
    TDOC_STG_REFERENCE_CONTEXT_OUTPUT,
    TDOC_STG_REFERENCE_VALIDATION_OUTPUT,
    REPORTS_DIR,
    REPORT_SUBTITLE,
    REPORT_TITLE,
    SOURCE_REGISTER_OUTPUT,
    TABLES_DIR,
    TBI_HATE_CRIME_BIAS_CONTEXT_OUTPUT,
    TBI_HATE_CRIME_CLEARANCE_CONTEXT_OUTPUT,
    TBI_HATE_CRIME_LOCATION_CONTEXT_OUTPUT,
    TBI_HATE_CRIME_OFFENSE_CONTEXT_OUTPUT,
    TBI_HATE_CRIME_REPORT_CONTEXT_SUMMARY_OUTPUT,
)


def _fmt(value, decimals: int = 1):
    try:
        return f"{float(value):.{decimals}f}"
    except Exception:
        return "0.0"


def _fmt_int(value):
    try:
        return f"{int(round(float(value))):,}"
    except Exception:
        return "0"


def _fmt_money(value, decimals: int = 0):
    try:
        return f"${float(value):,.{decimals}f}"
    except Exception:
        return "$0"


def _fmt_pct(value, decimals: int = 1):
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except Exception:
        return "0.0%"


def _bool_flag(value):
    return "Y" if bool(value) else "N"


def _safe_text(value):
    if pd.isna(value):
        return ""
    return str(value)


def _safe_image(path: Path, width=6.5 * inch, height=4.2 * inch):
    if path.exists():
        try:
            return Image(str(path), width=width, height=height)
        except Exception:
            pass

    return Paragraph(
        f"Chart unavailable: {path.name}",
        getSampleStyleSheet()["BodyText"],
    )


def _build_table(data, header_background="#1f2937", font_size=7.5):
    table = Table(data, repeatRows=1)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_background)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f3f4f6")],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    return table


def _page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))

    footer_text = (
        "Tennessee Domestic Security & Illicit Finance Risk Intelligence Model | "
        "County-level OSINT indicators only"
    )

    canvas.drawString(36, 22, footer_text)
    canvas.drawRightString(576, 22, f"Page {doc.page}")

    canvas.restoreState()


def _risk_interpretation(score):
    try:
        score = float(score)
    except Exception:
        return "Insufficient data"

    if score >= 70:
        return "High monitoring priority"
    if score >= 55:
        return "Elevated monitoring priority"
    if score >= 35:
        return "Guarded / watch condition"
    return "Lower relative exposure"


def _load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


def _load_source_register():
    return _load_csv(SOURCE_REGISTER_OUTPUT)


def _load_crime_mapping_validation():
    return _load_csv(TABLES_DIR / "crime_offense_label_mapping_validation.csv")


def _load_rank_stability():
    return _load_csv(TABLES_DIR / "top_county_rank_stability.csv")


def _load_sensitivity_results():
    return _load_csv(TABLES_DIR / "model_weight_sensitivity_results.csv")


def _load_crime_trend_analysis():
    return _load_csv(TABLES_DIR / "tn_crime_weapons_trend_analysis.csv")


def _load_operational_risk_features():
    return _load_csv(PROCESSED_DIR / "tn_operational_risk_features.csv")


def _load_public_group_reference():
    return _load_csv(PUBLIC_GROUP_REFERENCE_OUTPUT)


def _load_tdoc_stg_reference_context():
    return _load_csv(TDOC_STG_REFERENCE_CONTEXT_OUTPUT)


def _load_tdoc_stg_reference_validation():
    return _load_csv(TDOC_STG_REFERENCE_VALIDATION_OUTPUT)


def _load_tbi_hate_crime_bias_context():
    return _load_csv(TBI_HATE_CRIME_BIAS_CONTEXT_OUTPUT)


def _load_tbi_hate_crime_offense_context():
    return _load_csv(TBI_HATE_CRIME_OFFENSE_CONTEXT_OUTPUT)


def _load_tbi_hate_crime_clearance_context():
    return _load_csv(TBI_HATE_CRIME_CLEARANCE_CONTEXT_OUTPUT)


def _load_tbi_hate_crime_location_context():
    return _load_csv(TBI_HATE_CRIME_LOCATION_CONTEXT_OUTPUT)


def _load_tbi_hate_crime_context_summary():
    return _load_csv(TBI_HATE_CRIME_REPORT_CONTEXT_SUMMARY_OUTPUT)


def _paragraph_cell(value, style):
    return Paragraph(_safe_text(value), style)


def generate_report(scores_df: pd.DataFrame):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_path = REPORTS_DIR / "tennessee_domestic_security_finance_risk_report.pdf"

    scores_df = scores_df.copy()

    if "final_domestic_security_risk_score" in scores_df.columns:
        scores_df = scores_df.sort_values(
            "final_domestic_security_risk_score",
            ascending=False,
        )

    operational_df = _load_operational_risk_features()

    if (
        not operational_df.empty
        and "final_operational_risk_score" in operational_df.columns
    ):
        operational_df = operational_df.sort_values(
            "final_operational_risk_score",
            ascending=False,
        )

    doc = SimpleDocTemplate(
        str(report_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#374151"),
        spaceAfter=14,
    )

    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#111827"),
        spaceBefore=12,
        spaceAfter=8,
    )

    sub_section_style = ParagraphStyle(
        "SubSectionHeader",
        parent=styles["Heading3"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
        spaceAfter=8,
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=6,
    )

    story = []

    # ------------------------------------------------------------------
    # Cover / Executive Summary
    # ------------------------------------------------------------------
    story.append(Paragraph(REPORT_TITLE, title_style))
    story.append(Paragraph(REPORT_SUBTITLE, subtitle_style))
    story.append(
        Paragraph(
            f"Prepared by Jason Keen | Generated {datetime.now().strftime('%Y-%m-%d')}",
            small_style,
        )
    )
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Executive Summary", section_style))

    if not scores_df.empty:
        top_county = scores_df.iloc[0]

        executive_summary = f"""
        This report presents a county-level open-source intelligence model for Tennessee focused on
        domestic security risk conditions, illicit-finance vulnerability, cash-economy exposure,
        formal banking access gaps, regulated retail indicators, lawful firearm-license aggregate
        exposure, tactical-access indicators, TBI CrimeInsight crime/weapons pressure, TBI
        organized-crime and explosive-use aggregate indicators, hate-crime / targeted-harm indicators,
        law-enforcement ambush indicators, ACLED political violence / civil unrest exposure,
        disaster/disruption vulnerability, and institutional/enforcement pressure. In the current model run,
        the highest-scoring county is <b>{_safe_text(top_county.get('county'))}</b>, with a final
        domestic security risk score of <b>{_fmt(top_county.get('final_domestic_security_risk_score'))}</b>,
        a signal of <b>{_safe_text(top_county.get('risk_signal'))}</b>, and model confidence of
        <b>{_safe_text(top_county.get('model_confidence'))}</b>.
        """
    else:
        executive_summary = """
        This report presents a county-level open-source intelligence model for Tennessee. No score data
        was available for this run.
        """

    story.append(Paragraph(executive_summary, body_style))

    if not operational_df.empty:
        top_operational = operational_df.iloc[0]
        operational_summary = f"""
        The report also includes an <b>Operational Risk &amp; Protective Planning</b> layer. This
        separate county-level layer combines public indicators related to population exposure,
        transportation pressure, infrastructure needs, public-safety context, healthcare capacity,
        FEMA vulnerability/resilience, and CSLLEA law-enforcement response-capacity baseline. In
        the current run, the highest operational-risk county is
        <b>{_safe_text(top_operational.get('county'))}</b>, with a final operational-risk score of
        <b>{_fmt(top_operational.get('final_operational_risk_score'))}</b> and a tier of
        <b>{_safe_text(top_operational.get('operational_risk_tier'))}</b>.
        """
        story.append(Paragraph(operational_summary, body_style))

    caution_text = """
    This model does <b>not</b> predict attacks, identify suspects, assess individual businesses,
    assess individual licensees, or label lawful activity as suspicious. Gang-related crime,
    explosive-use offenses, hate-crime offense counts, law-enforcement ambush counts, and
    gang-related explosive-use offenses are not terrorism labels.
    They are county-level high-severity criminal activity indicators that may warrant additional
    analysis when combined with other public-source layers. All sensitive scoring inputs are aggregated
    to the county level. Public group/network, TDOC correctional-system STG context, and statewide hate-crime context
    appendices are reference-only and are not included in risk scoring.
    """

    story.append(Paragraph(caution_text, body_style))

    story.append(Paragraph("Phase 6 Model Structure", section_style))

    model_structure = [
        [
            Paragraph("Component", small_style),
            Paragraph("Purpose", small_style),
            Paragraph("Status", small_style),
        ],
        [
            Paragraph("Finance & Tactical Vulnerability", small_style),
            Paragraph(
                "Financial stress, banking access, cash-intensive retail, regulated retail, "
                "and FFL / tactical-access proxies.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Organized Violence / High-Severity Crime Pressure", small_style),
            Paragraph(
                "TBI crime/weapons, overall crime rate, gang activity, explosive-use, "
                "gang + explosive intersection, and targeted harm / public-safety layers.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Political Violence / Civil Unrest", small_style),
            Paragraph(
                "ACLED-derived county-level protest, public disorder, political violence, "
                "strategic development, and fatality indicators.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Disaster / Disruption Vulnerability", small_style),
            Paragraph(
                "FEMA disaster declarations plus county-level disruption, access stress, "
                "communications, recovery strain, and vulnerability indicators.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Institutional / Enforcement Pressure", small_style),
            Paragraph(
                "Public-safety personnel pressure, law-enforcement assault / ambush, crime pressure, "
                "targeted harm, and disruption strain.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Operational Risk & Protective Planning", small_style),
            Paragraph(
                "County-level exposure, resilience gap, infrastructure pressure, healthcare capacity, "
                "transportation pressure, and CSLLEA law-enforcement response-capacity baseline.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Data Quality / Model Confidence", small_style),
            Paragraph(
                "Coverage flags for ACS, CBP, FDIC, FFL, FEMA, TBI CrimeInsight, ACLED, "
                "gang, explosives, hate crime, ambush, and institutional layers.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Crime Trend Analysis", small_style),
            Paragraph(
                "2023-to-2024 TBI CrimeInsight selected crime/weapons trend analysis.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Sensitivity Analysis", small_style),
            Paragraph(
                "Alternative weighting scenarios and top-county rank stability.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
        [
            Paragraph("Reference / Context Appendices", small_style),
            Paragraph(
                "Public group / network reference register, TDOC correctional-system STG context, and statewide TBI hate-crime context."
                "Reference-only and not included in risk scoring.",
                small_style,
            ),
            Paragraph("Active", small_style),
        ],
    ]

    model_structure_table = Table(
        model_structure,
        colWidths=[1.75 * inch, 4.15 * inch, 0.65 * inch],
        repeatRows=1,
    )
    model_structure_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 6.3),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f3f4f6")],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ALIGN", (-1, 1), (-1, -1), "CENTER"),
            ]
        )
    )

    story.append(model_structure_table)
    story.append(Spacer(1, 0.15 * inch))

    # ------------------------------------------------------------------
    # Key Findings
    # ------------------------------------------------------------------
    story.append(Paragraph("Key Findings", section_style))

    if not scores_df.empty:
        top_final = scores_df.head(5)
        top_finance = scores_df.sort_values(
            "finance_tactical_vulnerability_score",
            ascending=False,
        ).head(5)

        if "organized_violence_pressure_score" in scores_df.columns:
            top_organized = scores_df.sort_values(
                "organized_violence_pressure_score",
                ascending=False,
            ).head(5)
            organized_counties = ", ".join(top_organized["county"].astype(str).tolist())
        else:
            organized_counties = "not available"

        if "political_violence_exposure_score" in scores_df.columns:
            top_acled = scores_df.sort_values(
                "political_violence_exposure_score",
                ascending=False,
            ).head(5)
            acled_counties = ", ".join(top_acled["county"].astype(str).tolist())
        else:
            acled_counties = "not available"

        if "gang_explosive_pressure_score" in scores_df.columns:
            top_gang_explosive = scores_df.sort_values(
                "gang_explosive_pressure_score",
                ascending=False,
            ).head(5)
            gang_explosive_counties = ", ".join(
                top_gang_explosive["county"].astype(str).tolist()
            )
        else:
            gang_explosive_counties = "not available"

        final_counties = ", ".join(top_final["county"].astype(str).tolist())
        finance_counties = ", ".join(top_finance["county"].astype(str).tolist())

        avg_completeness = (
            scores_df["data_completeness_score"].mean()
            if "data_completeness_score" in scores_df.columns
            else 0
        )

        findings_text = f"""
        The top counties by final domestic security risk score are <b>{final_counties}</b>.
        The top counties by finance and tactical vulnerability are <b>{finance_counties}</b>.
        The top counties by organized violence / high-severity crime pressure are
        <b>{organized_counties}</b>. The top counties by gang + explosive intersection pressure are
        <b>{gang_explosive_counties}</b>. The top counties by ACLED political violence / civil unrest
        exposure are <b>{acled_counties}</b>. Average active-source completeness for this model run is
        <b>{_fmt(avg_completeness)}</b>. These rankings should be interpreted as relative
        county-level monitoring-priority indicators, not as findings of criminal conduct,
        extremist activity, or terrorism.
        """

        story.append(Paragraph(findings_text, body_style))

    # ------------------------------------------------------------------
    # Top Rankings Table
    # ------------------------------------------------------------------
    story.append(Paragraph("Top County Risk Rankings", section_style))

    top_table_df = scores_df.head(15).copy()

    table_data = [
        [
            "County",
            "Finance / Tactical",
            "Organized Violence",
            "Political Violence",
            "Financial Stress",
            "Tactical Access",
            "Disaster / Disruption",
            "Final",
            "Signal",
            "Confidence",
        ]
    ]

    for _, row in top_table_df.iterrows():
        table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt(row.get("finance_tactical_vulnerability_score")),
                _fmt(row.get("organized_violence_pressure_score")),
                _fmt(row.get("political_violence_exposure_score")),
                _fmt(row.get("household_financial_stress_score")),
                _fmt(row.get("tactical_access_score")),
                _fmt(row.get("disaster_disruption_vulnerability_score")),
                _fmt(row.get("final_domestic_security_risk_score")),
                _safe_text(row.get("risk_signal")),
                _safe_text(row.get("model_confidence")),
            ]
        )

    ranking_table = _build_table(table_data, font_size=5.4)
    ranking_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 1), (-3, -1), "RIGHT"),
                ("ALIGN", (-2, 1), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(ranking_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Finance & Tactical Access Analysis
    # ------------------------------------------------------------------
    story.append(Paragraph("Finance, Cash Economy & Tactical Access Layer", section_style))

    finance_text = """
    The finance and tactical-access layer captures county-level exposure to household financial
    stress, formal banking access gaps, cash-intensive commerce, regulated retail environments,
    lawful firearm-license aggregates, and lawful tactical-access indicators. Importer FFL and
    destructive-device-related FFL counts are treated as high-sensitivity subtype indicators.
    The destructive-device-related field can overlap with importer/manufacturer categories and
    should not be summed with subtypes to reconcile to total FFL count.
    """

    story.append(Paragraph(finance_text, body_style))

    finance_method_table = [
        ["Subcomponent", "Variables / Proxies", "Interpretation"],
        [
            "Household Financial Stress",
            "Poverty, unemployment, rent burden, income stress",
            "Economic pressure and household vulnerability",
        ],
        [
            "Banking Access Gap",
            "Bank branches per 10k residents and deposits per capita",
            "Formal financial access and financial-system depth proxy",
        ],
        [
            "Cash-Intensive Retail",
            "Used merchandise, gas stations, convenience stores, lending, laundry, used auto",
            "Cash-flow and small-business exposure proxy",
        ],
        [
            "FFL / Tactical Access",
            "Dealer, manufacturer, pawnbroker, collector, importer, destructive-device subtype, training, surplus, ranges",
            "Lawful access and regulatory-complexity proxy",
        ],
    ]

    story.append(_build_table(finance_method_table, font_size=6.6))
    story.append(Spacer(1, 0.15 * inch))

    finance_rank_df = scores_df.sort_values(
        "finance_tactical_vulnerability_score",
        ascending=False,
    ).head(12)

    finance_table_data = [
        [
            "County",
            "Branches",
            "Deposits / Capita",
            "Bank Gap",
            "Cash Retail",
            "FFL",
            "Dealer",
            "Mfr.",
            "Importer",
            "Destr. Device",
            "Tactical",
            "Finance Score",
        ]
    ]

    for _, row in finance_rank_df.iterrows():
        finance_table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt_int(row.get("bank_branch_count")),
                _fmt_money(row.get("deposits_per_capita")),
                _fmt(row.get("banking_access_gap_score")),
                _fmt(row.get("cash_intensive_retail_score")),
                _fmt_int(row.get("ffl_count")),
                _fmt_int(row.get("dealer_ffl_count")),
                _fmt_int(row.get("manufacturer_ffl_count")),
                _fmt_int(row.get("importer_ffl_count")),
                _fmt_int(row.get("destructive_device_ffl_count")),
                _fmt(row.get("tactical_access_score")),
                _fmt(row.get("finance_tactical_vulnerability_score")),
            ]
        )

    finance_table = _build_table(finance_table_data, font_size=5.3)
    finance_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(finance_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Organized Violence / High-Severity Crime Pressure
    # ------------------------------------------------------------------
    story.append(Paragraph("Organized Violence & High-Severity Crime Pressure", section_style))

    organized_text = """
    The organized violence / high-severity crime pressure layer combines multiple TBI-derived
    aggregate indicators: selected crime/weapons pressure, overall crime-rate pressure, gang-related
    criminal activity pressure, explosive-use criminal activity pressure, the gang + explosive
    intersection pressure layer, and targeted harm / public-safety pressure. The gang, explosives, and gang + explosives layers are not terrorism
    indicators. They are high-severity county-level criminal activity indicators used to identify
    where additional analytical review may be warranted.
    """

    story.append(Paragraph(organized_text, body_style))

    organized_method_table = [
        ["Subcomponent", "Weight", "Interpretation"],
        ["Crime / Weapons Pressure", "30%", "Selected TBI crime/weapons categories"],
        ["Overall Crime Rate Index", "15%", "Overall county crime rate and total crime pressure"],
        ["Gang-Related Activity Pressure", "18%", "Organized/group criminal activity proxy"],
        ["Explosive-Use Pressure", "13%", "High-severity capability/criminal-use proxy"],
        ["Gang + Explosive Intersection", "13%", "High-severity organized/group + explosive-use intersection proxy"],
        ["Targeted Harm / Public-Safety Pressure", "11%", "Bias-motivated offense and public-safety personnel violence proxy"],
    ]

    story.append(_build_table(organized_method_table, font_size=6.8))
    story.append(Spacer(1, 0.15 * inch))

    if "organized_violence_pressure_score" in scores_df.columns:
        organized_rank_df = scores_df.sort_values(
            "organized_violence_pressure_score",
            ascending=False,
        ).head(15)
    else:
        organized_rank_df = scores_df.head(0)

    organized_table_data = [
        [
            "County",
            "Crime / Weapons",
            "Overall Crime",
            "Gang",
            "Explosive",
            "Gang + Explosive",
            "Targeted Harm",
            "Organized Score",
        ]
    ]

    for _, row in organized_rank_df.iterrows():
        organized_table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt(row.get("violent_crime_weapons_pressure_score")),
                _fmt(row.get("overall_crime_rate_index_score")),
                _fmt(row.get("gang_related_crime_pressure_score")),
                _fmt(row.get("explosive_related_pressure_score")),
                _fmt(row.get("gang_explosive_pressure_score")),
                _fmt(row.get("targeted_harm_public_safety_pressure_score")),
                _fmt(row.get("organized_violence_pressure_score")),
            ]
        )

    organized_table = _build_table(organized_table_data, font_size=6.0)
    organized_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(organized_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Gang, Explosives, and Gang + Explosives Deep Dive
    # ------------------------------------------------------------------
    story.append(Paragraph("Gang, Explosive-Use & Intersection Layers", section_style))

    sensitive_layer_text = """
    This section presents aggregate county-level counts for the Phase 6 TBI organized/high-severity layers. These fields
    do not identify individuals, groups, gang names, locations, incident IDs, addresses, victims,
    suspects, organizations, or case narratives. They are intended only to strengthen county-level
    monitoring-priority analysis.
    """

    story.append(Paragraph(sensitive_layer_text, body_style))

    sensitive_rank_df = scores_df.sort_values(
        "gang_explosive_pressure_score",
        ascending=False,
    ).head(15)

    sensitive_table_data = [
        [
            "County",
            "Gang Total",
            "Gang Violent",
            "Gang Weapon",
            "Explosive Total",
            "Explosive Weapon",
            "Gang+Explosive Total",
            "Gang+Explosive Weapon",
            "Gang+Explosive Score",
        ]
    ]

    for _, row in sensitive_rank_df.iterrows():
        sensitive_table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt_int(row.get("gang_related_total_crime_count")),
                _fmt_int(row.get("gang_related_violent_crime_count")),
                _fmt_int(row.get("gang_related_weapon_law_violation_count")),
                _fmt_int(row.get("explosive_related_total_offense_count")),
                _fmt_int(row.get("explosive_related_weapon_law_violation_count")),
                _fmt_int(row.get("gang_explosive_total_offense_count")),
                _fmt_int(row.get("gang_explosive_weapon_law_violation_count")),
                _fmt(row.get("gang_explosive_pressure_score")),
            ]
        )

    sensitive_table = _build_table(sensitive_table_data, font_size=5.4)
    sensitive_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(sensitive_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Targeted Harm / Public-Safety Personnel Pressure
    # ------------------------------------------------------------------
    story.append(Paragraph("Targeted Harm & Public-Safety Personnel Pressure", section_style))

    targeted_text = """
    The targeted harm / public-safety personnel pressure layer combines TBI hate-crime offense
    aggregates with law-enforcement ambush aggregates. These indicators are not terrorism labels
    and do not infer motive, ideology, or actor identity. They are county-level public-safety
    pressure indicators that may warrant further contextual review when combined with other
    model layers.
    """

    story.append(Paragraph(targeted_text, body_style))

    if "targeted_harm_public_safety_pressure_score" in scores_df.columns:
        targeted_rank_df = scores_df.sort_values(
            "targeted_harm_public_safety_pressure_score",
            ascending=False,
        ).head(15)
    else:
        targeted_rank_df = scores_df.head(0)

    targeted_table_data = [
        [
            "County",
            "Hate Crime Total",
            "Hate Intimidation",
            "Hate Agg. Assault",
            "Hate Weapon Law",
            "LE Ambush Total",
            "LE Ambush Agg. Assault",
            "LE Assault",
            "Targeted Harm Score",
        ]
    ]

    for _, row in targeted_rank_df.iterrows():
        targeted_table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt_int(row.get("hate_crime_total_count")),
                _fmt_int(row.get("hate_crime_intimidation_count")),
                _fmt_int(row.get("hate_crime_aggravated_assault_count")),
                _fmt_int(row.get("hate_crime_weapon_law_violation_count")),
                _fmt_int(row.get("le_ambush_total_count")),
                _fmt_int(row.get("le_ambush_aggravated_assault_count")),
                _fmt_int(row.get("law_enforcement_assault_count")),
                _fmt(row.get("targeted_harm_public_safety_pressure_score")),
            ]
        )

    targeted_table = _build_table(targeted_table_data, font_size=5.2)
    targeted_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(targeted_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Disaster / Disruption Vulnerability
    # ------------------------------------------------------------------
    story.append(Paragraph("Disaster & Disruption Vulnerability Layer", section_style))

    disaster_text = """
    The disaster / disruption vulnerability layer extends the FEMA disaster declaration history
    with optional county-level severe weather, power disruption, access stress, communications
    disruption, social vulnerability, recovery strain, and repeat-disruption exposure fields.
    This layer is designed to capture disruption conditions that can increase planning complexity,
    strain public resources, or affect continuity and response posture.
    """

    story.append(Paragraph(disaster_text, body_style))

    if "disaster_disruption_vulnerability_score" in scores_df.columns:
        disaster_rank_df = scores_df.sort_values(
            "disaster_disruption_vulnerability_score",
            ascending=False,
        ).head(15)
    else:
        disaster_rank_df = scores_df.head(0)

    disaster_table_data = [
        [
            "County",
            "FEMA Decl.",
            "Recent Decl.",
            "Severe Weather",
            "Power Disrupt.",
            "Access Stress",
            "Recovery Strain",
            "Disruption Score",
        ]
    ]

    for _, row in disaster_rank_df.iterrows():
        disaster_table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt_int(row.get("disaster_declaration_count")),
                _fmt_int(row.get("recent_disaster_declaration_count")),
                _fmt(row.get("severe_weather_exposure_score")),
                _fmt(row.get("power_disruption_exposure_score")),
                _fmt(row.get("access_stress_score")),
                _fmt(row.get("recovery_strain_exposure_score")),
                _fmt(row.get("disaster_disruption_vulnerability_score")),
            ]
        )

    disaster_table = _build_table(disaster_table_data, font_size=5.5)
    disaster_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(disaster_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Institutional / Enforcement Pressure
    # ------------------------------------------------------------------
    story.append(Paragraph("Institutional & Enforcement Pressure Layer", section_style))

    institutional_text = """
    Institutional / enforcement pressure is now an active derived layer. It combines
    law-enforcement ambush pressure, law-enforcement assault pressure, crime/weapons pressure,
    overall crime-rate pressure, targeted harm / public-safety pressure, and disaster/disruption
    vulnerability. The score is intended to represent county-level public-safety and institutional
    response pressure, not misconduct, ideology, or threat actor identity.
    """

    story.append(Paragraph(institutional_text, body_style))

    if "institutional_enforcement_pressure_score" in scores_df.columns:
        institutional_rank_df = scores_df.sort_values(
            "institutional_enforcement_pressure_score",
            ascending=False,
        ).head(15)
    else:
        institutional_rank_df = scores_df.head(0)

    institutional_table_data = [
        [
            "County",
            "LE Assault Pressure",
            "LE Ambush Pressure",
            "Crime / Weapons",
            "Overall Crime",
            "Targeted Harm",
            "Disruption",
            "Institutional Score",
        ]
    ]

    for _, row in institutional_rank_df.iterrows():
        institutional_table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt(row.get("law_enforcement_assault_pressure_score")),
                _fmt(row.get("law_enforcement_ambush_pressure_score")),
                _fmt(row.get("violent_crime_weapons_pressure_score")),
                _fmt(row.get("overall_crime_rate_index_score")),
                _fmt(row.get("targeted_harm_public_safety_pressure_score")),
                _fmt(row.get("disaster_disruption_vulnerability_score")),
                _fmt(row.get("institutional_enforcement_pressure_score")),
            ]
        )

    institutional_table = _build_table(institutional_table_data, font_size=5.5)
    institutional_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(institutional_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Crime / Weapons Pressure
    # ------------------------------------------------------------------
    story.append(Paragraph("TBI CrimeInsight Crime & Weapons Pressure Layer", section_style))

    crime_text = """
    The crime/weapons pressure layer uses TBI CrimeInsight or TNCrimeOnline aggregate county-level
    offense exports. Current fields include homicide, kidnapping/abduction, weapon law violations,
    violent crime, aggravated assault, arson, sex offenses, hate crime, and law-enforcement assault
    when available. The model uses county-level counts and per-capita rates only.
    """

    story.append(Paragraph(crime_text, body_style))

    if "violent_crime_weapons_pressure_score" in scores_df.columns:
        crime_rank_df = scores_df.sort_values(
            "violent_crime_weapons_pressure_score",
            ascending=False,
        ).head(15)
    else:
        crime_rank_df = scores_df.head(0)

    crime_table_data = [
        [
            "County",
            "Homicide",
            "Kidnap",
            "Weapon Law",
            "Violent Crime",
            "Agg Assault",
            "Arson",
            "Sex Off.",
            "Weapon Rate",
            "Crime Score",
        ]
    ]

    for _, row in crime_rank_df.iterrows():
        crime_table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt_int(row.get("homicide_count")),
                _fmt_int(row.get("kidnapping_abduction_count")),
                _fmt_int(row.get("weapons_law_violation_count")),
                _fmt_int(row.get("violent_crime_count")),
                _fmt_int(row.get("aggravated_assault_count")),
                _fmt_int(row.get("arson_count")),
                _fmt_int(row.get("sex_offense_count")),
                _fmt(row.get("weapons_law_violation_rate_per_10k")),
                _fmt(row.get("violent_crime_weapons_pressure_score")),
            ]
        )

    crime_table = _build_table(crime_table_data, font_size=5.5)
    crime_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(crime_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Crime Trend Analysis
    # ------------------------------------------------------------------
    story.append(Paragraph("CrimeInsight 2023-2024 Trend Analysis", section_style))

    trend_text = """
    The crime trend layer compares selected TBI CrimeInsight crime/weapons indicators between
    2023 and 2024. The trend table is used as supporting context and is not directly embedded into
    the final score unless separately modeled. It helps identify counties with rising selected
    crime/weapons pressure.
    """

    story.append(Paragraph(trend_text, body_style))

    trend_df = _load_crime_trend_analysis()

    if not trend_df.empty:
        trend_display = trend_df.sort_values(
            "crime_pressure_yoy_change",
            ascending=False,
        ).head(15)

        trend_table_data = [
            [
                "County",
                "Selected Crime 2023",
                "Selected Crime 2024",
                "Abs. Change",
                "Pct. Change",
                "Weapons YoY",
                "Violent YoY",
                "Trend Signal",
            ]
        ]

        for _, row in trend_display.iterrows():
            trend_table_data.append(
                [
                    _safe_text(row.get("county")),
                    _fmt_int(row.get("total_selected_crime_count_2023")),
                    _fmt_int(row.get("total_selected_crime_count_2024")),
                    _fmt_int(row.get("total_selected_crime_abs_change")),
                    _fmt(row.get("total_selected_crime_pct_change")),
                    _fmt_int(row.get("weapon_law_violation_yoy_change")),
                    _fmt_int(row.get("violent_crime_yoy_change")),
                    _safe_text(row.get("trend_signal")),
                ]
            )

        trend_table = _build_table(trend_table_data, font_size=5.8)
        trend_table.setStyle(TableStyle([("ALIGN", (1, 1), (-2, -1), "RIGHT")]))
        story.append(trend_table)

        story.append(Spacer(1, 0.15 * inch))
        story.append(_safe_image(CHARTS_DIR / "top_15_crime_pressure_yoy_change.png"))
        story.append(Paragraph("Top counties by selected crime/weapons YoY increase.", small_style))
    else:
        story.append(
            Paragraph(
                "Crime trend output was not found. Run python -m src.crime_trend_analysis "
                "or python main.py before generating the report.",
                body_style,
            )
        )

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # CrimeInsight Offense Mapping Validation
    # ------------------------------------------------------------------
    story.append(Paragraph("CrimeInsight Offense Mapping Validation", section_style))

    mapping_text = """
    This validation table documents how raw TBI CrimeInsight offense labels are mapped into
    model input fields. Unmapped labels are retained for audit review but are not included in the
    crime/weapons score unless intentionally mapped into a model field.
    """

    story.append(Paragraph(mapping_text, body_style))

    mapping_df = _load_crime_mapping_validation()

    if not mapping_df.empty:
        mapping_table_data = [
            [
                "CrimeInsight Label",
                "Normalized Label",
                "Mapped Model Field",
                "Total Count",
            ]
        ]

        display_mapping = mapping_df.sort_values(
            ["metric", "source_offense_label"]
        ).copy()

        for _, row in display_mapping.iterrows():
            mapping_table_data.append(
                [
                    Paragraph(_safe_text(row.get("source_offense_label")), small_style),
                    Paragraph(_safe_text(row.get("normalized_offense_label")), small_style),
                    Paragraph(_safe_text(row.get("metric")), small_style),
                    _fmt_int(row.get("total_count")),
                ]
            )

        mapping_table = _build_table(mapping_table_data, font_size=5.8)
        mapping_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(mapping_table)
    else:
        story.append(
            Paragraph(
                "CrimeInsight offense-label mapping validation file was not found. "
                "Run python -m src.crime_offense_processor before generating the report.",
                body_style,
            )
        )

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # ACLED Political Violence / Civil Unrest Layer
    # ------------------------------------------------------------------
    story.append(Paragraph("ACLED Political Violence & Civil Unrest Layer", section_style))

    acled_text = """
    The political violence and civil unrest layer uses ACLED-derived Tennessee event data
    aggregated to the county level. The model preserves only county-level aggregate counts and
    rates. It does not publish event notes, actor names, organization names, exact locations,
    coordinates, URLs, or site-level maps.
    """

    story.append(Paragraph(acled_text, body_style))

    if "political_violence_exposure_score" in scores_df.columns:
        acled_rank_df = scores_df.sort_values(
            "political_violence_exposure_score",
            ascending=False,
        ).head(15)
    else:
        acled_rank_df = scores_df.head(0)

    acled_table_data = [
        [
            "County",
            "Protest",
            "Violent Unrest",
            "Political Violence",
            "Strategic Dev.",
            "Public Disorder",
            "Total Events",
            "Fatalities",
            "ACLED Score",
        ]
    ]

    for _, row in acled_rank_df.iterrows():
        acled_table_data.append(
            [
                _safe_text(row.get("county")),
                _fmt_int(row.get("protest_event_count")),
                _fmt_int(row.get("violent_unrest_event_count")),
                _fmt_int(row.get("political_violence_event_count")),
                _fmt_int(row.get("strategic_development_count")),
                _fmt_int(row.get("public_disorder_event_count")),
                _fmt_int(row.get("total_acled_event_count")),
                _fmt_int(row.get("acled_fatalities")),
                _fmt(row.get("political_violence_exposure_score")),
            ]
        )

    acled_table = _build_table(acled_table_data, font_size=5.5)
    acled_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(acled_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Operational Risk & Protective Planning
    # ------------------------------------------------------------------
    story.append(Paragraph("Operational Risk & Protective Planning Layer", section_style))

    operational_text = """
    The operational-risk layer is a separate defensive planning layer. It is designed to help
    interpret where county-level exposure, infrastructure pressure, transportation pressure,
    public-safety context, healthcare capacity, FEMA vulnerability/resilience, and CSLLEA
    law-enforcement response-capacity baseline may create greater protective-planning complexity.
    This layer is not a targeting product and does not identify facilities, addresses, routes,
    individuals, schedules, agency-level tactical details, or exploitable vulnerabilities.
    """

    story.append(Paragraph(operational_text, body_style))

    operational_method_table = [
        [
            Paragraph("Component", small_style),
            Paragraph("Interpretation", small_style),
            Paragraph("Model Treatment", small_style),
        ],
        [
            Paragraph("Operational Exposure", small_style),
            Paragraph(
                "Population density, transportation pressure, infrastructure pressure, "
                "public-safety context, and socioeconomic pressure.",
                small_style,
            ),
            Paragraph("Higher values increase operational-risk context.", small_style),
        ],
        [
            Paragraph("Resilience Gap", small_style),
            Paragraph(
                "Healthcare capacity gap, FEMA resilience gap, FEMA vulnerability, "
                "and law-enforcement capacity gap.",
                small_style,
            ),
            Paragraph(
                "Higher values indicate weaker response-capacity / resilience context.",
                small_style,
            ),
        ],
        [
            Paragraph("Law-Enforcement Capacity", small_style),
            Paragraph(
                "CSLLEA 2018 county-level response-capacity baseline.",
                small_style,
            ),
            Paragraph(
                "Used as a defensive capacity proxy, not as a threat indicator.",
                small_style,
            ),
        ],
        [
            Paragraph("Infrastructure Pressure", small_style),
            Paragraph(
                "TACIR public infrastructure needs per capita.",
                small_style,
            ),
            Paragraph(
                "Used as a broad continuity and public-sector pressure proxy.",
                small_style,
            ),
        ],
    ]

    operational_method_table_obj = Table(
        operational_method_table,
        colWidths=[1.50 * inch, 3.35 * inch, 1.65 * inch],
        repeatRows=1,
    )
    operational_method_table_obj.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 5.8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f3f4f6")],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story.append(operational_method_table_obj)
    story.append(Spacer(1, 0.15 * inch))

    law_enforcement_capacity_note = """
    Higher law-enforcement capacity gap values indicate lower relative county-level
    response-capacity proxy values in the 2018 CSLLEA baseline. They should not be
    interpreted as agency performance ratings, current staffing adequacy, or tactical
    capability assessments.
    """
    story.append(Paragraph(law_enforcement_capacity_note, small_style))

    if not operational_df.empty:
        operational_rank_df = operational_df.sort_values(
            "final_operational_risk_score",
            ascending=False,
        ).head(15)

        operational_table_data = [
            [
                "County",
                "Final Op. Risk",
                "Tier",
                "Exposure",
                "Resilience Gap",
                "Infrastructure",
                "Healthcare Gap",
                "LE Capacity Gap",
                "Data Quality",
            ]
        ]

        for _, row in operational_rank_df.iterrows():
            operational_table_data.append(
                [
                    _safe_text(row.get("county")),
                    _fmt(row.get("final_operational_risk_score")),
                    _safe_text(row.get("operational_risk_tier")),
                    _fmt(row.get("operational_exposure_score")),
                    _fmt(row.get("resilience_gap_score")),
                    _fmt(row.get("infrastructure_pressure_score")),
                    _fmt(row.get("healthcare_capacity_gap_score")),
                    _fmt(row.get("law_enforcement_capacity_gap_score")),
                    _safe_text(row.get("data_quality_flag")),
                ]
            )

        operational_table = _build_table(operational_table_data, font_size=5.4)
        operational_table.setStyle(TableStyle([("ALIGN", (1, 1), (-2, -1), "RIGHT")]))
        story.append(operational_table)
        story.append(Spacer(1, 0.15 * inch))

        story.append(_safe_image(CHARTS_DIR / "top_15_operational_risk_counties.png"))
        story.append(Paragraph("Top counties by final operational-risk score.", small_style))
        story.append(Spacer(1, 0.15 * inch))

        story.append(_safe_image(CHARTS_DIR / "operational_exposure_vs_resilience_gap_scatter.png"))
        story.append(
            Paragraph(
                "Operational exposure compared with resilience gap. Counties in the upper-right quadrant warrant closer defensive planning review.",
                small_style,
            )
        )
    else:
        story.append(
            Paragraph(
                "Operational-risk output was not found. Run python main.py after preparing the operational-risk source layers.",
                body_style,
            )
        )

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Data Quality and Model Confidence
    # ------------------------------------------------------------------
    story.append(Paragraph("Data Quality & Model Confidence", section_style))

    data_quality_text = """
    The model includes a data-quality layer that measures whether each county has usable data
    from the active Phase 6 source layers: ACS, CBP, FDIC, FFL, FEMA, disaster/disruption, TBI CrimeInsight
    crime/weapons, TBI crime rate, ACLED, TBI gang activity, TBI explosive-use activity, TBI gang +
    explosives intersection data, hate-crime offenses, law-enforcement ambush, targeted harm /
    public-safety, and institutional/enforcement pressure. This score does not measure risk. It measures source coverage.
    """

    story.append(Paragraph(data_quality_text, body_style))

    if "data_completeness_score" in scores_df.columns:
        quality_df = scores_df.sort_values(
            "data_completeness_score",
            ascending=True,
        ).head(15)

        quality_table_data = [
            [
                "County",
                "ACS",
                "CBP",
                "FDIC",
                "FFL",
                "FEMA",
                "Disrupt.",
                "Crime",
                "Rate",
                "ACLED",
                "Gang",
                "Expl.",
                "G+E",
                "Hate",
                "Ambush",
                "Inst.",
                "Completeness",
                "Confidence",
            ]
        ]

        for _, row in quality_df.iterrows():
            quality_table_data.append(
                [
                    _safe_text(row.get("county")),
                    _bool_flag(row.get("acs_data_available")),
                    _bool_flag(row.get("cbp_data_available")),
                    _bool_flag(row.get("fdic_data_available")),
                    _bool_flag(row.get("ffl_data_available")),
                    _bool_flag(row.get("fema_data_available")),
                    _bool_flag(row.get("disaster_disruption_data_available")),
                    _bool_flag(row.get("crime_data_available")),
                    _bool_flag(row.get("crime_rate_data_available")),
                    _bool_flag(row.get("political_violence_data_available")),
                    _bool_flag(row.get("gang_activity_data_available")),
                    _bool_flag(row.get("explosives_activity_data_available")),
                    _bool_flag(row.get("gang_explosives_activity_data_available")),
                    _bool_flag(row.get("hate_crime_offense_data_available")),
                    _bool_flag(row.get("law_enforcement_ambush_data_available")),
                    _bool_flag(row.get("institutional_data_available")),
                    _fmt(row.get("data_completeness_score")),
                    _safe_text(row.get("model_confidence")),
                ]
            )

        quality_table = _build_table(quality_table_data, font_size=4.8)
        story.append(quality_table)

        story.append(Spacer(1, 0.12 * inch))
        quality_note_text = """
        Data-quality notes are retained in outputs/tables/tn_county_data_quality_flags.csv.
        Lower completeness should be interpreted as lower confidence in the county's ranking,
        not as lower or higher risk by itself.
        """
        story.append(Paragraph(quality_note_text, small_style))
    else:
        story.append(
            Paragraph(
                "Data-quality fields were not found in the scored dataset. "
                "Run the updated risk_scoring.py with src/data_quality.py enabled.",
                body_style,
            )
        )

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Sensitivity Analysis
    # ------------------------------------------------------------------
    story.append(Paragraph("Model Sensitivity & Rank Stability", section_style))

    sensitivity_text = """
    The Phase 6 sensitivity-analysis layer tests whether county rankings remain stable when the
    final score weights are adjusted. Scenarios include finance-heavy, organized-violence-heavy,
    targeted-harm/public-safety-heavy, institutional/enforcement-heavy, gang/explosives-heavy,
    political-violence-heavy, disaster/disruption-heavy, socioeconomic-heavy, and tactical-access-heavy alternatives.
    """

    story.append(Paragraph(sensitivity_text, body_style))

    rank_stability_df = _load_rank_stability()

    if not rank_stability_df.empty:
        rank_display = rank_stability_df.sort_values(
            ["top_10_scenario_count", "average_rank"],
            ascending=[False, True],
        ).head(15)

        rank_table_data = [
            [
                "County",
                "Top-10 Scenario Count",
                "Best Rank",
                "Worst Rank",
                "Average Rank",
                "Rank Range",
                "Stability Signal",
            ]
        ]

        for _, row in rank_display.iterrows():
            rank_table_data.append(
                [
                    _safe_text(row.get("county")),
                    _fmt_int(row.get("top_10_scenario_count")),
                    _fmt_int(row.get("best_rank")),
                    _fmt_int(row.get("worst_rank")),
                    _fmt(row.get("average_rank")),
                    _fmt_int(row.get("rank_range")),
                    _safe_text(row.get("rank_stability_signal")),
                ]
            )

        rank_table = _build_table(rank_table_data, font_size=6.2)
        rank_table.setStyle(TableStyle([("ALIGN", (1, 1), (-2, -1), "RIGHT")]))
        story.append(rank_table)

        story.append(Spacer(1, 0.15 * inch))

        stability_chart = CHARTS_DIR / "rank_stability_top_counties.png"
        story.append(_safe_image(stability_chart))
        story.append(
            Paragraph(
                "Counties appearing in the top 10 across multiple alternative weighting scenarios.",
                small_style,
            )
        )
    else:
        story.append(
            Paragraph(
                "Sensitivity-analysis rank stability output was not found. "
                "Run python main.py after adding src/sensitivity_analysis.py.",
                body_style,
            )
        )

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Charts
    # ------------------------------------------------------------------
    story.append(Paragraph("Risk Visualizations", section_style))

    chart_files = [
        ("top_15_final_risk_counties.png", "Top 15 counties by final domestic security risk score."),
        ("top_15_operational_risk_counties.png", "Top 15 counties by final operational-risk / protective-planning score."),
        ("top_15_operational_exposure_counties.png", "Top 15 counties by operational exposure score."),
        ("top_15_resilience_gap_counties.png", "Top 15 counties by resilience gap score."),
        ("top_15_infrastructure_pressure_counties.png", "Top 15 counties by infrastructure pressure score."),
        ("top_15_law_enforcement_capacity_gap_counties.png", "Top 15 counties by law-enforcement capacity gap score."),
        ("operational_exposure_vs_resilience_gap_scatter.png", "Operational exposure vs. resilience gap."),
        ("top_15_finance_tactical_risk_counties.png", "Top 15 counties by finance and tactical vulnerability score."),
        ("top_15_organized_violence_pressure_counties.png", "Top 15 counties by organized violence / high-severity crime pressure score."),
        ("top_15_institutional_enforcement_pressure_counties.png", "Top 15 counties by institutional / enforcement pressure score."),
        ("top_15_disaster_disruption_vulnerability_counties.png", "Top 15 counties by disaster / disruption vulnerability score."),
        ("top_15_targeted_harm_public_safety_pressure_counties.png", "Top 15 counties by targeted harm / public-safety pressure score."),
        ("top_15_hate_crime_targeted_harm_pressure_counties.png", "Top 15 counties by hate-crime / targeted-harm pressure score."),
        ("top_15_law_enforcement_ambush_pressure_counties.png", "Top 15 counties by law-enforcement ambush pressure score."),
        ("top_15_overall_crime_rate_index_counties.png", "Top 15 counties by overall crime rate index score."),
        ("top_15_crime_weapons_pressure_counties.png", "Top 15 counties by TBI CrimeInsight crime/weapons pressure score."),
        ("top_15_gang_related_crime_pressure_counties.png", "Top 15 counties by gang-related criminal activity pressure score."),
        ("top_15_explosive_related_pressure_counties.png", "Top 15 counties by explosive-use criminal activity pressure score."),
        ("top_15_gang_explosive_pressure_counties.png", "Top 15 counties by gang + explosive intersection pressure score."),
        ("top_15_importer_ffl_counties.png", "Top 15 counties by importer FFL count."),
        ("top_15_destructive_device_ffl_counties.png", "Top 15 counties by destructive-device-related FFL count."),
        ("top_15_political_violence_exposure_counties.png", "Top 15 counties by ACLED political violence / civil unrest exposure score."),
        ("top_15_tactical_access_counties.png", "Top 15 counties by tactical-access exposure score."),
        ("top_15_banking_access_gap_counties.png", "Top 15 counties by banking access gap score."),
        ("finance_vs_final_risk_scatter.png", "Finance/tactical vulnerability vs. final domestic security risk."),
        ("institutional_enforcement_vs_final_risk_scatter.png", "Institutional / enforcement pressure vs. final domestic security risk."),
        ("disaster_disruption_vs_final_risk_scatter.png", "Disaster / disruption vulnerability vs. final domestic security risk."),
        ("targeted_harm_vs_institutional_enforcement_scatter.png", "Targeted harm / public-safety pressure vs. institutional / enforcement pressure."),
        ("organized_violence_vs_final_risk_scatter.png", "Organized violence / high-severity crime pressure vs. final domestic security risk."),
        ("organized_violence_vs_finance_tactical_scatter.png", "Organized violence / high-severity crime pressure vs. finance/tactical vulnerability."),
        ("overall_crime_rate_vs_organized_violence_scatter.png", "Overall crime rate index vs. organized violence pressure."),
        ("gang_pressure_vs_final_risk_scatter.png", "Gang-related criminal activity pressure vs. final domestic security risk."),
        ("explosive_pressure_vs_final_risk_scatter.png", "Explosive-use pressure vs. final domestic security risk."),
        ("gang_explosive_vs_final_risk_scatter.png", "Gang + explosive intersection pressure vs. final domestic security risk."),
        ("political_violence_vs_final_risk_scatter.png", "ACLED political violence / civil unrest exposure vs. final domestic security risk."),
        ("rank_stability_top_counties.png", "Top-10 rank stability across Phase 6 alternative weighting scenarios."),
        ("average_rank_top_counties.png", "Best average rank across Phase 6 alternative weighting scenarios."),
        ("top_15_crime_pressure_yoy_change.png", "Top counties by selected crime/weapons YoY increase."),
    ]

    for filename, caption in chart_files:
        chart_path = CHARTS_DIR / filename
        story.append(_safe_image(chart_path))
        story.append(Paragraph(caption, small_style))
        story.append(Spacer(1, 0.15 * inch))

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # County Deep Dive
    # ------------------------------------------------------------------
    story.append(Paragraph("Top County Deep Dive", section_style))

    deep_dive_df = scores_df.head(5).copy()

    for _, row in deep_dive_df.iterrows():
        county = _safe_text(row.get("county"))
        final_score = row.get("final_domestic_security_risk_score")
        signal = _safe_text(row.get("risk_signal"))

        story.append(Paragraph(county, sub_section_style))

        paragraph = f"""
        <b>{county}</b> has a final domestic security risk score of
        <b>{_fmt(final_score)}</b>, corresponding to a model signal of
        <b>{signal}</b>. The county's finance and tactical vulnerability score is
        <b>{_fmt(row.get('finance_tactical_vulnerability_score'))}</b>, organized violence /
        high-severity crime pressure score is <b>{_fmt(row.get('organized_violence_pressure_score'))}</b>,
        political violence / civil unrest exposure score is
        <b>{_fmt(row.get('political_violence_exposure_score'))}</b>, and model confidence is
        <b>{_safe_text(row.get('model_confidence'))}</b>. Interpreted operationally, this county is
        classified as: <b>{_risk_interpretation(final_score)}</b>.
        """

        story.append(Paragraph(paragraph, body_style))

        county_table = [
            ["Metric", "Value"],
            ["Population", _fmt_int(row.get("population"))],
            ["Poverty Rate", _fmt_pct(row.get("poverty_rate"))],
            ["Unemployment Rate", _fmt_pct(row.get("unemployment_rate"))],
            ["Rent Burden Rate", _fmt_pct(row.get("rent_burden_rate"))],
            ["Bank Branches", _fmt_int(row.get("bank_branch_count"))],
            ["Deposits Per Capita", _fmt_money(row.get("deposits_per_capita"))],
            ["Banking Access Gap Score", _fmt(row.get("banking_access_gap_score"))],
            ["Household Financial Stress Score", _fmt(row.get("household_financial_stress_score"))],
            ["Cash-Intensive Retail Score", _fmt(row.get("cash_intensive_retail_score"))],
            ["Tobacco / Vape Exposure Score", _fmt(row.get("poverty_adjusted_tobacco_vape_score"))],
            ["FFL Count", _fmt_int(row.get("ffl_count"))],
            ["Dealer FFL Count", _fmt_int(row.get("dealer_ffl_count"))],
            ["Manufacturer FFL Count", _fmt_int(row.get("manufacturer_ffl_count"))],
            ["Importer FFL Count", _fmt_int(row.get("importer_ffl_count"))],
            ["Destructive-Device-Related FFL Count", _fmt_int(row.get("destructive_device_ffl_count"))],
            ["Tactical Access Score", _fmt(row.get("tactical_access_score"))],
            ["Overall Crime Rate Index Score", _fmt(row.get("overall_crime_rate_index_score"))],
            ["Crime / Weapons Pressure Score", _fmt(row.get("violent_crime_weapons_pressure_score"))],
            ["Gang-Related Crime Pressure Score", _fmt(row.get("gang_related_crime_pressure_score"))],
            ["Explosive-Use Pressure Score", _fmt(row.get("explosive_related_pressure_score"))],
            ["Gang + Explosive Pressure Score", _fmt(row.get("gang_explosive_pressure_score"))],
            ["Organized Violence Pressure Score", _fmt(row.get("organized_violence_pressure_score"))],
            ["ACLED Political Violence / Civil Unrest Score", _fmt(row.get("political_violence_exposure_score"))],
            ["Infrastructure Disruption Score", _fmt(row.get("infrastructure_disruption_score"))],
            ["Disaster / Disruption Vulnerability Score", _fmt(row.get("disaster_disruption_vulnerability_score"))],
            ["Targeted Harm / Public-Safety Score", _fmt(row.get("targeted_harm_public_safety_pressure_score"))],
            ["Hate-Crime / Targeted-Harm Score", _fmt(row.get("hate_crime_targeted_harm_pressure_score"))],
            ["Law-Enforcement Ambush Pressure Score", _fmt(row.get("law_enforcement_ambush_pressure_score"))],
            ["Institutional / Enforcement Pressure Score", _fmt(row.get("institutional_enforcement_pressure_score"))],
            ["Data Completeness Score", _fmt(row.get("data_completeness_score"))],
            ["Model Confidence", _safe_text(row.get("model_confidence"))],
            ["Final Domestic Security Risk Score", _fmt(row.get("final_domestic_security_risk_score"))],
        ]

        story.append(_build_table(county_table, font_size=6.1))
        story.append(Spacer(1, 0.12 * inch))

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Methodology and Limitations
    # ------------------------------------------------------------------
    story.append(Paragraph("Methodology", section_style))

    methodology_text = """
    The model uses a weighted index approach. Each county-level indicator is normalized to a
    0-to-100 score using min-max scaling. Higher values indicate higher relative exposure or
    vulnerability. Component scores are then combined into broader indices, including household
    financial stress, banking access gap, cash-intensive retail exposure, tobacco/vape exposure,
    tactical-access exposure, organized violence / high-severity crime pressure, targeted harm /
    public-safety pressure, ACLED political violence / civil unrest exposure, disaster/disruption
    vulnerability, institutional/enforcement pressure, and the final domestic security risk score.
    """

    story.append(Paragraph(methodology_text, body_style))

    operational_methodology_text = """
    The operational-risk layer is intentionally calculated outside the main domestic-security risk
    score. It combines an existing threat-context score with operational exposure and resilience-gap
    indicators. This separation prevents response-capacity and protective-planning indicators from
    being misread as threat indicators.
    """

    story.append(Paragraph(operational_methodology_text, body_style))

    final_scoring_table = [
        ["Final Phase 6 Score Component", "Weight"],
        ["Finance & Tactical Vulnerability", "30%"],
        ["Organized Violence / High-Severity Crime Pressure", "20%"],
        ["Political Violence / Civil Unrest Exposure", "15%"],
        ["Household Financial Stress", "15%"],
        ["Disaster / Disruption Vulnerability", "10%"],
        ["Tactical Access Exposure", "5%"],
        ["Institutional / Enforcement Pressure", "5%"],
    ]

    story.append(_build_table(final_scoring_table, font_size=7.5))
    story.append(Spacer(1, 0.15 * inch))

    organized_scoring_table = [
        ["Organized Violence / High-Severity Crime Subcomponent", "Weight"],
        ["TBI Crime / Weapons Pressure", "30%"],
        ["Overall Crime Rate Index", "15%"],
        ["Gang-Related Criminal Activity Pressure", "18%"],
        ["Explosive-Use Criminal Activity Pressure", "13%"],
        ["Gang + Explosive Intersection Pressure", "13%"],
        ["Targeted Harm / Public-Safety Pressure", "11%"],
    ]

    story.append(_build_table(organized_scoring_table, font_size=7.0))
    story.append(Spacer(1, 0.15 * inch))

    limitations_text = """
    The model should be interpreted as a county-level relative exposure and monitoring-priority
    framework. It does not establish causation, predict incidents, identify threat actors, or
    determine whether criminal activity, extremist activity, or terrorism exists in a county.
    Gang-related crime, explosive-use activity, hate-crime offense counts, law-enforcement ambush
    counts, and the gang + explosive intersection layer are county-level indicators only. They are
    not labels for terrorism, motive, ideology, or actor identity.
    """

    story.append(Paragraph(limitations_text, body_style))

    interpretive_caution = """
    The tactical-access, regulated-retail, FFL, crime/weapons, gang, explosives, and political
    violence / civil unrest components are sensitive and should be interpreted carefully. Firearm
    retail, FFL licensing, tactical training, sporting goods, surplus retail, tobacco/vape retail,
    pawn/used merchandise, lending, convenience stores, and other business categories are lawful
    commercial activities. Their inclusion in this model is based only on aggregate exposure logic.
    """

    story.append(Paragraph(interpretive_caution, body_style))

    # ------------------------------------------------------------------
    # Appendix: Publicly Documented Group / Network Reference Register
    # ------------------------------------------------------------------
    public_reference_df = _load_public_group_reference()

    if not public_reference_df.empty:
        story.append(PageBreak())
        story.append(
            Paragraph(
                "Appendix: Publicly Documented Group / Network Reference Register",
                section_style,
            )
        )

        public_reference_text = """
        This appendix presents source-documented public group / network references from approved
        public sources. It is a reference-only layer and is <b>not included in the model score</b>.
        It should not be interpreted as a terrorism, extremism, criminality, operational-presence,
        or county-risk label. The table intentionally excludes addresses, coordinates, individual
        names, social handles, meeting locations, recruitment channels, case narratives, and
        operational details.
        """

        story.append(Paragraph(public_reference_text, body_style))

        valid_reference_df = public_reference_df.copy()

        if "is_valid_reference" in valid_reference_df.columns:
            valid_reference_df = valid_reference_df[
                valid_reference_df["is_valid_reference"].astype(str).str.lower().isin(
                    ["true", "1", "yes"]
                )
            ]

        if "include_in_report" in valid_reference_df.columns:
            valid_reference_df = valid_reference_df[
                valid_reference_df["include_in_report"].astype(str).str.lower().isin(
                    ["true", "1", "yes"]
                )
            ]

        valid_reference_df = valid_reference_df.head(25)

        if not valid_reference_df.empty:
            reference_table_data = [
                [
                    "Reference",
                    "Category",
                    "Source",
                    "Geographic Ref.",
                    "Confidence",
                    "Use Note",
                ]
            ]

            for _, row in valid_reference_df.iterrows():
                reference_table_data.append(
                    [
                        Paragraph(_safe_text(row.get("group_or_network_name")), small_style),
                        Paragraph(_safe_text(row.get("category")), small_style),
                        Paragraph(_safe_text(row.get("source_name")), small_style),
                        Paragraph(_safe_text(row.get("geographic_reference")), small_style),
                        Paragraph(_safe_text(row.get("confidence_level")), small_style),
                        Paragraph(_safe_text(row.get("responsible_use_flag")), small_style),
                    ]
                )

            reference_table = _build_table(reference_table_data, font_size=5.4)
            story.append(reference_table)

            story.append(Spacer(1, 0.12 * inch))
            story.append(
                Paragraph(
                    "Note: Only the first 25 report-ready references are displayed in the PDF. "
                    "The full validated reference table is saved in outputs/tables.",
                    small_style,
                )
            )
        else:
            story.append(
                Paragraph(
                    "No valid report-ready public group / network reference rows were found. "
                    "Run python -m src.public_group_reference after reviewing the input CSV.",
                    body_style,
                )
            )


    # ------------------------------------------------------------------
    # Appendix: TDOC STG Correctional-System Context
    # ------------------------------------------------------------------
    tdoc_stg_df = _load_tdoc_stg_reference_context()
    tdoc_stg_validation_df = _load_tdoc_stg_reference_validation()

    if not tdoc_stg_df.empty:
        story.append(PageBreak())
        story.append(
            Paragraph(
                "Appendix: TDOC STG Correctional-System Context",
                section_style,
            )
        )

        tdoc_context_text = """
        This appendix presents sanitized Tennessee Department of Correction Security Threat Group
        (STG) correctional-system context. It is a <b>non-scoring</b> reference layer and is not
        included in the county risk score, organized-violence score, public group reference score,
        operational-risk score, scenario analysis, or county ranking. FY2025 rows summarize
        facility-level confirmed and suspected TDOC correctional classifications. Historical 2010
        rows provide broad institutional context only. These rows should not be interpreted as
        current community presence, county-level activity, terrorism, ideology, or suspicious conduct
        by any person, group, business, facility, or place.
        """

        story.append(Paragraph(tdoc_context_text, body_style))

        if not tdoc_stg_validation_df.empty:
            clean_validation = tdoc_stg_validation_df.copy()
            validation_table_data = [["Validation Item", "Status", "Detail"]]

            for _, row in clean_validation.iterrows():
                validation_table_data.append(
                    [
                        Paragraph(_safe_text(row.get("validation_item")), small_style),
                        Paragraph(_safe_text(row.get("status")), small_style),
                        Paragraph(_safe_text(row.get("detail")), small_style),
                    ]
                )

            validation_table = Table(
                validation_table_data,
                colWidths=[1.75 * inch, 0.75 * inch, 4.0 * inch],
                repeatRows=1,
            )
            validation_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 6.0),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f3f4f6")],
                        ),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            story.append(Paragraph("Validation Summary", sub_section_style))
            story.append(validation_table)
            story.append(Spacer(1, 0.12 * inch))

        facility_df = tdoc_stg_df.copy()

        if "record_type" in facility_df.columns:
            facility_df = facility_df[
                facility_df["record_type"].astype(str).eq("facility_total")
            ].copy()

        if "source_year" in facility_df.columns:
            facility_df = facility_df[
                facility_df["source_year"].astype(str).eq("2025")
            ].copy()

        if not facility_df.empty:
            facility_df = facility_df.sort_values("facility_context")

            facility_table_data = [
                [
                    "Facility Context",
                    "Confirmed",
                    "Suspected",
                    "Total",
                    "Source Page",
                ]
            ]

            for _, row in facility_df.iterrows():
                facility_table_data.append(
                    [
                        Paragraph(_safe_text(row.get("facility_context")), small_style),
                        _fmt_int(row.get("confirmed_member_count")),
                        _fmt_int(row.get("suspected_member_count")),
                        _fmt_int(row.get("total_member_count")),
                        _fmt_int(row.get("source_page")),
                    ]
                )

            facility_table = Table(
                facility_table_data,
                colWidths=[3.15 * inch, 0.85 * inch, 0.85 * inch, 0.75 * inch, 0.75 * inch],
                repeatRows=1,
            )
            facility_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 6.2),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f3f4f6")],
                        ),
                        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )

            story.append(Paragraph("FY2025 Facility-Level Aggregate Context", sub_section_style))
            story.append(facility_table)
            story.append(Spacer(1, 0.12 * inch))
            story.append(
                Paragraph(
                    "Note: Confirmed, suspected, and total values reflect TDOC correctional "
                    "classification context in the FY2025 Statistical Abstract. They are not "
                    "county-level activity measures and are not scoring inputs.",
                    small_style,
                )
            )

        historical_df = tdoc_stg_df.copy()

        if "record_type" in historical_df.columns:
            historical_df = historical_df[
                historical_df["record_type"].astype(str).eq("historical_major_group_reference")
            ].copy()

        if not historical_df.empty:
            historical_df = historical_df.sort_values("group_or_network_name")

            historical_table_data = [["Historical Reference", "Source Year", "Use Note"]]

            for _, row in historical_df.iterrows():
                historical_table_data.append(
                    [
                        Paragraph(_safe_text(row.get("group_or_network_name")), small_style),
                        _safe_text(row.get("source_year")),
                        Paragraph(
                            "Historical TDOC institutional context only; broad reference retained without recognition details.",
                            small_style,
                        ),
                    ]
                )

            historical_table = Table(
                historical_table_data,
                colWidths=[2.25 * inch, 0.85 * inch, 3.4 * inch],
                repeatRows=1,
            )
            historical_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 6.2),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f3f4f6")],
                        ),
                        ("ALIGN", (1, 1), (1, -1), "CENTER"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )

            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph("Historical 2010 TDOC Institutional Context", sub_section_style))
            story.append(historical_table)


    # ------------------------------------------------------------------
    # Appendix: TBI 2024 Hate Crime Context
    # ------------------------------------------------------------------
    tbi_summary_df = _load_tbi_hate_crime_context_summary()
    tbi_bias_df = _load_tbi_hate_crime_bias_context()
    tbi_offense_df = _load_tbi_hate_crime_offense_context()
    tbi_clearance_df = _load_tbi_hate_crime_clearance_context()
    tbi_location_df = _load_tbi_hate_crime_location_context()

    if (
        not tbi_summary_df.empty
        or not tbi_bias_df.empty
        or not tbi_offense_df.empty
        or not tbi_clearance_df.empty
        or not tbi_location_df.empty
    ):
        story.append(PageBreak())
        story.append(Paragraph("Appendix: TBI 2024 Hate Crime Context", section_style))

        tbi_context_text = """
        This appendix summarizes statewide context from the Tennessee Bureau of Investigation
        2024 Hate Crime Report. It is a context-only layer and is <b>not included in model
        scoring</b>. It does not replace the county-level TBI hate-crime offense input used in the
        targeted-harm layer. The context tables do not retain agency-level, incident-level,
        victim-level, suspect-level, address, coordinate, narrative, or case-level records.
        """

        story.append(Paragraph(tbi_context_text, body_style))

        if not tbi_summary_df.empty:
            story.append(Paragraph("Statewide Context Summary", sub_section_style))

            summary_table_data = [["Context Item", "Value", "Note"]]

            for _, row in tbi_summary_df.iterrows():
                summary_table_data.append(
                    [
                        Paragraph(_safe_text(row.get("context_item")), small_style),
                        _fmt_int(row.get("value")),
                        Paragraph(_safe_text(row.get("note")), small_style),
                    ]
                )

            summary_table = _build_table(summary_table_data, font_size=5.8)
            summary_table.setStyle(TableStyle([("ALIGN", (1, 1), (1, -1), "RIGHT")]))
            story.append(summary_table)
            story.append(Spacer(1, 0.12 * inch))

        if not tbi_bias_df.empty:
            story.append(Paragraph("Bias Motivation Context", sub_section_style))

            bias_table_data = [
                [
                    "Bias Category",
                    "2022",
                    "2023",
                    "2024",
                    "% Known Bias 2024",
                ]
            ]

            for _, row in tbi_bias_df.iterrows():
                percent_value = row.get("percent_of_known_bias_2024")
                percent_display = (
                    ""
                    if pd.isna(percent_value)
                    else f"{float(percent_value):.2f}%"
                )

                bias_table_data.append(
                    [
                        Paragraph(_safe_text(row.get("bias_category")), small_style),
                        _fmt_int(row.get("known_bias_2022")),
                        _fmt_int(row.get("known_bias_2023")),
                        _fmt_int(row.get("known_bias_2024")),
                        percent_display,
                    ]
                )

            bias_table = _build_table(bias_table_data, font_size=6.0)
            bias_table.setStyle(TableStyle([("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
            story.append(bias_table)
            story.append(Spacer(1, 0.12 * inch))

        if not tbi_offense_df.empty:
            story.append(Paragraph("Offense Type Context", sub_section_style))

            offense_table_data = [["Crime Category", "Offense Type", "2024 Total"]]

            for _, row in tbi_offense_df.iterrows():
                offense_table_data.append(
                    [
                        Paragraph(_safe_text(row.get("crime_category")), small_style),
                        Paragraph(_safe_text(row.get("offense_type")), small_style),
                        _fmt_int(row.get("reported_total_2024")),
                    ]
                )

            offense_table = _build_table(offense_table_data, font_size=6.0)
            offense_table.setStyle(TableStyle([("ALIGN", (-1, 1), (-1, -1), "RIGHT")]))
            story.append(offense_table)
            story.append(Spacer(1, 0.12 * inch))

        if not tbi_clearance_df.empty or not tbi_location_df.empty:
            story.append(Paragraph("Clearance and Location Context", sub_section_style))

            if not tbi_clearance_df.empty:
                clearance_table_data = [["Clearance Type", "2024 Total"]]

                for _, row in tbi_clearance_df.iterrows():
                    clearance_table_data.append(
                        [
                            Paragraph(_safe_text(row.get("clearance_type")), small_style),
                            _fmt_int(row.get("reported_total_2024")),
                        ]
                    )

                clearance_table = _build_table(clearance_table_data, font_size=6.2)
                clearance_table.setStyle(
                    TableStyle([("ALIGN", (-1, 1), (-1, -1), "RIGHT")])
                )
                story.append(clearance_table)
                story.append(Spacer(1, 0.12 * inch))

            if not tbi_location_df.empty:
                location_table_data = [["Location Type", "2024 Total"]]

                for _, row in tbi_location_df.iterrows():
                    location_table_data.append(
                        [
                            Paragraph(_safe_text(row.get("location_type")), small_style),
                            _fmt_int(row.get("reported_total_2024")),
                        ]
                    )

                location_table = _build_table(location_table_data, font_size=6.2)
                location_table.setStyle(
                    TableStyle([("ALIGN", (-1, 1), (-1, -1), "RIGHT")])
                )
                story.append(location_table)

        story.append(Spacer(1, 0.12 * inch))
        story.append(
            Paragraph(
                "Interpretation note: TBI hate-crime context strengthens the targeted-harm discussion, "
                "but it is not a terrorism indicator and is not included in the model score.",
                small_style,
            )
        )

    # ------------------------------------------------------------------
    # Source Register
    # ------------------------------------------------------------------
    source_df = _load_source_register()

    if not source_df.empty:
        story.append(PageBreak())
        story.append(Paragraph("Source Register", section_style))

        source_table_data = [["Source", "Use", "Notes"]]

        for _, row in source_df.iterrows():
            source_table_data.append(
                [
                    Paragraph(_safe_text(row.get("source")), small_style),
                    Paragraph(_safe_text(row.get("use")), small_style),
                    Paragraph(_safe_text(row.get("notes")), small_style),
                ]
            )

        source_table = _build_table(source_table_data, font_size=6.5)
        story.append(source_table)

    doc.build(
        story,
        onFirstPage=_page_footer,
        onLaterPages=_page_footer,
    )

    return report_path


if __name__ == "__main__":
    scored_path = TABLES_DIR / "tn_county_domestic_security_scores.csv"

    if not scored_path.exists():
        raise FileNotFoundError(
            "Scored county output not found. Run python main.py first or call "
            "generate_report(scores_df) from the main pipeline."
        )

    scored_df = pd.read_csv(scored_path)
    output_path = generate_report(scored_df)
    print(f"PDF report created: {output_path}")
