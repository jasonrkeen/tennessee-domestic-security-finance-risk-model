"""Frozen synthetic baseline from master before PR #2, independent of new logic."""

import json
from pathlib import Path

import pandas as pd
import pytest

from src import data_quality, risk_scoring, sensitivity_analysis


FIXTURE = json.loads((Path(__file__).parent / "fixtures/scoring_base.json").read_text())


def frame(snapshot: dict) -> pd.DataFrame:
    return pd.DataFrame(snapshot["data"], columns=snapshot["columns"])


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["name"])
def test_base_score_scenario_and_output_parity(case, monkeypatch, tmp_path):
    for module in (risk_scoring, data_quality, sensitivity_analysis):
        monkeypatch.setattr(module, "TABLES_DIR", tmp_path)
    source = frame(case["input"])
    scores = risk_scoring.build_scores(source)
    expected = frame(case["scores"])
    pd.testing.assert_frame_equal(
        scores[expected.columns].reset_index(drop=True), expected,
        check_dtype=False, rtol=1e-12, atol=1e-12,
    )
    scenarios = sensitivity_analysis.build_sensitivity_results(scores)
    expected_scenarios = frame(case["scenarios"])
    pd.testing.assert_frame_equal(
        scenarios[expected_scenarios.columns].reset_index(drop=True), expected_scenarios,
        check_dtype=False, rtol=1e-12, atol=1e-12,
    )
    ranks = sensitivity_analysis.build_rank_stability_table(scenarios)
    pd.testing.assert_frame_equal(
        ranks.reset_index(drop=True), frame(case["ranks"]),
        check_dtype=False, rtol=1e-12, atol=1e-12,
    )
    # Verify emitted score tables too, while excluding intentionally changed
    # availability/confidence diagnostics. All writes are temporary.
    tables = list(tmp_path.glob("tn_county_*scores.csv"))
    assert len(tables) == 9
    for path in tables:
        actual = pd.read_csv(path)
        shared = [column for column in actual if column in expected.columns]
        pd.testing.assert_frame_equal(
            actual[shared], expected[shared],
            check_dtype=False, rtol=1e-12, atol=1e-12,
        )
