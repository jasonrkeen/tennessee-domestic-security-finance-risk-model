# Evidence-limited sensitivity protocol, version 1

Status: specified before new variant calculations; **not executed** in this branch. This is an exploratory follow-up informed by earlier overlap and leave-one-family-out results, not a blinded preregistration or predictive validation.

## Question and fixed reference

How much does the preserved county ordering depend on repeated measurements and indicators whose constant values lack verified observed-zero evidence? This study tests arithmetic dependence on explicit assumptions. It cannot decide the correct historical filters, recover missing values, or select a scientifically validated replacement model.

Use only the hash-pinned v1.0.1 95-county score table and the `fema_fallback`, `final` coefficients in the effective-weight audit. Preserve saved normalized values, population denominators, county support and the FEMA fallback. Do not invoke the production pipeline or recompute normalization. The reference is the released final score, reconstructed from terminal coefficients to rtol=atol=1e-12 before any variant. Reject missing, nonfinite, duplicate-county or hash-mismatched inputs. No random simulation or seed is needed.

## Prespecified variants

The exact constant-indicator membership is recorded in `config.json`; use evidence-class membership rather than interpreting all zeros as equivalent.

| ID | Excluded terminal indicators | Purpose |
|---|---|---|
| C1 | Three `unverified_zero_optional_input` leaves | Isolate the optional training, retail and range inputs |
| C2 | One `category_absent_from_retained_listing` and two `metric_absent_from_retained_mapping` leaves | Isolate unsupported source-category/mapping zeros |
| C3 | Eight `blank_export_cells` leaves | Isolate blank-derived TBI constants |
| C4 | Union of C1, C2 and C3: all 14 constants | Quantify their combined level contribution; unchanged ordering is an expected arithmetic control |
| D1 | All six `gang_explosive_*_pressure_score` terminal leaves plus `gang_related_total_pressure_score` | Retain one representative of each documented repeated vector; this is a hypothetical redundancy choice, not proof the labels describe the same construct |
| CD | Union of C4 and D1, counting overlapping leaves only once | Joint constant/duplication stress test |

Exact exclusion sets, including D1's six gang-explosive leaves and one gang-total leaf, are frozen in `config.json` under `sensitivity_exclusion_sets`. Before execution, validate those names against the pinned weight table and confirm pairwise equality with the retained explosives counterparts and overall-crime count pressure score. If the names/support/equality checks fail, stop and revise the protocol explicitly; do not select substitutes after viewing ranks. Removing the other representative can change results because its coefficient differs; D1 is not a unique deduplication rule. Do not generalize it to merely correlated indicators.

For variant set F, let C_i be the sum of its weighted saved values and W the sum of its flattened coefficients across every path. Report both `S_i - C_i` and `(S_i - C_i)/(1-W)`, with retained and excluded contributions reconciling to baseline. Assert 0 <= W < 1. Relative coefficients among retained leaves stay fixed. These are research scores only. Do not apply released risk-category thresholds or overwrite released ranks.

## Missingness uncertainty, separate from exclusion

Do not replace blanks, unpublished CBP cells, unknown county coverage, or absent source categories with asserted observed zeros. This audit preserves the released fallback numbers solely as the reference. No new imputation is authorized by this protocol.

A later bounding study would require a separately frozen county-by-indicator missingness mask and defensible domain bounds. The documented CBP 0–2 interval applies to the particular unpublished cells identified in the prior source review; it is not a general bound for TBI or ATF. Do not assign arbitrary probability distributions or call scenario ranges confidence intervals. Leave values unresolved when their support/bounds cannot be justified.

## Required outputs and decision rules

Report every prespecified variant, including small or null changes: retained weight, constant contribution, score-level changes, Spearman rank agreement, median/maximum absolute rank movement, per-county rank movement and top-ten membership retained/lost/gained. Rank descending with average ties after rounding scores to ten decimal places; include all boundary ties in top-ten sets and report actual set sizes. Report the largest movements with source-family contribution context. Do not cherry-pick a variant based on agreement with expected county reputations.

Constant-only exclusions must preserve county ordering within the stated tie convention; explain numerical tie-boundary effects if any. D1 must remove all paths of each selected leaf. CD must deduplicate its exclusion set. Reject a run if reconstruction, support, preservation hashes or test gates fail. Numerical stability is not evidence of construct validity, acquisition completeness, prediction or causal effects.

Any later promotion requires a stated use case and independent validation criteria. Predictive claims additionally require a defined future outcome, leakage controls and an untouched temporal holdout. This protocol supplies neither those outcomes nor a promotion rule.

## Execution boundary

Implementation and execution of these variants require a separate research task/review. Store any results only under a new `research/` location, with input/config/code hashes and tests of exclusion arithmetic, overlap handling and ties. Retain this protocol version/hash and explain amendments before running changed variants. No release, source refresh, outreach, formula edit, data replacement or dated-report rewrite is authorized by this document.
