# Effective-weight audit of the preserved Tennessee county model

Research audit | November 13, 2026 | Baseline: v1.0.1, commit `35ab5cc1635a7d1499998e7409d005bfc01bbeb6`

The headline weights understate the total coefficients of several components because the same components enter through multiple paths. Household financial stress carries 22.2% after expansion, tactical access 11%, and disaster/disruption 12.9%. These are properties of the existing formulas, not proposed replacement weights. The audit changes no source data, scoring formula, scenario, county score, rank, threshold, or dated report.

All 95 published baseline scores and all ten scenarios reconcile to the expanded formulas at relative and absolute tolerance `1e-12`; the largest absolute difference is `4.263256414560601e-14` score points. Every published county uses the FEMA fallback for disruption. The full optional-disruption formula is therefore documented as a separate regime, not described as active in the release.

## What an effective weight means

For a linear path, multiply the coefficients along the path. For an indicator that appears through several paths, add those products. For example:

`household financial stress = 0.15 + (0.30 × 0.24) = 0.222`

The audit ends at normalized indicators on the model's 0–100 scale. A coefficient of 0.0921 means that one point in that normalized indicator contributes 0.0921 final-score points, holding the other normalized indicators fixed and retaining the same disruption regime. It does not mean that the indicator explains 9.21% of observed variation, causes 9.21% of risk, or accounts for 9.21% of a particular county's score.

Raw-count changes can alter rates, correlated indicators, normalization endpoints and the disruption regime. A normalized coefficient is not a raw-count marginal effect. Min-max scaling, inverse scaling, missing-value defaults and constant-series scores remain outside the linear expansion. Shared underlying events or populations can connect distinct normalized leaves even where the algebra contains no repeated leaf.

## Main baseline findings

| Component | Direct final-score weight | Total through all paths | Explanation |
|---|---:|---:|---|
| Household financial stress | 15% | 22.2% | Direct plus finance/tactical: 15 + 30 × 0.24 |
| Tactical access | 5% | 11% | Direct plus finance/tactical: 5 + 30 × 0.20 |
| Disaster/disruption | 10% | 12.9% | Direct, finance/tactical, institutional: 10 + 30 × 0.08 + 5 × 0.10 |
| Crime/weapons pressure | 0% | 7% | Organized violence and institutional: 20 × 0.30 + 5 × 0.20 |
| Overall crime-rate index | 0% | 3.75% | Organized violence and institutional: 20 × 0.15 + 5 × 0.15 |
| Targeted harm/public safety | 0% | 2.7% | Organized violence and institutional: 20 × 0.11 + 5 × 0.10 |
| Law-enforcement ambush | 0% | 2.465% | Through targeted harm plus institutional: 2.7 × 0.45 + 5 × 0.25 |

These rows mix levels of the hierarchy and **must not be summed**. They describe coefficients at different intermediate nodes. Only terminal weights for a single score and regime form a partition summing to 100%.

At the terminal level, poverty has three paths: 5.25% through the direct household component, 2.52% through household stress within finance/tactical, and 1.44% through poverty-adjusted tobacco/vape exposure. Its total coefficient is **9.21%**, the largest terminal weight in the released baseline. Income stress and unemployment each carry 5.55%; rent burden carries 3.33%. The extra poverty path is in addition to the 22.2% household component, not another independent socioeconomic observation.

