import re

import pandas as pd

from src.config import (
    PUBLIC_GROUP_REFERENCE_INPUT,
    PUBLIC_GROUP_REFERENCE_OUTPUT,
    PUBLIC_GROUP_REFERENCE_VALIDATION_OUTPUT,
)


ALLOWED_CATEGORIES = {
    "criminal_gang_or_organized_crime",
    "extremist_or_hate_group",
    "antigovernment_or_militia",
    "terrorism_linked_case",
    "violent_extremism_case",
    "public_safety_reference",
    "other_public_reference",
}

ALLOWED_SOURCE_TYPES = {
    "official_government",
    "court_document",
    "law_enforcement_report",
    "civil_society_tracker",
    "academic_report",
    "credible_news",
    "other_public_source",
}

ALLOWED_GEO_LEVELS = {
    "statewide",
    "county",
    "multi_county",
    "city_or_region",
    "unknown",
}

ALLOWED_CONFIDENCE_LEVELS = {
    "high",
    "moderate",
    "low",
}

PROHIBITED_COLUMNS = {
    "address",
    "street_address",
    "exact_address",
    "latitude",
    "longitude",
    "lat",
    "lon",
    "coordinates",
    "gps",
    "phone",
    "email",
    "social_media_handle",
    "username",
    "screen_name",
    "individual_name",
    "member_name",
    "suspect_name",
    "victim_name",
    "officer_name",
    "meeting_location",
    "facility_address",
    "tactical_location",
    "recruitment_channel",
    "chatroom",
    "telegram",
    "discord",
    "case_narrative",
    "operational_notes",
}

EXPECTED_COLUMNS = [
    "reference_id",
    "group_or_network_name",
    "category",
    "source_type",
    "source_name",
    "source_url",
    "geographic_reference",
    "geo_level",
    "county",
    "date_observed",
    "source_publication_date",
    "confidence_level",
    "summary_note",
    "legal_status_note",
    "responsible_use_flag",
    "include_in_report",
    "include_in_score",
]


def _normalize_text(value) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def _normalize_choice(value) -> str:
    text = _normalize_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text


def _normalize_reference_text(value) -> str:
    """
    Normalize text for duplicate detection only.

    This is intentionally separate from display cleaning so the public-facing
    output preserves the source language while duplicate checks are stable.
    """

    text = _normalize_text(value).lower()
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def _normalize_county(value) -> str:
    text = _normalize_text(value)

    text = (
        text.replace(" County", "")
        .replace(" county", "")
        .replace(", Tennessee", "")
        .replace(", TN", "")
        .strip()
    )

    return text


def _safe_bool(value, default: bool = True) -> bool:
    if pd.isna(value):
        return default

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "y"}:
        return True

    if text in {"false", "0", "no", "n"}:
        return False

    return default


def _create_template() -> pd.DataFrame:
    """
    Create a safe, non-operational template for public-source group references.

    Do not add addresses, coordinates, individual names, social handles,
    recruitment channels, meeting locations, operational details, or case narratives.
    """

    rows = [
        {
            "reference_id": "REF-001",
            "group_or_network_name": "Example: Source-documented group or network",
            "category": "extremist_or_hate_group",
            "source_type": "civil_society_tracker",
            "source_name": "Example: SPLC Hate Map / ADL H.E.A.T. Map / DOJ / TBI / Court filing",
            "source_url": "https://example.com/source",
            "geographic_reference": "Statewide or county-level reference only",
            "geo_level": "statewide",
            "county": "",
            "date_observed": "",
            "source_publication_date": "",
            "confidence_level": "moderate",
            "summary_note": (
                "Brief source-grounded summary. Do not include exact locations, "
                "individual names, addresses, handles, or operational details."
            ),
            "legal_status_note": (
                "Use careful language: alleged, charged, convicted, designated, "
                "listed by source, or publicly documented by source."
            ),
            "responsible_use_flag": (
                "Reference-only. Not a terrorism label. Not used to identify people, "
                "locations, members, or operational activity."
            ),
            "include_in_report": True,
            "include_in_score": False,
        }
    ]

    return pd.DataFrame(rows, columns=EXPECTED_COLUMNS)


