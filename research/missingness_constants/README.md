# Missingness and constant-input audit

Research audit | November 13, 2026 (America/Chicago) | v1.0.1 remains the reference

The 14 constant terminal indicators are not evidence of uniform observed conditions. Eight arise from blank selected TBI export columns, three are unverified all-zero optional inputs, two have no contributing labels in the retained broad-crime mapping, and one has no corresponding license type in the retained ATF listing. All 14 prepared fields are zero for all 95 counties; the unchanged scoring function maps each constant series to 50.

These leaves carry **7.69025% of baseline coefficient mass** and add **3.845125 points to every county**. They affect score levels, but supply no county differentiation in this snapshot. Neither a prepared zero nor a normalized 50 authenticates an observed absence.

## Evidence register

| Evidence class | Constant indicators | Weight | Common score contribution | Interpretation |
|---|---|---:|---:|---|
| Blank export cells | Explosives and gang-explosives homicide, arson and property damage; ambush weapon-law and property damage (8) | 2.43625% | 1.218125 | Each selected column has 95 blank cells and no explicit numeric zero; processors turn blanks into zeros |
| Unverified optional input | Training, surplus/tactical retail and gun-range density (3) | 3.85% | 1.925 | Prepared values match an all-zero template pattern; no availability markers or observation history establish measured absence |
| Metric absent from retained mapping | Broad-input hate crime and law-enforcement assault (2) | 1.14% | 0.57 | Neither metric has a contributing label in the saved mapping; expected-column insertion supports zero defaults, not observed absence |
| Category absent from retained listing | Collector FFL density (1) | 0.264% | 0.132 | The 1,978 retained TN license rows contain no type 03; the processor inserts an absent category as zero. This does not establish county collector-license absence |

The [indicator-level register](results/constant_evidence_register.csv) supplies exact field names, prepared-file references, source-cell counts, code locators, coefficients and interpretation limits. Eight columns imply 760 examined blank cells, including the repeated explosives/gang-explosives measurements; these are not 760 independent observations. Homicide here follows the processor's `Murder` mapping, not an expanded homicide definition.

The broad-input `hate_crime_count` is distinct from the separately retained `hate_crime_total_count`; the broad law-enforcement assault field is not interchangeable with the ambush input. No substitution is performed. No claim about ATF's general publication policy is inferred from the retained listing alone.

## Missingness mechanisms

The unchanged `src/risk_scoring.py` preserves several legacy numerical fallbacks: `minmax_score` coerces invalid/nonfinite values to missing, fills missing with zero and returns 50 for a constant series; `_ensure_numeric_columns` inserts absent fields and fills nonnumeric/missing cells with zero; `per_capita` fills missing counts and undefined divisions with zero. These functions explain why fully populated final score columns do not prove complete source evidence.

The explosives processors' `_safe_number` and ambush processor's `_to_int` map blanks or conversion failures to zero. The broad-crime processor inserts absent expected metrics after pivoting. The FFL processor inserts absent categories. The optional tactical loader can create an all-zero template. These are verified code mechanisms; the audit does not claim to reconstruct every historical execution event or recover deleted missingness information.

The [74 active-indicator profiles](results/active_indicator_profiles.csv) record saved operand cell states, normalization expressions and normalized zero counts. A normalized zero may be a valid minimum, not an absence. Operand counts are post-processing observations, not original missingness. The overall-crime count operand precedes an inline per-capita calculation; the expression column makes that distinction explicit.

The [prepared-cell profiles](results/prepared_cell_profiles.csv) cover every field in the six county input files used for the constant trace. `explicit_zero` describes literal numeric zero in that particular file, not verified observed zero at the source. No cells are recoded by the audit. This is a focused constant-input audit plus baseline profile, not a fresh source-completeness assessment of all 74 indicators.

Other unresolved issues remain separate: [CBP unpublished cells](../../docs/source_coverage_followup.md), [TBI coverage/filter limitations](../../docs/final-report-2026-11-10/README.md), ACLED acquisition completeness, and the unverified disruption template. The saved baseline uses the FEMA fallback, so inactive disruption leaves are not added to the 14 active constants. The missing overall-crime export remains [unrecovered](../tbi_download_backups/THUMB_DRIVE_CHECK.md). No source refresh or outreach was undertaken.

## Sensitivity protocol

[SENSITIVITY_PROTOCOL.md](SENSITIVITY_PROTOCOL.md) defines six research variants separating optional constants, unsupported source categories, blank-derived constants, repeated TBI vectors and their union. It fixes the reference data, normalization, arithmetic, ties, diagnostics, stopping rules and interpretation limits. **No variant scores or new county ranks have been computed.** Earlier overlap results informed the protocol; it is not a blinded validation.

## Reproduction and preservation

Use the locked environment, with the preserved source snapshot and released score table outside this checkout:

```powershell
python -m research.missingness_constants.audit --frozen-root "<preserved-snapshot>" --saved-scores "<v1.0.1-package>/outputs/tables/tn_county_domestic_security_scores.csv"
python -m pytest -q
```

The audit checks input hashes before and after reading, pins the relevant source/earlier-audit files with LF-normalized hashes, checks county support and rejects changed constant membership. It writes only its own research results. It imports the prior read-only matrix parser, not the production pipeline. It reads only license type/state columns from the retained FFL listing and exports no business names, addresses or individual records. No original data or large binaries are committed.

The [verification record](results/verification.json) pins the configuration, audit and protocol and reports the completed diagnostic checks. The [preservation record](results/preservation.json) verifies all 170 original files, 170 frozen files and five listed release assets. New tests use synthetic inputs to distinguish blank/invalid/zero cells and reject changed filters, duplicate counties and mismatched county support. All 76 local offline tests passed (188 existing pandas fragmentation warnings). Existing released scores, formulas, data, scenarios, thresholds and the dated report remain unchanged.
