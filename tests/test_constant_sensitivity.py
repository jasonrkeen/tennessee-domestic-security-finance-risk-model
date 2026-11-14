"""Synthetic arithmetic, membership and tie checks for the protocol runner."""
import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from research.constant_sensitivity.run import evaluate, validate_sets
from research.indicator_overlap.analyze import Study, top_set


def test_hand_calculated_constant_exclusion_and_family_context():
    values = pd.DataFrame({'c': [50., 50.], 'x': [0., 100.], 'y': [100., 0.]})
    coefficients = pd.Series({'c': .2, 'x': .3, 'y': .5})
    study = Study(pd.Series(['A', 'B']), pd.Series([60., 40.]), values, coefficients)
    config = dict(rank_round_decimals=10, top_k=1, largest_movement_k=1,
                  rtol=1e-12, atol=1e-12, variant_order=['C1', 'D1'])
    result = evaluate(study, {'C1': ['c'], 'D1': ['y']},
                      {x: {'source_family': x} for x in values}, config)
    c = result['county_variants'].query("variant == 'C1'")
    np.testing.assert_allclose(c.unscaled_retained_score, [50, 30])
    np.testing.assert_allclose(c.research_score, [62.5, 37.5])
    assert c.rank_change_positive_is_down.eq(0).all()
    d = result['county_variants'].query("variant == 'D1'")
    np.testing.assert_allclose(d.research_score, [20, 80])
    contexts = result['largest_movement_context']
    np.testing.assert_allclose(contexts.groupby('county').contribution_change.sum().sort_index(), [-40, 40])


def test_boundary_ties_are_all_included_after_rounding():
    assert top_set(pd.Series([90., 80., 80.+1e-12, 70.]),
                   pd.Series(['A', 'B', 'C', 'D']), 2, 10) == {'A', 'B', 'C'}


def protocol_fixture():
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root/'research/missingness_constants/config.json').read_text())
    sets = copy.deepcopy(config['sensitivity_exclusion_sets'])
    names = set(sets['CD'])
    names.update(x.replace('gang_explosive_', 'explosive_related_') for x in sets['D1'] if x.startswith('gang_explosive_'))
    names.add('overall_crime_count_pressure_score')
    values = pd.DataFrame({n: [50., 50.] if n in sets['C4'] else [0., 100.] for n in names})
    return sets, values


def test_combined_union_counts_overlap_only_once():
    sets, values = protocol_fixture()
    assert len(validate_sets(sets, values)) == 7
    assert len(sets['CD']) == 18
    assert len(set(sets['C4']) & set(sets['D1'])) == 3


@pytest.mark.parametrize('fault', ['duplicate', 'union', 'equality', 'nonconstant', 'unknown'])
def test_protocol_checks_reject_drift(fault):
    sets, values = protocol_fixture()
    if fault == 'duplicate':
        sets['CD'].append(sets['CD'][0])
    elif fault == 'union':
        sets['CD'].pop()
    elif fault == 'equality':
        values.loc[0, 'overall_crime_count_pressure_score'] = 1
    elif fault == 'nonconstant':
        values.loc[0, sets['C1'][0]] = 2
    else:
        sets['C1'][0] = 'unknown'
    with pytest.raises(ValueError):
        validate_sets(sets, values)
