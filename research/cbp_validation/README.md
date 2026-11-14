# Intended use, CBP publication mask and bounding protocol

Research preparation | November 14, 2026 | Released v1.0.1 preserved

The exact CBP publication mask was rebuilt from eight retained Census responses and reconciled against the prior cell ledger, county coverage table, frozen cache and released score-table inputs. **368 of 760 county-category pairs are published; 392 are unpublished and bounded at 0–2 establishments by the dated Census clarification.** No missing counts were recovered, imputed or written into model data. No score bounds or new ranks were calculated.

## Deliverables

- [Intended-use/validation charter](INTENDED_USE_CHARTER.md): descriptive county screening as the current research purpose; independent descriptive validation requirements; a separate gate for any predictive use; no promotion based on rank stability alone.
- [Bounding protocol](BOUNDING_PROTOCOL.md): fixed-normalization, nonprobabilistic bounds for the exact 392-cell mask, including interval-based rank uncertainty rather than relying only on all-low/all-high rankings. Not executed.
- [Cell mask](results/cell_mask.csv): all 760 county/category keys, publication status, bounds only for unpublished cells, and cache-row presence. Published observations are held fixed but their counts are not republished in this mask.
- [County coverage](results/county_coverage.csv): eight fully published counties and 87 with at least one unpublished category. Moore and Van Buren have no published categories.
- [Retrieval provenance](results/retrieval_provenance.json) and [verification](results/verification.json): original retained query settings, October 26 timestamps, response hashes and reconciliation results.

## Evidence and verification

The reference universe comes from the frozen 95-county ACS roster, joined by five-digit FIPS and cross-checked with county names. The eight categories are NAICS2017 453991, 451110, 453310, 447110, 445120, 522291, 812310 and 441120. Every retained response is for 2023, state 47, county `*`, LFO=001 and EMPSZES=001. All eight files match the original retrieval-manifest hashes. The verifier checks headers, response filters, successful retrieval status, unique keys, integer counts, the publication threshold and manifest row counts before interpreting absent rows.

Every published value matches the frozen CBP cache and the released count column. The reconstructed mask matches the existing 760-cell evidence ledger exactly, including absent published values and cache values, and reproduces the earlier 95-county coverage table.

The frozen cache has **93 county rows**, not 95. Among the 392 unpublished cells, 376 have numeric zero fallbacks in existing cache rows; the remaining 16 belong to the absent Moore and Van Buren rows. The old evidence ledger preserves those 16 cache values as missing. The released table has zero fallbacks for all 392. These are three distinct observations—unpublished source cells, absent cache rows, and released numerical fallbacks—not evidence of observed zero establishments. The mask's `legacy_cache_row_present` flag retains this distinction.

The [October 28–29 Census clarification](../../docs/census_cbp_clarification_2026-10-28.md) attributes the 0–2 bound to source-owner correspondence under these exact query conditions; the exactly-three publication threshold was clarified separately. This branch relies on that retained, dated record. It does not recontact Census or independently recertify its correspondence. The retrieved responses demonstrate compatibility with 2023 data, not authentication of the original collector's year or request logs. No new live query was made.

## Reproduction

```powershell
python -m research.cbp_validation.verify_mask --evidence-root "<retained-audit-workspace>" --saved-scores "<v1.0.1-package>/outputs/tables/tn_county_domestic_security_scores.csv"
python -m pytest -q
```

`config.json` pins retained paths relative to the supplied evidence root and checks the frozen roster/cache against the historical snapshot manifest. It also pins repository source documentation and the released score table. The verifier rejects changed files before and after reading. It writes only this research directory's results, exports no credentials or private correspondence, and does not copy raw Census responses into the repository. Those retained responses are necessary to reproduce the check; the committed mask alone is not an independent source.

The [preservation record](results/preservation.json) verifies all 170 original files, 170 frozen copies and five listed release assets. All 94 local offline tests passed (188 existing pandas fragmentation warnings). Ten new synthetic cases distinguish an omitted county from a literal count, validate the exactly-three threshold and reject duplicate, malformed, empty, wrong-filter or missing-category evidence. Existing released scores, data, formulas, scenarios and dated report remain unchanged. The next separately reviewed task may implement the bounding protocol; independent validation remains an additional research requirement.
