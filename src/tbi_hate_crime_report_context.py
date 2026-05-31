import pandas as pd

from src.config import (
    TBI_HATE_CRIME_BIAS_CONTEXT_OUTPUT,
    TBI_HATE_CRIME_CLEARANCE_CONTEXT_OUTPUT,
    TBI_HATE_CRIME_LOCATION_CONTEXT_OUTPUT,
    TBI_HATE_CRIME_OFFENSE_CONTEXT_OUTPUT,
    TBI_HATE_CRIME_REPORT_CONTEXT_SUMMARY_OUTPUT,
)


REPORT_SOURCE_NAME = "Tennessee Bureau of Investigation 2024 Hate Crime Report"
REPORT_SOURCE_FILE = "2024 Hate Crime Final SECURED.pdf"


def build_tbi_hate_crime_report_context() -> dict[str, pd.DataFrame]:
    """
    Build statewide context tables from the TBI 2024 Hate Crime Report.

    This module creates report-context tables only. It does not replace the
    county-level TBI hate-crime processor and does not change risk scoring.

    Responsible-use boundary:
    - Statewide context only.
    - No agency-level, incident-level, victim-level, suspect-level, address,
      coordinate, narrative, case-level, or operational records are retained.
    - Hate-crime statistics are targeted-harm context, not terrorism labels.
    - Unknown-bias counts are retained as context but excluded from known-bias
      percentage interpretation.
    """

    TBI_HATE_CRIME_REPORT_CONTEXT_SUMMARY_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    bias_rows = [
        {
            "bias_category": "Race/Ethnicity/Ancestry Bias",
            "known_bias_2022": 94,
            "known_bias_2023": 62,
            "known_bias_2024": 94,
            "percent_of_known_bias_2024": 71.76,
        },
        {
            "bias_category": "Religious Bias",
            "known_bias_2022": 18,
            "known_bias_2023": 18,
            "known_bias_2024": 9,
            "percent_of_known_bias_2024": 6.87,
        },
        {
            "bias_category": "Sexual Orientation / Gender Bias",
            "known_bias_2022": 10,
            "known_bias_2023": 35,
            "known_bias_2024": 26,
            "percent_of_known_bias_2024": 19.85,
        },
        {
            "bias_category": "Disability Bias",
            "known_bias_2022": 7,
            "known_bias_2023": 7,
            "known_bias_2024": 2,
            "percent_of_known_bias_2024": 1.53,
        },
        {
            "bias_category": "Total Known Bias",
            "known_bias_2022": 129,
            "known_bias_2023": 122,
            "known_bias_2024": 131,
            "percent_of_known_bias_2024": 100.00,
        },
        {
            "bias_category": "Unknown Bias",
            "known_bias_2022": 126,
            "known_bias_2023": 86,
            "known_bias_2024": 22,
            "percent_of_known_bias_2024": None,
        },
    ]

    offense_rows = [
        {
            "crime_category": "Crimes Against Persons",
            "offense_type": "Murder",
            "reported_total_2024": 0,
        },
        {
            "crime_category": "Crimes Against Persons",
            "offense_type": "Kidnapping/Abduction",
            "reported_total_2024": 0,
        },
        {
            "crime_category": "Crimes Against Persons",
            "offense_type": "Forcible Rape",
            "reported_total_2024": 1,
        },
        {
            "crime_category": "Crimes Against Persons",
            "offense_type": "Aggravated Assault",
            "reported_total_2024": 10,
        },
        {
            "crime_category": "Crimes Against Persons",
            "offense_type": "Simple Assault",
            "reported_total_2024": 34,
        },
        {
            "crime_category": "Crimes Against Persons",
            "offense_type": "Intimidation",
            "reported_total_2024": 53,
        },
        {
            "crime_category": "Crimes Against Persons",
            "offense_type": "Total",
            "reported_total_2024": 98,
        },
        {
            "crime_category": "Crimes Against Property",
            "offense_type": "Arson",
            "reported_total_2024": 7,
        },
        {
            "crime_category": "Crimes Against Property",
            "offense_type": "Destruction/Damage/Vandalism",
            "reported_total_2024": 24,
        },
        {
            "crime_category": "Crimes Against Property",
            "offense_type": "Robbery",
            "reported_total_2024": 0,
        },
        {
            "crime_category": "Crimes Against Property",
            "offense_type": "Theft - Shoplifting",
            "reported_total_2024": 1,
        },
        {
            "crime_category": "Crimes Against Property",
            "offense_type": "Theft From Building",
            "reported_total_2024": 1,
        },
        {
            "crime_category": "Crimes Against Property",
            "offense_type": "Theft - All Other Larceny",
            "reported_total_2024": 1,
        },
        {
            "crime_category": "Crimes Against Property",
            "offense_type": "Total",
            "reported_total_2024": 34,
        },
    ]

    clearance_rows = [
        {
            "clearance_type": "Cleared by Arrest",
            "reported_total_2024": 27,
        },
        {
            "clearance_type": "Prosecution Declined",
            "reported_total_2024": 3,
        },
        {
            "clearance_type": "Victim Refused to Cooperate",
            "reported_total_2024": 4,
        },
        {
            "clearance_type": "Juvenile / No Custody",
            "reported_total_2024": 1,
        },
        {
            "clearance_type": "Not Cleared",
            "reported_total_2024": 86,
        },
    ]

    location_rows = [
        {"location_type": "Residence/Home", "reported_total_2024": 46},
        {"location_type": "Commercial", "reported_total_2024": 18},
        {"location_type": "Educational Facility", "reported_total_2024": 28},
        {
            "location_type": "Government/Public Building and other",
            "reported_total_2024": 7,
        },
        {"location_type": "Transportation", "reported_total_2024": 26},
        {"location_type": "Highway/Road/Alley", "reported_total_2024": 16},
        {"location_type": "Parking Lot/Garage", "reported_total_2024": 10},
        {"location_type": "Recreational Spaces", "reported_total_2024": 5},
        {"location_type": "Other/Unknown", "reported_total_2024": 4},
    ]

    summary_rows = [
        {
            "context_item": "known_bias_total_2024",
            "value": 131,
            "note": (
                "Total known bias motivations in the TBI 2024 Hate Crime Report, "
                "excluding Unknown bias from analysis."
            ),
        },
        {
            "context_item": "unknown_bias_total_2024",
            "value": 22,
            "note": (
                "TBI notes Unknown bias is being reviewed and is generally not a hate "
                "crime unless later categorized."
            ),
        },
        {
            "context_item": "crimes_against_persons_total_2024",
            "value": 98,
            "note": (
                "TBI report states Crimes Against Persons accounted for 74.24% of "
                "reported hate crimes in 2024."
            ),
        },
        {
            "context_item": "crimes_against_property_total_2024",
            "value": 34,
            "note": (
                "TBI report states Crimes Against Property accounted for 25.76% of "
                "reported hate crimes in 2024."
            ),
        },
        {
            "context_item": "most_common_offense_2024",
            "value": 53,
            "note": (
                "Intimidation was the most common reported bias-motivated offense, "
                "making up 40.15% of total reports."
            ),
        },
        {
            "context_item": "not_cleared_total_2024",
            "value": 86,
            "note": "TBI report states the majority of hate crimes were not cleared.",
        },
        {
            "context_item": "cleared_by_arrest_total_2024",
            "value": 27,
            "note": (
                "TBI report states that when a bias-motivated crime was cleared, it "
                "was more often cleared by arrest than by exceptional clearance."
            ),
        },
    ]

    bias_df = pd.DataFrame(bias_rows)
    offense_df = pd.DataFrame(offense_rows)
    clearance_df = pd.DataFrame(clearance_rows)
    location_df = pd.DataFrame(location_rows)
    summary_df = pd.DataFrame(summary_rows)

    for df in [bias_df, offense_df, clearance_df, location_df, summary_df]:
        df["source_name"] = REPORT_SOURCE_NAME
        df["source_file"] = REPORT_SOURCE_FILE
        df["responsible_use_note"] = (
            "Statewide context only. Not a terrorism label. Not used to identify "
            "people, agencies, addresses, exact locations, or operational details."
        )

    bias_df.to_csv(TBI_HATE_CRIME_BIAS_CONTEXT_OUTPUT, index=False)
    offense_df.to_csv(TBI_HATE_CRIME_OFFENSE_CONTEXT_OUTPUT, index=False)
    clearance_df.to_csv(TBI_HATE_CRIME_CLEARANCE_CONTEXT_OUTPUT, index=False)
    location_df.to_csv(TBI_HATE_CRIME_LOCATION_CONTEXT_OUTPUT, index=False)
    summary_df.to_csv(TBI_HATE_CRIME_REPORT_CONTEXT_SUMMARY_OUTPUT, index=False)

    print("\nTBI 2024 hate crime context tables created:")
    print(f"- {TBI_HATE_CRIME_BIAS_CONTEXT_OUTPUT}")
    print(f"- {TBI_HATE_CRIME_OFFENSE_CONTEXT_OUTPUT}")
    print(f"- {TBI_HATE_CRIME_CLEARANCE_CONTEXT_OUTPUT}")
    print(f"- {TBI_HATE_CRIME_LOCATION_CONTEXT_OUTPUT}")
    print(f"- {TBI_HATE_CRIME_REPORT_CONTEXT_SUMMARY_OUTPUT}")
    print("\nThese outputs are statewide context only and are not included in risk scoring.")

    return {
        "bias": bias_df,
        "offense": offense_df,
        "clearance": clearance_df,
        "location": location_df,
        "summary": summary_df,
    }


def main():
    build_tbi_hate_crime_report_context()


if __name__ == "__main__":
    main()
