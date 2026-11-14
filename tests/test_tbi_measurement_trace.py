"""Synthetic tests for retained-export lineage diagnostics; no real input fixtures."""
import pandas as pd
import pytest
from research.tbi_measurement_trace.trace import matrix, all_clearances, compare_cells, legacy_sum, number


def sample():
    return [['Measures','Number of Crimes','','Number of Offenses'],
            ['Incident Date','2024','','2024'],
            ['Offense Type','Murder','Arson','Murder'],
            ['Type of Weapon/Force Involved','Explosives','Other','Explosives'],
            ['Jurisdiction by Geography'],['Synthetic A','2','','99'],['Synthetic B','','0','88']]


def test_matrix_selects_crime_block_and_explicit_weapon_only():
    result=matrix(sample(),explosives=True)
    assert list(result.cells)==['Murder']
    assert result.cells.loc['Synthetic A','Murder']=='2'
    assert result.cells.loc['Synthetic B','Murder']==''
    assert result.columns[0]['source_column_1based']==2
    assert result.headers['Incident Date'][0]==2


def test_blank_is_not_observed_zero_but_legacy_arithmetic_is_reproduced():
    assert number('') is None
    assert number('0')==0
    assert number('1,234')==1234
    with pytest.raises(ValueError): number('suppressed')
    with pytest.raises(ValueError): number('NaN')
    cells=matrix(sample()).cells
    assert legacy_sum(cells,list(cells)).tolist()==[2,0]
    assert cells.loc['Synthetic B','Murder']==''


def test_comparison_distinguishes_text_numeric_and_blank_matches():
    left=pd.DataFrame({'x':['1,000','','0']},index=['A','B','C'])
    right=pd.DataFrame({'x':['1000','0','0']},index=['A','B','C'])
    result=compare_cells(left,right)
    assert result['exact_text_matches']==1
    assert result['numeric_or_blank_mismatches']==1
    assert result['both_explicit_zero']==1
    assert result['both_blank']==0


def test_comparison_aligns_counties_and_rejects_support_mismatch():
    left=pd.DataFrame({'x':['2','3']},index=['A','B'])
    assert compare_cells(left,left.iloc[::-1])['exact_text_matches']==2
    with pytest.raises(ValueError,match='support'): compare_cells(left,left.iloc[:1])
    with pytest.raises(ValueError,match='support'): compare_cells(left,left.rename(columns={'x':'y'}))


def test_duplicate_county_or_offense_fails():
    rows=sample(); rows.append(['Synthetic A','1','','2'])
    with pytest.raises(ValueError,match='county'): matrix(rows)
    rows=sample(); rows[2][2]='Murder'
    with pytest.raises(ValueError,match='offenses'): matrix(rows)


def test_all_clearances_excludes_cleared_block_and_rate_measures():
    rows=[['Incident Clearance','All Clearances','','Cleared'],
          ['Jurisdiction by Geography','Synthetic A','','Synthetic A'],
          ['Measures','Number of Crimes','Crime Rate','Number of Crimes'],
          ['Offense Type'],['Murder','7','900','3'],['Arson','','200','2']]
    result=all_clearances(rows)
    assert result.loc['Synthetic A'].to_dict()=={'Murder':'7','Arson':''}
