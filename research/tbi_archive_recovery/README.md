# Archived TBI query and export recovery

Research note | November 13, 2026 | Released v1.0.1 preserved

A historical browser record identifies a download named **Crimes Rates by Jurisdiction.csv**, with 9,798 received/total bytes, on May 28, 2026 at 09:23:18.925940 UTC (4:23:18.925940 AM CDT). The file itself was not recovered. This supplies a more specific recovery target than the processor's expected renamed file, `crime_rates_by_jurisdiction_2024.csv`, but it does not establish the download's year selection, values or relationship to the prepared model input.

No archived May selected-member list or query body was recovered. The existing uncertainty around All Gang Activities therefore remains. No released scores, data, formulas, dated report, or earlier research files are changed. No live TBI query, source refresh, outreach, merge or release is part of this branch.

## Evidence recovered

The [sanitized browser metadata](results/browser_metadata.json) comes from the local Edge Default profile's retained Chromium history tables, read through SQLite in read-only mode. It includes five allowlisted May TBI download records and one later report-definition visit. It excludes local usernames/paths, browser GUIDs, account parameters, tokens, unrelated browsing and raw correspondence.

| Record | UTC start | Received / total bytes | What it establishes |
|---|---|---:|---|
| Crimes Rates by Jurisdiction.csv | May 28, 09:23:18.925940 | 9,798 / 9,798 | A locally retained download record with this exact filename, endpoint and byte count |
| Crimes and Clearances by Offense Type (2).csv | May 28, 06:22:29.452217 | 37,263 / 37,263 | A possible historical download counterpart to the retained gang-plus-explosives export |

The records have `state_code = 1`, `interrupt_reason_code = 0`, and no stored content hash. Those numeric state fields are preserved as browser metadata. The recorded target files are absent at their historical paths. No file body has been reconstructed from the browser record.

For the 37,263-byte record, the size matches the retained `tn_gang_explosives_activity_raw_2024.csv` and its download starts roughly four seconds after that file's displayed May 28, 1:22:25 AM CDT export timestamp. This is **size/time corroboration**, not a cryptographic identity check or proof that the retained file was the download. The previously retained file's hash remains the custody reference described in the [TBI measurement trace](../tbi_measurement_trace/README.md).

Both download chains point to `/public/View/dispview.aspx` on `crimeinsight.tbi.tn.gov`, with `download=yes`, `DownloadFormat=CSV`, and `CsvDataFormat=CSV_MD`. These specify download format, not Incident Date, geography, gang membership or offense filters. No selected-member list or request body is present in the extracted records.

## Later report-definition record

The recovered definition-page visit is **October 23, 2026 at 23:25:40.213622 UTC**, roughly five months after the May exports. Its retained parameters are:

- `ReportId=52`
- `DetailedDefinition=1`
- `SelectedMembersDisplayLimit=10`
- `SummaryCubeId=7`

The URL records a page visit, not the returned definition text. A display-limit parameter is not evidence that ten members were selected or what those members were. The date and surrounding retained work concern a later research session; this record cannot authenticate the May model's filter settings. It does not close the All Gang Activities interpretation question.

## Bounded search performed

[search_summary.json](results/search_summary.json) records the search coverage and limitations. Counts are examined file instances, including copies, not unique documents.

| Surface | Method | Result |
|---|---|---|
| Downloads, Desktop, OneDrive Documents, Codex Documents | 14,512 CSV files screened using the first 65,536 bytes for `Crime Rate (per 1,000)` or `Crimes Rates by Jurisdiction`, case-insensitive UTF-8 decoding | No matching standalone export header |
| ZIP archives under those roots | 782 ZIP central directories checked for crime/jurisdiction member names, HAR or ReportDefinition names, and 9,798-byte CSV members | No candidate member; no nested archive expansion or arbitrary member-body search |
| User-profile filename search | Case variants of rate/jurisdiction and Crimes/Clearances names; relevant local HAR/filter/query/parameter names | No missing CSV recovered; later October parameter artifacts are not May evidence |
| Original repository history | Available Git history searched for crime/jurisdiction filenames | No tracked original export found |
| Retained ChatGPT archive | Four identified conversation shards, 302 conversations; exact filename/filter terms screened | No matching original filename/filter record; these shards are not assumed to be the complete account history |
| Edge browser history | Relevant download records, URL chains and report-definition visits | Five May CSV records and one October definition visit retained in the sanitized evidence |
| Chrome browser history | Initial ordinary read was locked; immutable base-file read used for a bounded metadata check | No matching TBI download rows in that base-file view; uncheckpointed journal state was not included |
| Connected Gmail | Filename/filter/CrimeInsight search, plus a pre-June-15 query; relevant county clarification thread inspected | Pre-June query returned no messages; the October county thread contains the researcher's inquiry, not a recovered historical definition or attached CSV |
| Connected Drive | CrimeInsight, Crime Rates and TIBRS searches | No relevant export or query record returned; broad Crime Rates results were unrelated |
| Download duplicate-removal ledger | Relevant crime/TBI/gang/explosives/jurisdiction strings | No matching ledger entry; no inference about how the missing file disappeared |

The CSV/archive screen reported no read errors. It did not search alternate drives, offline backups, OneDrive version history, recycled/deleted bytes, every cloud account, arbitrary screenshot OCR, or browser cache/request bodies. The negative result is **not proof of nonexistence**. A differently encoded file, an unsearched archive member, another filename/format, or an external backup may still contain the original.

No earlier filename-based non-discovery is overwritten. This note adds a browser-record lead while leaving the raw-file and historical-filter gaps open. The October correspondence remains an attributed research inquiry, not agency certification; its private contents are not committed here.

## Reproduction and validation

The extractor is deliberately narrow. It accepts the local history database path and writes only the requested research evidence file:

```powershell
python research/tbi_archive_recovery/extract_history.py --history "<Edge-profile>/History" --output research/tbi_archive_recovery/results/browser_metadata.json
python -m pytest -q
```

It opens the database with `mode=ro`, filters to the exact TBI host and allowlisted filenames, exports only allowlisted URL parameters, and keeps UTC timestamps. It does not modify the browser database or read cookies, passwords or authentication stores. A live history database can change or be locked; a future extraction is a fresh observation, not guaranteed to reproduce this snapshot. Two current extractions produced identical evidence bytes.

The broad file searches are discovery steps, not a replacement model pipeline. Their recorded roots are described by category rather than personal absolute paths. No raw browser database, private mail, full ChatGPT export, original data, or large binary is committed.

## Next recovery target

Search any separately retained backup of the May Downloads folder for **Crimes Rates by Jurisdiction.csv** (9,798 bytes). A recovered candidate must be preserved under its own hash and compared with the 95-county prepared input; the filename and size alone cannot authenticate it. Retain any query-definition text, selected-member list, screenshot or request capture with its own date and provenance.

If such a backup is unavailable, continue to label the overall raw export and May gang filter semantics as unresolved. Do not recreate a CSV from the prepared totals and call it recovered evidence, or substitute a current portal result for the missing historical export. Any scoring candidate remains a separate research decision.

Validation: 69 offline tests passed (188 existing pandas fragmentation warnings). The [verification record](results/verification.json) confirms unchanged hashes for all 170 original files, 170 frozen copies and five listed release assets; it also records hashes for this research evidence. These checks establish local integrity, not independent source authentication.
