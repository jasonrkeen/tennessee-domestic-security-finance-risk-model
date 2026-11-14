# Constant-input and repeated-measurement sensitivity

Research results | November 14, 2026 | Released v1.0.1 preserved

All six variants in the [merged protocol](../missingness_constants/SENSITIVITY_PROTOCOL.md) were executed without amendment. Removing constant inputs changes score levels but leaves every county rank unchanged. The repeated-vector exclusion (D1) and its union with all constants (CD) produce the same county ordering: 59 counties move, the median absolute movement is one place, and the maximum is eight. Hancock enters the top ten and Hardeman exits; nine original members remain.

These are hypothetical weighting alternatives, not corrections, updated risk assessments or validation of historical source filters. No released score, data, formula, scenario, threshold or dated report was changed. The missing export remains unresolved.

## Design and execution gates

The protocol and exact exclusion sets were merged in PR #10 at `448e8d15e2a547d13bf9d083e079e40fc04fd933`. Their earlier “not executed” status is preserved as a historical record; this directory records execution. Config/code/protocol hashes are pinned in [config.json](config.json) and [verification.json](results/verification.json). This remains exploratory research informed by prior audits, not blinded preregistration.

The runner reads the v1.0.1 95-county table, SHA-256 `70821e90e66ff116f13d520317d0c390dce7843b2d5d9533ffbbb73bd67f1216`. It reuses the pinned effective-weight/overlap audit's read-only loader, verifies the all-FEMA-fallback regime, and reconstructs released final scores within rtol=atol=1e-12. Saved normalized values, county support and population denominators remain fixed. All seven D1 excluded vectors exactly equal their retained counterparts in this snapshot; the [pair checks](results/duplicate_checks.csv) do not establish that their source concepts are equivalent.

For excluded set F, C is its weighted contribution and W its flattened coefficient sum. Both `S-C` and `(S-C)/(1-W)` are reported. Exclusion removes every coefficient path of a selected leaf, leaving relative retained coefficients fixed. CD is a set union: its 18 leaves count the three shared constant gang-explosive leaves once. No new imputation or normalization occurs.

Ranks descend using average ties after rounding scores to ten decimal places. Top-ten membership includes every boundary tie; all sets here contain ten counties. Positive rank changes mean moving down. Source-family context is reported for the five largest absolute movements per variant, including all ties at that boundary (seven counties for each of D1 and CD). There are no nonzero movements to explain for C1–C4.

## Results

| Variant | Exclusion | Weight removed | Constant points removed | Rank correlation | Median / maximum absolute movement | Top ten retained |
|---|---|---:|---:|---:|---:|---:|
| C1 | Optional training, retail and range constants | 3.85000% | 1.925000 | 1.000000 | 0 / 0 | 10/10 |
| C2 | Unsupported category/mapping constants | 1.40400% | 0.702000 | 1.000000 | 0 / 0 | 10/10 |
| C3 | Blank-derived TBI constants | 2.43625% | 1.218125 | 1.000000 | 0 / 0 | 10/10 |
| C4 | All 14 constants | 7.69025% | 3.845125 | 1.000000 | 0 / 0 | 10/10 |
| D1 | Six gang-explosive leaves and gang-total leaf | 3.50000% | 0.455000 | 0.997368 | 1 / 8 | 9/10 |
| CD | Union of C4 and D1 | 10.28025% | 3.845125 | 0.997368 | 1 / 8 | 9/10 |

The unscaled C4 score is exactly the baseline minus 3.845125 within numerical tolerance. After renormalization, its mean change is -1.415167 points and its county changes range from -2.529303 to +0.746513. Thus removing constant contributions need not lower every renormalized score; the denominator also changes. The full [summary](results/summary.csv) gives retained weights and minimum/mean/maximum level changes for both scales for every variant.

D1's mean renormalized score change is +0.395544 points (range -0.888397 to +0.845819). CD's mean is -0.858291 (range -2.585094 to +1.337330). CD removes an additional common 3.390125 points from D1's unscaled numerator and then rescales by a positive common denominator. Their identical ranks are therefore an arithmetic consequence, not two independent confirmations of robustness.

## Largest movements and contribution context

In both D1 and CD, Anderson moves from 29 to 37 and DeKalb from 32 to 40. Marshall moves from 56 to 62 and Van Buren from 80 to 86. Decatur (39 to 35), Pickett (60 to 56), and Polk (38 to 34) each move up four places. The [county table](results/county_variants.csv) contains all 570 county/variant observations, including unchanged ranks.

For D1, all removed leaves belong to the scored TBI family. Anderson loses 1.392919 unscaled contribution points; after renormalization, its TBI contribution changes from 6.692609 to 5.491907. DeKalb loses 1.325292 unscaled points and its TBI contribution changes from 6.426163 to 5.285877. Van Buren has the largest excluded contribution, 1.852592 points. Nonexcluded families receive larger effective coefficients through renormalization, partly offsetting these losses. A county can move up in rank even as its TBI contribution falls, because ranks depend on all counties' relative changes.

The [family-context table](results/largest_movement_context.csv) reports baseline, excluded, research and change contributions for all eight source families for every highlighted county in D1 and CD. Source-family attribution is to scored leaves; removing a family does not remove population denominators sourced elsewhere.

## Interpretation and limits

Constant-only rank invariance does not validate the underlying inputs. High overall D1 rank correlation coexists with a top-ten membership change and eight-place local movements. D1 is one specified choice of representative: retaining a differently weighted duplicate instead can yield different results. Numerical equality, including equality after blank-to-zero processing, is not evidence of independent measurement or verified source semantics.

Released risk-category cutoffs are not applied to these research scores. No current source query, recovered evidence, missing-value bound, probability distribution, confidence interval, predictive outcome or temporal holdout is supplied by this study. It does not select a replacement model or justify a new release. The next decision is whether the intended use and external validation evidence support a separately defined candidate; stability alone cannot do that.

## Reproduction and validation

```powershell
python -m research.constant_sensitivity.run --saved-scores "<v1.0.1-package>/outputs/tables/tn_county_domestic_security_scores.csv"
python -m pytest -q
```

Outputs stay in this directory's `results/`; no production pipeline or source processor runs. Inputs and dependencies are checked before and after calculation. The run stops on changed protocol hashes, county/indicator mismatch, nonfinite values, failed duplicate equality, union errors, failed baseline reconciliation or unexpected constant-only rank movement. All prespecified variants are reported.

All 84 offline tests passed (188 existing pandas fragmentation warnings), including eight new synthetic tests covering hand-calculated exclusion arithmetic, family contribution reconciliation, union overlap, boundary ties and rejected protocol drift. The [preservation record](results/preservation.json) separately verifies 170 original files, 170 frozen copies and five listed release assets. Integrity and arithmetic checks do not establish external validity.
