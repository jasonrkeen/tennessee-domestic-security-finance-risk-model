"""Independent path arithmetic and reconciliation against frozen observations."""
import json
from fractions import Fraction
from pathlib import Path

import pandas as pd
import pytest

from research.effective_weights.audit import (
    Graph, Leaf, active_mask, build_graph, node_weights, validate_saved,
    verify_sources, weights,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "research/effective_weights/config.json").read_text())
FIXTURE = json.loads((ROOT / "tests/fixtures/scoring_base.json").read_text())


def frame(snapshot):
    return pd.DataFrame(snapshot["data"], columns=snapshot["columns"])


def test_shared_leaf_paths_sum_without_counting_intermediate_nodes_twice():
    graph = Graph({"root": {"branch": Fraction(1, 2), "x": Fraction(1, 2)},
                   "branch": {"x": Fraction(1, 4), "y": Fraction(3, 4)}},
                  {name: Leaf(name, "test", 0, name) for name in ("x", "y")}, {})
    assert weights(graph, "root") == {"x": Fraction(5, 8), "y": Fraction(3, 8)}
    assert len(graph.paths("root")) == 3


def test_hand_calculated_baseline_and_conditional_weights():
    graph, _ = build_graph(ROOT, CONFIG, "fema_fallback")
    nodes = node_weights(graph, CONFIG["final_score"])
    assert nodes["household_financial_stress_score"] == Fraction("0.222")
    assert nodes["tactical_access_score"] == Fraction("0.11")
    assert nodes["disaster_disruption_vulnerability_score"] == Fraction("0.129")
    leaves = weights(graph, CONFIG["final_score"])
    assert leaves["poverty_score"] == Fraction("0.0921")
    assert leaves["recent_disaster_score"] == Fraction("0.03225")
    assert "severe_weather_exposure_score" not in leaves
    active, scenarios = build_graph(ROOT, CONFIG, "phase6_active")
    active_leaves = weights(active, CONFIG["final_score"])
    assert active_leaves["recent_disaster_score"] == Fraction("0.0274125")
    assert active_leaves["severe_weather_exposure_score"] == Fraction("0.0258")
    for regime_graph in (graph, active):
        for name in scenarios:
            assert sum(weights(regime_graph, f"scenario::{name}").values()) == 1


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda c: c["name"])
def test_reconstructs_frozen_scores_and_ten_scenarios(case):
    scores = frame(case["scores"])
    before = scores.copy(deep=True)
    result = validate_saved(scores, frame(case["scenarios"]), ROOT, CONFIG)
    assert result["passed"]
    pd.testing.assert_frame_equal(scores, before)


def test_mixed_regimes_reconcile_against_scorer_in_temporary_directory(monkeypatch, tmp_path):
    from src import risk_scoring, data_quality, sensitivity_analysis
    for module in (risk_scoring, data_quality, sensitivity_analysis):
        monkeypatch.setattr(module, "TABLES_DIR", tmp_path)
    # Combine fixture inputs before normalization so both branch types coexist.
    left = frame(FIXTURE["cases"][0]["input"]).iloc[:2].copy()
    right = frame(FIXTURE["cases"][1]["input"]).iloc[:2].copy()
    left["county"] = ["Fallback A", "Fallback B"]
    right["county"] = ["Active A", "Active B"]
    scores = risk_scoring.build_scores(pd.concat([left, right], ignore_index=True))
    scenarios = sensitivity_analysis.build_sensitivity_results(scores)
    result = validate_saved(scores, scenarios, ROOT, CONFIG)
    assert result["regimes"] == {"phase6_active": 2, "fema_fallback": 2}


def test_source_drift_fails_closed():
    config = {**CONFIG, "source_sha256_lf": {"src/risk_scoring.py": "wrong"}}
    with pytest.raises(ValueError, match="Pinned source changed"):
        verify_sources(ROOT, config)


def test_signal_uses_group_sum_not_any_positive_field():
    scores = frame(FIXTURE["cases"][0]["scores"])
    scores.loc[0, "severe_storm_event_count"] = 1
    scores.loc[0, "flood_event_count"] = -1
    assert not active_mask(scores, ROOT, CONFIG).iloc[0]
