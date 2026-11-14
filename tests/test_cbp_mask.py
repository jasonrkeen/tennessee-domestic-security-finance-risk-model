"""Synthetic evidence tests: omission is not a numeric zero or a failed query."""
import copy

import pytest

from research.cbp_validation.verify_mask import build_mask, parse_response


def fixture():
    return [['NAME','ESTAB','NAICS2017','LFO','EMPSZES','state','county'],
            ['Alpha County, Tennessee','3','123456','001','001','47','001']]


def test_published_threshold_and_omitted_county_remain_distinct():
    roster = {'47001':'Alpha','47003':'Beta'}
    observed = parse_response(fixture(), '123456', roster)
    mask = build_mask(roster, {'123456':'example'}, {'123456':observed})
    assert observed == {'47001':3}
    assert mask.status.tolist() == ['published','unpublished_bounded_0_2']
    assert mask.lower_bound.tolist() == ['',0]
    assert mask.upper_bound.tolist() == ['',2]
    assert '47003' not in observed


@pytest.mark.parametrize('fault', ['duplicate','filter','state','name','noninteger','threshold','empty','ragged'])
def test_reject_invalid_or_incomplete_response(fault):
    rows = copy.deepcopy(fixture())
    if fault == 'duplicate': rows.append(rows[1].copy())
    elif fault == 'filter': rows[1][3] = '002'
    elif fault == 'state': rows[1][5] = '48'
    elif fault == 'name': rows[1][0] = 'Beta County, Tennessee'
    elif fault == 'noninteger': rows[1][1] = 'D'
    elif fault == 'threshold': rows[1][1] = '2'
    elif fault == 'empty': rows.pop()
    else: rows[1].pop()
    with pytest.raises(ValueError):
        parse_response(rows,'123456',{'47001':'Alpha'})


def test_missing_category_cannot_be_promoted_to_unpublished():
    with pytest.raises(ValueError, match='Missing category'):
        build_mask({'47001':'Alpha'}, {'123456':'example'}, {})
