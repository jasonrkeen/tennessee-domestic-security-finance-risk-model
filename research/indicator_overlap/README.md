# Indicator overlap and leave-one-family-out analysis

Research results | November 13, 2026 | Preserved v1.0.1 baseline

The county ordering is most sensitive to removing socioeconomic indicators. Removing all scored TBI leaves changes five of the original top-ten memberships. Several saved TBI vectors are identical, while other near-perfect correlations arise from sparse observations. These findings identify measurement and weighting questions for further review; they do not establish which alternative model is more accurate.

This branch adds research analysis and tests. Released scores, rankings, data, normalization, formulas, scenarios, thresholds and the November 10 report remain unchanged. Every alternative score below is a research calculation, not a replacement county assessment.

## Scope and design

The analysis reads the 95-county score table distributed in [v1.0.1](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/releases/tag/v1.0.1). Its SHA-256 is `70821e90e66ff116f13d520317d0c390dce7843b2d5d9533ffbbb73bd67f1216`. Source formulas are pinned to `35ab5cc1635a7d1499998e7409d005bfc01bbeb6`; the effective-weight audit was merged at `f3d655d6bc37b5de609d717ae82cc1b6317f9483`.

The [effective-weight audit](../effective_weights/README.md) supplies the flattened baseline coefficients. All 95 released counties use the FEMA fallback. This study holds that branch, normalization endpoints, population denominators and all saved normalized values fixed. It does not re-estimate min-max scaling, alter missing-value handling, refresh sources, or evaluate the other ten weighting scenarios or operational-risk layer.

Two disjoint partitions are specified in [config.json](config.json): eight source families and fifteen finer component families. Every active normalized indicator belongs to one family in each partition; each partition covers 100% of the baseline coefficient mass. The groupings were specified before this run's correlation and exclusion calculations, but this is an exploratory retrospective study, not a preregistered validation. Selected saved-column equality checks were added after inspecting the correlations.

“Source family” means scored terminal indicators attributed to that source, not every piece of information derived from that agency. For example, excluding ACS socioeconomic leaves does not remove Census population denominators from other rates. The finer groups are also terminal-leaf groups, not the original nested composites. All repeated paths to a selected leaf are removed together.

## Indicator overlap

There are 74 active normalized indicators. Fourteen are constant at 50 across all counties. Correlations involving a constant are recorded as unavailable, not zero. Of 2,701 distinct indicator pairs, 1,770 have estimable correlations. Thirty-one have absolute Spearman correlation at least 0.80, and sixteen at least 0.95. These are descriptive screening cutoffs, not significance tests or automatic deletion rules.

| Finding in the saved table | Evidence | Interpretation |
|---|---|---|
| Explosive and gang-explosive total, violent and weapon-law indicators match | Three varying normalized pairs are exactly equal; the corresponding saved count columns also match across all 95 counties | The two composite scores are identical. Their separate 2.6% coefficients create a combined 5.2% coefficient on the same saved composite vector. This is numerical duplication in this snapshot; its acquisition or filtering cause is unresolved. |
| Gang-related total and overall crime count match | Saved count columns are exactly equal across all 95 counties; normalized pressure columns are also equal | Their terminal weights of 0.9% and 1.125% sum to 2.025% on one saved normalized vector. Review export filters and mappings before interpreting these as independent evidence. |
| Protest and public-disorder measures closely track | Spearman 1.000; Pearson approximately 0.999987; 72 joint normalized-zero rows | Identical ordering does not mean identical values. The source classification already puts protests in public disorder, so structural overlap is expected. |
| Hate-crime weapon-law and violent-unrest normalized indicators match | Both equal 100 in Davidson and zero in the other 94 counties | One jointly positive county produces an exact match. It does not establish a general empirical relationship or shared incidents. |
| ACLED fatalities and political-violence measures have identical ordering | Spearman 1.000; Pearson approximately 0.850; 93 joint normalized-zero rows | The result rests on two nonzero counties, not broad independent corroboration. |
| Overall supplied crime rate and count-derived rate closely track | Spearman approximately 0.995591; Pearson approximately 0.998656 | Both are rate measures; differences in denominators or construction still matter. |

