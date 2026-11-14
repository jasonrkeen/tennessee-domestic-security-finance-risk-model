# Intended-use and validation charter, version 1

Research specification | November 14, 2026 | No released-model change

## Intended use

The present research use is **descriptive county-level screening and prioritization of further evidence review** for the Tennessee Financial Security Risk Model. Its composite is an index of selected exposures and vulnerabilities under stated weights, source limitations and missing-value conventions. It is not a probability of crime, terrorism, financial loss or future harm, and its published category names are not calibrated outcome thresholds.

The unit is the county, not an individual, business or neighborhood. A higher score can identify a county for additional source review; it does not establish wrongdoing or justify enforcement, exclusion, credit decisions or resource allocation by itself. The historical release combines source vintages and is not a live county assessment. All released scores, formulas, data and the dated report remain the immutable reference.

## Research questions

1. Are the measurements and source definitions fit for this descriptive purpose, and are unavailable observations distinguishable from observed zeros?
2. How much do defensible source uncertainty and explicit weighting assumptions affect the screening order?
3. Does an independently assessed screening task benefit from the composite compared with simpler, transparent alternatives?

Completed effective-weight, overlap, constant-input and sensitivity audits address arithmetic and dependence. They do not answer question 3. The CBP bounding protocol addresses a narrowly supported portion of question 2, not all uncertainty.

## Descriptive validation design

Before collecting or inspecting validation outcomes, freeze a task-specific protocol identifying the intended reviewer, decision, time period, evidence sources, sampling plan and success criteria. Use county dossiers assembled independently of the score's input tables and rankings. Reviewers should receive a common evidence rubric and be blinded to index scores and experimental variant labels where feasible. Record source availability, disagreements and adjudication rather than forcing uncertain cases into binary labels.

Assess whether the index helps select cases warranting further evidence review, not whether reviewers agree with county reputations. Compare it with a prespecified simple baseline suited to the task, such as one transparent source measure or population-adjusted historical frequency, using the same counties and period. Include evidence-rich and evidence-poor counties; do not recruit cases solely because they support the model. Record inter-reviewer agreement, missing evidence, useful-case yield at a stated review budget and errors in both directions. A rubric derived from the same index inputs cannot independently validate the composite.

No external validation dataset, independent reviewer result or performance threshold is claimed here. The task owner must freeze the practical improvement required, tolerated error types, coverage minimum, sample-size rationale and uncertainty method **before** outcome evaluation. Until then, this charter supports protocol design, not a claim that a candidate passed validation.

## Predictive use is a separate gate

Any proposed predictive use requires a separately specified outcome, forecast horizon, data-availability cutoff, county/time support and prospective or genuinely untouched temporal holdout. Define incident date, report date, revision vintage and acquisition time separately. Freeze feature construction and selection on development data, then evaluate once on the holdout. A later-revised data extract is not automatically information available at the historical forecast origin.

Use identical holdout support for the candidate and simple benchmarks, prevent leakage from outcome-derived inputs, and account for county size, sparse counts, spatial dependence and uncertainty in reporting. Choose evaluation metrics suited to the defined outcome before scoring: discrimination/ranking alone is insufficient for probability claims, which also require calibration. A consumed holdout becomes development evidence; tuning requires a new untouched evaluation set. This branch does not select an outcome or claim predictive validity.

## Promotion and stopping rules

Keep the frozen release, research assumptions and independently validated claims separate. No sensitivity variant is promoted simply because its ranks resemble the baseline, appear intuitively reasonable, or reduce duplicated inputs. Stop an evaluation on failed source identity, leakage, incompatible vintages, changed outcome definitions or unresolvable county support. Report negative and inconclusive findings.

A future candidate needs an explicit measurement rationale, pre-evaluation protocol, independent evidence appropriate to its intended use, reproducible comparisons, quantified limitations and a separate review/release decision. No new weights, imputation, source replacement, threshold calibration, outreach or publication is authorized by this charter. Missing TBI export/filter evidence remains unresolved; no research calculation repairs that history.