def _validate_no_prohibited_columns(df: pd.DataFrame) -> None:
    """
    Block columns that could store unsafe operational or individual-level details.
    """

    lower_cols = {str(col).strip().lower() for col in df.columns}
    prohibited_found = sorted(lower_cols.intersection(PROHIBITED_COLUMNS))

    if prohibited_found:
        raise ValueError(
            "The public group reference input contains prohibited columns:\n"
            + "\n".join(f"- {col}" for col in prohibited_found)
            + "\n\nRemove address, coordinate, individual, social-handle, meeting-place, "
            "recruitment-channel, case-narrative, and operational-detail fields before rerunning."
        )


def _is_template_example_row(row: pd.Series) -> bool:
    """
    Identify the starter template row so it does not appear in report outputs.

    This protects the PDF appendix if the template row is accidentally left in
    data/raw/tn_public_group_reference_inputs.csv.
    """

    name = _normalize_reference_text(row.get("group_or_network_name"))
    source_name = _normalize_reference_text(row.get("source_name"))
    source_url = _normalize_reference_text(row.get("source_url"))

    return (
        name.startswith("example:")
        or "example:" in source_name
        or source_url == "https://example.com/source"
    )


def _deduplicate_references(output: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Deduplicate reference rows before validation and report output.

    The key is intentionally source-level and non-operational:
    - group/network name
    - source name
    - geographic reference
    - observed year/date
    - category

    The function keeps the last occurrence, which preserves the most recently
    appended version when the SPLC processor is rerun.
    """

    if output.empty:
        return output, 0

    working = output.copy()

    dedupe_fields = [
        "group_or_network_name",
        "source_name",
        "geographic_reference",
        "date_observed",
        "category",
    ]

    for col in dedupe_fields:
        if col not in working.columns:
            working[col] = ""

    for col in dedupe_fields:
        working[f"_dedupe_{col}"] = working[col].apply(_normalize_reference_text)

    dedupe_key_cols = [f"_dedupe_{col}" for col in dedupe_fields]

    before_count = len(working)
    working = working.drop_duplicates(subset=dedupe_key_cols, keep="last").copy()
    removed_count = before_count - len(working)

    working = working.drop(columns=dedupe_key_cols, errors="ignore")

    return working, removed_count


def _validate_and_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int, int]:
    """
    Clean, deduplicate, and validate manually reviewed public-source reference rows.
    """

    _validate_no_prohibited_columns(df)

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    output = df[EXPECTED_COLUMNS].copy()

    text_cols = [
        "reference_id",
        "group_or_network_name",
        "source_name",
        "source_url",
        "geographic_reference",
        "county",
        "date_observed",
        "source_publication_date",
        "summary_note",
        "legal_status_note",
        "responsible_use_flag",
    ]

    for col in text_cols:
        output[col] = output[col].apply(_normalize_text)

    output["category"] = output["category"].apply(_normalize_choice)
    output["source_type"] = output["source_type"].apply(_normalize_choice)
    output["geo_level"] = output["geo_level"].apply(_normalize_choice)
    output["confidence_level"] = output["confidence_level"].apply(_normalize_choice)
    output["county"] = output["county"].apply(_normalize_county)

    output["include_in_report"] = output["include_in_report"].apply(
        lambda value: _safe_bool(value, default=True)
    )
    output["include_in_score"] = output["include_in_score"].apply(
        lambda value: _safe_bool(value, default=False)
    )

    # This layer is reference-only by design. Force score inclusion to False
    # even if a row is accidentally marked as True.
    output["include_in_score"] = False

    # Remove the example/template row from actual outputs if it was left in
    # the raw input file.
    template_mask = output.apply(_is_template_example_row, axis=1)
    template_removed_count = int(template_mask.sum())

    if template_removed_count > 0:
        output = output[~template_mask].copy()

    # Deduplicate rows after normalization but before validation.
    output, duplicate_removed_count = _deduplicate_references(output)

    # Fill missing reference IDs after cleaning/deduplication.
    missing_reference_id = output["reference_id"].eq("")
    if missing_reference_id.any():
        output.loc[missing_reference_id, "reference_id"] = [
            f"REF-AUTO-{idx + 1:04d}" for idx in range(missing_reference_id.sum())
        ]

    validation_records = []

    for _, row in output.iterrows():
        issues = []

        if not row["group_or_network_name"]:
            issues.append("missing_group_or_network_name")

        if row["category"] not in ALLOWED_CATEGORIES:
            issues.append("invalid_category")

        if row["source_type"] not in ALLOWED_SOURCE_TYPES:
            issues.append("invalid_source_type")

        if row["geo_level"] not in ALLOWED_GEO_LEVELS:
            issues.append("invalid_geo_level")

        if row["confidence_level"] not in ALLOWED_CONFIDENCE_LEVELS:
            issues.append("invalid_confidence_level")

        if row["geo_level"] == "county" and not row["county"]:
            issues.append("county_geo_level_without_county")

        if not row["source_name"]:
            issues.append("missing_source_name")

        if not row["source_url"]:
            issues.append("missing_source_url")

        if not row["responsible_use_flag"]:
            issues.append("missing_responsible_use_flag")

        validation_records.append(
            {
                "reference_id": row["reference_id"],
                "group_or_network_name": row["group_or_network_name"],
                "validation_issue_count": len(issues),
                "validation_issues": "; ".join(issues),
                "is_valid_reference": len(issues) == 0,
                "include_in_report": row["include_in_report"],
                "include_in_score": row["include_in_score"],
            }
        )

    validation_df = pd.DataFrame(validation_records)

    output = output.merge(
        validation_df[
            [
                "reference_id",
                "validation_issue_count",
                "validation_issues",
                "is_valid_reference",
            ]
        ],
        on="reference_id",
        how="left",
    )

    return output, validation_df, template_removed_count, duplicate_removed_count


def build_public_group_reference() -> pd.DataFrame:
    """
    Build a source-validated public group / network reference table.

    This layer is intentionally non-scoring. It is designed for a report appendix
    or dashboard reference tab. It should not be used to label counties, people,
    businesses, organizations, or lawful activity as suspicious.
    """

    PUBLIC_GROUP_REFERENCE_INPUT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_GROUP_REFERENCE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if not PUBLIC_GROUP_REFERENCE_INPUT.exists():
        template = _create_template()
        template.to_csv(PUBLIC_GROUP_REFERENCE_INPUT, index=False)

        print("\nPublic group reference template created:")
        print(f"- {PUBLIC_GROUP_REFERENCE_INPUT}")
        print(
            "\nPopulate this file with source-validated, county/state-level references only. "
            "Do not include addresses, coordinates, individual names, handles, meeting places, "
            "case narratives, or operational details."
        )

        return template

    raw_df = pd.read_csv(PUBLIC_GROUP_REFERENCE_INPUT)

    (
        cleaned_df,
        validation_df,
        template_removed_count,
        duplicate_removed_count,
    ) = _validate_and_clean(raw_df)

    cleaned_df.to_csv(PUBLIC_GROUP_REFERENCE_OUTPUT, index=False)
    validation_df.to_csv(PUBLIC_GROUP_REFERENCE_VALIDATION_OUTPUT, index=False)

    print("\nPublic group reference outputs created:")
    print(f"- {PUBLIC_GROUP_REFERENCE_OUTPUT}")
    print(f"- {PUBLIC_GROUP_REFERENCE_VALIDATION_OUTPUT}")

    if template_removed_count > 0:
        print(f"\nTemplate/example rows removed from output: {template_removed_count}")

    if duplicate_removed_count > 0:
        print(f"Duplicate reference rows removed from output: {duplicate_removed_count}")

    invalid_count = int((~validation_df["is_valid_reference"]).sum())

    if invalid_count > 0:
        print(f"\nWarning: {invalid_count} reference row(s) have validation issues.")
        print(f"Review: {PUBLIC_GROUP_REFERENCE_VALIDATION_OUTPUT}")

    valid_report_rows = cleaned_df[
        cleaned_df["is_valid_reference"] & cleaned_df["include_in_report"]
    ]

    print(f"\nValid report-ready references: {len(valid_report_rows)}")
    print("This layer is reference-only and is not included in risk scoring.")

    return cleaned_df


def main():
    build_public_group_reference()


if __name__ == "__main__":
    main()