Five pairs of varying normalized indicators are exactly equal. Equal values do not prove an ingestion bug, shared source records or a valid source filter. The [saved-column comparisons](results/saved_column_comparisons.csv) establish only what is present in this released table. No historical raw exports were reacquired or reauthenticated.

The 14 constant leaves carry 7.69025% of baseline coefficient mass and contribute 3.845125 score points to every county. They affect score levels but do not distinguish counties in this snapshot. Their constant value does not by itself distinguish observed uniformity from earlier missing-data defaults. The optional local-access family consists entirely of three such leaves: training, surplus/tactical retail and gun-range density. Its 3.85% coefficient contributes 1.925 points to every baseline score.

Broad family subindices show less correlation than some individual pairs. The largest absolute cross-source-family Spearman correlation among nonconstant families is approximately 0.412, between CBP business indicators and TBI public safety. Aggregation can obscure duplicated indicators within a family; it does not eliminate them. The [family correlations](results/family_correlations.csv) include both partitions.

## Leave-one-family-out method

For county i and family F, let the preserved baseline be S, the family's weighted contribution be C, and its sum of flattened coefficients be W:

`retained score = S - C`

`research score excluding F = (S - C) / (1 - W)`

The implementation sums retained leaves directly and verifies that retained plus excluded contributions reconstruct the saved baseline within `rtol=atol=1e-12`. The remaining coefficients retain their relative proportions. No normalization or within-parent weights are recalculated. Removing a family therefore removes every path to its leaves, including paths through other named composites.

The unscaled retained score and the renormalized score have the same ordering for a given family because W is fixed across these counties. Both are saved for interpretation. Their level differences from the baseline partly reflect the scale change; original Low/Guarded/Elevated/High cutoffs are not applied to research variants.

Rank metrics use descending average ranks, with scores rounded to ten decimal places only for tie handling. Top-ten sets include all counties tied at the boundary. In this run, all compared top-ten sets contain exactly ten counties. Positive county rank changes mean moving down the ordering. Spearman agreement is computed on the tie-aware baseline and research ranks.

## Broad source-family results

| Scored family excluded | Weight removed | Rank correlation with baseline | Median absolute rank change | Largest rank change | Original top ten retained |
|---|---:|---:|---:|---:|---:|
| ACS socioeconomic | 23.64% | 0.757 | 10 | 67 | 6/10 |
| CBP business | 10.36% | 0.914 | 8 | 38 | 7/10 |
| TBI public safety | 24.50% | 0.917 | 7 | 40 | 5/10 |
| FEMA declarations | 12.90% | 0.929 | 6 | 35 | 7/10 |
| ACLED events | 15.00% | 0.974 | 2 | 28 | 9/10 |
| ATF FFL | 4.95% | 0.986 | 2 | 17 | 10/10 |
| FDIC banking | 4.80% | 0.987 | 2 | 17 | 8/10 |
| Optional local access | 3.85% | 1.000 | 0 | 0 | 10/10 |

The ACS family is 23.64%, rather than the earlier audit's 22.2% household composite coefficient, because this family also removes the additional poverty path embedded in tobacco/vape exposure. The extra 1.44 percentage points are not a new weight.

Removing ACS leaves moves Hancock from rank 11 to 78, the largest movement in these source-family variants. Removing TBI leaves moves Lauderdale from rank 6 to 46. These are examples of dependence on the selected inputs, not findings that either county's actual conditions changed. The [county diagnostics](results/county_ablation.csv) provide every county movement and candidate score.

FDIC exclusion has high overall rank agreement but changes two top-ten memberships. ACLED exclusion has a median movement of two places but a maximum of 28. These examples show why a single global correlation or median is insufficient to characterize stability.

Optional local-access exclusion leaves all rankings unchanged because the removed contribution is constant. This is an arithmetic consequence, not evidence that the fields are measured adequately or unimportant outside the saved snapshot.

The fifteen finer component exclusions are also reported. Excluding either explosives or gang-explosives gives the same rankings: Spearman 0.997830, median absolute movement 0, maximum 9, and 9/10 retained. Small individual exclusion effects can occur because an identical vector remains elsewhere in the model. Low sensitivity to removing one duplicated component is not evidence of independent information or lack of duplication.

## Evidence quality and limits

