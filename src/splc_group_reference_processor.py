import re
from pathlib import Path

import pandas as pd

from src.config import (
    PUBLIC_GROUP_REFERENCE_INPUT,
    SPLC_HATE_MAP_INPUT,
    SPLC_PUBLIC_GROUP_REFERENCE_CANDIDATES_OUTPUT,
)


SPLC_SOURCE_URL = "https://www.splcenter.org/hate-map/?hm_year=2024&hm_state=TN"


IDEOLOGY_CATEGORY_MAP = {
    "anti-lgbtq": "extremist_or_hate_group",
    "anti-muslim": "extremist_or_hate_group",
    "antigovernment general": "antigovernment_or_militia",
    "antigovernment": "antigovernment_or_militia",
    "white nationalist": "extremist_or_hate_group",
    "neo-nazi": "extremist_or_hate_group",
    "neo-confederate": "extremist_or_hate_group",
    "racist skinhead": "extremist_or_hate_group",
    "christian identity": "extremist_or_hate_group",
    "general hate": "extremist_or_hate_group",
}


PUBLIC_REFERENCE_COLUMNS = [
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


PROHIBITED_OUTPUT_TERMS = [
    "address",
    "street",
    "latitude",
    "longitude",
    "coordinate",
    "gps",
    "phone",
    "email",
    "member",
    "suspect",
    "victim",
    "officer",
    "meeting",
    "handle",
    "username",
    "telegram",
    "discord",
]


def _clean_text(value) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def _normalize_choice(value) -> str:
    text = _clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return text


def _normalize_county(value) -> str:
    text = _clean_text(value)

    text = (
        text.replace(" County", "")
        .replace(" county", "")
        .replace(", Tennessee", "")
        .replace(", TN", "")
        .strip()
    )

    return text


def _derive_category(ideology_name: str) -> str:
    ideology_key = _normalize_choice(ideology_name)
    return IDEOLOGY_CATEGORY_MAP.get(ideology_key, "other_public_reference")


def _derive_geo_level(city_name: str, statewide) -> str:
    city = _clean_text(city_name)
    statewide_bool = str(statewide).strip().lower() in {"true", "1", "yes", "y"}

    if statewide_bool:
        return "statewide"

    if "county" in city.lower():
        return "county"

    if city:
        return "city_or_region"

    return "unknown"


def _derive_county(city_name: str, geo_level: str) -> str:
    if geo_level != "county":
        return ""

    return _normalize_county(city_name)


def _validate_safe_output_columns(df: pd.DataFrame) -> None:
    """
    Prevent accidentally creating output fields that could store operational detail.
    """

    lower_cols = [str(col).lower() for col in df.columns]

    for col in lower_cols:
        for term in PROHIBITED_OUTPUT_TERMS:
            if term in col:
                raise ValueError(
                    f"Unsafe output column detected: {col}. "
                    "Do not store addresses, coordinates, individuals, handles, "
                    "meeting locations, or operational details in this layer."
                )


def _deduplicate_public_reference_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate source references while preserving the most recent row.

    The combination below is intentionally source-level and non-operational.
    """

    dedupe_cols = [
        "group_or_network_name",
        "source_name",
        "geographic_reference",
        "date_observed",
    ]

    for col in dedupe_cols:
        if col not in df.columns:
            df[col] = ""

    return df.drop_duplicates(subset=dedupe_cols, keep="last")


def process_splc_hate_map_csv(
    input_path: Path = SPLC_HATE_MAP_INPUT,
    append_to_public_reference_input: bool = False,
) -> pd.DataFrame:
    """
    Convert the SPLC Tennessee Hate Map CSV into a safe public reference table.

    This processor is reference-only:
    - It does not score counties.
    - It does not infer criminality, terrorism, motive, or operational activity.
    - It does not retain addresses, coordinates, people, handles, meeting places,
      recruitment channels, or operational details.
    - The SPLC ideology/category field is preserved as a source classification,
      not as an independent finding by this model.

    Expected SPLC columns:
    name, ideology_name, state_name, city_name, ein, statewide
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(
            f"SPLC input not found: {input_path}\n\n"
            "Save the downloaded SPLC Tennessee 2024 CSV as:\n"
            "data/raw/splc_hate_data_2024.csv"
        )

    raw_df = pd.read_csv(input_path)

    required_cols = [
        "name",
        "ideology_name",
        "state_name",
        "city_name",
        "statewide",
    ]

    missing = [col for col in required_cols if col not in raw_df.columns]

    if missing:
        raise ValueError(
            "SPLC CSV is missing required columns:\n"
            + "\n".join(f"- {col}" for col in missing)
        )

    df = raw_df.copy()
    df["state_name"] = df["state_name"].apply(_clean_text)

    tn_df = df[df["state_name"].str.lower().eq("tennessee")].copy()

    if tn_df.empty:
        raise ValueError("No Tennessee rows found in SPLC CSV.")

    records = []

    for idx, row in tn_df.reset_index(drop=True).iterrows():
        name = _clean_text(row.get("name"))
        ideology = _clean_text(row.get("ideology_name"))
        city = _clean_text(row.get("city_name"))
        statewide = row.get("statewide")

        geo_level = _derive_geo_level(city, statewide)
        county = _derive_county(city, geo_level)

        geographic_reference = "Statewide" if geo_level == "statewide" else city

        summary_note = (
            f"SPLC 2024 Hate Map lists this public reference in Tennessee "
            f"with source category/ideology '{ideology}'. Geographic reference "
            f"is retained only at statewide, county, or city/region level."
        )

        legal_status_note = (
            "Listed by SPLC Hate Map as a public-source civil-society tracker reference. "
            "This model does not independently verify membership, activity, criminality, "
            "motive, ideology, or operational conduct."
        )

        responsible_use_flag = (
            "Reference-only. Not included in risk scoring. Not a terrorism label. "
            "Do not use to identify people, exact locations, members, meeting places, "
            "recruitment channels, or operational activity."
        )

        records.append(
            {
                "reference_id": f"SPLC-2024-TN-{idx + 1:03d}",
                "group_or_network_name": name,
                "category": _derive_category(ideology),
                "source_type": "civil_society_tracker",
                "source_name": "Southern Poverty Law Center Hate Map 2024",
                "source_url": SPLC_SOURCE_URL,
                "geographic_reference": geographic_reference,
                "geo_level": geo_level,
                "county": county,
                "date_observed": "2024",
                "source_publication_date": "2024",
                "confidence_level": "moderate",
                "summary_note": summary_note,
                "legal_status_note": legal_status_note,
                "responsible_use_flag": responsible_use_flag,
                "include_in_report": True,
                "include_in_score": False,
                "source_ideology_name": ideology,
                "source_city_name": city,
                "source_statewide_flag": bool(
                    str(statewide).strip().lower() in {"true", "1", "yes", "y"}
                ),
            }
        )

    output = pd.DataFrame(records)

    _validate_safe_output_columns(output)

    SPLC_PUBLIC_GROUP_REFERENCE_CANDIDATES_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.to_csv(SPLC_PUBLIC_GROUP_REFERENCE_CANDIDATES_OUTPUT, index=False)

    print("\nSPLC public group reference candidates created:")
    print(f"- {SPLC_PUBLIC_GROUP_REFERENCE_CANDIDATES_OUTPUT}")
    print(f"Rows: {len(output)}")
    print("\nCategory counts:")
    print(output["category"].value_counts().to_string())

    if append_to_public_reference_input:
        public_reference_rows = output[PUBLIC_REFERENCE_COLUMNS].copy()

        if PUBLIC_GROUP_REFERENCE_INPUT.exists():
            existing = pd.read_csv(PUBLIC_GROUP_REFERENCE_INPUT)

            for col in PUBLIC_REFERENCE_COLUMNS:
                if col not in existing.columns:
                    existing[col] = ""

            combined = pd.concat(
                [
                    existing[PUBLIC_REFERENCE_COLUMNS],
                    public_reference_rows,
                ],
                ignore_index=True,
            )

            combined = _deduplicate_public_reference_rows(combined)
        else:
            combined = public_reference_rows

        PUBLIC_GROUP_REFERENCE_INPUT.parent.mkdir(parents=True, exist_ok=True)
        combined.to_csv(PUBLIC_GROUP_REFERENCE_INPUT, index=False)

        print("\nUpdated public reference input:")
        print(f"- {PUBLIC_GROUP_REFERENCE_INPUT}")
        print(
            "Next run: python -m src.public_group_reference "
            "to validate the merged reference input."
        )

    print(
        "\nResponsible-use note: this output is reference-only and is not included "
        "in risk scoring."
    )

    return output


def main():
    process_splc_hate_map_csv(append_to_public_reference_input=True)


if __name__ == "__main__":
    main()
