# Final research report and source decisions

November 10, 2026. This documentation release consolidates the current county-level research model and its source review. It does not refresh data, rerun scoring, modify quality flags, or establish predictive validity.

- [Final report PDF](final_report.pdf): five-page report, including the ten highest preserved numerical results, coverage interpretation, source findings and verification.
- [Editable report](final_report.md): the same report text; `---PAGE---` marks print page breaks.
- [Verification record](verification.json): fresh file-integrity and test results, retained historical numerical-parity evidence, and the dated draft-PR snapshot.
- [Census clarification](../census_cbp_clarification_2026-10-28.md): exactly-three publication threshold and the interpretation of unpublished 2023 cells.
- [Earlier missing-source fix](../source_availability_fix.md) and [source audit](../source_coverage_followup.md): dated implementation and validation history.

The PDF was rendered with PDFium and all five pages visually inspected before publication. The PDF and editable report are byte-identical copies of the final local package. This directory does not include raw datasets, private correspondence, credentials, or the local archive of score tables. Paths beginning `outputs/` in the report's evidence index identify retained local audit artifacts, not files committed to this repository. The source decisions below summarize that evidence for repository readers.

## What remains unchanged

All original data, numerical scores, ranks, scenarios, weights, thresholds, and scoring formulas remain unchanged by this documentation update. The full PR contains the earlier availability/confidence repair; this final documentation commit introduces no further code or test changes. Historical reports and tables retain their old coverage labels for provenance. Those labels should not be interpreted as the reviewed coverage assessment.

The initial availability repair produced 7 High, 48 Good and 40 Moderate counties. The separate CBP-reviewed copy produced 4 High, 29 Good and 62 Moderate with unchanged numerical scores. These bands describe available input layers and retain some legacy availability inference; they are not probabilities of accuracy or certifications of complete source reporting. The reviewed local copy has not replaced the original project inputs.

## Consolidated source decisions

### Census County Business Patterns

The 2023 query returned 368 of 760 selected county/industry cells. All published values matched the saved cache. Census correspondence clarified that the remaining 392 represent zero, one or two establishments, with no exact distinction available; exactly three establishments are published. Eight counties have all selected categories. Do not promote unpublished cells to observed zero or extend this interpretation to later releases without evidence. The correspondence does not authenticate the historical cache retrieval or endorse the model. See the separate Census note and its evidence hashes.

### TBI CrimeInsight

The preserved May 28, 2026 exports select Incident Date 2024. The local review found 24 counties with usable observed inputs for explosives, 24 for gang plus explosives, 31 for the hate-crime clearance input, and 4 for the ambush input. The corresponding gaps of 71, 71, 64 and 91 remain unverified. These are county/input classifications, not incident totals or nonreporting-agency counts. The gang report retains an Explosives filter, and the hate-crime input uses an All Clearances block.

The locally downloaded *Crime in Tennessee 2024*, PDF page 3, identifies June 20, 2025 as its database snapshot, reports no agencies failing compliance at release, and lists 13 covered-by relationships. Its covering letter is dated August 15, 2025. This is useful published compliance context, not a definition of blanks in the later exports or independent certification of Tennessee_UOF. The PDF was reviewed locally; this phase did not authenticate a new download against the official server.

Jason's November 10 participant debrief attributes daily CrimeInsight updates and the possibility of revisions/clearance changes to the TBI contact. These are attributed verbal explanations, not a transcript or written certification. They do not settle report-specific blank semantics or the precise historical agency-month coverage. Further email outreach has ended at the researcher's direction; unresolved questions are limitations of this release rather than silently resolved assumptions. The [TBI publications catalog](https://www.tn.gov/tbi/divisions/cjis-division/recent-publications.html) identifies the annual publication series.

### NOAA Storm Events

The preserved 2024 extract has 1,677 event reports: 846 county-coded and 831 zone-coded. All 831 zone records map to one county using historical NWS county-correlation files. The inspected Tennessee mappings agree across the checked releases. County assignment does not imply countywide impact.

The proposed six-family definition includes 1,267 reports, 853 county/family episodes, and 814 distinct county/episodes across families. Flood and Flash Flood overlap in seven county-episodes; the family aggregation gives 76 rather than the 83 obtained by separately counting published types. Keep the count unit explicit. Retain event 1220078 under its published Astronomical Low Tide type with its drought narrative noted. Empty extract selections are not real-world absence. None of these candidate counts enters the model scores.

Historical references used in the audit: [September 2023 correlation file](https://www.weather.gov/source/gis/Shapefiles/County/bp19se23.dbx), [March 2024 correlation file](https://www.weather.gov/source/gis/Shapefiles/County/bp05mr24.dbx), and [NWS change history](https://www.weather.gov/source/gis/Shapefiles/WSOM/zone_ch_log.txt). These links identify the audit sources; this commit does not claim a new retrieval.

### CDC social vulnerability

The 2022 Tennessee-ranked SVI file has valid ranks for all 95 counties and uses 2018–2022 ACS data. Its socioeconomic theme has Spearman correlation 0.758 with the model's household financial stress score; overall SVI has correlation 0.680. Retain SVI as preparedness context, not an additional scored component without separate review of overlap and incremental value. See [CDC's 2022 methods](https://stacks.cdc.gov/view/cdc/157287/cdc_157287_DS1.pdf).

### ACLED and the disruption template

The frozen ACLED file contains 336 unique events, 203 in 2023 and 133 in 2024, across 27 counties. Local replay reproduced 189 aggregate values in represented counties and reconciled 665 corresponding county/field entries in the 95-county master. All 68 absent-county gaps already occur in the saved raw extract. This establishes local processing fidelity, not acquisition completeness or real-world absence.

The all-zero 95-county, 15-field disruption input is byte-identical to the pinned loader's generated template. It remains unverified; historical creation is not proven. Constant-input normalization can produce a score of 50 without observed variation. The final report preserves these scores without describing them as measured resilience.

## Validation and review status

Fresh November 10 checks confirmed all 170 original files and all 170 frozen copies match their recorded SHA-256 hashes. All 39 local regression tests passed, with 188 pandas fragmentation performance warnings. The local package's 12 historical score/scenario tables match the frozen copies byte for byte, and its 95-county summary retains exact score strings.

The earlier 42 frozen-real-input comparisons and 12 CBP-reviewed comparisons passed at relative/absolute tolerance 1e-12. These remain historical replay evidence; this packaging phase did not rerun the full model or refresh APIs. It does not demonstrate hosted dashboard behavior, predictive accuracy or complete reporting.

PR #2 remains in draft. The head SHA recorded in verification.json is the pre-documentation November 10 verification snapshot, not the hash of this new documentation commit. Future scoring-method changes remain separately reviewable. No publication of the local data archive, merge or deployment is implied.