- Correlations describe saved normalized values, including historical zero filling and constant-series defaults. They do not resolve TBI blank semantics, CBP unpublished values or ACLED acquisition completeness. A normalized zero can be the observed minimum, not a verified absence of events.
- No new imputation is performed. Missing, nonfinite, differently versioned or unexpected input tables fail the analysis. Constant correlations are unavailable. Joint normalized-zero counts are supplied to reveal sparse patterns, not to recode them as observed absences.
- Counties have different population sizes and may be spatially dependent. Shared denominators, overlapping event categories and mixed source years can induce association. No independence-based p-values or confidence intervals are claimed.
- Removing an entire family is a structural stress test. It is not a realistic forecast, source outage simulation, optimal feature-selection rule or out-of-sample test. Grouping choices and the original coefficients affect the results.
- Current formulas and data are held fixed. No comparisons against a defined future outcome, causal identification, external calibration or improvement in predictive accuracy are established.

## Reproduction and deliverables

Use the repository's locked Windows/Python environment. Download and verify [v1.0.1](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/releases/tag/v1.0.1), extract it outside this checkout, then run from the repository root:

```powershell
python research/indicator_overlap/analyze.py --saved-scores "<release-folder>/outputs/tables/tn_county_domestic_security_scores.csv"
python -m pytest -q
```

The analysis reads the exact pinned table and the prior effective-weight code. It never calls `main.py`, collectors, or live APIs. It writes only the new research results directory. No randomness is used. Formula and input hashes are checked, and the input is hashed again after analysis. The release table itself is not committed to this branch.

| Artifact | Contents |
|---|---|
| [Configuration](config.json) | Exhaustive family assignments, pinned input/code, rank and screening rules |
| [Indicator profiles](results/indicator_profiles.csv) | Weights, constants, unique values and normalized-zero counts |
| [Indicator correlations](results/indicator_correlations.csv) | All 2,701 pairs; Pearson/Spearman, exact equality and sparsity diagnostics |
| [Family profiles](results/family_profiles.csv) | Family weights, constant shares and mean score contributions |
| [Family correlations](results/family_correlations.csv) | Correlations of disjoint weighted family subindices |
| [Exclusion summary](results/ablation_summary.csv) | All 23 source/component exclusions and top-ten changes |
| [County diagnostics](results/county_ablation.csv) | 2,185 explicitly labeled research county-variant rows |
| [Saved-column comparisons](results/saved_column_comparisons.csv) | Six follow-up equality checks, without source-cause claims |
| [Verification](results/verification.json) | Input/code hashes, analysis counts and result hashes |

The run also generates `source_family_rank_sensitivity.png` and `source_family_overlap.png`. These figures are excluded from Git and supplied with the local research deliverable; the committed CSVs contain their underlying values. Charts use a fixed -1 to +1 correlation scale and show unavailable correlations separately from zero. They were visually inspected. Re-running in the locked environment reproduced the result files byte for byte.

Tests use synthetic data and exercise exclusion arithmetic, repeated-path coefficients, constant-family invariance, sparse equality, missing correlations, boundary ties, partition reconstruction and rejection of a mismatched input version. No real observations are copied into test fixtures.

## Prioritized follow-up

1. Trace the matching TBI vectors through retained local exports, filter records and processors. Establish whether the selected measures are substantively distinct before interpreting or changing their weights. Exact numerical matches are documented; their provenance cause remains open.
2. Specify how a candidate should treat repeated measurements and constant/unverified inputs. Compare a deliberately defined candidate with the frozen baseline; do not silently delete correlated fields or convert unknowns to zero.
3. Evaluate candidate changes against a stated research purpose and, if prediction is intended, a defined outcome and temporal holdout. Rank stability alone cannot choose a valid model.

The released model remains the reference throughout these steps. No further outreach, data refresh, scoring change or publication of a new model version is part of this analysis.

Source interpretation is bounded by the [dated source review](../../docs/final-report-2026-11-10/README.md), [normalization/scoring code](../../src/risk_scoring.py), [ACLED classification](../../src/acled_processor.py), and prior [effective-weight audit](../effective_weights/README.md). The decisive empirical evidence in this report is the hash-pinned published table, not a newly authenticated upstream dataset.
