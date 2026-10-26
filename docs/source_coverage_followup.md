# Source coverage follow-up — 2026-10-26

The frozen-data parity result remains valid. Further source review found that
legacy CBP coverage was still overstated because the saved cache had already
filled unpublished county/category cells with zero. No scoring formulas or
original data/output files were changed. PR #2 remains draft.

## CBP: current source evidence, with historical provenance limits

Eight successful official Census API queries retrieved reference-year 2023,
state 47, county `*`, NAICS2017 categories 453991, 451110, 453310, 447110,
445120, 522291, 812310, and 441120, with LFO=001 and EMPSZES=001.
The endpoint was [2023 CBP](https://api.census.gov/data/2023/cbp).
Queries, retrieval timestamps, response row counts, and hashes of saved JSON
representations were retained locally without credentials.

Of 760 possible county/category pairs, 368 were published and every published
value matched the saved cache. The remaining 392 pairs were not published; these
are not retrieved numeric zeros. Only eight counties have all eight categories.
Moore and Van Buren have none. Thus 87 counties have incomplete category coverage,
including 85 previously treated as available by the legacy positive-row heuristic.

[Census methodology](https://www.census.gov/programs-surveys/cbp/technical-documentation/methodology.html)
describes omission of cells with fewer than three establishments beginning with
reference year 2017. The page currently warns its guidance is under revision;
this audit uses it as historical methodological context for the 2023 product,
not as a guarantee about future releases. A missing row does not identify a
specific suppressed value, and no suppressed values were inferred. The
[2023 user guide](https://www2.census.gov/programs-surveys/cbp/resources/2023-CBP-User-Guide.pdf)
also distinguishes unavailable and publication-standard flags.

The match supports compatibility with 2023 data, not proof that the historical
collector used that year for every category. Original request logs and cache-year
metadata were not retained. New evidence is dated separately from old inputs.

### Staged correction and verification

A separate local copy of the frozen master/cache now carries explicit CBP
availability markers based on the retrieved category coverage. Its numeric
values are unchanged. The original project and first validation snapshot remain
untouched; this overlay has not been installed into the original project.

All 12 score/scenario/rank table comparisons pass at rtol/atol 1e-12, including
377 non-quality fields for 95 counties, all nine score tables, ten scenarios,
scenario leaders, and rank stability. The staged coverage labels are 4 High,
29 Good, and 62 Moderate, superseding the earlier 7/48/40 distribution only for
this reviewed copy. They remain input-coverage bands, not predictive confidence.
The unresolved input-layer ledger expands from 462 to 547 county/layer pairs.
No TBI or ACLED records were promoted to confirmed observed zero.

The existing collector correctly preserves absent-category evidence on new
retrievals. A new synthetic regression covers successful queries where one
county has every category, another lacks one category, and a third has no rows.
It checks that CSV round trips and scoring preserve the availability distinction
while retaining existing numeric zero fallbacks. The suite now has 39 passing tests.

## TBI: distinguish empty cells, missing values, and zero reports

The public site was inspected in a browser after direct retrieval failed.
[CrimeInsight's home page](https://crimeinsight.tbi.tn.gov/) explains that reports
use a nightly copy of a continually updated database; annual publications use
separate frozen snapshots. A new query cannot silently replace the May 28, 2026
exports used in this model.

The hosted [Data Cells help](https://crimeinsight.tbi.tn.gov/public/Help/en/35309.htm)
distinguishes missing values from zero. Its
[suppression help](https://crimeinsight.tbi.tn.gov/public/Help/en/suppressing_values.htm)
offers separate options for empty cells and empty-or-zero cells. This supports
keeping the distinctions, but does not define why the particular 2024 export
cells are blank. The [missing-value dictionary help](https://crimeinsight.tbi.tn.gov/public/Help/en/35056.htm)
describes report-specific symbols; the dictionary option was greyed out and
did not open in public offense report 19. No report-specific mapping was recovered.

The [TBI error manual, edition 7.1](https://www.tn.gov/content/dam/tn/tbi/documents/tibrs/TIBRS_Error_Manual_Edition_7.1_5-23-171.pdf)
documents a distinct zero-reporting segment with month/year validation (printed
page 16). This is not evidence that every relevant agency submitted all 12 months
for 2024, nor does it certify the separate Tennessee_UOF data source.

Remaining questions for the source owner, prepared but not sent:

1. In the May 28, 2026 exports for Incident Date 2024, do blank count cells mean
   no matching reported records, unreported data, suppression, not applicable,
   or another state? Does this differ between TIBRS Offense Data and Tennessee_UOF?
2. Where can county/agency-month reporting and explicit zero-submission coverage
   be obtained for 2024, including late submissions and the May 28, 2026 cutoff?
3. What geography and reporting-status rules govern county aggregation, and can
   a blank filtered county result be called a zero among complete reporting units?
4. Can the exact export definitions and vintage be recovered without replacing
   them with today's revised data?

No contact was made. County reporting completeness remains unresolved.

## Disaster/disruption: template evidence

Running the pinned base loader in a temporary directory with the frozen ACS
county list generated a CSV byte-identical to the saved 95-county disruption file.
Both SHA-256 hashes are
`c300e84a6bd17d2b515d86661e9726ee4c8df000618b98a92c77362793cc5459`.
All 15 fields are zero. This establishes indistinguishability from the generated
template, not historical proof of how the file was created.

The repository's separate operational-risk sources (FEMA NRI, healthcare,
transport, and infrastructure context) do not establish a validated mapping to
these 15 scored fields. They were not substituted. Before populating the layer,
specify observation periods, units, aggregation rules, source locators, missing
states, and any proxy calibration for each field. Such population may change
scores and belongs in a separately reviewed data/scoring update.

## Disposition

Coverage-only handling and numerical parity are supported within the tested
scope. The reviewed local overlay is available for inspection; raw source data
and county-level artifacts are not in this PR. Retain draft status. Resolve TBI
semantics/reporting coverage and document the disruption-layer measurement plan
before treating those layers as complete. ACLED coverage remains unresolved as
recorded in the preceding audit.
