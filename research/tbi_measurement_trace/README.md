# Retained TBI measurement lineage

Research note | November 13, 2026 | Frozen v1.0.1 reference

The explosives/gang-explosives duplication is already present in the retained export cells, before aggregation or normalization. The broader gang total also reconstructs from its retained export and equals the saved overall-crime count for all 95 counties. This narrows the issue to source selection and interpretation; it does not establish that all explosives offenses were gang-involved, or authenticate how the historical portal query was configured.

Only this research directory and synthetic tests are added. Released scores, data, formulas, weights, scenarios and the November 10 report remain unchanged. No collector, production processor or scoring pipeline was executed. No new portal retrieval or outreach was performed.

## Evidence and custody

The analysis reads eleven retained files: four exports, four prepared input tables and three mapping-validation tables. All eleven match the SHA-256 values in the October 26 snapshot manifest, captured at `2026-10-26T11:45:04.297628+00:00`. Their hashes and the manifest hash are pinned in [config.json](config.json). The separate v1.0.1 score table is checked against SHA-256 `70821e90e66ff116f13d520317d0c390dce7843b2d5d9533ffbbb73bd67f1216`.

This authenticates continuity with the retained local snapshot, not the portal response at acquisition time. Export display dates are reproduced below as file contents, not trusted download timestamps. Full raw files and the historical manifest containing local paths are not published in this branch.

| Retained file | Displayed date (Central Daylight Time) | Visible selection |
|---|---|---|
| `tn_explosives_activity_raw_2024.csv` | May 28, 2026, 1:12:01 AM | Incident Date 2024; Type of Weapon/Force Involved = Explosives; no Gang Activity header |
| `tn_gang_explosives_activity_raw_2024.csv` | May 28, 2026, 1:22:25 AM | Incident Date 2024; Explosives; Gang Activity = All Gang Activities |
| `tn_gang_activity_raw_2024.csv` | May 28, 2026, 12:58:25 AM | Incident Date 2024; Gang Activity = All Gang Activities; no weapon header |
| `crimes_clearances_by_offense_type_2024.csv` | May 27, 2026, 10:14:40 PM | Incident Date 2024; separate All Clearances and Cleared blocks |

The three matrix exports contain separate Number of Crimes and Number of Offenses blocks. The production selection uses Number of Crimes. Thus fields named `*_offense_count` in this model are sums of selected Number of Crimes cells, not a direct read of the Number of Offenses block or unique incident counts.

The earlier dated source review's abbreviated statement that the “gang report” retains an Explosives filter should be read specifically as the **gang-plus-explosives** export. The broad gang export inspected here has no weapon header. This clarification is confined to this new research note; the historical report is preserved.

## Trace 1: explosives and gang-plus-explosives

Both exports select the same 52 offense columns in the Number of Crimes block for the same 95 counties. All **4,940 selected cell strings match exactly** after whitespace trimming and county alignment. Of these, 4,907 are blank and 33 contain nonzero numbers; neither file contains an explicit numeric zero in those selected cells. Twenty-four counties have at least one nonblank selected cell, while 71 have none.

The duplication therefore precedes the scoring stage. It is not created solely by min-max normalization, shared population denominators, or the constant-score fallback. Blank-to-zero processing does, however, turn the identical source blank patterns into identical zero-filled aggregate inputs. Those blanks remain unverified absences.

The lineage checks independently sum the selected total, violent, weapon-law, homicide, arson and property-damage cells using the production offense sets read as literals. All reconstructed counts match the retained prepared inputs and the released table. Both sets of normalized scores also reconcile with the published count/population transformations, including the constant-series value of 50. The released composite vectors match, consistent with the identical six component weights in the production formulas.

The [effective-weight audit](../effective_weights/README.md) and [overlap study](../indicator_overlap/README.md) establish that the two composites each receive a 2.6% baseline coefficient, totaling 5.2% on the same saved vector. This trace explains where that numerical duplication first becomes observable in retained evidence. It does not choose a replacement weight.

## Trace 2: broad gang total and overall crime

The broad gang export sums to the saved `gang_related_total_crime_count` for every county. Those totals also equal the retained `tn_crime_rate_inputs.csv` overall-crime counts and released `overall_crime_count_2024` values across all 95 counties. The normalized gang-total and overall-count scores reconcile under the same published population denominator.

