"""Read-only lineage checks on hash-pinned, retained county aggregates."""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_name('config.json')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(value: str) -> str:
    return re.sub('[^a-z0-9]', '', value.lower())


def number(text: str) -> float | None:
    """Keep blank distinct from zero; fail on unexpected tokens."""
    if not text.strip():
        return None
    value = float(text.replace(',', ''))
    if not np.isfinite(value):
        raise ValueError('Nonfinite source cell')
    return value


@dataclass(frozen=True)
class Matrix:
    headers: dict[str, tuple[int, list[str]]]
    cells: pd.DataFrame
    columns: list[dict]


def read_rows(path: Path) -> list[list[str]]:
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.reader(stream))


def matrix(rows: list[list[str]], explosives: bool = False) -> Matrix:
    end = next(i for i, r in enumerate(rows) if r and r[0] == 'Jurisdiction by Geography')
    headers = {r[0]: (i + 1, r) for i, r in enumerate(rows[:end+1]) if r and r[0]}
    measures = headers['Measures'][1]
    offenses = headers['Offense Type'][1]
    weapons = headers.get('Type of Weapon/Force Involved', (0, []))[1]
    measure, selected = '', []
    for col in range(1, len(offenses)):
        if col < len(measures) and measures[col].strip():
            measure = measures[col].strip()
        if measure != 'Number of Crimes' or not offenses[col].strip():
            continue
        if explosives and (col >= len(weapons) or weapons[col].strip() != 'Explosives'):
            continue
        selected.append({'source_column_1based': col+1, 'offense': offenses[col].strip(),
                         'measure': measure, 'weapon': weapons[col] if col < len(weapons) else ''})
    if not selected or len({x['offense'] for x in selected}) != len(selected):
        raise ValueError('Empty or duplicate selected offenses')
    records, counties = [], []
    for row in rows[end+1:]:
        if not row or not row[0].strip():
            continue
        counties.append(row[0].strip())
        records.append([row[x['source_column_1based']-1].strip() if len(row) >= x['source_column_1based'] else '' for x in selected])
    if len(set(counties)) != len(counties):
        raise ValueError('Duplicate county')
    return Matrix(headers, pd.DataFrame(records, index=counties, columns=[x['offense'] for x in selected]).sort_index(), selected)


def all_clearances(rows: list[list[str]]) -> pd.DataFrame:
    header = {r[0]: (i, r) for i, r in enumerate(rows) if r and r[0]}
    clearance = header['Incident Clearance'][1]
    end = next(i for i, value in enumerate(clearance) if value == 'Cleared')
    counties = header['Jurisdiction by Geography'][1]
    measures = header['Measures'][1]
    selected = [i for i in range(1, end) if measures[i] == 'Number of Crimes']
    records = {row[0]: [row[i].strip() if i < len(row) else '' for i in selected]
               for row in rows[header['Offense Type'][0]+1:] if row and row[0]}
    result = pd.DataFrame(records, index=[counties[i] for i in selected]).sort_index()
    if result.index.has_duplicates:
        raise ValueError('Duplicate county')
    return result


def compare_cells(left: pd.DataFrame, right: pd.DataFrame) -> dict:
    if set(left.index) != set(right.index) or set(left.columns) != set(right.columns):
        raise ValueError('County/offense support mismatch')
    right = right.reindex(index=left.index, columns=left.columns)
    a, b = left.to_numpy().ravel(), right.to_numpy().ravel()
    both_blank = sum(not x.strip() and not y.strip() for x, y in zip(a, b))
    mismatch = sum(number(x) != number(y) for x, y in zip(a, b))
    return {'counties': len(left), 'offenses': len(left.columns), 'cells': len(a),
            'exact_text_matches': int((a == b).sum()), 'both_blank': both_blank,
            'both_explicit_zero': sum(number(x) == 0 and number(y) == 0 for x,y in zip(a,b)),
            'numeric_or_blank_mismatches': mismatch}


def legacy_sum(cells: pd.DataFrame, offenses: list[str]) -> pd.Series:
    # Reconstruct historical blank-to-zero arithmetic; evidence retains blanks separately.
    return cells[offenses].map(lambda x: 0.0 if number(x) is None else number(x)).sum(axis=1)


