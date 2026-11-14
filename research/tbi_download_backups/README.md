# May Downloads backup check

Research observation | November 13, 2026 (America/Chicago) | v1.0.1 preserved

**The missing export was not recovered from the accessible locations checked. No separately retained May Downloads backup was identified.** This is bounded non-discovery, not proof that no backup exists.

The recovery target remains `Crimes Rates by Jurisdiction.csv`, recorded by Edge as a 9,798-byte download on May 28, 2026 at 09:23:18.925940 UTC. The [prior archive investigation](../tbi_archive_recovery/README.md) preserves that browser metadata. Filename, size and download time do not authenticate the missing file's content or selected filters.

## Locations checked

| Surface | Observation | Limit |
|---|---|---|
| Mounted filesystem drives | Only C: and a temporary-directory alias on C: were visible | No disconnected drive, other computer or unmounted network backup was examined |
| Windows backup locations | Conventional root FileHistory, local user FileHistory and Windows.old Downloads paths were absent; File History service was stopped | Present configuration does not establish whether May backups ever existed |
| Windows snapshots/recovery | Shadow-copy inventory failed with `Initialization failure`; Recovery directory access was denied | Snapshot availability remains unknown; no restore or recovery operation attempted |
| Current Downloads location | Known-folder setting points to the local user Downloads directory; no OneDrive Downloads directory was found | Current settings do not prove the May backup configuration |
| Local Dropbox | Only application/cache material was visible | No user backup identified; no remote Dropbox account or deleted-file history examined |
| Local directory-name discovery | 683 directories under Downloads, Desktop, OneDrive and Dropbox examined; no nested Downloads, FileHistory, WindowsImageBackup, Backup/Backups directory or selected backup/archive filename candidate found; no traversal errors | Skipped environment/dependency directories; name-based search does not detect arbitrary backup names or formats |
| Three additional Desktop ZIP archives | Central directories contained 308, 12,518 and 14 members respectively; no crime/jurisdiction filename, Downloads path or 9,798-byte CSV member matched | No nested archive expansion or arbitrary member-body search |
| Connected OneDrive | Root (8 items), Desktop (10) and Documents (31) immediate listings inspected; no obvious Downloads/backup folder identified | Each listing requested up to 200 items; deeper unrelated folders were not exhaustively traversed |
| OneDrive search | Exact target phrase and Downloads full-text searches returned no identified backup/export | Full-text results are not exact filename searches; Downloads search was capped at 50 results |
| OneDrive retained project | Older project `data/raw` listing contained 41 entries and no target-named export | A project copy is not a Downloads-folder backup |
| Connected Google Drive | Non-trashed metadata query for exact target filename or names containing Downloads/FileHistory returned no items | Deleted files, other accounts and arbitrary backup names were not covered |

The additional ZIP checks covered `UC Cumberland.zip`, `location-threat-monitor-mvp.zip` and `chokepoint-private.zip`. The directory-name scan excluded `.git`, `node_modules`, `.venv`, `venv`, `site-packages` and `__pycache__`. Selected file candidates were the target phrase or `.vhd`, `.vhdx`, `.tib`, `.tibx`, `.mrimg`, `.7z` and `.rar` extensions. These checks supplement, rather than repeat, the prior 14,512-CSV and 782-ZIP screen.

## OneDrive version-history lead

The retained project's `tn_crime_rate_inputs.csv` is 2,408 bytes, with cloud creation time May 27, 2026 at 22:15:36 UTC and modification time May 28 at 09:29:34 UTC. Its version-history response exposed only version `2.0`, also 2,408 bytes with that modification time, and no next-page link. No earlier raw-export version was exposed by this response.

This is the prepared-input filename and size, not the 9,798-byte historical download. Its body was not downloaded in this check; cloud metadata is not a byte-identity verification against the frozen input. The version number does not prove an earlier version is recoverable. Neither this item nor its timestamps close the missing-export or historical-filter gap.

## Remaining recovery options

A disconnected drive, another computer, a separately retained May Downloads archive, or a cloud backup service could still hold the file. No location for such a backup was available during this check. Recycle bins, deleted-file recovery, Personal Vault, arbitrary nested archives, cloud account-wide version history and remote Dropbox were not examined. The failed snapshot inventory must remain an unresolved access/inventory limitation.

If a backup becomes available, inspect it read-only for the exact name and variants, preserve any candidate with its own SHA-256 hash, and compare its headers, filters and 95-county measurements against the prepared input. Record any selected-member list or query definition separately. A matching name, size or county total is a lead, not proof of historical identity. Do not reconstruct the missing raw export from prepared totals or substitute a current portal export.

## Preservation and validation

This branch adds only this research note and a verification record. It does not restore files, alter backup settings, refresh sources, or run the production model. No raw cloud files, browser database, private account identifiers or unrelated file inventories are committed.

[verification.json](results/verification.json) records comparisons against all 170 original files, 170 frozen copies and five listed v1.0.1 release assets. Existing tracked files remain unchanged from the PR #8 merge. These integrity checks do not authenticate missing source evidence.
