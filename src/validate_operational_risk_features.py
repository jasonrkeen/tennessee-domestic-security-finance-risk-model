from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "tn_operational_risk_features.csv"

EXPECTED_COUNTIES = 95

CORE_FIELDS = [
    "county",
    "population",
    "population_density",
    "poverty_rate",
    "unemployment_rate",
    "median_household_income",
    "avg_aadt",
    "total_vmt",
    "violent_crime_rate",
    "weapon_law_violation_rate",
    "public_disorder_rate",
    "fema_social_vulnerability_score",
    "fema_community_resilience_score",
    "hospital_beds_per_100k",
    "infrastructure_needs_per_capita",
    "operational_exposure_score",
    "resilience_gap_score",
    "final_operational_risk_score",
    "operational_risk_tier",
    "data_quality_flag",
]


def main() -> None:
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(f"Missing file: {PROCESSED_PATH}")

    df = pd.read_csv(PROCESSED_PATH)

    print("=" * 80)
    print("Operational Risk Feature Validation")
    print("=" * 80)

    print(f"\nRows: {len(df)}")
    if len(df) == EXPECTED_COUNTIES:
        print("[OK] County row count is 95.")
    else:
        print(f"[WARN] Expected 95 counties, found {len(df)}.")

    if "county" in df.columns:
        duplicate_counties = df[df["county"].duplicated()]["county"].tolist()
        if duplicate_counties:
            print(f"[WARN] Duplicate counties found: {duplicate_counties}")
        else:
            print("[OK] No duplicate counties.")

        special = ["DeKalb", "McMinn", "McNairy"]
        missing_special = [c for c in special if c not in set(df["county"])]
        if missing_special:
            print(f"[WARN] Special-case county names missing: {missing_special}")
        else:
            print("[OK] DeKalb, McMinn, and McNairy are present.")

    print("\nField coverage:")
    for col in CORE_FIELDS:
        if col not in df.columns:
            print(f"[MISSING] {col}")
        else:
            non_null = df[col].notna().sum()
            pct = non_null / len(df) * 100
            print(f"[OK] {col}: {non_null}/{len(df)} populated ({pct:.1f}%)")

    if "data_quality_flag" in df.columns:
        print("\nData quality distribution:")
        print(df["data_quality_flag"].value_counts(dropna=False).to_string())

    if "final_operational_risk_score" in df.columns:
        print("\nTop 10 counties by operational risk:")
        print(
            df.sort_values("final_operational_risk_score", ascending=False)[
                ["county", "final_operational_risk_score", "operational_risk_tier", "data_quality_flag"]
            ]
            .head(10)
            .to_string(index=False)
        )

        print("\nBottom 10 counties by operational risk:")
        print(
            df.sort_values("final_operational_risk_score", ascending=True)[
                ["county", "final_operational_risk_score", "operational_risk_tier", "data_quality_flag"]
            ]
            .head(10)
            .to_string(index=False)
        )

    print("\nValidation complete.")


if __name__ == "__main__":
    main()