# Tennessee county risk research

## Final report for the current model and source review

Jason Keen | November 10, 2026 | Research release 1.0

The project now has a consolidated research output: the preserved county scores, reviewed source-coverage diagnostics, and an evidence record explaining what the results can and cannot support. No additional outreach is required to complete this release. Unresolved source questions are retained as limitations rather than converted into assumptions of complete reporting or zero events.

### Main findings

The model is a relative index across Tennessee's 95 counties. It combines socioeconomic conditions, banking access, lawful business and licensing aggregates, public-safety reports, political-violence and civil-unrest records, and disaster indicators. Population adjustments, min-max transformations and selected weights produce comparative scores. The result is not a calibrated probability of a future incident, a measure of criminal intent, or a finding about individual people or businesses.

The missing-source repair corrects inflated availability and coverage labels while preserving the numerical scoring logic. The original local replay passed 42 comparisons, including saved historical results, ten weighting scenarios and ranks. A subsequent CBP coverage review passed 12 additional table comparisons. These are numerical and engineering checks; they do not demonstrate predictive accuracy or the validity of the selected proxies. [1, 2]

This release freshly verified all 170 original input/output files and all 170 frozen copies against the original hashes. All matched. All 39 regression tests passed locally. The package copies 12 historical score/scenario tables byte for byte and provides a 95-county summary that pairs unchanged scores with the separately reviewed coverage assessment. [1, 2, 8]

### How to use the result

Use the report and county summary for research discussion and examination of assumptions. Read a county's score alongside its source limitations. The model's labels such as Low, Guarded and Elevated are inherited index categories, not externally validated safety ratings. A lower score is not evidence that unobserved harm is absent.

The final release preserves uncertainty about filtered TBI blanks, unpublished Census cells and ACLED acquisition completeness. The all-zero disruption input remains unverified. NOAA and CDC work is retained as candidate/context analysis and has not been added to the scoring model. [2–6]

### Release boundary

The research package is complete within this preserved-score scope. It is not a production deployment or a declaration of predictive validation. PR #2 remains open and in draft, verified November 10. No push, merge, source refresh or scoring change was performed. The existing dashboard and original historical reports were not republished. [8]

---PAGE---

# Preserved county results

The frozen model assigns one county to Elevated, 27 to Guarded and 67 to Low. These are the existing model categories. The ten highest numerical results are shown below to make the preserved output transparent, not to designate the most dangerous counties. Figures are rounded here; the CSV retains the original score strings. [1, 8]

| County | Preserved score | Model category | Reviewed coverage percent | Coverage band |
|---|---:|---|---:|---|
| Davidson | 58.96 | Elevated | 92.86 | High |
| Shelby | 54.79 | Guarded | 85.71 | High |
| Madison | 43.39 | Guarded | 57.14 | Moderate |
| Hamilton | 40.19 | Guarded | 85.71 | High |
| Hamblen | 39.22 | Guarded | 57.14 | Moderate |
| Lauderdale | 39.09 | Guarded | 64.29 | Good |
| Jackson | 38.42 | Guarded | 57.14 | Moderate |
| Hardeman | 38.32 | Guarded | 64.29 | Good |
| Lake | 38.21 | Guarded | 57.14 | Moderate |
| Coffee | 38.12 | Guarded | 57.14 | Moderate |

### What coverage means

The separately reviewed coverage assessment has 4 High, 29 Good and 62 Moderate counties. The initial missingness repair yielded 7 High, 48 Good and 40 Moderate; the additional CBP review explains the difference. The historical outputs labeled all 95 High. These are three different documentation states, not changes in the numerical risk scores. [1, 2]

Coverage percentages count available input layers under the reviewed rules. They are not the percentage of incidents observed, a statistical confidence interval, a probability of correctness, or certification of agency reporting. Positive legacy values in some sources still rely on an availability inference; missingness erased upstream cannot always be recovered. A High coverage band therefore does not establish independently validated data. [2]

### Why scores were preserved

