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
