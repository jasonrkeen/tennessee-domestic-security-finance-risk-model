"""Read-only, hash-pinned missingness audit; never calculate candidate scores."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass, asdict
from fractions import Fraction
from pathlib import Path

import pandas as pd

from research.tbi_measurement_trace.trace import matrix, read_rows

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class CellProfile:
    cells: int
    blank: int
    invalid: int
    explicit_zero: int
    positive: int
    negative: int


def profile(values: list[str]) -> CellProfile:
    """Keep blank, invalid and numeric zero distinct; do not impute."""
    counts = dict(blank=0, invalid=0, explicit_zero=0, positive=0, negative=0)
    for value in values:
        text = str(value).strip()
        if not text:
            counts['blank'] += 1
            continue
        try:
            number = float(text.replace(',', ''))
        except ValueError:
            counts['invalid'] += 1
            continue
        if not math.isfinite(number):
            counts['invalid'] += 1
        else:
            counts['explicit_zero' if number == 0 else 'positive' if number > 0 else 'negative'] += 1
    return CellProfile(len(values), **counts)


def sha(path: Path, lf: bool = False) -> str:
    data = path.read_text(encoding='utf-8').encode() if lf else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def checked_table(path: Path, counties: set[str]) -> pd.DataFrame:
    table = pd.read_csv(path, dtype=str, keep_default_na=False)
    if 'county' not in table or table.county.duplicated().any() or set(table.county) != counties:
        raise ValueError(f'County support mismatch: {path.name}')
    return table.set_index('county').sort_index()


def ambush_cells(rows: list[list[str]], counties: set[str]) -> pd.DataFrame:
    """Select the explicit ambushed-officer columns, retaining blank strings."""
    headers = {r[0]: (i, r) for i, r in enumerate(rows) if r and r[0]}
    labels = headers['Offense Committed'][1]
    filters = headers['Officer Ambushed'][1]
    selected = [i for i in range(1, len(labels)) if labels[i].strip()]
    if any(i >= len(filters) or filters[i] != 'Officer Was Ambushed' for i in selected):
        raise ValueError('Unexpected ambush filter')
    records = {}
    for row in rows[headers['Jurisdiction by Geography'][0] + 1:]:
        if not row or not row[0].strip():
            continue
        if row[0] in records:
            raise ValueError('Duplicate county')
        records[row[0]] = [row[i].strip() if i < len(row) else '' for i in selected]
    if set(records) != counties or len(set(labels[i] for i in selected)) != len(selected):
        raise ValueError('Ambush support mismatch')
    return pd.DataFrame.from_dict(records, orient='index', columns=[labels[i] for i in selected]).sort_index()


def run(frozen: Path, scores_path: Path) -> dict:
    config = json.loads((HERE / 'config.json').read_text())
    protected = {frozen / name: value for name, value in config['retained_sha256'].items()}
    protected[scores_path] = config['scores_sha256']
    for path, expected in protected.items():
        if sha(path) != expected:
            raise ValueError(f'Input hash mismatch: {path.name}')
    for name, expected in config['code_sha256_lf'].items():
        if sha(ROOT / name, lf=True) != expected:
            raise ValueError(f'Code/evidence changed: {name}')

    scores = pd.read_csv(scores_path).set_index('county').sort_index()
    if scores.index.has_duplicates or len(scores) != config['expected_counties']:
        raise ValueError('Expected distinct county score rows')
    counties = set(scores.index)
    weights = pd.read_csv(ROOT / 'research/effective_weights/results/terminal_weights.csv')
    weights = weights[(weights.regime == 'fema_fallback') & (weights.score == 'final')]
    if weights.indicator.duplicated().any() or len(weights) != 74:
        raise ValueError('Unexpected active leaves')
    profiles = []
    constant = set()
    for row in weights.itertuples():
        values = pd.to_numeric(scores[row.indicator], errors='raise')
        if not all(math.isfinite(x) for x in values):
            raise ValueError('Missing/nonfinite normalized score')
        match = re.search(r"\['([^']+)'\]", row.normalization)
        if match:
            source = match.group(1)
        elif row.normalization == "minmax_score(per_capita(df, 'overall_crime_count_2024'))":
            source = 'overall_crime_count_2024'
        else:
            raise ValueError('Unsupported normalization expression')
        raw = scores[source]
        same = values.nunique() == 1
        if same:
            constant.add(row.indicator)
        profiles.append(dict(indicator=row.indicator, saved_input_operand=source,
            normalization_expression=row.normalization,
            weight_percent=row.percent, unique_normalized=int(values.nunique()), constant=same,
            normalized_min=float(values.min()), normalized_max=float(values.max()),
            normalized_zero_rows=int(values.eq(0).sum()),
            **{'input_' + k: v for k, v in asdict(profile(raw.astype(str).tolist())).items()}))
    if constant != {r['indicator'] for r in config['constant_register']}:
        raise ValueError('Constant set changed')

    prepared = {n: checked_table(frozen / 'data/raw' / n, counties) for n in config['prepared_files']}
    prepared_profiles = [dict(file=name, field=col, **asdict(profile(df[col].tolist())))
                         for name, df in prepared.items() for col in df.columns]
    matrices = {n: matrix(read_rows(frozen / f'data/raw/tn_{n}_activity_raw_2024.csv'), True).cells
                for n in ['explosives', 'gang_explosives']}
    matrices['ambush'] = ambush_cells(read_rows(frozen / 'data/raw/tn_law_enforcement_ambush_raw_2024.csv'), counties)
    if any(set(df.index) != counties for df in matrices.values()):
        raise ValueError('Export county support mismatch')
    ffl = pd.read_csv(frozen / 'data/raw/atf_ffl_listing.csv', usecols=['LIC_TYPE', 'PREMISE_STATE'], dtype=str)
    if not ffl.PREMISE_STATE.eq('TN').all() or ffl.LIC_TYPE.isna().any():
        raise ValueError('Unexpected FFL state/type')
    mapping = pd.read_csv(frozen / 'outputs/tables/crime_offense_label_mapping_validation.csv')
    evidence = []
    for item in config['constant_register']:
        record = dict(item)
        p = profile(prepared[item['prepared_file']][item['prepared_field']].tolist())
        if p.explicit_zero != len(counties):
            raise ValueError('Expected all-zero prepared constant')
        record['prepared_explicit_zero_rows'] = p.explicit_zero
        record['normalized_value'] = float(scores[item['indicator']].iloc[0])
        w = weights.set_index('indicator').loc[item['indicator']]
        record['weight_percent'] = float(w.percent)
        record['constant_score_points'] = float(Fraction(w.coefficient_exact) * 50)
        if item['evidence_class'] == 'blank_export_cells':
            cells = matrices[item['matrix']][item['offense']]
            stats = asdict(profile(cells.tolist()))
            if stats['blank'] != len(counties):
                raise ValueError('Expected all-blank selected export column')
            record.update({'export_' + k: v for k, v in stats.items()})
        elif item['evidence_class'] == 'category_absent_from_retained_listing':
            record['source_rows'] = len(ffl)
            record['collector_type_rows'] = int(ffl.LIC_TYPE.eq('03').sum())
            if record['collector_type_rows']:
                raise ValueError('Collector source support changed')
        elif item['evidence_class'] == 'metric_absent_from_retained_mapping':
            record['mapped_source_labels'] = int(mapping.metric.eq(item['prepared_field']).sum())
            if record['mapped_source_labels']:
                raise ValueError('Mapping support changed')
        evidence.append(record)

    # All calculations above are diagnostics of preserved values, not variant scores.
    for path, expected in protected.items():
        if sha(path) != expected:
            raise ValueError('Input changed during audit')
    output = HERE / 'results'
    output.mkdir(exist_ok=True)
    pd.DataFrame(profiles).to_csv(output / 'active_indicator_profiles.csv', index=False)
    pd.DataFrame(prepared_profiles).to_csv(output / 'prepared_cell_profiles.csv', index=False)
    pd.DataFrame(evidence).to_csv(output / 'constant_evidence_register.csv', index=False)
    summary = dict(active_indicators=len(weights), constant_indicators=len(constant),
        constant_weight_percent=sum(x['weight_percent'] for x in evidence),
        constant_score_points=sum(x['constant_score_points'] for x in evidence),
        evidence_classes=pd.Series([x['evidence_class'] for x in evidence]).value_counts().to_dict(),
        retained_inputs_verified=len(protected), code_files_verified=len(config['code_sha256_lf']),
        original_inputs_written=False, candidate_scores_computed=False,
        config_sha256_lf=sha(HERE / 'config.json', True),
        audit_sha256_lf=sha(Path(__file__), True),
        protocol_sha256_lf=sha(HERE / 'SENSITIVITY_PROTOCOL.md', True))
    (output / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frozen-root', type=Path, required=True)
    parser.add_argument('--saved-scores', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.frozen_root, args.saved_scores), indent=2))


if __name__ == '__main__':
    main()
