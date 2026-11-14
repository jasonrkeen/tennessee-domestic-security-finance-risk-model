"""Reconstruct a CBP publication mask from retained responses, never live queries."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path: Path, lf: bool = False) -> str:
    return hashlib.sha256(path.read_text(encoding='utf-8').encode() if lf else path.read_bytes()).hexdigest()


def parse_response(rows: list[list[str]], naics: str, roster: dict[str, str]) -> dict[str, int]:
    required = {'NAME', 'ESTAB', 'NAICS2017', 'LFO', 'EMPSZES', 'state', 'county'}
    if not rows or len(set(rows[0])) != len(rows[0]) or not required <= set(rows[0]):
        raise ValueError('Unexpected response header')
    result = {}
    for row in rows[1:]:
        if len(row) != len(rows[0]):
            raise ValueError('Ragged response row')
        r = dict(zip(rows[0], row))
        if (r['NAICS2017'], r['LFO'], r['EMPSZES'], r['state']) != (naics, '001', '001', '47'):
            raise ValueError('Response filters mismatch')
        fips = r['state'] + r['county']
        if fips not in roster or fips in result:
            raise ValueError('Unknown or duplicate county')
        if r['NAME'] != roster[fips] + ' County, Tennessee':
            raise ValueError('County name/FIPS mismatch')
        if not r['ESTAB'].isdigit() or int(r['ESTAB']) < 3:
            raise ValueError('Invalid published establishment count')
        result[fips] = int(r['ESTAB'])
    if not result:
        raise ValueError('Empty response is not an unpublished-cell mask')
    return result


def build_mask(roster: dict[str, str], categories: dict[str, str], published: dict[str, dict[str, int]]) -> pd.DataFrame:
    if set(categories) != set(published):
        raise ValueError('Missing category response')
    records = []
    for naics, field in categories.items():
        if not set(published[naics]) <= set(roster):
            raise ValueError('Unexpected geography')
        for fips, county in sorted(roster.items()):
            found = fips in published[naics]
            records.append(dict(fips=fips, county=county, year=2023, naics=naics, field=field,
                status='published' if found else 'unpublished_bounded_0_2',
                lower_bound='' if found else 0, upper_bound='' if found else 2))
    return pd.DataFrame(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--saved-scores', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((HERE/'config.json').read_text())
    def verify() -> None:
        for name, expected in config['retained_sha256'].items():
            if digest(args.evidence_root/name) != expected:
                raise ValueError(f'Retained hash mismatch: {name}')
        for name, expected in config['repo_sha256_lf'].items():
            if digest(ROOT/name, True) != expected:
                raise ValueError(f'Repository source changed: {name}')
        if digest(args.saved_scores) != config['scores_sha256']:
            raise ValueError('Released score hash mismatch')
    verify()
    frozen = args.evidence_root/'work/real-validation/frozen'
    historical = json.loads((args.evidence_root/'outputs/real-validation/snapshot_manifest.json').read_text())
    recorded = {r['path']: r['sha256'] for r in historical['files']}
    for name in ['data/processed/tn_acs_county_data.csv', 'data/processed/tn_cbp_business_exposure.csv']:
        if digest(frozen/name) != recorded[name]:
            raise ValueError('Historical snapshot identity mismatch')
    acs = pd.read_csv(frozen/'data/processed/tn_acs_county_data.csv', dtype=str)
    if len(acs) != config['expected_counties'] or acs.fips.duplicated().any() or acs.county.duplicated().any():
        raise ValueError('Unexpected county roster')
    roster = dict(zip(acs.fips, acs.county))
    manifest = json.loads((args.evidence_root/'outputs/source-followup/cbp_retrieval_manifest.json').read_text())
    categories = config['categories']
    published, provenance = {}, []
    for item in manifest:
        n = item['query']['NAICS2017']
        query = dict(get='NAME,NAICS2017_LABEL,ESTAB', **{'for': 'county:*', 'in': 'state:47'}, NAICS2017=n, LFO='001', EMPSZES='001')
        if n not in categories or n in published or item['query'] != query or item['column'] != categories[n]:
            raise ValueError('Manifest category/filter mismatch')
        if item['source_url'] != 'https://api.census.gov/data/2023/cbp' or item['year'] != 2023 or item['http_status'] != 200 or item['status'] != 'retrieved':
            raise ValueError('Unsuccessful or wrong-vintage retrieval')
        path = args.evidence_root/'work/source-followup'/item['file']
        if digest(path) != item['sha256']:
            raise ValueError('Retrieval manifest hash mismatch')
        published[n] = parse_response(json.loads(path.read_text()), n, roster)
        if len(published[n]) != item['rows']:
            raise ValueError('Manifest row count mismatch')
        provenance.append({k: item[k] for k in ['source_url', 'query', 'retrieved_utc', 'sha256', 'rows', 'column']})
    mask = build_mask(roster, categories, published)
    if len(mask) != config['expected_cells'] or sum(map(len, published.values())) != config['expected_published'] or mask.status.ne('published').sum() != config['expected_unpublished']:
        raise ValueError('Mask totals changed')
    cache = pd.read_csv(frozen/'data/processed/tn_cbp_business_exposure.csv', dtype={'fips': str}).set_index('fips')
    scores = pd.read_csv(args.saved_scores).set_index('county')
    if cache.index.has_duplicates or not set(cache.index) <= set(roster) or scores.index.has_duplicates or set(scores.index) != set(roster.values()):
        raise ValueError('Cache/release county support mismatch')
    absent_cache = set(roster)-set(cache.index)
    if any(fips in response for fips in absent_cache for response in published.values()):
        raise ValueError('Published county missing from cache')
    mask['legacy_cache_row_present'] = mask.fips.isin(cache.index)
    evidence = pd.read_csv(args.evidence_root/'outputs/source-followup/cbp2023_cell_evidence.csv', dtype={'fips': str, 'naics': str}).set_index(['fips', 'naics'])
    if evidence.index.has_duplicates or set(evidence.index) != set(zip(mask.fips, mask.naics)):
        raise ValueError('Prior evidence support mismatch')
    for row in mask.itertuples():
        found = row.status == 'published'
        value = published[row.naics].get(row.fips)
        # Absent cache rows are not observed zeros; compare the released fallback separately.
        legacy = cache.loc[row.fips, row.field] if row.legacy_cache_row_present else 0
        old = evidence.loc[(row.fips, row.naics)]
        if legacy != (value if found else 0) or scores.loc[row.county, row.field] != legacy:
            raise ValueError('Cache/release value mismatch')
        legacy_matches = old.legacy_cache_value == legacy if row.legacy_cache_row_present else pd.isna(old.legacy_cache_value)
        if old.status != ('published' if found else 'not_published') or old.field != row.field or old.county != row.county or old.year != 2023 or old.published_rows != int(found) or not legacy_matches:
            raise ValueError('Prior cell evidence mismatch')
        if (found and old.published_establishments != value) or (not found and not pd.isna(old.published_establishments)):
            raise ValueError('Prior published-value evidence mismatch')
    coverage = mask.assign(published=mask.status.eq('published')).groupby(['fips','county']).published.sum().reset_index(name='published_categories')
    coverage['unpublished_categories'] = len(categories)-coverage.published_categories
    prior = pd.read_csv(args.evidence_root/'outputs/source-followup/cbp2023_county_coverage.csv', dtype={'fips':str}).sort_values('fips').reset_index(drop=True)
    pd.testing.assert_frame_equal(coverage, prior[coverage.columns], check_dtype=False)
    if not prior.failed_categories.eq(0).all():
        raise ValueError('Prior category failures')
    verify()
    output = HERE/'results'; output.mkdir(exist_ok=True)
    mask.to_csv(output/'cell_mask.csv', index=False)
    coverage.to_csv(output/'county_coverage.csv', index=False)
    (output/'retrieval_provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    summary = dict(cells=len(mask), published_cells=config['expected_published'], unpublished_cells=config['expected_unpublished'],
        fully_published_counties=int(coverage.published_categories.eq(8).sum()),
        incomplete_counties=int(coverage.unpublished_categories.gt(0).sum()),
        no_published_categories=coverage.loc[coverage.published_categories.eq(0),'county'].tolist(),
        frozen_cache_rows=len(cache), absent_cache_counties=sorted(roster[f] for f in absent_cache),
        original_response_hashes_verified=len(published), prior_cell_ledger_matched=True,
        published_values_match_frozen_cache_and_release=True, unpublished_release_values_are_legacy_zeros=True,
        retrieval_vintage='2026-10-26 retained responses for 2023 CBP; not original collection logs',
        live_queries_performed=False, scoring_bounds_computed=False,
        document_sha256_lf={n: digest(HERE/n, True) for n in ['INTENDED_USE_CHARTER.md', 'BOUNDING_PROTOCOL.md']},
        config_sha256_lf=digest(HERE/'config.json', True), code_sha256_lf=digest(Path(__file__), True),
        mask_sha256=digest(output/'cell_mask.csv'))
    (output/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
