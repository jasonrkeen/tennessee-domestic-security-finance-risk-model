# Public Group, TDOC STG Context, and Targeted-Harm Source Guide

**Project:** Tennessee Domestic Security & Illicit Finance Risk Intelligence Model  
**Version:** Phase 6 Dashboard / Reference / Context / TDOC STG Context Add-On  
**Purpose:** Document approved source types, workflows, validation rules, dashboard treatment, GitHub publication boundaries, and responsible-use rules for the public group / network reference layer, the TBI hate-crime context layer, and the TDOC correctional-system STG context layer.

---

## Purpose

This guide supports three **reference-only / context-only** layers:

1. **Publicly Documented Group / Network Reference Register**
   - Built from approved public sources such as SPLC, ADL, DOJ, court documents, TBI reports, and credible public reporting.
   - Used as a PDF appendix, Streamlit dashboard reference tab, or analyst-reference table.
   - Not included in risk scoring, county ranking, risk signals, or sensitivity scenarios.

2. **TBI 2024 Hate Crime Report Context**
   - Built from the Tennessee Bureau of Investigation 2024 Hate Crime Report.
   - Used to provide statewide context for the targeted-harm layer.
   - Not used to identify people, agencies, addresses, exact incident locations, or case-level records.
   - Does not replace the county-level `hate_crime_processor.py`.

3. **TDOC Correctional-System STG Context**
   - Built from sanitized TDOC correctional-system sources, including the FY2025 TDOC Statistical Abstract and a historical 2010 TDOC STG source.
   - Used as a PDF appendix, Streamlit dashboard context tab, and analyst-reference table.
   - Not included in risk scoring, county ranking, organized-violence scoring, operational-risk scoring, risk signals, or sensitivity scenarios.
   - Does not identify current community presence, county-level activity, street-level activity, individuals, facility security details, or operational indicators.

These layers are designed to strengthen the report and dashboard context while keeping the scoring model limited to aggregate county-level indicators.

---

## Responsible-Use Summary

The public group / network reference layer, statewide hate-crime context layer, and TDOC correctional-system STG context layer are **not investigative products** and are **not operational-intelligence outputs**.

They should not be used to:

- Identify individuals
- Identify members, suspects, victims, officers, or associates
- Publish addresses, coordinates, meeting locations, or facility-level details
- Infer criminal conduct from source-reference listings
- Infer terrorism, extremism, motive, ideology, or actor identity
- Label a county as having confirmed operational group presence
- Score or rank counties based on group-reference entries or correctional-system STG context
- Make law-enforcement, investigative, legal, employment, financial, or security decisions
- Infer current street-level activity from TDOC correctional-system classification context

The layers should be used only as a cautious source register, dashboard reference tab, or context appendix.

---

## Dashboard Treatment

The Streamlit dashboard includes dedicated tabs for:

```text
Public References
TDOC STG Context
TBI Hate-Crime Context
Sources
Model Card
```

These tabs are presentation layers only. They read existing validated outputs and do not change the scoring model.

### Public References Tab

The Public References tab reads:

```text
outputs/tables/tn_public_group_activity_reference.csv
outputs/tables/tn_public_group_reference_validation.csv
```

The tab should display only validated, report-ready references where possible. It should preserve the same responsible-use caveats used in the PDF appendix.

The Public References tab should not be used to:

- Filter county risk rankings
- Increase or decrease county scores
- Confirm operational presence
- Identify people, addresses, or meeting locations
- Make investigative, enforcement, employment, financial, or security decisions

### TBI Hate-Crime Context Tab

The TBI Hate-Crime Context tab reads:

```text
outputs/tables/tn_2024_hate_crime_bias_context.csv
outputs/tables/tn_2024_hate_crime_offense_context.csv
outputs/tables/tn_2024_hate_crime_clearance_context.csv
outputs/tables/tn_2024_hate_crime_location_context.csv
outputs/tables/tn_2024_hate_crime_report_context_summary.csv
```

This tab provides statewide context only. It does not replace the county-level hate-crime processor and does not change county-level scoring.

