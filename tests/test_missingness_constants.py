"""Synthetic checks for preserving source-cell evidence in the research audit."""
import pytest

from research.missingness_constants.audit import ambush_cells, checked_table, profile


def test_profile_preserves_blanks_invalids_and_numeric_zeros():
    result = profile(['', '  ', '0', '0.0', 'NaN', 'inf', 'bad', '1,234', '-2'])
    assert (result.cells, result.blank, result.invalid, result.explicit_zero,
            result.positive, result.negative) == (9, 2, 3, 2, 1, 1)


def test_zero_filled_prepared_values_do_not_recover_raw_evidence():
    blank_source = profile(['', ''])
    zero_source = profile(['0', '0'])
    assert blank_source.explicit_zero == 0
    assert zero_source.explicit_zero == 2
    assert blank_source != zero_source


def test_table_rejects_duplicate_counties_and_preserves_empty_cells(tmp_path):
    path = tmp_path / 'input.csv'
    path.write_text('county,value\nA,\nB,0\n')
    df = checked_table(path, {'A', 'B'})
    assert df.loc['A', 'value'] == ''
    assert df.loc['B', 'value'] == '0'
    path.write_text('county,value\nA,1\nA,2\n')
    with pytest.raises(ValueError, match='County support'):
        checked_table(path, {'A', 'B'})


def ambush_fixture():
    return [['Offense Committed', 'Weapon Law Violations', 'Other'],
            ['Officer Ambushed', 'Officer Was Ambushed', 'Officer Was Ambushed'],
            ['Jurisdiction by Geography'], ['A', '', '2'], ['B', '0', '']]


def test_ambush_parser_keeps_blanks_and_explicit_zero_distinct():
    cells = ambush_cells(ambush_fixture(), {'A', 'B'})
    assert profile(cells['Weapon Law Violations'].tolist()).blank == 1
    assert profile(cells['Weapon Law Violations'].tolist()).explicit_zero == 1


@pytest.mark.parametrize('fault', ['filter', 'duplicate', 'missing_county'])
def test_ambush_parser_fails_on_changed_filter_or_support(fault):
    rows = ambush_fixture()
    if fault == 'filter':
        rows[1][1] = 'All Officers'
    elif fault == 'duplicate':
        rows.append(['A', '0', '0'])
    else:
        rows.pop()
    with pytest.raises(ValueError):
        ambush_cells(rows, {'A', 'B'})
