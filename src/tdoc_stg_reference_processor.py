"""
Build a non-scoring TDOC Security Threat Group (STG) reference context table.

Purpose
-------
This processor adds a correctional-system STG context appendix to the
Tennessee Domestic Security & Illicit Finance Risk Intelligence Model.

It is intentionally NON-SCORING. It does not modify county risk scores,
gang-related crime pressure scores, operational-risk scores, or county ranks.

Safe-use boundaries
-------------------
The output is intentionally broad and aggregate. It must not include:
- individual names
- person identifiers
- staff contact details
- visual identifiers, coded identifiers, or recognition details
- addresses, coordinates, maps, routes, facility security details, or operational notes
- incident narratives or intelligence-priority details

Outputs
-------
outputs/tables/tn_tdoc_stg_reference_context.csv
outputs/tables/tn_tdoc_stg_reference_validation.csv

Expected raw source file names
------------------------------
data/raw/stg_threat_assessment__tn_major_groups__apr_2010__les_.pdf
data/raw/2025 Statistical Abstract.pdf

Notes
-----
The 2010 TDOC file is treated as historical correctional-system context only.
The FY2025 Statistical Abstract is treated as public aggregate facility-level
context only. Neither should be interpreted as current community presence,
county-level activity, terrorism, ideology, or suspicious activity.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"

TDOC_2010_PDF = RAW_DIR / "stg_threat_assessment__tn_major_groups__apr_2010__les_.pdf"
TDOC_2025_PDF = RAW_DIR / "2025 Statistical Abstract.pdf"

CONTEXT_OUTPUT = TABLES_DIR / "tn_tdoc_stg_reference_context.csv"
VALIDATION_OUTPUT = TABLES_DIR / "tn_tdoc_stg_reference_validation.csv"

# Keep this false by default. Facility-level totals are cleaner and less likely
# to misread chart extraction. Top-five group chart extraction can be enabled
# later after manual QA if needed.
INCLUDE_FY2025_TOP_GROUP_ROWS = False

RESPONSIBLE_USE_NOTE = (
    "TDOC correctional-system Security Threat Group context only. "
    "This row is non-scoring and should not be interpreted as current community presence, "
    "county-level activity, terrorism, ideology, suspicious conduct, or criminal conduct by any "
    "specific person, group, business, facility, or place."
)

HISTORICAL_USE_NOTE = (
    "Historical TDOC institutional context only. Do not publish visual identifiers, coded identifiers, "
    "staff contact details, incident narratives, or operational notes."
)

FY2025_USE_NOTE = (
    "Public FY2025 TDOC facility-level aggregate context. Counts refer to TDOC correctional classification "
    "within the correctional-system context and should not be inferred as county-level or street-level activity."
)

# Historical major groups listed in the 2010 TDOC threat assessment table of contents.
# We retain only broad names, not identifiers, imagery, structures, or recognition details.
HISTORICAL_2010_MAJOR_GROUPS = [
    "Gangster Disciples",
    "Crips",
    "Aryan Nation",
    "Vice Lords",
    "Aryan Brotherhood / Brotherhood Forever",
    "Bloods",
]

FACILITY_CODE_TO_NAME = {
    "BCCX": "Bledsoe County Correctional Complex",
    "DJRC": "Debra K. Johnson Rehabilitation Center",
    "DSNF": "Lois M. DeBerry Special Needs Facility",
    "HCCF": "Hardeman County Correctional Facility",
    "MCCX": "Morgan County Correctional Complex",
    "MLTC": "Mark Luttrell Transition Center",
    "NECX": "Northeast Correctional Complex",
    "NWCX": "Northwest Correctional Complex",
    "RMSI": "Riverbend Maximum Security Institution",
    "SCCF": "South Central Correctional Facility",
    "TCIX": "Turney Center Industrial Complex",
    "TTCC": "Trousdale Turner Correctional Center",
    "WCFA": "Whiteville Correctional Facility",
    "WTSP": "West Tennessee State Penitentiary",
}

FACILITY_NAME_PATTERNS = list(FACILITY_CODE_TO_NAME.values())

COMMON_STG_NAMES = [
    "Gangster Disciples",
    "Vice Lords",
    "Crips",
    "Bloods",
    "Aryan Nation",
    "Aryan Brotherhood",
    "Aryan Brotherhood / Brotherhood Forever",
    "Brotherhood Forever",
    "White Aryan Resistance",
]


@dataclass
class ReferenceRow:
    reference_id: str
    group_or_network_name: str
    record_type: str
    category: str
    source_type: str
    source_name: str
    source_year: int | str
    source_file: str
    source_page: int | None
    geographic_reference: str
    geo_level: str
    correctional_context_flag: bool
    historical_context_flag: bool
    facility_context: str
    confirmed_member_count: int | None
    suspected_member_count: int | None
    total_member_count: int | None
    source_status_note: str
    responsible_use_flag: str
    include_in_report: bool
    include_in_score: bool


def _require_pdf_text_dependency():
    try:
        import pdfplumber  # noqa: F401
    except Exception as exc:
        raise ImportError(
            "Missing dependency: pdfplumber. Install it with `pip install pdfplumber` "
            "or add `pdfplumber>=0.11.0` to requirements.txt."
        ) from exc


def _clean_space(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalize_group_name(value: str) -> str:
    value = _clean_space(value)

    replacements = {
        "Gangster Disciple": "Gangster Disciples",
        "Vice Lord": "Vice Lords",
        "Aryan Brotherhood/Brotherhood Forever": "Aryan Brotherhood / Brotherhood Forever",
        "Aryan Brotherhood Brotherhood Forever": "Aryan Brotherhood / Brotherhood Forever",
    }

    return replacements.get(value, value)


def _sanitize_output_text(value: str) -> str:
    """Remove sensitive-detail terms from public-facing output text."""
    if not isinstance(value, str):
        return value

    replacements = {
        "tattoos": "visual identifiers",
        "tattoo": "visual identifier",
        "symbols": "coded identifiers",
        "symbol": "coded identifier",
        "signs": "recognition details",
        "phrases": "coded language",
        "phrase": "coded language",
        "rank structures": "internal structures",
        "rank structure": "internal structure",
        "inmate classification": "TDOC correctional classification",
        "inmate": "TDOC population member",
        "inmates": "TDOC population members",
    }

    out = value
    for old, new in replacements.items():
        out = re.sub(re.escape(old), new, out, flags=re.IGNORECASE)

    return out


def build_historical_2010_rows() -> list[ReferenceRow]:
    rows: list[ReferenceRow] = []

    if not TDOC_2010_PDF.exists():
        print(f"Historical TDOC STG file not found: {TDOC_2010_PDF}")
        return rows

    for idx, group_name in enumerate(HISTORICAL_2010_MAJOR_GROUPS, start=1):
        rows.append(
            ReferenceRow(
                reference_id=f"TDOC-STG-HIST-2010-{idx:03d}",
                group_or_network_name=group_name,
                record_type="historical_major_group_reference",
                category="correctional_security_threat_group_context",
                source_type="state_corrections_historical_assessment",
                source_name="Tennessee Department of Correction Security Threat Assessment: TN Major Groups",
                source_year=2010,
                source_file=TDOC_2010_PDF.name,
                source_page=None,
                geographic_reference="TDOC correctional system",
                geo_level="state_correctional_system",
                correctional_context_flag=True,
                historical_context_flag=True,
                facility_context="Statewide TDOC institutional context",
                confirmed_member_count=None,
                suspected_member_count=None,
                total_member_count=None,
                source_status_note=(
                    "Historical TDOC document describing major groups recognized in the correctional-system "
                    "context. Counts and operational identifiers are not retained in this output."
                ),
                responsible_use_flag=f"{RESPONSIBLE_USE_NOTE} {HISTORICAL_USE_NOTE}",
                include_in_report=True,
                include_in_score=False,
            )
        )

    return rows


def _find_facility_for_page_text(text: str) -> str:
    # The FY2025 abstract pages normally include a short marker such as
    # "Facility Profiles: BCCX" on the same page as the STG aggregate chart.
    marker = re.search(r"Facility Profiles:\s*([A-Z]{3,5})", text)
    if marker:
        code = marker.group(1).strip().upper()
        if code in FACILITY_CODE_TO_NAME:
            return FACILITY_CODE_TO_NAME[code]

    for facility in FACILITY_NAME_PATTERNS:
        if facility in text:
            return facility

    return "TDOC facility profile"


def _extract_total_counts_from_page_text(text: str) -> tuple[int | None, int | None, int | None]:
    """
    Extract facility-level confirmed/suspected/total counts.

    The PDF text extraction sometimes inserts unrelated chart numbers between
    the section title and the Confirmed/Suspected line, so this regex allows a
    short noisy gap before the count line.
    """
    match = re.search(
        r"All Security Threat Group\s*\(STG/Gang\)\s*Members[\s\S]{0,180}?"
        r"Confirmed:\s*([0-9,]+)\s+Suspected:\s*([0-9,]+)\s+Total:\s*([0-9,]+)",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None, None, None

    return tuple(int(x.replace(",", "")) for x in match.groups())  # type: ignore[return-value]


def _extract_group_counts_from_page_text(text: str) -> list[tuple[str, int | None, int | None]]:
    """
    Optional best-effort parser for top-five group chart text.

    Disabled by default through INCLUDE_FY2025_TOP_GROUP_ROWS because chart OCR/text
    order is inconsistent. The safe facility-total rows are the primary output.
    """
    if "Top 5 STGs by Confirmed Members" not in text:
        return []

    # Use only the segment between the chart title and the next page footer when possible.
    segment = text.split("Top 5 STGs by Confirmed Members", 1)[1]
    segment = segment.split("TDOC Statistical Abstract", 1)[0]

    names = [name for name in COMMON_STG_NAMES if name in segment]
    names = sorted(set(names), key=lambda n: segment.find(n))

    if "Aryan Brotherhood / Brotherhood Forever" in names and "Aryan Brotherhood" in names:
        names.remove("Aryan Brotherhood")

    if not names:
        return []

    numbers = [int(x.replace(",", "")) for x in re.findall(r"\b\d{1,4}\b", segment)]
    needed = len(names) * 2

    if len(numbers) >= needed:
        chart_numbers = numbers[:needed]
        confirmed = chart_numbers[: len(names)]
        suspected = chart_numbers[len(names) :]
        return [(_normalize_group_name(name), confirmed[i], suspected[i]) for i, name in enumerate(names)]

    return [(_normalize_group_name(name), None, None) for name in names]


def build_fy2025_rows() -> list[ReferenceRow]:
    rows: list[ReferenceRow] = []

    if not TDOC_2025_PDF.exists():
        print(f"FY2025 TDOC Statistical Abstract file not found: {TDOC_2025_PDF}")
        return rows

    _require_pdf_text_dependency()
    import pdfplumber

    with pdfplumber.open(TDOC_2025_PDF) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            if "All Security Threat Group" not in text:
                continue

            facility = _find_facility_for_page_text(text)
            total_confirmed, total_suspected, total_members = _extract_total_counts_from_page_text(text)

            # PDF text extraction can occasionally misread one component count while
            # preserving the printed total. When confirmed + suspected does not equal
            # total, preserve confirmed and total, then reconcile suspected to the
            # arithmetic difference. This keeps the public aggregate internally
            # consistent without adding any sensitive detail.
            count_reconciled_flag = False
            original_suspected_count = total_suspected

            if (
                total_confirmed is not None
                and total_suspected is not None
                and total_members is not None
                and total_confirmed + total_suspected != total_members
            ):
                corrected_suspected = total_members - total_confirmed
                if corrected_suspected >= 0:
                    total_suspected = corrected_suspected
                    count_reconciled_flag = True

            ref_base = f"TDOC-STG-FY2025-P{page_index:03d}"

            rows.append(
                ReferenceRow(
                    reference_id=f"{ref_base}-TOTAL",
                    group_or_network_name="All Security Threat Groups / Gangs",
                    record_type="facility_total",
                    category="correctional_security_threat_group_context",
                    source_type="state_corrections_statistical_abstract",
                    source_name="Tennessee Department of Correction Statistical Abstract FY2025",
                    source_year=2025,
                    source_file=TDOC_2025_PDF.name,
                    source_page=page_index,
                    geographic_reference="TDOC facility profile",
                    geo_level="state_correctional_facility",
                    correctional_context_flag=True,
                    historical_context_flag=False,
                    facility_context=facility,
                    confirmed_member_count=total_confirmed,
                    suspected_member_count=total_suspected,
                    total_member_count=total_members,
                    source_status_note=(
                        "FY2025 TDOC facility-level aggregate count of confirmed and suspected "
                        "Security Threat Group / gang classifications."
                        + (
                            f" Suspected count reconciled from extracted value {original_suspected_count} "
                            f"because confirmed plus suspected did not equal the printed total."
                            if count_reconciled_flag
                            else ""
                        )
                    ),
                    responsible_use_flag=f"{RESPONSIBLE_USE_NOTE} {FY2025_USE_NOTE}",
                    include_in_report=True,
                    include_in_score=False,
                )
            )

            if INCLUDE_FY2025_TOP_GROUP_ROWS:
                group_rows = _extract_group_counts_from_page_text(text)

                for group_idx, (group_name, confirmed, suspected) in enumerate(group_rows, start=1):
                    total = None
                    if confirmed is not None or suspected is not None:
                        total = int(confirmed or 0) + int(suspected or 0)

                    rows.append(
                        ReferenceRow(
                            reference_id=f"{ref_base}-GROUP-{group_idx:02d}",
                            group_or_network_name=group_name,
                            record_type="facility_top_group_chart",
                            category="correctional_security_threat_group_context",
                            source_type="state_corrections_statistical_abstract",
                            source_name="Tennessee Department of Correction Statistical Abstract FY2025",
                            source_year=2025,
                            source_file=TDOC_2025_PDF.name,
                            source_page=page_index,
                            geographic_reference="TDOC facility profile",
                            geo_level="state_correctional_facility",
                            correctional_context_flag=True,
                            historical_context_flag=False,
                            facility_context=facility,
                            confirmed_member_count=confirmed,
                            suspected_member_count=suspected,
                            total_member_count=total,
                            source_status_note=(
                                "FY2025 TDOC top-five STG chart by confirmed members for the facility profile. "
                                "Chart extraction is treated as appendix context only."
                            ),
                            responsible_use_flag=f"{RESPONSIBLE_USE_NOTE} {FY2025_USE_NOTE}",
                            include_in_report=True,
                            include_in_score=False,
                        )
                    )

    return rows


def rows_to_dataframe(rows: Iterable[ReferenceRow]) -> pd.DataFrame:
    df = pd.DataFrame([row.__dict__ for row in rows])

    if df.empty:
        return df

    df["group_or_network_name"] = df["group_or_network_name"].fillna("").map(_clean_space)
    df = df[df["group_or_network_name"].ne("")].copy()

    # Force non-scoring and sanitize public-facing text fields.
    df["include_in_score"] = False

    text_cols = [
        "group_or_network_name",
        "source_name",
        "geographic_reference",
        "geo_level",
        "facility_context",
        "source_status_note",
        "responsible_use_flag",
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].map(_sanitize_output_text)

    dedupe_cols = [
        "group_or_network_name",
        "record_type",
        "source_year",
        "facility_context",
        "confirmed_member_count",
        "suspected_member_count",
        "total_member_count",
    ]
    df = df.drop_duplicates(subset=[c for c in dedupe_cols if c in df.columns]).copy()

    sort_cols = ["source_year", "record_type", "facility_context", "group_or_network_name"]
    df = df.sort_values([c for c in sort_cols if c in df.columns]).reset_index(drop=True)

    df["reference_id"] = [f"TDOC-STG-REF-{i:04d}" for i in range(1, len(df) + 1)]

    preferred_cols = [
        "reference_id",
        "group_or_network_name",
        "record_type",
        "category",
        "source_type",
        "source_name",
        "source_year",
        "source_file",
        "source_page",
        "geographic_reference",
        "geo_level",
        "correctional_context_flag",
        "historical_context_flag",
        "facility_context",
        "confirmed_member_count",
        "suspected_member_count",
        "total_member_count",
        "source_status_note",
        "responsible_use_flag",
        "include_in_report",
        "include_in_score",
    ]

    return df[[c for c in preferred_cols if c in df.columns]]


def validate_reference_context(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            [
                {
                    "validation_item": "row_count",
                    "status": "WARN",
                    "detail": "No TDOC STG reference rows were created.",
                }
            ]
        )

    validation_rows = []

    validation_rows.append(
        {
            "validation_item": "row_count",
            "status": "OK" if len(df) > 0 else "WARN",
            "detail": f"{len(df)} TDOC STG reference rows created.",
        }
    )

    validation_rows.append(
        {
            "validation_item": "non_scoring",
            "status": "OK" if df["include_in_score"].eq(False).all() else "FAIL",
            "detail": "All rows must have include_in_score=False.",
        }
    )

    if "record_type" in df.columns and "source_year" in df.columns:
        fy2025_total = df[
            (df["source_year"].astype(str).eq("2025"))
            & (df["record_type"].astype(str).eq("facility_total"))
        ].copy()

        expected_facilities = 14
        count_rows_ok = len(fy2025_total) == expected_facilities
        counts_populated_ok = False

        if not fy2025_total.empty:
            counts_populated_ok = fy2025_total[
                ["confirmed_member_count", "suspected_member_count", "total_member_count"]
            ].notna().all().all()

        validation_rows.append(
            {
                "validation_item": "fy2025_facility_total_rows",
                "status": "OK" if count_rows_ok else "REVIEW",
                "detail": f"Found {len(fy2025_total)} FY2025 facility-total rows; expected {expected_facilities}.",
            }
        )

        validation_rows.append(
            {
                "validation_item": "fy2025_facility_counts_populated",
                "status": "OK" if counts_populated_ok else "REVIEW",
                "detail": (
                    "All FY2025 facility-total rows have confirmed/suspected/total counts."
                    if counts_populated_ok
                    else "Some FY2025 facility-total rows are missing confirmed/suspected/total counts."
                ),
            }
        )

        count_consistency_ok = False
        inconsistent_rows = pd.DataFrame()

        if counts_populated_ok:
            numeric_counts = fy2025_total[
                [
                    "facility_context",
                    "confirmed_member_count",
                    "suspected_member_count",
                    "total_member_count",
                ]
            ].copy()

            for col in ["confirmed_member_count", "suspected_member_count", "total_member_count"]:
                numeric_counts[col] = pd.to_numeric(numeric_counts[col], errors="coerce")

            inconsistent_rows = numeric_counts[
                (numeric_counts["confirmed_member_count"] + numeric_counts["suspected_member_count"])
                != numeric_counts["total_member_count"]
            ].copy()

            count_consistency_ok = inconsistent_rows.empty

        validation_rows.append(
            {
                "validation_item": "fy2025_facility_count_consistency",
                "status": "OK" if count_consistency_ok else "REVIEW",
                "detail": (
                    "All FY2025 facility-total rows satisfy confirmed + suspected = total."
                    if count_consistency_ok
                    else "Some FY2025 facility-total rows do not satisfy confirmed + suspected = total."
                ),
            }
        )

    prohibited_terms = [
        "tattoo",
        "symbol",
        "phrase",
        "rank structure",
        "address",
        "coordinate",
        "phone",
        "email",
        "#",
    ]

    text_cols = [
        "group_or_network_name",
        "source_status_note",
        "responsible_use_flag",
        "facility_context",
    ]

    combined_text = (
        df[[c for c in text_cols if c in df.columns]]
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
    )

    hits = {
        term: int(combined_text.str.contains(re.escape(term.lower()), regex=True).sum())
        for term in prohibited_terms
    }

    risky_hits = {k: v for k, v in hits.items() if v > 0}

    validation_rows.append(
        {
            "validation_item": "prohibited_detail_screen",
            "status": "REVIEW" if risky_hits else "OK",
            "detail": f"Potential sensitive terms found: {risky_hits}" if risky_hits else "No prohibited detail terms found.",
        }
    )

    validation_rows.append(
        {
            "validation_item": "correctional_context_flag",
            "status": "OK" if df["correctional_context_flag"].eq(True).all() else "WARN",
            "detail": "All rows should be clearly marked as correctional-system context.",
        }
    )

    return pd.DataFrame(validation_rows)


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    rows.extend(build_historical_2010_rows())
    rows.extend(build_fy2025_rows())

    df = rows_to_dataframe(rows)
    validation_df = validate_reference_context(df)

    df.to_csv(CONTEXT_OUTPUT, index=False)
    validation_df.to_csv(VALIDATION_OUTPUT, index=False)

    print("=" * 80)
    print("TDOC STG Reference Context Processor")
    print("=" * 80)
    print(f"Rows created: {len(df)}")
    print(f"Saved: {CONTEXT_OUTPUT}")
    print(f"Saved: {VALIDATION_OUTPUT}")

    if not validation_df.empty:
        print("\nValidation summary:")
        print(validation_df.to_string(index=False))

    if not df.empty and {"record_type", "source_year"}.issubset(df.columns):
        fy2025_total = df[
            (df["source_year"].astype(str).eq("2025"))
            & (df["record_type"].astype(str).eq("facility_total"))
        ]
        if not fy2025_total.empty:
            print("\nFY2025 facility totals preview:")
            preview_cols = [
                "facility_context",
                "confirmed_member_count",
                "suspected_member_count",
                "total_member_count",
            ]
            print(fy2025_total[preview_cols].to_string(index=False))


if __name__ == "__main__":
    main()
