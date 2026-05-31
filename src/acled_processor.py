import os

import pandas as pd
import requests

from src.config import (
    ACLED_END_DATE,
    ACLED_PASSWORD,
    ACLED_START_DATE,
    ACLED_USERNAME,
    OPTIONAL_POLITICAL_VIOLENCE_INPUT,
    RAW_DIR,
    TABLES_DIR,
)


ACLED_TOKEN_URL = "https://acleddata.com/oauth/token"
ACLED_ENDPOINT = "https://acleddata.com/api/acled/read"

# Keep this False by default to avoid storing event-level detail unnecessarily.
# If you ever need a full audit pull locally, add this to .env:
# ACLED_SAVE_FULL_RAW=true
ACLED_SAVE_FULL_RAW = os.getenv("ACLED_SAVE_FULL_RAW", "false").strip().lower() == "true"


def _require_credentials():
    if not ACLED_USERNAME or not ACLED_PASSWORD:
        raise RuntimeError(
            "Missing ACLED credentials. Add these to your project .env file:\n\n"
            "ACLED_USERNAME=your_acled_username_or_email\n"
            "ACLED_PASSWORD=your_acled_password\n"
        )


def get_acled_token() -> str:
    """
    Request an ACLED OAuth token using myACLED username/password.

    Credentials are read from .env through src.config.
    """

    _require_credentials()

    payload = {
        "username": ACLED_USERNAME,
        "password": ACLED_PASSWORD,
        "grant_type": "password",
        "client_id": "acled",
    }

    response = requests.post(ACLED_TOKEN_URL, data=payload, timeout=45)

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        print("\nACLED authentication failed.")
        print(f"Status code: {response.status_code}")
        print(f"Response preview: {response.text[:1000]}")
        raise exc

    data = response.json()
    token = data.get("access_token")

    if not token:
        raise RuntimeError(
            "ACLED authentication response did not include an access_token. "
            "Check your myACLED access level and credentials."
        )

    return token


def _safe_get_json(url: str, headers: dict, params: dict):
    response = requests.get(url, headers=headers, params=params, timeout=60)

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        print("\nACLED API request failed.")
        print(f"URL: {response.url}")
        print(f"Status code: {response.status_code}")
        print(f"Response preview: {response.text[:1000]}")
        raise exc

    try:
        return response.json()
    except Exception as exc:
        print("\nACLED API did not return valid JSON.")
        print(f"URL: {response.url}")
        print(f"Status code: {response.status_code}")
        print(f"Response preview: {response.text[:1000]}")
        raise exc


def _save_sanitized_acled_pull(df: pd.DataFrame) -> None:
    """
    Save a reduced ACLED pull for audit/debugging without retaining event notes,
    actor names, exact coordinates, URLs, or site-level detail.
    """

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    safe_cols = [
        "event_id_cnty",
        "event_date",
        "year",
        "country",
        "admin1",
        "admin2",
        "admin3",
        "event_type",
        "sub_event_type",
        "disorder_type",
        "fatalities",
    ]

    existing_cols = [col for col in safe_cols if col in df.columns]

    if existing_cols:
        sanitized_output = RAW_DIR / "acled_tennessee_events_sanitized.csv"
        df[existing_cols].to_csv(sanitized_output, index=False)
        print(f"\nSanitized ACLED Tennessee events saved: {sanitized_output}")

    if ACLED_SAVE_FULL_RAW:
        raw_output = RAW_DIR / "acled_tennessee_events_raw_full.csv"
        df.to_csv(raw_output, index=False)
        print(f"Full ACLED raw pull saved locally: {raw_output}")


def fetch_acled_tennessee_events() -> pd.DataFrame:
    """
    Pull ACLED events for Tennessee within the configured date range.

    The model should only use county-level aggregate outputs. This function saves
    a sanitized audit file by default, not a full event-level file.
    """

    token = get_acled_token()
    headers = {"Authorization": f"Bearer {token}"}

    all_records = []
    page = 1
    limit = 5000

    while True:
        params = {
            "country": "United States",
            "admin1": "Tennessee",
            "event_date": f"{ACLED_START_DATE}|{ACLED_END_DATE}",
            "event_date_where": "BETWEEN",
            "limit": limit,
            "page": page,
        }

        data = _safe_get_json(ACLED_ENDPOINT, headers=headers, params=params)
        records = data.get("data", [])

        if not records:
            break

        all_records.extend(records)

        print(f"ACLED page {page}: {len(records)} records")

        if len(records) < limit:
            break

        page += 1

    df = pd.DataFrame(all_records)

    if df.empty:
        raise ValueError(
            "No ACLED Tennessee records were returned. "
            "Check ACLED credentials, date range, and API filters."
        )

    _save_sanitized_acled_pull(df)

    print(f"Raw ACLED shape: {df.shape}")

    return df


