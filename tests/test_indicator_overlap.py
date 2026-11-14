"""Ablation arithmetic, ties and unknown correlation behavior on synthetic data."""
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from research.indicator_overlap.analyze import (
    Study, analyze, correlations, load_study, pair_table, ranks, remove_family, top_set,
)


def test_correlation_distinguishes_order_from_scale_and_constant():
    x = pd.Series([0., 1., 2., 3.])
    pearson, spearman = correlations(x, x**2)
    assert .95 < pearson < 1
    assert spearman == pytest.approx(1)
    assert correlations(x, -x) == pytest.approx((-1, -1))
    assert correlations(x, pd.Series([50.] * 4)) == (None, None)
    with pytest.raises(ValueError, match="nonfinite"):
        correlations(x, pd.Series([0., 1., 2., np.nan]))
    with pytest.raises(ValueError, match="indices"):
        correlations(x, pd.Series([0., 1., 2., 3.], index=[1, 2, 3, 4]))


def test_sparse_exact_equality_does_not_imply_many_informative_observations():
    data = pd.DataFrame({"a": [100.] + [0.] * 94, "b": [100.] + [0.] * 94, "c": [50.] * 95})
    pairs = pair_table(data)
    pair = pairs.iloc[0]
    assert pair.exact_values_equal and pair.joint_normalized_zero_rows == 94
    assert pair.spearman == pytest.approx(1)
    assert pairs.iloc[1].status == "constant_indicator"
    assert pd.isna(pairs.iloc[1].spearman)


def test_all_paths_removed_using_flattened_weight_and_one_denominator():
    # x has 0.2 direct and 0.3 indirect weight in the already expanded formula.
    values = pd.DataFrame({"x": [20., 80.], "y": [100., 0.], "z": [0., 100.]})
    coefficients = pd.Series({"x": .5, "y": .3, "z": .2})
    candidate, retained, removed, weight = remove_family(values, coefficients, ["x"])
    np.testing.assert_allclose(candidate, [60., 40.])
    np.testing.assert_allclose(retained, [30., 20.])
    np.testing.assert_allclose(removed, [10., 40.])
    assert weight == .5
    np.testing.assert_allclose(retained + removed, values.mul(coefficients).sum(axis=1))
    pd.testing.assert_frame_equal(values, pd.DataFrame({"x": [20., 80.], "y": [100., 0.], "z": [0., 100.]}))


def test_removing_constant_family_preserves_order():
    values = pd.DataFrame({"fixed": [50.] * 4, "variable": [20., 80., 60., 40.]})
    coefficients = pd.Series({"fixed": .25, "variable": .75})
    baseline = values.mul(coefficients).sum(axis=1)
    candidate, _, _, _ = remove_family(values, coefficients, ["fixed"])
    pd.testing.assert_series_equal(ranks(candidate, 10), ranks(baseline, 10))
    np.testing.assert_allclose(candidate, values.variable)


def test_top_k_includes_boundary_ties_and_rounding_is_explicit():
    scores = pd.Series([10., 9., 9. + 1e-12, 8.])
    counties = pd.Series(["A", "B", "C", "D"])
    assert top_set(scores, counties, 2, 10) == {"A", "B", "C"}
    assert ranks(scores, 10).tolist() == [1., 2.5, 2.5, 4.]


def test_degenerate_or_duplicate_family_is_rejected():
    values = pd.DataFrame({"x": [0., 100.]})
    coefficients = pd.Series({"x": 1.})
    with pytest.raises(ValueError, match="retained"):
        remove_family(values, coefficients, ["x"])
    with pytest.raises(ValueError, match="membership"):
        remove_family(values, coefficients, ["x", "x"])


def test_partition_results_reconcile_and_do_not_mutate_baseline():
    values = pd.DataFrame({"x": [0., 100., 50., 25.], "y": [100., 0., 50., 25.], "z": [50.] * 4})
    coefficients = pd.Series({"x": .4, "y": .4, "z": .2})
    study = Study(pd.Series(["A", "B", "C", "D"]), values.mul(coefficients).sum(axis=1), values, coefficients)
    before = study.baseline.copy()
    config = {"partitions": ["source_family", "component_family"], "rank_round_decimals": 10,
              "top_k": 2, "large_rank_change_threshold": 10, "rtol": 1e-12, "atol": 1e-12,
              "indicator_families": {name: {"source_family": "one" if name == "x" else "two", "component_family": name} for name in values}}
    output = analyze(study, config)
    assert len(output["ablation_summary"]) == 5
    assert len(output["county_ablation"]) == 20
    for partition in config["partitions"]:
        assert output["family_profiles"].query("partition == @partition").weight_percent.sum() == pytest.approx(100)
    pd.testing.assert_series_equal(study.baseline, before)
    with pytest.raises(AssertionError):
        analyze(replace(study, baseline=study.baseline + 1), config)


def test_input_version_mismatch_fails_before_analysis(tmp_path):
    source = tmp_path / "different.csv"
    source.write_text("county,score\nSynthetic,1\n")
    config = json.loads((Path(__file__).resolve().parents[1] / "research/indicator_overlap/config.json").read_text())
    with pytest.raises(ValueError, match="pinned"):
        load_study(source, config)