### TDOC STG Context Tab

The TDOC STG Context tab reads:

```text
outputs/tables/tn_tdoc_stg_reference_context.csv
outputs/tables/tn_tdoc_stg_reference_validation.csv
```

This tab provides correctional-system context only. It is non-scoring and should not be used to infer current community presence, county-level activity, street-level activity, criminality, terrorism, ideology, or operational conduct.

The tab may display:

- FY2025 TDOC facility-level aggregate STG/Gang confirmed, suspected, and total counts
- Historical 2010 broad TDOC institutional group references
- Validation results confirming the layer is non-scoring, sanitized, and internally consistent

The tab should not display recognition details, visual identifiers, coded identifiers, staff contact details, person identifiers, addresses, maps, operational notes, case narratives, facility security details, or other sensitive detail.

### Dashboard Filter Behavior

The county and risk-signal dashboard filters apply to county-level scoring tabs. They should not be interpreted as filtering or validating the public group / network reference layer or the statewide TBI hate-crime context layer.

Public reference, TDOC STG context, and TBI context tabs remain appendix/context layers even when county-level dashboard filters are active.


## Approved Source Types

| Source Type | Example | Use |
|---|---|---|
| Civil society tracker | SPLC Hate Map, ADL H.E.A.T. Map | Public group / network or incident-reference context |
| Official government source | TBI, DOJ, FBI, DHS | Legal, statistical, or official public-safety context |
| Court document | Federal or state criminal filings | Case-level legal reference only |
| Law enforcement report | TBI annual reports, TDOC public statistical reports, public crime-statistical reports | Aggregate statistical or correctional-system context |
| Academic report | University or research institute publication | Background and typology context |
| Credible news | Established news outlet | Secondary public reporting when primary sources are unavailable |
| Other public source | Carefully reviewed public documentation | Use only when source quality is clear and operational details are excluded |

---

## Approved Reference Categories

The current `public_group_reference.py` validator supports the following categories:

| Category | Meaning |
|---|---|
| `criminal_gang_or_organized_crime` | Public-source reference to organized criminal activity or network context |
| `extremist_or_hate_group` | Public-source reference to hate/extremist group context |
| `antigovernment_or_militia` | Public-source reference to antigovernment, militia, or similar movement context |
| `terrorism_linked_case` | Public-source legal or government reference to a terrorism-linked case |
| `violent_extremism_case` | Public-source legal or government reference to a violent-extremism case |
| `public_safety_reference` | Public-source public-safety reference that does not fit another category |
| `other_public_reference` | Public-source reference retained for context but not mapped to a more specific category |

Use the narrowest accurate category. When in doubt, use `other_public_reference` and explain the limitation in the `legal_status_note`.

---

## Approved Source Types in Input File

The current `public_group_reference.py` validator supports the following `source_type` values:

| Source Type Value | Use |
|---|---|
| `official_government` | DOJ, FBI, DHS, TBI, or other government source |
| `court_document` | Public court filing or legal document |
| `law_enforcement_report` | Public statistical or agency report |
| `civil_society_tracker` | SPLC, ADL, or similar tracker |
| `academic_report` | Academic or research publication |
| `credible_news` | Established news reporting |
| `other_public_source` | Public source that does not fit another category |

---

## Geographic Reference Rules

Use only broad, non-operational geography.

| Allowed Geo Level | Example |
|---|---|
| `statewide` | Tennessee |
| `county` | Davidson |
| `multi_county` | Middle Tennessee |
| `city_or_region` | Nashville, Knoxville, West Tennessee |
| `unknown` | Unknown or unclear public geography |

Do not include addresses, coordinates, meeting sites, exact event locations, facilities, or maps.

---

## Prohibited Fields

Do not include:

- Addresses
- Street addresses
- Coordinates
- Latitude / longitude
- GPS values
- Exact meeting locations
- Facility names tied to sensitive activity
- Facility security details or site-level security notes
- Individual names
- Member names
- Suspect names
- Victim names
- Officer names
- Social media handles
- Usernames
- Recruitment channels
- Chatrooms
- Telegram, Discord, or other platform identifiers
- Phone numbers
- Emails
- Facility-level vulnerability details
- Tactical maps
- Operational notes
- Case narratives
- Incident IDs
- Agency case numbers
- Victim details
- Suspect details
- Officer details

The reference layer is not a place to store operational, individual-level, address-level, or case-level detail.

---

## Public Group Reference Input Schema

The public group reference input file is:

```text
data/raw/tn_public_group_reference_inputs.csv
```

Expected columns:

| Column | Description |
|---|---|
| `reference_id` | Unique reference ID |
| `group_or_network_name` | Public-source name or reference label |
| `category` | Approved category value |
| `source_type` | Approved source type |
| `source_name` | Name of source |
| `source_url` | Public source URL or source file reference |
| `geographic_reference` | Broad public geography only |
| `geo_level` | `statewide`, `county`, `multi_county`, `city_or_region`, or `unknown` |
| `county` | County name only when `geo_level` is `county` |
| `date_observed` | Year or date observed in source |
| `source_publication_date` | Source publication date or year |
| `confidence_level` | `high`, `moderate`, or `low` |
| `summary_note` | Short non-operational source-grounded summary |
| `legal_status_note` | Careful status language such as listed, alleged, charged, convicted, or publicly documented |
| `responsible_use_flag` | Required caveat language |
| `include_in_report` | `TRUE` or `FALSE` |
| `include_in_score` | Forced to `FALSE` by the processor |

The processor forces `include_in_score = False` even if a row is accidentally marked as true.

---

## SPLC Hate Map CSV Workflow

Save the SPLC Tennessee CSV as:

```text
data/raw/splc_hate_data_2024.csv
```

Then run:

```powershell
python -m src.splc_group_reference_processor
python -m src.public_group_reference
```

Expected outputs:

```text
outputs/tables/tn_splc_public_group_reference_candidates_2024.csv
data/raw/tn_public_group_reference_inputs.csv
outputs/tables/tn_public_group_activity_reference.csv
outputs/tables/tn_public_group_reference_validation.csv
```

The SPLC source category is retained as a source classification. The model does not independently verify membership, activity, criminality, motive, ideology, operational conduct, or active local presence.

The SPLC processor is a **source-assisted candidate generator**. The validated public reference table remains the authoritative report input.

---

## Public Group Reference Validation Workflow

Run:

```powershell
python -m src.public_group_reference
```

The validator:

- Creates a template if the input file does not exist
- Blocks prohibited columns
- Normalizes allowed category, source type, geography, and confidence values
- Removes the starter example/template row from output
- Deduplicates repeated references
- Forces `include_in_score = False`
- Writes a validation table for review

Expected outputs:

```text
outputs/tables/tn_public_group_activity_reference.csv
outputs/tables/tn_public_group_reference_validation.csv
```

---

## TBI Hate Crime Report Context Workflow

Run:

```powershell
python -m src.tbi_hate_crime_report_context
```

Expected outputs:

```text
outputs/tables/tn_2024_hate_crime_bias_context.csv
outputs/tables/tn_2024_hate_crime_offense_context.csv
outputs/tables/tn_2024_hate_crime_clearance_context.csv
outputs/tables/tn_2024_hate_crime_location_context.csv
outputs/tables/tn_2024_hate_crime_report_context_summary.csv
```

These tables provide statewide context for the targeted-harm layer. They do not replace the county-level `hate_crime_processor.py`.

The TBI hate-crime context layer should remain statewide and non-scoring unless a future update introduces a carefully reviewed aggregate county-level source.

---

## TDOC Correctional-System STG Context Workflow

Run:

```powershell
python src/tdoc_stg_reference_processor.py
```

Expected outputs:

```text
outputs/tables/tn_tdoc_stg_reference_context.csv
outputs/tables/tn_tdoc_stg_reference_validation.csv
```

Expected raw source files:

```text
data/raw/stg_threat_assessment__tn_major_groups__apr_2010__les_.pdf
data/raw/2025 Statistical Abstract.pdf
```