Changing missingness handling in the numerical scorer, replacing a measure, removing a proxy or changing weights would alter the substantive model. Those changes require separate review. This release preserves the historical numbers while making their limitations visible. It does not suggest that numerical parity makes zero-filled inputs scientifically preferable.

The package's main county_results.csv is the recommended starting point. The preserved_score_tables directory contains unmodified historical artifacts, including their old quality columns and notes. Those old columns are retained for provenance and must not be used as the current coverage assessment. Use reviewed_coverage for that assessment. [8]

---PAGE---

# Source findings and final dispositions

### TBI CrimeInsight

The four preserved selections use Incident Date 2024 and were generated May 28, 2026. Usable observed inputs exist for 24 counties in explosives, 24 in gang plus explosives, 31 in the hate-crime clearance input, and 4 in ambush. The respective 71, 71, 64 and 91 gaps remain unverified. These are county/input classifications, not incident totals or nonreporting-agency counts. The gang selection retains an Explosives filter; the hate-crime input uses an All Clearances block. Broader labels must not erase those distinctions. [1, 7]

The locally reviewed Crime in Tennessee 2024 publication, PDF page 3, identifies a June 20, 2025 snapshot, reports no agencies failing reporting compliance at release, and lists 13 covered-by agency relationships. This adds affirmative reporting context. It does not define blanks in our later filtered exports, provide their agency-month acceptance ledger, or independently certify Tennessee_UOF coverage. The covering letter is dated August 15, 2025. [7]

Jason's November 10 call debrief attributes daily refreshes and possible revisions/clearance updates to Steven Jancarek. That helps explain why data states can change; it does not establish the cause of a particular difference or prove a blank is zero. No further email is planned. Remaining source questions are explicit limitations of this release. [7]

### Census County Business Patterns

Of 760 selected 2023 county/industry cells, 368 published values matched the saved cache. The other 392 are unpublished. Census clarified that those cells contain zero, one or two establishments without revealing the exact count; exactly three establishments are published. Eight counties have all eight selected categories. Keep unpublished cells distinct from observed zeros. Numerical compatibility with 2023 does not authenticate the original retrieval history. [2, 3]

### ACLED

The saved extract contains 336 unique events: 203 in 2023 and 133 in 2024, across 27 counties. Independent local aggregation reproduced all 189 represented-county aggregate values and reconciled 665 corresponding county/field entries in the master. The 68 absent counties already have no rows in the raw extract. The checked processing did not lose those counties; historical acquisition completeness and real-world absence remain unverified. [6]

### Disruption inputs

The existing all-zero 95-county, 15-field disruption file matches the pinned loader's generated template byte for byte. That supports unverified status, not a proven historical creation story or zero disruption. The current numerical scorer assigns 50 to a constant input series, so neutral-looking component scores can arise without observed variation. Preserve the output, but do not describe it as measured county resilience. [2, 8]

---PAGE---

# Candidate sources and methodological limits

### NOAA Storm Events

The 2024 Tennessee extract has 1,677 distinct event reports: 846 county-coded and 831 forecast-zone-coded. Historical NWS correlation files assign each zone-coded record to one county. The checked Tennessee zone-to-county relationships agree across the inspected releases. These administrative assignments do not establish countywide impact, and multiple reports can describe the same episode. [4, 6]

The proposed six hazard families cover 1,267 reports. Grouping by county, family and NOAA episode gives 853 county/family episodes, or 814 county/episodes when families are combined. Flood and Flash Flood overlap in seven county-episodes: the family count is 76 rather than the 83 obtained by counting types separately. Neither unit is automatically the correct measure for every research question. Drought duration and repeated reporting remain separate design issues. The zero wildfire row means no matching records in this extract. [6]

Retain event 1220078 under its published Astronomical Low Tide classification and annotate the drought narrative; do not silently recode it. Candidate counts are supplied for review, not substituted into the current scores. [4, 6]

### CDC social vulnerability