The earlier All Clearances export provides a separate, imperfect comparison. It has 51 common offense categories, whereas the gang matrix has an additional Justifiable Homicide column that is blank in all 95 counties. Across the 4,845 common county/offense cells, **4,835 match exactly**, including 1,738 joint blanks. Ten numeric cells differ across six counties, by one or two counts. The specific differences are retained in [common_offense_differences.csv](results/common_offense_differences.csv). The files display different export times; the reason for these differences is not established. They must not be silently reconciled or attributed to revisions as a fact.

The Crime Rate processor expects `crime_rates_by_jurisdiction_2024.csv`. That raw export was not found in the retained snapshot, the original project directory, the searched Codex workspaces, or Downloads by that filename. The trace for overall crime therefore starts at the retained prepared input. Matching totals do not prove which upstream raw file generated that table. A differently named copy may still exist outside this bounded search.

## Filter-record and code findings

- The gang processor locates the Gang Activity header but does not require it or test its values when choosing columns. It selects the Number of Crimes offense block and sums those cells.
- The gang-plus-explosives processor requires a weapon header and selects cells explicitly labeled Explosives. It locates, but does not require or validate, the Gang Activity header. Its comment assumes the export is already filtered to All Gang Activities.
- The retained mapping-validation tables each have 52 offense rows matching the selected columns. However, their `gang_activity_filter = All Gang Activities` and `weapon_force_filter = Explosives` strings are written as code literals. They are not independent evidence that the historical portal enforced a gang-involvement restriction.
- “All Gang Activities” is a visible aggregate label. The retained files do not supply its portal-member definition, selected-member list, query payload, or an explicit gang-involved-only predicate. Its substantive meaning remains unresolved by this local evidence.

Code references: [gang selection](../../src/gang_activity_processor.py), [gang/explosives selection](../../src/gang_explosives_processor.py), [explosives selection](../../src/explosives_processor.py), [overall-crime preparation](../../src/crime_rate_processor.py), and [normalization/composites](../../src/risk_scoring.py). All five files are hash-pinned and unchanged.

Taken together, the matching explosives cells, broad gang totals matching overall crime, and absent validation of gang membership are consistent with a nonrestrictive aggregate selection. This is a **source-selection hypothesis**, not proof of the portal's semantics, an acquisition mistake, or gang involvement in the underlying offenses. The current evidence does not support treating these saved vectors as independently measured gang-specific signals.

## Reproduction and artifacts

From the repository root in the locked Windows/Python environment:

```powershell
python research/tbi_measurement_trace/trace.py --frozen-root "<retained-snapshot-root>" --snapshot-manifest "<retained-snapshot-manifest.json>" --saved-scores "<v1.0.1-folder>/outputs/tables/tn_county_domestic_security_scores.csv"
python -m pytest -q
```

The script reads pinned inputs, preserves source blanks in the cell comparison, and reconstructs the legacy blank-to-zero arithmetic only for lineage reconciliation. Unexpected nonnumeric values fail. It never imports or invokes production processors. The 54 numerical lineage checks use relative and absolute tolerance `1e-12`. They establish local consistency, not source correctness or predictive validity. Inputs are hashed before and after execution. Repeated runs in the locked environment reproduce the committed result files.

- [Header evidence](results/header_evidence.csv): selection labels and one-based CSV row references.
- [Selected columns](results/selected_columns.csv): one-based column references, offense labels and measure block.
- [Cell comparisons](results/cell_comparisons.csv): exact equality, blanks and discrepancies.
- [Blank diagnostics](results/blank_diagnostics.csv): county-level counts of blank, explicit-zero and nonzero cells, without recoding blank as observed zero.
- [Mapping checks](results/mapping_checks.csv): retained mapping-table reconciliation and interpretation limits.
- [Lineage checks](results/lineage_checks.csv): raw-to-prepared, prepared-to-released and normalization comparisons.
- [Verification](results/verification.json): custody, code/configuration hashes and result hashes.

## Next decision

Before designing a scoring candidate, recover an archived query/member-selection record or contemporaneous definition that establishes whether All Gang Activities restricts the selected records. Also recover the original overall Crime Rate export if available. No new outreach is authorized or required by this note.

If those records cannot be recovered, retain the limitation explicitly. Any candidate that removes, relabels or combines the repeated measurements needs a separately specified research comparison. Do not reinterpret source blanks as zero, silently replace gang measurements with broad crime, or update the released model based on numerical matching alone.

Validation completed: 64 offline tests passed (188 existing pandas fragmentation warnings). The [preservation check](results/preservation.json) found all 170 original and 170 frozen files unchanged against the historical manifest; all five listed v1.0.1 release-asset checksums also match. These are local integrity checks, not independent source authentication.