def load_table(path: Path) -> pd.DataFrame:
    table = pd.read_csv(path).set_index('county').sort_index()
    if table.index.has_duplicates or len(table) != 95:
        raise ValueError('Expected 95 distinct counties')
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frozen-root', required=True, type=Path)
    parser.add_argument('--snapshot-manifest', required=True, type=Path)
    parser.add_argument('--saved-scores', required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    if digest(args.snapshot_manifest) != config['snapshot_manifest_sha256']:
        raise ValueError('Snapshot manifest changed')
    manifest = json.loads(args.snapshot_manifest.read_text())
    historical = {r['path']: r['sha256'] for r in manifest['files']}
    protected = {args.frozen_root / n: sha for n, sha in config['retained_files'].items()}
    protected[args.saved_scores] = config['scores_sha256']
    protected[args.snapshot_manifest] = config['snapshot_manifest_sha256']
    for path, sha in protected.items():
        if digest(path) != sha:
            raise ValueError(f'Pinned input mismatch: {path.name}')
    for name, sha in config['retained_files'].items():
        if historical.get(name) != sha:
            raise ValueError(f'Historical custody mismatch: {name}')
    for name, sha in config['code_sha256_lf'].items():
        if hashlib.sha256((ROOT/name).read_text(encoding='utf-8').encode()).hexdigest() != sha:
            raise ValueError(f'Code changed: {name}')
    raw = args.frozen_root/'data/raw'
    matrices = {n: matrix(read_rows(raw/f'tn_{n}_activity_raw_2024.csv'), n != 'gang') for n in ['explosives', 'gang_explosives', 'gang']}
    broad = all_clearances(read_rows(raw/'crimes_clearances_by_offense_type_2024.csv'))
    comparisons = [dict(pair='explosives_vs_gang_explosives', **compare_cells(matrices['explosives'].cells, matrices['gang_explosives'].cells)),
                   dict(pair='gang_vs_all_clearances', **compare_cells(matrices['gang'].cells.reindex(columns=broad.columns), broad))]
    # Explicitly compare common offense support; do not silently treat an absent column as zero.
    if set(matrices['gang'].cells.columns) - set(broad.columns) != {'Justifiable Homicide'} or set(broad.columns) - set(matrices['gang'].cells.columns):
        raise ValueError('Unexpected common-offense support')
    differences = []
    for county in broad.index:
        for offense in broad.columns:
            left, right = matrices['gang'].cells.loc[county, offense], broad.loc[county, offense]
            if number(left) != number(right):
                differences.append({'county':county,'offense':offense,'gang_export_cell':left,'earlier_all_clearances_cell':right})
    headers, selections, blanks, mappings = [], [], [], []
    for name, mat in matrices.items():
        for label in ['Measures','Incident Date','Gang Activity','Type of Weapon/Force Involved']:
            line, row = mat.headers.get(label, (None, []))
            headers.append({'export': name, 'header': label, 'row_1based': line,
                            'present': bool(row), 'distinct_nonblank_values': ' | '.join(dict.fromkeys(v for v in row[1:] if v))})
        mapping = pd.read_csv(args.frozen_root/f'outputs/tables/tn_{name}_activity_mapping_validation.csv')
        if set(mapping.source_offense_label) != set(mat.cells) or len(mapping) != len(mat.cells.columns):
            raise ValueError('Saved mapping differs from selected offenses')
        mappings.append({'export':name,'selected_offenses':len(mat.columns),'saved_mapping_rows':len(mapping),
                         'offense_labels_match':True,'gang_activity_filter': ' | '.join(mapping.gang_activity_filter.unique()) if 'gang_activity_filter' in mapping else '',
                         'weapon_force_filter':' | '.join(mapping.weapon_force_filter.unique()) if 'weapon_force_filter' in mapping else '',
                         'caution':'Mapping filter labels are code literals, not independent filter validation'})
        for item in mat.columns:
            selections.append({'export':name, **item})
        for county, row in mat.cells.iterrows():
            values = [number(v) for v in row]
            blanks.append({'export': name, 'county':county, 'selected_cells':len(values),
                           'blank_cells':sum(v is None for v in values), 'explicit_zero_cells':sum(v == 0 for v in values),
                           'nonzero_cells':sum(v is not None and v != 0 for v in values)})
    saved = load_table(args.saved_scores)
    reconciliation = []
    def check(label: str, a: pd.Series, b: pd.Series) -> None:
        if set(a.index) != set(b.index):
            raise ValueError('County support mismatch')
        b = b.reindex(a.index)
        close = np.isclose(a, b, rtol=config['rtol'], atol=config['atol'])
        reconciliation.append({'check':label, 'counties':len(a), 'matching_counties':int(close.sum()), 'max_absolute_difference':float(np.max(np.abs(a-b)))})
        if not close.all():
            raise ValueError(f'Lineage comparison failed: {label}')
    for name, mat in matrices.items():
        code = ROOT/f'src/{name}_processor.py' if name != 'gang' else ROOT/'src/gang_activity_processor.py'
        # Only read literal offense sets from the production file; never invoke processors.
        constants = {node.targets[0].id: ast.literal_eval(node.value) for node in ast.parse(code.read_text()).body
                     if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Set)}
        prefix = {'explosives':'explosive_related', 'gang_explosives':'gang_explosive','gang':'gang_related'}[name]
        total = 'total_crime_count' if name == 'gang' else 'total_offense_count'
        violent = 'violent_crime_count' if name == 'gang' else 'violent_offense_count'
        groups = {total:list(mat.cells), violent:[v for v in mat.cells if key(v) in constants['VIOLENT_OFFENSES']],
                  'weapon_law_violation_count':[v for v in mat.cells if key(v) == 'weaponlawviolations']}
        if name != 'gang':
            groups.update({suffix:[v for v in mat.cells if key(v)==offense] for suffix, offense in
                           [('homicide_count','murder'),('arson_count','arson'),('property_damage_count','destructiondamagevandalism')]})
        prepared = load_table(raw/f'tn_{name}_activity_inputs.csv')
        for suffix, offenses in groups.items():
            field = f'{prefix}_{suffix}'
            reconstructed = legacy_sum(mat.cells, offenses)
            check(f'{name}: export -> prepared {field}', reconstructed, prepared[field])
            check(f'{name}: prepared -> released {field}', prepared[field], saved[field])
    check('gang offense sum -> retained overall crime count', legacy_sum(matrices['gang'].cells,list(matrices['gang'].cells)), load_table(raw/'tn_crime_rate_inputs.csv')['overall_crime_count_2024'])
    check('retained overall count -> released overall count', load_table(raw/'tn_crime_rate_inputs.csv')['overall_crime_count_2024'], saved['overall_crime_count_2024'])
    for suffix in ['total_offense_count','violent_offense_count','weapon_law_violation_count','homicide_count','arson_count','property_damage_count']:
        check(f'explosive vs gang-explosive released {suffix}', saved[f'explosive_related_{suffix}'],saved[f'gang_explosive_{suffix}'])
    for prefix in ['explosive_related', 'gang_explosive']:
        for count_suffix, score_suffix in [('total_offense_count','total'),('violent_offense_count','violent'),('weapon_law_violation_count','weapon_law'),('homicide_count','homicide'),('arson_count','arson'),('property_damage_count','property_damage')]:
            rate = saved[f'{prefix}_{count_suffix}'] / saved['population'] * 10000
            score = pd.Series(50.,index=rate.index) if rate.max() == rate.min() else 100*(rate-rate.min())/(rate.max()-rate.min())
            check(f'{prefix}: count/population -> normalized {score_suffix}',score,saved[f'{prefix}_{score_suffix}_pressure_score'])
    for field, target in [('gang_related_total_crime_count','gang_related_total_pressure_score'),('overall_crime_count_2024','overall_crime_count_pressure_score')]:
        rate=saved[field]/saved['population']*10000
        score=100*(rate-rate.min())/(rate.max()-rate.min())
        check(f'{field}: count/population -> normalized score',score,saved[target])
    check('gang normalized total -> overall normalized count',saved['gang_related_total_pressure_score'],saved['overall_crime_count_pressure_score'])
    check('explosive composite -> gang-explosive composite',saved['explosive_related_pressure_score'],saved['gang_explosive_pressure_score'])
    output=ROOT/config['output_dir']
    output.mkdir(parents=True, exist_ok=True)
    for name, records in [('mapping_checks',mappings),('common_offense_differences',differences),('header_evidence',headers),('selected_columns',selections),('cell_comparisons',comparisons),('blank_diagnostics',blanks),('lineage_checks',reconciliation)]:
        pd.DataFrame(records).to_csv(output/f'{name}.csv',index=False,float_format='%.12g')
    for path, sha in protected.items():
        if digest(path) != sha:
            raise ValueError('Input changed during analysis')
    result={'scope':'Retained local evidence; no new acquisition or source certification', 'base_commit':config['base_commit'],
            'snapshot_captured_utc':manifest['captured_utc'],'retained_files_verified':len(config['retained_files']),
            'historical_manifest_matches':True,'inputs_unchanged':True,'lineage_checks':len(reconciliation),
            'all_lineage_checks_passed':True,'gang_only_offense':'Justifiable Homicide','gang_only_offense_blank_count':int((matrices['gang'].cells['Justifiable Homicide']=='').sum()),'config_sha256_lf':hashlib.sha256(CONFIG.read_text().encode()).hexdigest(),
            'analysis_sha256_lf':hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
            'results_sha256':{p.name:digest(p) for p in sorted(output.glob('*.csv'))}}
    (output/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'comparisons':comparisons, 'verification':result},indent=2))


if __name__ == '__main__':
    main()
