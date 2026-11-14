"""Execute the six frozen research variants without modifying release artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.indicator_overlap.analyze import Study, load_study, ranks, top_set, remove_family

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def digest(path: Path, lf: bool = False) -> str:
    return hashlib.sha256(path.read_text(encoding='utf-8').encode() if lf else path.read_bytes()).hexdigest()


def validate_sets(sets: dict[str, list[str]], indicators: pd.DataFrame) -> pd.DataFrame:
    if set(sets) != {'C1', 'C2', 'C3', 'C4', 'D1', 'CD'}:
        raise ValueError('Expected exactly the six protocol variants')
    for names in sets.values():
        if len(names) != len(set(names)) or not set(names) <= set(indicators):
            raise ValueError('Duplicate or unknown excluded leaf')
    if set(sets['C4']) != set(sets['C1'] + sets['C2'] + sets['C3']):
        raise ValueError('Constant union mismatch')
    if set(sets['CD']) != set(sets['C4']) | set(sets['D1']):
        raise ValueError('Combined union mismatch')
    if any(indicators[x].nunique() != 1 for x in sets['C4']):
        raise ValueError('Expected constant input')
    pairs = []
    for name in sets['D1']:
        other = (name.replace('gang_explosive_', 'explosive_related_')
                 if name.startswith('gang_explosive_') else 'overall_crime_count_pressure_score')
        if other not in indicators or not np.array_equal(indicators[name], indicators[other]):
            raise ValueError(f'Duplicate equality failed: {name}')
        pairs.append(dict(excluded=name, retained=other, exact_equal=True))
    if len(pairs) != 7 or sum(x['excluded'].startswith('gang_explosive_') for x in pairs) != 6:
        raise ValueError('Unexpected D1 support')
    return pd.DataFrame(pairs)


def evaluate(study: Study, sets: dict[str, list[str]], families: dict, config: dict) -> dict[str, pd.DataFrame]:
    decimals, k = config['rank_round_decimals'], config['top_k']
    baseline_rank = ranks(study.baseline, decimals)
    baseline_top = top_set(study.baseline, study.counties, k, decimals)
    summary, county_rows, context = [], [], []
    weighted = study.indicators.mul(study.coefficients)
    np.testing.assert_allclose(weighted.sum(axis=1), study.baseline, rtol=config['rtol'], atol=config['atol'])
    for variant in config['variant_order']:
        names = sets[variant]
        candidate, retained, excluded, weight = remove_family(study.indicators, study.coefficients, names)
        np.testing.assert_allclose(retained + excluded, study.baseline, rtol=config['rtol'], atol=config['atol'])
        np.testing.assert_allclose(retained, study.baseline - excluded, rtol=config['rtol'], atol=config['atol'])
        ranked = ranks(candidate, decimals)
        shift = ranked - baseline_rank
        if variant.startswith('C') and variant != 'CD' and not shift.eq(0).all():
            raise ValueError('Constant-only rank change: inspect tie rounding before accepting')
        top = top_set(candidate, study.counties, k, decimals)
        constant_names = [x for x in names if study.indicators[x].nunique() == 1]
        constant_points = float(weighted[constant_names].sum(axis=1).iloc[0])
        delta = candidate - study.baseline
        summary.append(dict(variant=variant, excluded_leaves=len(names), retained_weight=1-weight,
            excluded_weight_percent=100*weight, excluded_constant_points=constant_points,
            rank_spearman=baseline_rank.corr(ranked), median_absolute_rank_change=float(shift.abs().median()),
            maximum_absolute_rank_change=float(shift.abs().max()), counties_with_rank_change=int(shift.ne(0).sum()),
            baseline_top_count=len(baseline_top), research_top_count=len(top), top_retained=len(top & baseline_top),
            top_lost=' | '.join(sorted(baseline_top-top)), top_gained=' | '.join(sorted(top-baseline_top)),
            renormalized_delta_min=float(delta.min()), renormalized_delta_mean=float(delta.mean()),
            renormalized_delta_max=float(delta.max()), unscaled_delta_min=float((-excluded).min()),
            unscaled_delta_mean=float((-excluded).mean()), unscaled_delta_max=float((-excluded).max())))
        largest = shift.abs().nlargest(config['largest_movement_k'], keep='all')
        selected = set(largest[largest > 0].index)
        for i in study.indicators.index:
            county_rows.append(dict(variant=variant, county=study.counties[i], baseline_score=study.baseline[i],
                excluded_contribution=excluded[i], unscaled_retained_score=retained[i], research_score=candidate[i],
                research_score_delta=delta[i], baseline_rank=baseline_rank[i], research_rank=ranked[i],
                rank_change_positive_is_down=shift[i], baseline_top=study.counties[i] in baseline_top,
                research_top=study.counties[i] in top))
        for family in sorted({x['source_family'] for x in families.values()}):
            group = [x for x in study.indicators if families[x]['source_family'] == family]
            removed = [x for x in group if x in names]
            before = weighted[group].sum(axis=1)
            removed_points = weighted[removed].sum(axis=1)
            after = (before-removed_points)/(1-weight)
            for i in sorted(selected):
                context.append(dict(variant=variant, county=study.counties[i], source_family=family,
                    rank_change_positive_is_down=shift[i], baseline_contribution=before[i],
                    excluded_contribution=removed_points[i], research_contribution=after[i],
                    contribution_change=after[i]-before[i]))
    return {'summary': pd.DataFrame(summary), 'county_variants': pd.DataFrame(county_rows),
            'largest_movement_context': pd.DataFrame(context)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved-scores', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((HERE/'config.json').read_text())
    def verify() -> None:
        if digest(args.saved_scores) != config['scores_sha256']:
            raise ValueError('Released score hash mismatch')
        for name, expected in config['pinned_sha256_lf'].items():
            if digest(ROOT/name, True) != expected:
                raise ValueError(f'Pinned dependency changed: {name}')
    verify()
    previous = json.loads((ROOT/'research/indicator_overlap/config.json').read_text())
    protocol = json.loads((ROOT/'research/missingness_constants/config.json').read_text())
    study = load_study(args.saved_scores, previous)
    sets = protocol['sensitivity_exclusion_sets']
    equality = validate_sets(sets, study.indicators)
    results = evaluate(study, sets, previous['indicator_families'], config)
    results['duplicate_checks'] = equality
    verify()
    output = HERE/'results'
    output.mkdir(exist_ok=True)
    for name, frame in results.items():
        frame.to_csv(output/f'{name}.csv', index=False, float_format='%.15g')
    verification = dict(protocol_commit=config['protocol_commit'], protocol_amended=False,
        scores_sha256=digest(args.saved_scores), counties=len(study.counties), variants=list(sets),
        duplicate_pairs_checked=len(equality), baseline_reconstruction_passed=True,
        input_and_dependency_hashes_unchanged=True, production_pipeline_run=False,
        config_sha256_lf=digest(HERE/'config.json', True), code_sha256_lf=digest(Path(__file__), True),
        result_sha256={p.name: digest(p) for p in sorted(output.glob('*.csv'))})
    (output/'verification.json').write_text(json.dumps(verification, indent=2)+'\n')
    print(results['summary'].to_string(index=False))


if __name__ == '__main__':
    main()
