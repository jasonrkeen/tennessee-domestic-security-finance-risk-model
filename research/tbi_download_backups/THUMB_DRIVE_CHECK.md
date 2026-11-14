# Newly connected thumb drive

Follow-up observation | November 13, 2026 (America/Chicago)

After the initial backup check, the owner connected a thumb drive. It contained a Tennessee model folder and ZIP archive, but **the missing `Crimes Rates by Jurisdiction.csv` was not recovered**. This extends the accessible-source search; it does not establish permanent deletion.

The read-only search inventoried 56 directories and 483 files, screened 157 standalone CSV files, inspected five ZIP central directories, and screened 461 CSV members within those archives. CSV screening read at most the first 65,536 bytes, decoded as UTF-8 with errors ignored, looking case-insensitively for `Crime Rate (per 1,000)` or `Crimes Rates by Jurisdiction`. Filename checks covered crime/jurisdiction variants, and 9,798-byte CSV files/members were treated as candidates. ZIP entries were also checked for HAR filenames. No header/size candidates or matching ZIP entries were found; the completed scan reported no read errors.

The standalone filename hits were the existing 2,408-byte prepared input, its processor and two chart filenames. The drive's `data/raw/tn_crime_rate_inputs.csv` is SHA-256 identical to the frozen prepared input. It is not a recovered raw export. A separate check of the Tennessee ZIP's 144 CSV headers also returned no target-header match; those CSVs are included in the broader archive count, not additional independent observations.

An initial scan was stopped after dependency folders slowed traversal. The completed scan excluded directories whose names begin `.venv` or `venv`, plus `.git`, `node_modules`, `site-packages`, `__pycache__`, System Volume Information and the recycle-bin directory. Counts refer to this completed bounded scan and include file copies, not unique evidence. No nested archives, deleted sectors, recycle-bin contents, arbitrary non-CSV bodies, UTF-16 decoding or screenshot OCR were examined. No files on the thumb drive were changed or restored.

The raw-export and historical-filter gaps remain unresolved. Any later candidate still needs its own hash and content/filter comparison; matching prepared inputs do not authenticate the missing download. Released scores, data, formulas and dated report remain unchanged. The follow-up [verification record](results/thumb_drive_verification.json) records fresh preservation checks. No production pipeline or source refresh was run, and no raw files from the drive are committed.