This layer is a **correctional-system context appendix only**. It is not included in:

- Final domestic-security risk score
- Organized violence / high-severity crime score
- Gang-related crime pressure score
- Operational Risk & Protective Planning score
- Scenario controls or sensitivity analysis
- County rank or county risk signal

### TDOC Source Treatment

| Source | Treatment | Output Use |
|---|---|---|
| FY2025 TDOC Statistical Abstract | Public aggregate statistical source | Facility-level aggregate confirmed, suspected, and total STG/Gang counts only. |
| 2010 TDOC STG source | Historical correctional-system context | Broad historical group references only. No recognition details or operational detail retained. |

### TDOC STG Context Output Rules

The TDOC processor should retain only broad, sanitized context fields such as:

- `reference_id`
- `group_or_network_name`
- `record_type`
- `source_type`
- `source_name`
- `source_year`
- `source_file`
- `source_page`
- `facility_context`
- `confirmed_member_count`
- `suspected_member_count`
- `total_member_count`
- `correctional_context_flag`
- `historical_context_flag`
- `responsible_use_flag`
- `include_in_report`
- `include_in_score`

The processor should force `include_in_score = False` for every row.

### TDOC STG Validation Rules

The validation output should confirm:

- Rows were created.
- All rows are non-scoring.
- FY2025 facility-total rows are present for all expected TDOC facilities.
- FY2025 confirmed, suspected, and total counts are populated.
- FY2025 counts are internally consistent where `confirmed + suspected = total`.
- Prohibited detail terms are not present in the public output.
- All rows are marked as correctional-system context.

### TDOC STG Responsible-Use Wording

Use language such as:

> TDOC correctional-system STG context is non-scoring and should not be interpreted as current community presence, county-level activity, street-level activity, terrorism, ideology, suspicious conduct, or criminal conduct by any specific person, group, business, facility, or place.

Also acceptable:

> FY2025 TDOC counts reflect correctional-system classification context within facility profiles. They do not measure county-level or community-level group activity.

Avoid language such as:

- “Gang presence in county”
- “Active local group”
- “Confirmed street activity”
- “Threat group location”
- “Operational group presence”
- “Facility threat details”
- “Current community activity”
- “Local gang membership estimate”

---

## How These Layers Fit the Main Pipeline

The updated `main.py` runs the reference/context layers first:

```text
[1/9] Building reference/context layers
[2/9] Collecting public-source county data
[3/9] Building Phase 6 risk scores
[4/9] Running Phase 6 sensitivity analysis
[5/9] Running CrimeInsight trend analysis
[6/9] Building Operational Risk & Protective Planning layer
[7/9] Generating charts
[8/9] Generating PDF report
[9/9] Pipeline summary
```

The reference/context layers are produced before the PDF so the appendices can load the latest validated public reference, TDOC STG context, and TBI context tables.

They are **not merged into the master dataset** and are **not used in scoring**.

After `python main.py` runs, the dashboard can be launched with:

```powershell
streamlit run app.py
```

The dashboard reads these same outputs and presents them in non-scoring reference/context tabs.

---

## Interpretation Rules

A public group reference means:

- A public source documented the group, network, case, or public reference.
- The reference may be useful for contextual analysis.
- The entry may be included in a report appendix or dashboard reference tab.

A public group reference does **not** mean:

- The group is active in a specific county.
- A county is unsafe.
- A county has confirmed operational activity.
- A person, business, licensee, or organization is suspicious.
- A terrorism threat exists.
- The model has verified membership, intent, ideology, motive, or operational activity.
- The reference should change a county’s score.

A TDOC STG context row means:

- A TDOC source documented correctional-system STG/Gang context.
- FY2025 facility-total rows reflect public aggregate correctional classification counts.
- Historical 2010 rows preserve broad institutional context only.
- The row may be useful for appendix or dashboard context.

A TDOC STG context row does **not** mean:

- A group is active in a county or community.
- A facility location should be treated as a target or risk site.
- A county has street-level gang activity based on correctional classification data.
- A person, facility, business, or agency is suspicious.
- The row should change any county score, risk signal, or rank.

---

## Recommended Report / Dashboard Language

Use language such as:

> This appendix/dashboard tab presents source-documented public references from approved public sources. It is not included in the model score and should not be interpreted as a terrorism, extremism, criminality, operational-presence, or county-risk label.

Also acceptable:

> Public group / network references are retained only as source-context records. They are not used for county scoring, risk classification, or operational assessment.

For TDOC STG context:

> TDOC correctional-system STG context is retained only as sanitized correctional-system appendix context. It is non-scoring and should not be interpreted as current county-level, community-level, or street-level activity.

Avoid language such as:

- “Confirmed terrorist group in county”
- “Known threat group”
- “High-risk group location”
- “Operational presence”
- “Recruitment site”
- “Meeting location”
- “Active extremist cell”
- “Terrorism-linked county”
- “Confirmed local threat”
- “Current county STG presence”
- “Facility threat group intelligence”

---

## Manual Review Checklist

Before including a public reference in the report or dashboard, verify:

| Check | Question |
|---|---|
| Source quality | Is the source approved or defensible? |
| Geography | Is the geography broad and non-operational? |
| Detail level | Are addresses, coordinates, names, and operational details excluded? |
| Category | Is the category careful and source-grounded? |
| Legal status | Does the note avoid overstating allegations or listings? |
| Scoring | Is `include_in_score` false? |
| Report/dashboard inclusion | Should this be displayed in the PDF appendix or dashboard reference tab? |
| Responsible-use note | Does the row include a clear caveat? |
| TDOC context | If using TDOC data, is the row clearly marked correctional-system context and non-scoring? |
| Count consistency | If using FY2025 TDOC facility totals, do confirmed + suspected counts equal the reported total? |

---

## Best Practice

Keep the group reference and TDOC STG context layers separate from scoring. They are strongest as source registers, dashboard reference tabs, appendices, or analyst-reference tables.

Use the TBI hate-crime report context to explain statewide targeted-harm patterns, not to infer county-level motive, actor identity, or threat conditions. Use TDOC STG context only to explain correctional-system aggregate context, not community presence or county-level activity.

When adding new sources, prefer official reports, court documents, and carefully documented public trackers. Avoid social media, forums, screenshots, or unverified claims unless they are cited by a credible primary or secondary source.

---

## Summary

The public group / network reference layer, TDOC STG context layer, and TBI hate-crime context layer strengthen the final report and dashboard by adding defensible context. Their value comes from careful source documentation, cautious language, and strict separation from scoring.

The safest rule is:

```text
Reference/context layers may inform the appendix and dashboard reference tabs.
They should not drive county scores, risk labels, operational conclusions, or community-presence claims.
```

---

## GitHub Publication Notes

For GitHub publication, this guide should be tracked as:

```text
docs/public_group_reference_sources.md
```

Recommended GitHub handling:

- Track this documentation file.
- Track `src/public_group_reference.py`.
- Track `src/splc_group_reference_processor.py`.
- Track `src/tbi_hate_crime_report_context.py`.
- Track `src/tdoc_stg_reference_processor.py`.
- Track `app.py`.
- Do not commit raw SPLC CSV files.
- Do not commit raw TBI report exports if they contain unsanitized source material.
- Do not commit raw TDOC PDFs if they contain sensitive or historical correctional-system detail; commit only sanitized generated samples if intentionally publishing them.
- Do not commit `.env`.
- Do not commit large generated `outputs/` folders unless publishing a deliberate sanitized sample.
- Use `.gitkeep` files to preserve folder structure.

Recommended ignored paths:

```text
data/raw/*
data/processed/*
outputs/charts/*
outputs/tables/*
outputs/reports/*
.env
.venv/
__pycache__/
```

The GitHub-facing documentation should make clear that public group / network references, TDOC correctional-system STG context, and statewide hate-crime context are non-scoring, non-operational, and for contextual interpretation only.