The Tennessee-ranked 2022 SVI file covers all 95 counties with valid ranks and uses 2018–2022 ACS data. Its socioeconomic theme correlates 0.758 with the model's household financial stress ordering; overall SVI correlates 0.680. These associations show overlap, not incremental predictive value. Retain SVI as preparedness context. Adding it to the weighted score would require a separate rationale and comparison against existing socioeconomic components. [5]

### Rigor and limitations

The strongest evidence concerns reproducibility within saved inputs, preservation of the baseline, regression coverage for missing-data behavior, and transparent source reconciliation. The analysis remains limited by mixed source years, unverified coverage in some layers, sparse counts and population denominators, correlated indicators, and judgment-based weights and category thresholds.

Min-max scaling depends on the observed county distribution and can be sensitive to extremes. Lawful business and licensing counts are indirect proxies; they do not establish illicit activity. Multiple transformations of related inputs can repeat the influence of the same underlying condition. County averages cannot support conclusions about individuals, facilities or neighborhoods.

Sensitivity to weights is useful but does not replace validation against a defined outcome. No independent holdout evaluation, calibrated forecast performance or causal identification was established in this review. The package is a reproducible research index with qualified source coverage, not a validated predictive model.

---PAGE---

# Verification and release record

### Checks completed for this release

All 340 fresh file-hash comparisons passed: 170 original data/output files and 170 frozen copies. All 12 packaged historical score/scenario tables match their frozen originals byte for byte. The 95-county summary preserves score strings exactly and joins the previously reviewed coverage file one-to-one by county. All 39 regression tests passed locally; 188 pandas fragmentation performance warnings were reported. No scoring logic was changed to address those warnings. [8]

The earlier 42 numerical comparisons and 12 coverage-review comparisons used relative and absolute tolerances of 1e-12. They were inspected as retained evidence, not represented as a fresh end-to-end run today. The earlier replay used frozen inputs with HTTP blocked. Today's release did not refresh APIs, rerun the full pipeline or validate the hosted dashboard. [1, 2, 8]

PR #2 was verified open and draft at head ed7a63a6e152eab2034be5605ab4e111b14e0ae8. Existing local documentation changes were left in place. Nothing was pushed, merged, sent or scheduled. The previous email draft is superseded by the user's decision to end outreach. [8]

### Separate future work if the model is extended

First define the intended outcome and resolve measure choices, including clearance versus offense units and the treatment of missing inputs. Then assess redundant proxies, population effects and normalization sensitivity using an isolated candidate. Freeze a validation design before outcome evaluation. Pin dependencies and test the full retrieval-to-report workflow separately. None of these changes is required to preserve and document the present research result; none has been silently incorporated.

### Evidence index

[1] Frozen real-input validation, October 26: outputs/real-validation/README.md, parity_results.json and snapshot_manifest.json. Selected evidence is included in this package.

[2] Source follow-up and reviewed CBP availability: outputs/source-followup/README.md, reviewed_coverage_validation.json, updated_source_review_ledger.csv and disruption_template_check.json. The unresolved ledger is a dated review, not a new count of reporting failures.

[3] Census clarification record, October 28 with October 29 update: outputs/source-followup/census_clarification_2026-10-28.md. Exactly-three threshold closed; exact unpublished counts unavailable.

[4] NOAA classification and historical mapping: outputs/source-feasibility-2026-10-29 and outputs/zone-svi-2026-11-02/README.md.

[5] CDC SVI overlap review: outputs/zone-svi-2026-11-02/README.md and svi_overlap.csv.

[6] Weather and ACLED audit: outputs/weather-acled-audit-2026-11-02/README.md, checks.json, weather_county_family.csv and acled_county_trace.csv.

[7] TBI post-call source note: outputs/tbi-followup-2026-11-10/README.md and source_manifest.json. Publication pages were reviewed from an existing local download; no new official-download authentication is claimed. Verbal explanations remain attributed participant recollections.

[8] This release: verification.json, evidence/file_integrity_checks.json, county_results.csv, package_manifest.json and the local README. Model description checked against the local repository README, docs/methodology.md and src/risk_scoring.py.

Repository: https://github.com/jasonrkeen/tennessee-domestic-security-finance-risk-model