def _normalize_county(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()

    text = (
        text.replace(" County", "")
        .replace(" county", "")
        .replace(", Tennessee", "")
        .replace(", TN", "")
        .strip()
    )

    return text


def _extract_county_from_row(row: pd.Series) -> str:
    """
    Try to derive county from ACLED fields.

    Preferred:
    - admin2
    - admin3
    - location only if it explicitly contains county text

    The model output should remain county-level only.
    """

    for col in ["admin2", "admin3"]:
        if col in row.index and pd.notna(row[col]):
            value = str(row[col]).strip()

            if value:
                return _normalize_county(value)

    if "location" in row.index and pd.notna(row["location"]):
        value = str(row["location"]).strip()

        if "county" in value.lower():
            return _normalize_county(value)

    return ""


def _classify_event(row: pd.Series) -> dict:
    event_type = str(row.get("event_type", "")).strip()
    sub_event_type = str(row.get("sub_event_type", "")).strip()
    disorder_type = str(row.get("disorder_type", "")).strip()

    event_lower = event_type.lower()
    sub_lower = sub_event_type.lower()
    disorder_lower = disorder_type.lower()

    protest = 1 if event_lower == "protests" else 0

    violent_unrest = 1 if (
        event_lower == "riots"
        or "violent demonstration" in sub_lower
        or "mob violence" in sub_lower
    ) else 0

    political_violence = 1 if event_lower in {
        "battles",
        "explosions/remote violence",
        "violence against civilians",
    } else 0

    strategic_development = 1 if event_lower == "strategic developments" else 0

    public_disorder = 1 if (
        "demonstrations" in disorder_lower
        or event_lower in {"protests", "riots"}
    ) else 0

    return {
        "protest_event_count": protest,
        "violent_unrest_event_count": violent_unrest,
        "political_violence_event_count": political_violence,
        "strategic_development_count": strategic_development,
        "public_disorder_event_count": public_disorder,
    }


def process_acled_events_to_county_inputs(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert ACLED event-level records into county-level aggregate inputs.

    Model outputs exclude event notes, actor names, organization names,
    participant details, exact locations, coordinates, URLs, narratives,
    and site-level details.
    """

    if events_df.empty:
        raise ValueError("No ACLED events were returned for the configured filter.")

    working = events_df.copy()

    working["county"] = working.apply(_extract_county_from_row, axis=1)

    classification_df = working.apply(_classify_event, axis=1, result_type="expand")
    working = pd.concat([working, classification_df], axis=1)

    if "fatalities" in working.columns:
        working["acled_fatalities"] = pd.to_numeric(
            working["fatalities"],
            errors="coerce",
        ).fillna(0)
    else:
        working["acled_fatalities"] = 0

    working["total_acled_event_count"] = 1

    matched = working[working["county"].astype(str).str.len() > 0].copy()
    unmatched = working[working["county"].astype(str).str.len() == 0].copy()

    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    validation_cols = [
        col
        for col in [
            "event_id_cnty",
            "event_date",
            "year",
            "event_type",
            "sub_event_type",
            "disorder_type",
            "admin1",
            "admin2",
            "admin3",
        ]
        if col in working.columns
    ]

    if validation_cols:
        working[validation_cols + ["county"]].to_csv(
            TABLES_DIR / "acled_county_aggregation_validation.csv",
            index=False,
        )

    if not unmatched.empty and validation_cols:
        unmatched[validation_cols].to_csv(
            TABLES_DIR / "acled_unmatched_county_rows.csv",
            index=False,
        )

    event_summary_cols = [
        col
        for col in [
            "event_type",
            "sub_event_type",
            "disorder_type",
        ]
        if col in working.columns
    ]

    if event_summary_cols:
        summary = (
            working.groupby(event_summary_cols, dropna=False)
            .size()
            .reset_index(name="event_count")
            .sort_values("event_count", ascending=False)
        )

        summary.to_csv(
            TABLES_DIR / "acled_tennessee_event_type_summary.csv",
            index=False,
        )

    county_output = (
        matched.groupby("county", as_index=False)
        .agg(
            protest_event_count=("protest_event_count", "sum"),
            violent_unrest_event_count=("violent_unrest_event_count", "sum"),
            political_violence_event_count=("political_violence_event_count", "sum"),
            strategic_development_count=("strategic_development_count", "sum"),
            public_disorder_event_count=("public_disorder_event_count", "sum"),
            total_acled_event_count=("total_acled_event_count", "sum"),
            acled_fatalities=("acled_fatalities", "sum"),
        )
        .sort_values("county")
    )

    OPTIONAL_POLITICAL_VIOLENCE_INPUT.parent.mkdir(parents=True, exist_ok=True)
    county_output.to_csv(OPTIONAL_POLITICAL_VIOLENCE_INPUT, index=False)

    print("\nACLED county political violence input created:")
    print(f"- {OPTIONAL_POLITICAL_VIOLENCE_INPUT}")
    print(f"Output shape: {county_output.shape}")

    print("\nTop 10 counties by total ACLED events:")
    print(
        county_output.sort_values("total_acled_event_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print(f"\nUnmatched rows without county: {len(unmatched)}")

    if len(unmatched) > 0:
        print("- Review outputs/tables/acled_unmatched_county_rows.csv")

    return county_output


def main():
    events_df = fetch_acled_tennessee_events()
    process_acled_events_to_county_inputs(events_df)


if __name__ == "__main__":
    main()