Source: [final composites](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/risk_scoring.py#L1053), [household stress](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/risk_scoring.py#L336), and [poverty-adjusted retail](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/risk_scoring.py#L421).

## Disruption: formula weights depend on the branch

The scorer tests three groups: weather counts, outage count, and the duration/stress/recovery fields. A positive sum in any group activates the optional Phase 6 formula. Otherwise, it replaces the entire disruption composite with the FEMA infrastructure component. The audit reads this condition from the pinned source and evaluates it on the saved scored frame.

In all 95 released counties, the fallback is active. The final-score weights are therefore:

| FEMA normalized indicator | Released baseline effective weight |
|---|---:|
| Disaster declarations | 6.45% |
| Disaster-type diversity | 3.225% |
| Recent disaster declarations | 3.225% |
| Optional weather, outage, access and recovery indicators | 0% |

Stored optional components can equal 50 because their inputs are constant. In these released rows, those optional components do **not** contribute through the disruption composite: the fallback replaces it. This narrows the earlier generic concern about neutral-looking optional scores. FEMA itself remains a historical exposure proxy, not measured current resilience.

When the optional formula is active, recent disaster declarations enter both directly and through infrastructure disruption. Their combined final weight is 2.74125%; severe-weather exposure carries 2.58%. Both regimes sum to 100% over terminal leaves: 74 leaves under fallback and 84 under the active formula. These counts do not represent independent data sources.

Source: [conditional disruption formula and override](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/risk_scoring.py#L1008).

## Repeated measurements and interpretation

- **ACLED:** protest, public-disorder and total-event normalized measures each receive 3% of the final baseline score, collectively 9% out of the ACLED component's 15%. The processor counts protests within public disorder and total events. These are overlapping measurements, not three independent corroborating sources. Political-violence and violent-unrest measures each receive 2.25%, and fatalities 0.75%. The source comment saying violent measures are weighted more heavily does not match these individual formula coefficients. This audit records the discrepancy without changing the released source. [Classification](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/acled_processor.py#L239), [weights](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/risk_scoring.py#L917).
- **Crime totals and subsets:** the broad violent-crime measure can contain homicide, assault and other categories that are also scored separately. The processor creates a partial violent-crime sum when the exported total is absent. Algebraic path counting alone cannot quantify the resulting empirical redundancy. [Fallback construction](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/crime_offense_processor.py#L513).
- **Overall crime-rate index:** contrary to the earlier review's raw-count description, the count input is passed through `per_capita` before min-max normalization. The two terminal weights are 2.625% for the supplied rate and 1.125% for the count-derived rate. Their redundancy depends on matching numerators and denominators; the audit does not assume equivalence. [Implementation](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/risk_scoring.py#L557).
- **FFL measures:** total density contributes 2.75%, while the combined subtype component contributes another 2.2%. Categories can overlap; their coefficients do not establish independent evidence of unlawful activity. [FFL composite](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/src/risk_scoring.py#L467).
- **TBI selections:** gang/explosives filters and clearance-versus-offense distinctions remain as documented in the final source review. A precise coefficient does not improve the validity or completeness of the underlying measure. [Source review](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/blob/35ab5cc1635a7d1499998e7409d005bfc01bbeb6/docs/final-report-2026-11-10/README.md).

## Scenario implications

Headline scenario weights also omit indirect paths. Selected examples:

| Scenario | Selected component | Direct weight | Effective weight |
|---|---|---:|---:|
| Socioeconomic-heavy | Household financial stress | 37% | 41.32% |
| Tactical-access-heavy | Tactical access | 25% | 29.6% |
| Disaster/disruption-heavy | Disaster/disruption | 35% | 37.14% |
| Targeted-harm/public-safety-heavy | Law-enforcement ambush | 10% | 22.464% |

The ambush example includes direct entry, targeted harm, organized violence and institutional paths. This is useful evidence for reviewing the scenario's intended emphasis; it is not a finding that 22.464% is necessarily wrong. All ten scenarios, including baseline, are expanded in the tables. Interactive dashboard slider combinations and the separate operational-risk layer are outside this audit.

## Reproduction and evidence

Use the repository's locked Python environment, from the repository root:

```powershell
python research/effective_weights/audit.py
python -m pytest -q
```

The first command regenerates formula tables and checks three frozen synthetic cases. It never calls the pipeline, fetches source data, or writes to the model's `data/` or `outputs/` directories. It overwrites only the audit's `research/effective_weights/results/` files. No randomness or simulation is used. Source hashes are normalized to LF line endings and pinned in `config.json`; a changed source fails closed and requires a separately reviewed audit update.

To reproduce the additional published-data reconciliation, download and verify the [v1.0.1 release](https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model/releases/tag/v1.0.1), extract it outside the checkout, and supply the two preserved tables:

```powershell
python research/effective_weights/audit.py --saved-scores "<release-folder>/outputs/tables/tn_county_domestic_security_scores.csv" --saved-scenarios "<release-folder>/outputs/tables/model_weight_sensitivity_results.csv"
```

The checked-in verification record includes that optional reconciliation. A default run replaces it with synthetic-only evidence; it does not claim to repeat the published-data check. Input hashes are checked before and after reading; saved data is never written. The public tables are not copied into this branch.

| Artifact | Purpose |
|---|---|
| [Terminal weights](results/terminal_weights.csv) | Exact fractions, percentages, path counts and normalization expressions; sum to 100% per score/regime |
| [All paths](results/paths.csv) | Every root-to-terminal coefficient product |
| [Node weights](results/node_weights.csv) | Total incoming coefficients at each level; not additive across levels |
| [Equations](results/equations.csv) | Extracted parent-child coefficients with source locators |
| [Verification](results/verification.json) | Pinned sources, fixture hashes and reconciliation errors |

The extractor handles the pinned scalar sums, the equal-weight cash-category mean, normalization boundaries and the conditional FEMA override. Exact fractions avoid rounding during coefficient expansion. New tests independently check shared paths, hand-calculated weights, both conditional regimes, mixed-regime rows, source drift, group-sum semantics and frozen-score reconstruction. Existing regression tests continue to protect production behavior.

Reconciliation is deliberately conditional on the saved normalized columns. It verifies algebra and branch handling; it does not revalidate raw-source acquisition, missingness, county completeness, normalization choices, predictive performance or causal interpretation. Scenario ranks are not recalculated. The reconstruction leaves their underlying scores unchanged within the stated tolerance.

## Research disposition

Retain the released model as the reference. Before proposing new weights, specify whether repeated paths are intentional emphasis or unintended duplication. Next compare normalized-input correlations and leave-one-family-out variants in a separate candidate, with explicit missing-data rules and fixed normalization choices. Any score or rank changes belong in that candidate and require their own evidence; none is part of this audit.
