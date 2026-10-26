# Source availability and confidence correction

This change fixes coverage metadata only. Existing score formulas, numeric
fallbacks, weights, thresholds, and scenario definitions remain unchanged.
Previously generated tables, charts, and the sample PDF have not been regenerated.
Their old confidence labels should not be treated as corrected results.

## Availability contract

- Coverage is captured before loaders add default fields, coerce invalid numbers,
  aggregate duplicate counties, or fill unmatched county rows.
- All expected numeric fields in an input layer must be finite, nonnegative,
  and present for that county. Partial input is not complete layer coverage.
  Nullable `pd.NA` cells are missing, not skipped during completeness checks.
  Population denominators must be strictly positive.
- A layer-specific `*_data_available` boolean is carried in master CSVs and
  respected by scoring. False, blank, and unrecognized markers are unavailable.
- Newly created zero templates have an explicit false marker. Re-reading the
  template cannot promote it to observed data.
- Old all-zero local rows without markers are ambiguous because earlier loaders
  generated identical templates. They remain unverified. After checking the
  original export and county coverage, set the relevant marker to `True` for
  a confirmed observed zero. Do not blanket-mark templates as available.
- Complete legacy rows with positive values retain inferred availability. This
  is a coverage heuristic, not independent verification of the source or its
  reporting completeness. Upstream processors that have already erased missingness
  require source review; this patch cannot recover that lost evidence.
- API collection records coverage separately: failed/empty FEMA retrieval and
  incomplete CBP category retrieval do not become observed zero exposure.
  FEMA records must contain the year, incident type, and declaration title used
  by the existing aggregates. A first page at the request limit is unverified.
  ACS coverage also checks raw components, so sums/ratios cannot hide missing data.
- Availability uses the same county keys as the value join. The existing exact
  county-name join in the crime-rate loader is preserved; unmatched values cannot
  acquire coverage solely because an evidence key was normalized.
- Supported legacy ACLED aliases are mapped before availability is captured.

Completeness counts 14 input layers. Targeted-harm and institutional composites
retain diagnostic flags based on their dependencies, but do not add independent
coverage. The existing `model_confidence` field and bands remain for compatibility;
they describe input coverage, not predictive confidence.

## Reproduced regression

Three synthetic counties containing only population, poverty, unemployment,
income, and rent burden previously received 13/16 available layers (81.25%, High).
They now receive 1/14 (approximately 7.14%, Low). Missing crime inputs are no longer
reported as true zeros. Their original scores remain 38.18, 50.00, and 61.82.

## Offline verification

```text
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use synthetic data, mock API responses, and redirect outputs to temporary
directories. They cover missing files, repeated template reads, partial schemas,
invalid values, explicit observed zeros, absent counties, duplicate rows, CSV
round trips, API failure, and master assembly. No live data refresh is required.

## Follow-up review

The expanded suite has 38 passing tests, including nullable missing cells, invalid
population denominators, county-key mismatches, legacy aliases, incomplete FEMA
records, a potentially truncated FEMA page, and missing ACS component values.

Frozen expectations from base commit
`bb6f0b5f7955c09b36db66202e77d29ed3c7d9ad` verify 374 non-quality fields across
three five-county synthetic cases. All ten weighting scenarios, rank-stability
results, and non-quality projections of all nine emitted county score tables
match the base within 1e-12. Coverage/confidence metadata is intentionally changed.
The fixture provenance is documented in `tests/fixtures/README.md`.

All eight saved dashboard images and `docs/sample_report.pdf` retain their base
Git blob hashes. The Windows PDF checkout has Git's pre-existing CRLF conversion;
its bytes match `git cat-file --filters` for the base revision. The stored PDF
SHA-256 remains `b060d313b51244eca5ecf064315186fa7f8345ef0878dd60831a1e52234f9ab3`.
No existing data/output artifacts were overwritten. The synthetic checks above
were followed by the frozen real-data validation below.

## Frozen real-data validation (2026-10-26)

Subsequent source review found additional legacy CBP category gaps. See
[source_coverage_followup.md](source_coverage_followup.md) for the staged,
source-reviewed coverage correction and its separate parity checks. The results
below describe the first frozen replay and are retained as audit history.

The original local project supplied 170 data/output files (50,801,037 bytes).
They were copied into a separate validation workspace with per-file SHA-256,
size, and file-modification metadata. All original file hashes were checked again
after replay and remained unchanged. File modification dates are not observation
dates. Raw data and county-level validation artifacts remain local, outside this PR.

Base `bb6f0b5f7955c09b36db66202e77d29ed3c7d9ad` and candidate
`b26350111fe0cd0f76a9e6a76410c2058733eb96` were run in separate directories.
Each scored both the saved master and a master rebuilt through the local loaders.
ACS, CBP, and FEMA collectors were replaced with frozen saved-cache reads;
HTTP requests were blocked. This checks local assembly and scoring, not fresh API
collection or an end-to-end refresh of every upstream preparation script.

All 42 comparison checks passed at relative/absolute tolerance 1e-12:

- 95 county rows and 377 non-quality fields agree between base and candidate.
- All ten scenarios (950 county-scenario rows), 100 scenario-leader rows, and
  95 rank-stability rows agree.
- Non-quality projections of all nine emitted county score tables agree.
- Rebuilt and saved-master scores agree in each version. The base replay also
  agrees with the saved historical score, scenario, and rank tables.
- County/population identity in the quality table agrees after county alignment;
  its row order intentionally changes because it is sorted by completeness.

Coverage/confidence metadata intentionally differs. The original 95 High labels
become 7 High, 48 Good, and 40 Moderate. These remain coverage bands, not validated
probabilities or predictive confidence. No numeric scoring changes were made.
Historical charts/PDFs were preserved rather than regenerated; their old coverage
labels are not corrected by this replay.

### Source review and unresolved coverage

The review recorded 462 unresolved county/input-layer pairs across seven layers:

| Layer | Unverified counties | Evidence |
| --- | ---: | --- |
| CBP | 2 | Moore and Van Buren FIPS absent from the 93-row saved cache |
| Disaster/disruption | 95 | All 15 input fields zero; no observed-zero provenance |
| Political violence | 68 | Counties absent from the 27-county event aggregation |
| Explosives | 71 | Selected raw TBI cells blank |
| Gang/explosives | 71 | Selected raw TBI cells blank |
| Hate-crime offenses | 64 | Selected raw TBI cells blank |
| Law-enforcement ambush | 91 | Selected raw TBI cells blank |

For every flagged county in the four TBI layers, all selected raw count cells
were blank, rather than explicit numeric zeros. The saved exports identify
Incident Date 2024 and export date 2026-05-28. Existing processors convert these
blanks to zero; the exports alone do not establish the meaning of blanks or
county reporting completeness. No county was promoted to confirmed observed zero.
The ACS cache records 2024; the CBP cache does not record its retrieval year.

Before promoting coverage, establish TBI blank-cell semantics and county/year
reporting coverage, recover the two missing CBP counties with year/category
provenance, supply measured disruption inputs, and document ACLED query coverage
and pagination. Positive legacy rows still use inferred availability and are not
independently certified by this audit. Derived availability flags were excluded
from the 462 input-layer count.

Disposition: numerical parity is supported within the reviewed frozen-input
scope; source coverage remains qualified. Keep PR #2 in draft for review of these
limitations. Other scoring changes remain separate.
