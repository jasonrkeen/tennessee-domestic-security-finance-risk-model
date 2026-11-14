# CBP source-uncertainty bounding protocol, version 1

Specified November 14, 2026, before score-bound calculations. **Not executed in this branch.** This is an exploratory retrospective uncertainty study, not external validation or a probability model.

## Scope and evidence

Use the verified 760-cell county-by-category mask in `results/cell_mask.csv`. The mask is reconstructed from eight retained October 26, 2026 responses for 2023 CBP, state 47, county `*`, NAICS2017, LFO=001 and EMPSZES=001. Match its hash to `results/verification.json` before execution. All 368 published values must continue to match the frozen cache and v1.0.1 table. All 392 unpublished pairs are bounded integer establishment counts in {0,1,2} under the [dated Census correspondence](../../docs/census_cbp_clarification_2026-10-28.md); no exact value is recovered.

This source-owner statement applies only to those query conditions and year. Do not generalize to other CBP years or measures, TBI blanks, ATF categories or ACLED missingness. October response compatibility with the cache does not prove the original collector's acquisition year or query settings. The original May request logs remain unavailable.

The 16 cells for Moore and Van Buren have absent cache rows, not numeric cache zeros. They nevertheless have the same unpublished status in the complete query universe and the same bounded domain; their released zeros remain computational fallbacks. Keep `legacy_cache_row_present` in the execution evidence.

## Frozen arithmetic specification

Work in a new research directory. Pin this protocol, mask, code, the v1.0.1 score table and the effective-weight table. Reconstruct the released final score using `fema_fallback`/`final` terminal coefficients at rtol=atol=1e-12. Keep all non-CBP normalized indicators, all population denominators, poverty contributions, coefficients and the FEMA fallback fixed. Do not combine the D1/CD exclusions with this study.

For each of the eight CBP count columns, derive and record the original per-10,000 rate and its original cross-county min/max endpoints from the saved release. Verify that the corresponding normalized leaf is reproduced, including the existing constant-series rule and clipping to 0–100. Use the exact terminal-leaf mapping in the effective-weight audit; the six cash-category leaves, tobacco/vape density and sporting-goods density cover the scored CBP family. Assert complete, unique coverage and the expected 10.36% coefficient mass. Include every flattened coefficient path; do not separately add a parent composite or its fixed poverty component again.

Freeze those baseline endpoints for the primary bounds. For each unpublished cell, evaluate count 0 and count 2 with the original population denominator, fixed endpoints and clipping. Published cells remain at their observed retained values. If any baseline range is constant or a mapping/normalization check fails, stop and amend the protocol before viewing bound results rather than silently choosing a new convention. Record every upper rate exceeding its original maximum and whether clipping activates. Do not re-estimate endpoints across hypothetical county configurations; that would couple counties and constitute a different study.

With fixed endpoints, positive populations and nonnegative terminal coefficients, each affected leaf and final composite is nondecreasing in its establishment count. Verify these conditions and test the endpoint transformation synthetically. The all-zero and all-two assignments then provide each county's lower and upper score within this specified rectangular domain. Also verify the all-zero assignment reproduces the released baseline and each county interval contains it. The all-two assignment is a stress endpoint, not an estimate of likely counts.

The rectangular domain does not impose unknown cross-category or cross-county constraints. These are outer bounds conditional on that domain and fixed normalization, not assertions that all combinations are jointly realistic. Do not assign uniform distributions, midpoint estimates or Monte Carlo probabilities without a separate evidentiary basis.

## Outputs and ranking interpretation

Report all 95 county score intervals, width, affected-cell counts, per-category contribution ranges, clipping diagnostics, endpoint rank comparisons and top-ten membership changes. Identify the largest interval widths with population and category context; retain every result, including zero-width intervals.

All-low versus all-high rankings alone do not bound ranking uncertainty because they move counties together. Additionally report conservative possible-position bounds using other counties' intervals: best position `1 + count(L_j > U_i)`; worst position `N - count(U_j < L_i)`, excluding county i. Treat overlapping/tied intervals as unresolved rather than claiming a strict order. Apply comparisons to ten-decimal rounded endpoints, and test tie cases. These position bounds are conservative ordinal bounds, not the average-tie ranks used in endpoint tables.

For endpoint tables, use descending average ranks at ten decimal places and include every top-ten boundary tie, as in prior studies. A county is certainly in the inclusive top ten if at most nine other upper endpoints strictly exceed its lower endpoint; it is certainly outside if at least ten other lower endpoints strictly exceed its upper endpoint. Otherwise classify membership as unresolved by these sufficient conditions. Report actual inclusive set sizes and never reinterpret these labels as risk categories or probabilities.

## Acceptance and execution boundary

Stop on mismatched hashes, missing/duplicate keys, unsupported bounds, failed baseline reconstruction, published-value drift, negative coefficients, nonpositive population, changed normalization behavior or failed conservation tests. Test county-specific bounds, clipping, fixed published values, missing-cache rows, coefficient path handling, endpoint ordering and interval/rank ties using synthetic data before the real calculation.

Save config/code/input/output hashes and verify all original/frozen files and listed release assets before and after execution. Do not overwrite any released inputs, scores, formulas or the dated report. No live query, source refresh, external validation or new release is part of this protocol. Implementation and execution require a separate research task/review; this branch verifies the cell mask and writes the protocol only.
