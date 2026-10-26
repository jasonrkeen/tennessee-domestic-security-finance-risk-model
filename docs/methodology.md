# Methodology

**Project:** Tennessee Domestic Security & Illicit Finance Risk Intelligence Model  
**Prepared by:** Jason Keen  
**Version:** Phase 6 Operational Risk / Dashboard / TDOC STG Context / Reference Build  
**Purpose:** Explain the analytical design, data-processing workflow, scoring logic, validation approach, sensitivity testing, dashboard presentation layer, non-scoring reference/context layers, and responsible-use boundaries for the Tennessee county-level model.

---

## 1. Project Objective

The Tennessee Domestic Security & Illicit Finance Risk Intelligence Model is a county-level open-source intelligence framework designed to compare relative exposure, vulnerability, and monitoring-priority conditions across Tennessee counties.

The model combines public and aggregate indicators related to:

- Household financial stress
- Banking access and deposit depth
- Cash-economy and regulated-retail exposure
- Lawful FFL and tactical-access aggregate indicators
- TBI CrimeInsight crime/weapons pressure
- TBI overall crime-rate pressure
- TBI gang-related criminal activity
- TBI explosive-use criminal activity
- TBI gang + explosive-use intersection activity
- TBI hate-crime / targeted-harm offense activity
- TBI law-enforcement ambush activity
- ACLED political violence / civil unrest exposure
- FEMA disaster exposure
- Phase 6 disaster / disruption vulnerability
- Institutional / enforcement pressure
- Operational risk and protective-planning exposure
- Transportation pressure, infrastructure needs, healthcare capacity, and law-enforcement response-capacity baseline
- Public group / network reference context
- TDOC correctional-system STG reference context
- TBI 2024 statewide hate-crime context
- Data completeness and model confidence
- Sensitivity and rank-stability testing
- 2023–2024 selected crime/weapons trend analysis
- Streamlit dashboard presentation and county intelligence brief generation

The model is intended for **relative county-level risk intelligence and defensive protective-planning support**, not prediction, attribution, law-enforcement targeting, or individual/entity assessment. The Streamlit dashboard is a presentation layer that reads the model outputs and does not create new baseline model scores.

---

## 2. Responsible-Use Framework

This model follows a responsible-use design principle: all scoring inputs are aggregated to the county level, and the model does not retain or publish individual-level, incident-level, address-level, tactical-site-level, business-level, licensee-level, gang-name, organization-name, suspect/victim, event-note, coordinate, or case-narrative records.

The model does **not**:

- Predict attacks
- Identify suspects
- Identify threat actors
- Label counties as having terrorism or extremism activity
- Infer motive, ideology, or actor identity
- Assess individual businesses, FFLs, licensees, institutions, agencies, addresses, or facilities
- Treat lawful business activity as suspicious
- Treat FFL licensing as suspicious activity
- Treat gang activity, explosive-use crime, hate-crime offense counts, or law-enforcement ambush counts as terrorism labels
- Treat public group / network references as county-risk labels
- Treat statewide hate-crime context as county-level scoring input
- Treat dashboard scenario controls as official replacement scores
- Treat operational-risk scores as target lists, facility vulnerability disclosures, route-selection tools, or agency performance ratings
- Use law-enforcement response-capacity indicators to evaluate individual agencies or current staffing adequacy

Sensitive fields are treated as **aggregate pressure indicators** only. They may warrant additional contextual review when combined with other county-level signals, but they are not standalone findings.

The public group / network reference register, TDOC correctional-system STG context layer, and TBI 2024 statewide hate-crime context outputs are **reference-only / context-only appendices**. They are not used in the final score, county ranking, risk signal, model sensitivity scenarios, operational-risk score, or county-level monitoring-priority calculations.

The TDOC STG context layer is limited to sanitized correctional-system context. It should not be interpreted as current community presence, street-level activity, county-level group activity, terrorism, ideology, suspicious conduct, or criminal conduct by any specific person, group, business, facility, or place.

The dashboard includes filters, scenario controls, an operational-risk tab, and a county intelligence brief generator. These are user-interface and presentation tools. They do not change the baseline methodology or the underlying scored output tables. The operational-risk layer is kept separate from the main domestic-security risk score so response-capacity and resilience indicators are not misread as threat indicators.

---

## 3. Geographic Unit of Analysis

The unit of analysis is the Tennessee county.

County names are standardized through the ACS county base. Optional local inputs are crosswalked back to the ACS county list using normalized county keys. This prevents dropped counties when source files use slightly different naming conventions such as:

- `Davidson`
- `Davidson County`
- `Davidson, Tennessee`
- `Davidson, TN`

Summary rows such as `Total`, `Statewide`, `Tennessee`, `Unknown`, and blank rows are removed from optional aggregate inputs.

The public group / network reference layer may preserve broad geography such as statewide, county, multi-county, city, or region references, but those records are not merged into the scoring dataset.

---

## 4. Data Sources

### 4.1 U.S. Census ACS 5-Year API

ACS data provides the core county base and socioeconomic indicators.

Primary fields include:

- Population
- Median household income
- Poverty count and poverty universe
- Labor force and unemployed count
- Renter households and rent-burden categories

Derived indicators include:

- Poverty rate
- Unemployment rate
- Rent-burden rate
- Household financial stress score

### 4.2 Census County Business Patterns API

County Business Patterns data provides selected establishment counts by NAICS industry. These are used only as exposure proxies.

Selected categories include:

- Tobacco/vape retail
- Sporting goods stores
- Used merchandise stores
- Gas stations with convenience stores
- Convenience stores
- Consumer lending
- Coin-operated laundry / dry cleaning
- Used auto dealers

These categories are lawful business categories and are not indicators of wrongdoing.

### 4.3 FDIC Banking Inputs

The FDIC-derived county-level banking input captures:

- Bank branch count
- Total deposits in thousands of dollars

Derived indicators include:

- Branches per 10,000 residents
- Deposits per capita
- Banking access gap score

The model does not retain branch-level or institution-level records.

### 4.4 ATF FFL Aggregate Inputs

The FFL input captures county-level license-type aggregates only.

Fields include:

- Total FFL count
- Dealer FFL count
- Manufacturer FFL count
- Pawnbroker FFL count
- Collector FFL count
- Importer FFL count
- Destructive-device-related FFL subtype count

The destructive-device-related field may overlap with importer/manufacturer categories and should not be summed with other subtypes to reconcile to total FFL count.

FFL counts are lawful licensing and access-complexity proxies only.

### 4.5 Tactical-Access Optional Inputs

Optional county-level tactical-access inputs include:

- Tactical training count
- Surplus / tactical retail count
- Gun range count

These are lawful access and planning-complexity proxies only. The model should not include business names, addresses, URLs, owners, coordinates, or site-level maps.

### 4.6 FEMA Disaster Declarations

FEMA disaster declaration data is used to capture historical disaster exposure.

Fields include:

- Disaster declaration count
- Unique disaster types
- Recent disaster declaration count

These feed the FEMA-based infrastructure disruption score.

### 4.7 Phase 6 Disaster / Disruption Inputs

The optional disaster/disruption layer extends the FEMA layer with county-level aggregate fields related to:

- Severe storms
- Floods
- Tornadoes
- Winter weather
- Wildfires
- Drought
- Power outage frequency
- Average outage duration
- Hospital access stress
- Airport access stress
- Road access stress
- Communications disruption
- Social vulnerability
- Recovery strain
- Repeat disruption exposure

These fields are intended to capture county-level continuity, access, response-strain, and disruption vulnerability. They should not include facility addresses, exact locations, utility maps, road chokepoints, infrastructure diagrams, or operational vulnerability details.

### 4.8 TBI CrimeInsight Crime / Weapons Inputs

The crime/weapons layer uses county-level aggregate TBI CrimeInsight or TNCrimeOnline offense exports.

Mapped categories include:

- Homicide
- Kidnapping / abduction
- Weapon law violations
- Violent crime
- Aggravated assault
- Arson
- Sex offenses
- Hate crime count, if available in the broad export
- Law-enforcement assault count, if available in the broad export

If violent crime is not separately exported, the processor may create a partial violent-crime count from selected violent offense categories.

### 4.9 TBI Overall Crime-Rate Inputs

The overall crime-rate layer uses county-level aggregate crime-rate exports from TBI/TNCrimeOnline.

Fields include:

- Overall crime rate per 1,000 residents
- Overall number of crimes
- Crime-rate population denominator

These fields are used to build the overall crime-rate index.

### 4.10 TBI Gang-Related Criminal Activity Inputs

The gang activity layer uses county-level aggregate exports filtered to gang-related activity.

Fields include:

- Total gang-related crime count
- Gang-related violent crime count
- Gang-related weapon law violation count
- Gang-related drug offense count
- Gang-related property offense count
- Gang-related homicide count
- Gang-related kidnapping / abduction count
- Gang-related aggravated assault count
- Gang-related robbery count
- Gang-related arson count
- Gang-related sex offense count

Gang-related crime is not a terrorism label. It is treated as an organized/group criminal activity pressure indicator.

### 4.11 TBI Explosive-Use Criminal Activity Inputs

The explosive-use layer uses county-level aggregate exports filtered to offenses involving explosive use.

Fields include:

- Total explosive-related offense count
- Explosive-related violent offense count
- Explosive-related weapon law violation count
- Explosive-related drug offense count
- Explosive-related property offense count
- Explosive-related homicide count
- Explosive-related kidnapping / abduction count
- Explosive-related aggravated assault count
- Explosive-related robbery count
- Explosive-related arson count
- Explosive-related sex offense count
- Explosive-related property damage count

Explosive-use activity is not a terrorism label. It is treated as a high-severity criminal activity and capability proxy.

### 4.12 TBI Gang + Explosive-Use Intersection Inputs

The gang + explosive-use layer captures the intersection of gang-related activity and explosive-use activity.

Fields include:

- Gang-related explosive-use total offense count
- Gang-related explosive-use violent offense count
- Gang-related explosive-use weapon law violation count
- Gang-related explosive-use drug offense count
- Gang-related explosive-use property offense count
- Gang-related explosive-use homicide count
- Gang-related explosive-use kidnapping / abduction count
- Gang-related explosive-use aggravated assault count
- Gang-related explosive-use robbery count
- Gang-related explosive-use arson count
- Gang-related explosive-use sex offense count
- Gang-related explosive-use property damage count

This is a high-severity intersection indicator only. It does not infer terrorism, motive, ideology, or actor identity.

### 4.13 TBI Hate-Crime / Targeted-Harm Inputs

The hate-crime offense layer uses county-level aggregate TBI/TNCrimeOnline hate-crime offense exports.

Fields include:

- Hate-crime total count
- Hate-crime homicide count
- Hate-crime kidnapping / abduction count
- Hate-crime sex offense count
- Hate-crime aggravated assault count
- Hate-crime simple assault count
- Hate-crime intimidation count
- Hate-crime arson count
- Hate-crime weapon law violation count
- Hate-crime property damage count
- Hate-crime property offense count
- Hate-crime other offense count

These indicators are treated as targeted-harm / bias-motivated offense pressure proxies only.

### 4.14 TBI Law-Enforcement Ambush Inputs

The law-enforcement ambush layer uses county-level aggregate TBI/TNCrimeOnline exports.

Fields include:

- Law-enforcement ambush total count
- Law-enforcement ambush homicide count
- Law-enforcement ambush kidnapping / abduction count
- Law-enforcement ambush aggravated assault count
- Law-enforcement ambush simple assault count
- Law-enforcement ambush intimidation count
- Law-enforcement ambush weapon law violation count
- Law-enforcement ambush arson count
- Law-enforcement ambush property damage count
- Law-enforcement ambush property offense count
- Law-enforcement ambush drug offense count
- Law-enforcement ambush other offense count

Law-enforcement ambush activity is a public-safety personnel violence / tactical-planning proxy. It is not a terrorism indicator by itself and does not infer motive, ideology, or actor identity.

### 4.15 ACLED Political Violence / Civil Unrest Inputs

ACLED data is processed into county-level aggregate indicators.

Fields include:

- Protest event count
- Violent unrest event count
- Political violence event count
- Strategic development count
- Public disorder event count
- Total ACLED event count
- ACLED fatalities

The processor saves a sanitized audit file by default and does not preserve event notes, actor names, organization names, exact locations, coordinates, URLs, narratives, or site-level maps in model outputs.

### 4.16 SPLC Public Group / Network Reference Inputs

The SPLC public group / network reference layer is a non-scoring reference layer based on a Tennessee-specific SPLC Hate Map CSV.

The processor creates:

- `tn_splc_public_group_reference_candidates_2024.csv`
- `tn_public_group_activity_reference.csv`
- `tn_public_group_reference_validation.csv`

This layer is used only for the PDF appendix or analyst-reference context. It is not included in scoring, ranking, risk signals, or sensitivity analysis.

The processor does not retain or publish:

- Addresses
- Coordinates
- Individual names
- Social media handles
- Meeting locations
- Recruitment channels
- Operational notes
- Case narratives

The SPLC source category is retained as a source classification only. The model does not independently verify membership, activity, criminality, motive, ideology, operational conduct, or active local presence.

### 4.17 TBI 2024 Hate Crime Report Context

The TBI 2024 Hate Crime Report context layer creates statewide context tables.

The processor creates:

- `tn_2024_hate_crime_bias_context.csv`
- `tn_2024_hate_crime_offense_context.csv`
- `tn_2024_hate_crime_clearance_context.csv`
- `tn_2024_hate_crime_location_context.csv`
- `tn_2024_hate_crime_report_context_summary.csv`

This layer is context-only. It does not replace the county-level hate-crime offense input and is not included in scoring.


### 4.18 TDOC Correctional-System STG Context

The TDOC correctional-system Security Threat Group (STG) context layer is a non-scoring appendix layer created by `tdoc_stg_reference_processor.py`.

It uses two source types:

- A 2010 TDOC historical correctional-system STG assessment, treated only as historical institutional context.
- The TDOC FY2025 Statistical Abstract, treated only as public facility-level aggregate correctional-system context.

The processor creates:

- `tn_tdoc_stg_reference_context.csv`
- `tn_tdoc_stg_reference_validation.csv`

The FY2025 output retains only broad facility-level aggregate counts for confirmed, suspected, and total TDOC correctional classifications. The 2010 output retains only broad historical group names from the correctional-system context. It does not retain recognition details, identifiers, imagery, staff contact details, incident narratives, intelligence-priority details, addresses, coordinates, or operational notes.

This layer is not merged into the county scoring dataset, the organized-violence score, the public group reference score, the operational-risk layer, the scenario analysis, or the county ranking. It is used only as a sanitized appendix and dashboard context table.

### 4.19 Operational Risk & Protective Planning Source Layers

The Operational Risk & Protective Planning layer is a separate defensive planning layer. It is designed to compare county-level exposure, resilience gap, infrastructure pressure, transportation pressure, healthcare capacity, FEMA vulnerability/resilience, and law-enforcement response-capacity context.

This layer is not a targeting product and does not identify facilities, addresses, routes, schedules, coordinates, individuals, agency-level tactical details, or exploitable vulnerabilities.

### 4.20 Census / ACS County Profile Data

The county profile preparation script creates a reusable county baseline file used by the operational-risk layer.

Fields include:

- County name
- Population
- Population density
- Poverty rate
- Unemployment rate
- Median household income
- FEMA social vulnerability indicators when available
- FEMA community resilience indicators when available

This file supports exposure and resilience calculations but remains county-level only.

### 4.21 TDOT Transportation Context

The transportation context layer uses TDOT traffic-line data aggregated to the county level.

Fields include:

- Average annual daily traffic proxy
- Total vehicle miles traveled
- Truck percentage
- Traffic station count
- Total traffic-line mileage

These values feed the transportation pressure score. They are broad mobility and continuity proxies only, not route-selection or movement-planning guidance.

### 4.22 Sycamore Healthcare Capacity Context

The healthcare capacity layer uses county-level Tennessee healthcare resource data from the Sycamore Institute health care capacity workbook.

Fields include:

- Hospital beds per 100,000 residents
- Emergency department count
- Primary care rate
- Trauma access proxy
- Supporting audit fields such as hospital count, staffed inpatient beds, general surgeons, primary care physicians, and PA/NP counts where available

The model uses these fields as healthcare and emergency-capacity proxies. Facility names, addresses, coordinates, and site-level details are not retained in scoring outputs.

### 4.23 TACIR Infrastructure Needs Context

The infrastructure context layer uses TACIR public infrastructure needs reporting, especially county-level infrastructure-needs totals and per-capita values.

Fields include:

- Total infrastructure needs
- Infrastructure needs per capita
- Infrastructure project count
- Regional infrastructure needs
- Local infrastructure needs

This layer supports broad public-sector continuity and infrastructure pressure analysis. It should not include individual project addresses, facility vulnerability descriptions, infrastructure diagrams, or site-specific operational details.

### 4.24 CSLLEA Law-Enforcement Response-Capacity Baseline

The law-enforcement capacity layer uses the 2018 Census of State and Local Law Enforcement Agencies, processed to Tennessee county-level aggregates.

Fields include:

- Law-enforcement agency count
- Complete-reporting agency count
- Sheriff office count
- Local police agency count
- Full-time employees
- Sworn personnel
- Sworn personnel per 100,000 residents
- Full-time employees per 100,000 residents
- Patrol/response agency count
- Dispatch agency count
- Criminal investigation agency count
- Traffic enforcement agency count
- Specialized response agency count
- Law-enforcement capacity score
- Law-enforcement capacity gap score

This layer is a 2018 structural response-capacity baseline. It is not a current staffing estimate, not an agency-performance rating, and not a threat indicator. The project does not publish agency names, ORI identifiers, station locations, addresses, or tactical details.

### 4.25 Streamlit Dashboard Inputs

The Streamlit dashboard reads the pipeline's existing output tables, charts, and report files.

Primary dashboard inputs include:

- `tn_county_domestic_security_scores.csv`
- `data/processed/tn_operational_risk_features.csv`
- `tn_county_component_scores.csv`
- `tn_county_finance_tactical_scores.csv`
- `tn_county_organized_violence_scores.csv`
- `tn_county_targeted_harm_public_safety_scores.csv`
- `tn_county_disaster_disruption_scores.csv`
- `tn_county_institutional_enforcement_scores.csv`
- `tn_county_political_violence_scores.csv`
- `tn_county_data_quality_flags.csv`
- `model_weight_sensitivity_results.csv`
- `top_county_rank_stability.csv`
- `tn_public_group_activity_reference.csv`
- `tn_public_group_reference_validation.csv`
- `tn_tdoc_stg_reference_context.csv`
- `tn_tdoc_stg_reference_validation.csv`
- `tn_2024_hate_crime_*_context.csv`
- `source_register.csv`
- `outputs/charts/*.png`
- `outputs/reports/tennessee_domestic_security_finance_risk_report.pdf`

The dashboard does not write to the baseline scoring outputs. It is a presentation layer for exploration, filtering, scenario review, source review, and county brief generation.

---

## 5. Data Processing Workflow

The current project pipeline follows this general structure:

1. Create or refresh public group / network reference outputs.
2. Create or refresh TBI 2024 statewide hate-crime context outputs.
3. Create or refresh TDOC correctional-system STG context outputs.
3. Create required directories.
4. Pull ACS county socioeconomic data.
5. Pull CBP business exposure data.
6. Pull FEMA disaster declaration data.
7. Load optional tactical-access inputs.
8. Load FDIC banking aggregates.
9. Load FFL county aggregates.
10. Load TBI crime/weapons aggregates.
11. Load TBI crime-rate aggregates.
12. Load ACLED county political violence / civil unrest aggregates.
13. Load TBI gang activity aggregates.
14. Load TBI explosive-use aggregates.
15. Load TBI gang + explosive-use aggregates.
16. Load TBI hate-crime offense aggregates.
17. Load TBI law-enforcement ambush aggregates.
18. Load Phase 6 disaster/disruption inputs.
19. Merge scoring sources into the master county dataset.
20. Fill missing numeric values defensively.
21. Calculate per-capita rates.
22. Normalize indicators into 0-to-100 scores.
23. Build component scores.
24. Build final composite score and risk signal.
25. Add data-quality and model-confidence flags.
26. Prepare operational-risk source layers: Census/ACS county profile, TBI public-safety context, TDOT transportation context, healthcare capacity, TACIR infrastructure needs, and CSLLEA law-enforcement capacity.
27. Build `data/processed/tn_operational_risk_features.csv`.
28. Run sensitivity analysis.
29. Run crime trend analysis.
30. Generate charts, including operational-risk charts.
31. Generate the PDF report, including the operational-risk section.
32. Print the pipeline summary.
33. Open the Streamlit dashboard with `streamlit run app.py` for interactive review.

The public group / network reference and TBI statewide hate-crime context outputs are generated before the PDF so the appendices can load the latest validated tables. They are **not merged into the master scoring dataset**.

---

## 6. Normalization Method

Most model indicators are converted to 0-to-100 scores using min-max normalization.

For indicators where higher raw values indicate higher exposure:

```text
score = ((value - min_value) / (max_value - min_value)) * 100
```

For inverse indicators where lower raw values indicate higher vulnerability, the scoring direction is reversed. Examples include:

- Lower median household income
- Lower bank branch density
- Lower deposit depth

```text
inverse_score = 100 - normalized_score
```

If all values are equal or if a variable has no usable variation, the model uses a neutral or zero-safe fallback depending on the component logic. Neutral-only charts are skipped in visualization outputs to avoid presenting non-informative flat rankings.

---

## 7. Per-Capita Rate Method

Many count indicators are converted into per-capita rates to improve comparability across counties.

The standard rate calculation is:

```text
rate_per_10k = (count / population) * 10,000
```

This approach is used for:

- FFL counts
- Tactical-access counts
- TBI crime/weapons counts
- Gang-related activity counts
- Explosive-use activity counts
- Gang + explosive-use activity counts
- Hate-crime offense counts
- Law-enforcement ambush counts
- ACLED event counts
- Disaster/disruption event counts

Population values are drawn from ACS.

The public group / network reference layer is not converted to per-capita rates because it is non-scoring and reference-only.

---

## 8. Component Score Methodology

### 8.1 Household Financial Stress Score

The household financial stress score combines:

| Indicator | Interpretation |
|---|---|
| Poverty score | Higher poverty rate indicates greater financial stress. |
| Unemployment score | Higher unemployment rate indicates greater labor-market stress. |
| Income stress score | Lower median household income indicates greater stress. |
| Rent burden score | Higher rent burden indicates greater household cost pressure. |

The resulting score represents county-level socioeconomic stress.

### 8.2 Banking Access Gap Score

The banking access gap score combines:

| Indicator | Interpretation |
|---|---|
| Low branch access score | Higher values indicate fewer bank branches per capita. |
| Low deposit depth score | Higher values indicate lower deposits per capita. |

The score is a formal financial access and deposit-depth proxy.

### 8.3 Cash-Intensive Retail Score

The cash-intensive retail score combines selected establishment categories such as:

- Used merchandise stores
- Gas stations / convenience stores
- Consumer lending
- Laundry services
- Used auto dealers

These are lawful business categories and are used only as county-level exposure proxies.

### 8.4 Tobacco / Vape Exposure Score

The tobacco/vape exposure score combines tobacco/vape establishment density with household financial stress. This is a regulated retail exposure proxy and should not be interpreted as suspicious activity.

### 8.5 Tactical Access Score

The tactical-access score combines:

- Sporting goods density
- FFL density
- FFL subtype score
- Tactical training count
- Surplus/tactical retail count
- Gun range count

FFL subtype scoring includes dealer, manufacturer, pawnbroker, collector, importer, and destructive-device-related subtype fields.

This is a lawful access-complexity proxy only.

### 8.6 FEMA Infrastructure Disruption Score

The FEMA-based infrastructure disruption score combines:

- Disaster declaration count
- Unique disaster types
- Recent disaster declaration count

This score is retained as a historical disaster exposure component.

### 8.7 Phase 6 Disaster / Disruption Vulnerability Score

The Phase 6 disaster/disruption score extends the FEMA layer by combining:

| Subcomponent | Inputs |
|---|---|
| Severe weather exposure | Severe storm, flood, tornado, winter weather, wildfire, drought |
| Power disruption exposure | Power outage frequency and average outage duration |
| Access stress | Hospital access, airport access, road access, communications disruption |
| Recovery strain exposure | Social vulnerability, recovery strain, repeat disruption exposure |
| FEMA disruption exposure | FEMA disaster declaration history |

When optional Phase 6 disruption fields are not populated, the model can fall back to the FEMA-based infrastructure disruption score.

### 8.8 Crime / Weapons Pressure Score

The crime/weapons pressure score combines selected TBI CrimeInsight categories, including:

- Homicide
- Kidnapping / abduction
- Weapon law violations
- Violent crime
- Aggravated assault
- Arson
- Sex offenses
- Hate crime count, if available from broad crime/weapons input
- Law-enforcement assault count, if available

The score uses county-level counts and per-capita rates.

### 8.9 Overall Crime-Rate Index Score

The overall crime-rate index combines:

- Overall crime rate per 1,000 residents
- Overall crime count / pressure

This layer provides a broad public-safety pressure context.

### 8.10 Gang-Related Criminal Activity Pressure Score

The gang-related activity score combines:

- Total gang-related crime
- Gang-related violent crime
- Gang-related weapon law violations
- Gang-related drug offenses
- Gang-related property offenses
- Selected high-severity offense categories

This layer is an organized/group criminal activity pressure proxy.

### 8.11 Explosive-Use Criminal Activity Pressure Score

The explosive-use score combines:

- Total explosive-related offenses
- Explosive-related violent offenses
- Explosive-related weapon law violations
- Explosive-related homicide
- Explosive-related arson
- Explosive-related property damage

This layer is a high-severity capability / criminal-use proxy.

### 8.12 Gang + Explosive Intersection Pressure Score

The gang + explosive intersection score combines:

- Gang-related explosive-use total offenses
- Gang-related explosive-use violent offenses
- Gang-related explosive-use weapon law violations
- Gang-related explosive-use homicide
- Gang-related explosive-use arson
- Gang-related explosive-use property damage

This score captures a narrow high-severity intersection of organized/group criminal activity and explosive-use activity.

### 8.13 Hate-Crime / Targeted-Harm Pressure Score

The hate-crime / targeted-harm score combines:

- Hate-crime total rate
- Hate-crime violent rate
- Hate-crime intimidation rate
- Hate-crime weapon law violation rate
- Hate-crime property damage rate

This layer is a targeted-harm / bias-motivated offense pressure proxy.

### 8.14 Law-Enforcement Ambush Pressure Score

The law-enforcement ambush score combines:

- Ambush total rate
- Ambush violent rate
- Ambush weapon law violation rate
- Ambush intimidation rate
- Ambush property damage rate

This layer is a public-safety personnel violence / tactical-planning proxy.

### 8.15 Targeted Harm / Public-Safety Pressure Score

The targeted harm / public-safety pressure score combines:

| Component | Weight |
|---|---:|
| Hate-crime / targeted-harm pressure | 55% |
| Law-enforcement ambush pressure | 45% |

### 8.16 ACLED Political Violence / Civil Unrest Exposure Score

The ACLED political violence / civil unrest score combines county-level ACLED indicators such as:

- Protests
- Violent unrest
- Political violence
- Strategic developments
- Public disorder
- Total ACLED events
- ACLED fatalities

The ACLED layer is an aggregate civil unrest and political violence exposure proxy.

### 8.17 Organized Violence / High-Severity Crime Pressure Score

The organized violence / high-severity crime pressure score combines:

| Component | Weight |
|---|---:|
| Crime / weapons pressure | 30% |
| Overall crime-rate index | 15% |
| Gang-related criminal activity pressure | 18% |
| Explosive-use criminal activity pressure | 13% |
| Gang + explosive intersection pressure | 13% |
| Targeted harm / public-safety pressure | 11% |

### 8.18 Finance & Tactical Vulnerability Score

The finance/tactical vulnerability score combines:

- Household financial stress
- Banking access gap
- Cash-intensive retail exposure
- Tobacco/vape regulated retail exposure
- Tactical-access exposure
- FEMA / disaster disruption exposure, where applicable

This score captures financial vulnerability, cash-economy exposure, and lawful access-complexity conditions.

### 8.19 Institutional / Enforcement Pressure Score

The institutional/enforcement pressure score is now an active derived layer.

| Component | Weight |
|---|---:|
| Law-enforcement ambush pressure | 25% |
| Law-enforcement assault pressure | 20% |
| Crime / weapons pressure | 20% |
| Overall crime-rate index | 15% |
| Targeted harm / public-safety pressure | 10% |
| Disaster / disruption vulnerability | 10% |

This score is intended to represent county-level public-safety and institutional response pressure. It does not measure agency performance, misconduct, ideology, or threat actor identity.



### 8.20 Operational Risk & Protective Planning Layer

The operational-risk layer is intentionally calculated outside the final domestic-security risk score. It combines existing threat/context information with separate exposure and response-capacity indicators.

The layer is built around three concepts:

| Concept | Interpretation |
|---|---|
| Existing threat context | Uses already-derived county-level public-safety and domestic-security context as one input, without adding new individual or site-level information. |
| Operational exposure | Captures population exposure, density, transportation pressure, infrastructure pressure, public-safety context, and socioeconomic pressure. |
| Resilience gap | Captures healthcare capacity gap, FEMA vulnerability/resilience context, and law-enforcement response-capacity gap. |

The final operational-risk score is a defensive planning score. Higher values indicate greater relative protective-planning complexity within Tennessee counties. It should not be interpreted as a threat forecast, target list, facility vulnerability assessment, route-selection tool, or agency performance rating.

### 8.21 Operational Exposure Score

The operational exposure score combines broad county-level exposure indicators such as:

- Population exposure
- Population density exposure
- Socioeconomic pressure
- Transportation pressure
- Infrastructure pressure
- Public-safety context

This score identifies counties where aggregate exposure conditions may increase planning complexity.

### 8.22 Resilience Gap Score

The resilience gap score combines broad response-capacity and resilience indicators such as:

- Healthcare capacity gap
- FEMA social vulnerability
- FEMA community resilience gap
- Law-enforcement capacity gap

Higher values indicate weaker relative resilience or response-capacity context. The score does not assess individual hospitals, agencies, facilities, or current staffing adequacy.

### 8.23 Law-Enforcement Capacity Gap Score

The law-enforcement capacity gap score is derived from county-level CSLLEA 2018 staffing and function aggregates. It is included as a defensive response-capacity proxy.

Interpretation rules:

- Higher gap values indicate lower relative county-level law-enforcement capacity proxy values in the 2018 baseline.
- The field is not a measure of agency quality, performance, preparedness, or current staffing adequacy.
- The processed model output does not include agency names, ORI identifiers, station addresses, coordinates, or tactical capability details.

### 8.24 Operational-Risk Data Quality

The operational-risk layer includes its own source coverage flag, usually expressed as `Strong`, `Partial`, or `Limited`.

This flag measures whether county-level operational-risk source layers were populated. It does not measure threat level. Neutral component scores may appear when a source field has no usable variation or when only a placeholder/fallback value is available.

---

## 9. Non-Scoring Reference and Context Methodology

### 9.1 Public Group / Network Reference Register

The public group / network reference register is designed as a source-register appendix, not a scoring input.

It uses:

- SPLC Tennessee 2024 Hate Map CSV source-assisted candidate generation
- Manually reviewed public group / network reference inputs
- Validation logic in `public_group_reference.py`

The validator:

- Blocks prohibited columns
- Removes example/template rows from output
- Deduplicates repeated references
- Validates category, source type, geography, and confidence values
- Requires source name, source URL, and responsible-use notes
- Forces `include_in_score = False`

This layer may include broad geographic references such as city, region, county, statewide, multi-county, or unknown. It should not include addresses, coordinates, exact meeting locations, individual names, handles, recruitment channels, operational notes, or case narratives.

The reference register does **not** mean:

- The group is active in a specific county.
- A county is unsafe.
- A terrorism threat exists.
- A public reference is an independent model finding.
- The model has verified membership, intent, ideology, motive, or operational conduct.


### 9.2 TDOC Correctional-System STG Context

The TDOC STG context layer is a sanitized, non-scoring appendix layer. It is designed to document correctional-system context without turning correctional classifications into county-level risk indicators.

The processor:

- Reads the 2010 TDOC historical assessment as historical institutional context only.
- Reads the FY2025 TDOC Statistical Abstract as public facility-level aggregate context only.
- Creates facility-total rows for confirmed, suspected, and total STG/gang correctional classifications.
- Creates broad historical-reference rows for the 2010 source.
- Forces `include_in_score = False`.
- Sanitizes public-facing text fields.
- Validates row count, facility count population, arithmetic consistency, prohibited-detail terms, and correctional-context flags.

The TDOC STG context layer does **not** mean:

- A group is active in a Tennessee county.
- A group is active in the community.
- A county has current STG activity.
- A facility total implies county-level activity around that facility.
- The model has identified individual members, suspects, or threat actors.
- The model is making a terrorism, ideology, public-safety threat, or criminality finding.

This layer is not included in the final score, organized-violence score, public group reference register, operational-risk score, sensitivity scenarios, county ranks, or data-completeness score.

### 9.3 TBI 2024 Hate Crime Report Context

The TBI 2024 statewide hate-crime context layer is used to explain the targeted-harm layer in the PDF appendix.

It creates statewide context tables for:

- Bias category
- Offense type
- Clearance status
- Location type
- Summary context

This layer does not replace county-level hate-crime offense inputs and is not used for scoring. It is intended to add statewide background and interpretation support only.

---

## 10. Dashboard Methodology

The Streamlit dashboard is an interactive presentation layer built in `app.py`. It reads the model's saved CSV, PNG, and PDF outputs from the `outputs/` directory.

The dashboard includes:

- Executive overview
- County rankings
- County deep dive
- County intelligence brief generator
- Operational Risk & Protective Planning tab
- Finance / tactical vulnerability tab
- Organized violence / high-severity crime tab
- Targeted harm / public-safety tab
- Disaster / disruption vulnerability tab
- Institutional / enforcement pressure tab
- Political violence / civil unrest tab
- Scenario controls
- Data-quality tab
- Public group / network reference tab
- TDOC STG correctional-system context tab
- TBI hate-crime context tab
- Source register tab
- Responsible-use model card
- PDF download tab

### 10.1 Dashboard Filter Logic

The sidebar includes county-level filters:

| Filter | Methodological Role |
|---|---|
| County filter | Narrows county-level dashboard tables and views. Empty selection means all counties. |
| Risk-signal filter | Narrows score-based dashboard views by risk signal. Empty selection means all risk signals. |

These filters do not change the underlying model outputs. They only change what is displayed in the dashboard.

The public group / network reference tab, TDOC STG context tab, and TBI hate-crime context tab are not treated as county-score filters because those layers are non-scoring appendix/context layers.

### 10.2 Dashboard Scenario Controls

The scenario tab calculates exploratory dashboard scenario scores using selected preset weights.

These dashboard scenario scores:

- Are calculated in the dashboard from existing component scores.
- Are intended for exploratory comparison only.
- Do not overwrite the baseline final score.
- Do not replace the formal sensitivity-analysis outputs.
- Should be interpreted alongside `model_weight_sensitivity_results.csv` and `top_county_rank_stability.csv`.

### 10.3 County Intelligence Brief Generator

The county brief generator creates a Markdown-style analyst summary for a selected county using existing output fields.

The brief includes:

- Final model score
- Risk signal
- Model confidence
- Data completeness
- Population
- Top contributing model layers
- Analytical interpretation
- Responsible-use notes
- Recommended analyst next steps
- Markdown download option

The county brief is a generated presentation product, not a separate model output. It does not create new risk findings or alter county rankings.

### 10.4 Operational-Risk Dashboard Tab

The dashboard includes an Operational Risk & Protective Planning tab that reads `data/processed/tn_operational_risk_features.csv`.

The tab displays:

- Top operational-risk county and score
- Average operational-risk score
- Limited-data row count
- County operational-risk ranking
- Component view
- Exposure vs. resilience gap scatter view
- Transportation, infrastructure, healthcare, and law-enforcement response-capacity context where available
- Operational-risk table download

This tab is defensive and aggregate-only. It does not identify facilities, routes, schedules, addresses, agency-level tactical details, individual people, or exploitable vulnerabilities.


### 10.5 TDOC STG Context Dashboard Tab

The dashboard includes a TDOC STG Context tab that reads:

- `outputs/tables/tn_tdoc_stg_reference_context.csv`
- `outputs/tables/tn_tdoc_stg_reference_validation.csv`

The tab displays sanitized non-scoring correctional-system context rows and validation output. It may include source-year and source-name filters, but those filters do not affect county scoring or ranking.

This tab is not a gang activity dashboard, community presence tracker, investigative list, or facility-risk assessment. It is a documentation appendix view for broad TDOC correctional-system context only.

### 10.6 Dashboard Responsible-Use Controls

The dashboard repeats responsible-use language in the overview, public reference tab, TBI context tab, county brief tab, and model card tab.

The dashboard should not be used to:

- Identify people, groups, businesses, licensees, or addresses
- Infer operational presence
- Make enforcement or investigative decisions
- Treat public group references as scoring inputs
- Treat exploratory scenario scores as official replacement scores

The dashboard is intended for portfolio demonstration, analytical review, and transparent exploration of aggregate county-level model outputs.


---

## 11. Final Composite Score

The final domestic security risk score is a weighted index of major model components.

| Component | Weight |
|---|---:|
| Finance & Tactical Vulnerability | 30% |
| Organized Violence / High-Severity Crime Pressure | 20% |
| Political Violence / Civil Unrest Exposure | 15% |
| Household Financial Stress | 15% |
| Disaster / Disruption Vulnerability | 10% |
| Tactical Access Exposure | 5% |
| Institutional / Enforcement Pressure | 5% |

The final score is interpreted as a relative county-level monitoring-priority score.

The public group / network reference register, TDOC correctional-system STG context layer, and TBI 2024 hate-crime context layer are not included in this weighted score.

---

## 12. Risk Signal Classification

The model assigns a risk signal based on the final composite score.

Typical interpretation:

| Score Range | Signal | Interpretation |
|---|---|---|
| 70+ | High | Highest relative monitoring priority. |
| 55–69.9 | Elevated | Elevated relative exposure and monitoring priority. |
| 35–54.9 | Guarded | Watch condition / moderate relative exposure. |
| Below 35 | Low | Lower relative exposure within the model. |

Risk signals are not findings of criminal conduct, terrorism, extremism, threat activity, public group activity, or active operational presence.

---

## 13. Data Quality and Model Confidence

The data-quality layer measures input coverage and source availability.

Active Phase 6 source flags include:

- ACS
- CBP
- FDIC
- FFL
- FEMA
- Disaster/disruption
- TBI crime/weapons
- TBI crime rate
- ACLED political violence / civil unrest
- TBI gang activity
- TBI explosive-use activity
- TBI gang + explosive-use activity
- TBI hate-crime offense activity
- TBI law-enforcement ambush activity

Targeted harm / public-safety and institutional / enforcement pressure retain
dependency-based diagnostic flags but are excluded from the source count.

The data completeness score is calculated as:

```text
data_completeness_score = (available_input_layer_count / 14) * 100
```

Model confidence is assigned as:

| Completeness Score | Confidence |
|---:|---|
| 0–40 | Low |
| 40–60 | Moderate |
| 60–80 | Good |
| 80–100 | High |

Data completeness measures source coverage, not risk or predictive confidence.
Availability requires complete finite nonnegative fields before imputation and
respects source-level availability markers. Column presence alone is insufficient.

Reference/context appendices have separate validation outputs and are not included in the county-level data-completeness score.

---

## 14. True-Zero and Missing-Data Handling

The model distinguishes between missing source layers and valid zero values.

Examples:

- A county may have true zero values for selected ACLED event categories.
- A county may have true zero values for selected gang-related activity categories.
- A county may have true zero values for selected hate-crime or law-enforcement ambush categories.
- A missing input file creates a zero-filled template with an explicit false
  availability marker. Re-reading it does not make it observed data.
- Legacy all-zero local rows are unverified unless source review confirms them
  and sets their layer-specific availability marker to true.
- Missing counties, incomplete schemas, and invalid values do not count as
  complete layer coverage, even though numeric scoring fallbacks remain unchanged.

See [source availability correction](source_availability_fix.md) for migration
notes and offline verification. Existing published artifacts are preserved.

Data-quality notes identify possible gaps, zero-filled inputs, and true-zero conditions.

For the public group / network reference layer, absence of a reference should not be interpreted as absence of activity. It only means no report-ready reference is present in the validated reference table.

---

## 15. Sensitivity Analysis

The sensitivity-analysis module tests whether county rankings remain stable under alternative weighting assumptions.

Current Phase 6 scenarios include:

| Scenario | Purpose |
|---|---|
| `baseline_phase6` | Current final model structure. |
| `finance_heavy` | Emphasizes finance and tactical vulnerability. |
| `organized_violence_heavy` | Emphasizes organized violence / high-severity crime pressure. |
| `targeted_harm_public_safety_heavy` | Emphasizes hate-crime, law-enforcement ambush, and targeted-harm indicators. |
| `institutional_enforcement_heavy` | Emphasizes institutional / enforcement pressure. |
| `gang_explosives_heavy` | Emphasizes gang, explosive-use, and gang + explosive-use indicators. |
| `political_violence_heavy` | Emphasizes ACLED political violence / civil unrest exposure. |
| `disaster_disruption_heavy` | Emphasizes disaster / disruption vulnerability. |
| `socioeconomic_heavy` | Emphasizes household financial stress. |
| `tactical_access_heavy` | Emphasizes tactical-access exposure. |

Outputs include:

- Scenario-level county scores
- Scenario-level ranks
- Best rank
- Worst rank
- Average rank
- Rank range
- Top-10 scenario count
- Rank stability signal

The public group / network reference, TDOC correctional-system STG context, and TBI 2024 hate-crime context layers are not included in sensitivity scenarios.

---

## 16. Crime Trend Analysis

The crime trend module compares selected TBI CrimeInsight crime/weapons indicators between 2023 and 2024.

Trend indicators include:

- Selected crime count in 2023
- Selected crime count in 2024
- Absolute change
- Percent change
- Weapon law violation YoY change
- Violent crime YoY change
- Selected crime pressure YoY change
- Trend signal

The trend layer is used as supporting context and is not automatically embedded into the final score unless separately modeled.

---

## 17. Output Tables

Primary output tables include:

| Output | Purpose |
|---|---|
| `tn_county_master_dataset.csv` | Merged county-level input dataset before scoring. |
| `tn_county_domestic_security_scores.csv` | Full scored county dataset. |
| `data/processed/tn_operational_risk_features.csv` | Operational Risk & Protective Planning feature layer with exposure, resilience gap, healthcare, infrastructure, transportation, law-enforcement capacity, final operational-risk score, tier, and data-quality flag. |
| `data/raw/tn_county_profile_data.csv` | Prepared county-level profile data used by the operational-risk layer. |
| `data/raw/tn_county_transport_context.csv` | TDOT-derived county-level transportation context used by the operational-risk layer. |
| `data/raw/tn_county_healthcare_capacity.csv` | Sycamore-derived county-level healthcare capacity context used by the operational-risk layer. |
| `data/raw/tn_county_infrastructure_needs.csv` | TACIR-derived county-level infrastructure-needs context used by the operational-risk layer. |
| `data/raw/tn_county_law_enforcement_capacity.csv` | CSLLEA-derived county-level law-enforcement response-capacity baseline used by the operational-risk layer. |
| `tn_county_component_scores.csv` | Major component scores and final score. |
| `tn_county_finance_tactical_scores.csv` | Finance, banking, retail, FFL, tactical, and disaster scores. |
| `tn_county_crime_weapons_scores.csv` | TBI crime/weapons counts, rates, and scores. |
| `tn_county_organized_violence_scores.csv` | Organized violence / high-severity crime component fields. |
| `tn_county_targeted_harm_public_safety_scores.csv` | Hate-crime, law-enforcement ambush, and targeted harm fields. |
| `tn_county_disaster_disruption_scores.csv` | FEMA and optional disaster/disruption fields. |
| `tn_county_institutional_enforcement_scores.csv` | Institutional/enforcement pressure fields. |
| `tn_county_political_violence_scores.csv` | ACLED political violence / civil unrest scores. |
| `tn_county_data_quality_flags.csv` | Data availability, true-zero, gap, and confidence fields. |
| `model_weight_sensitivity_results.csv` | Scenario-level sensitivity results. |
| `top_county_rank_stability.csv` | Rank-stability summary. |
| `scenario_top_county_leaders.csv` | Top counties under each scenario. |
| `tn_crime_weapons_trend_analysis.csv` | 2023–2024 selected crime/weapons trend analysis. |
| `tn_splc_public_group_reference_candidates_2024.csv` | SPLC-derived candidate public group / network references; non-scoring. |
| `tn_public_group_activity_reference.csv` | Validated public group / network reference register; non-scoring. |
| `tn_public_group_reference_validation.csv` | Validation output for the public group / network reference layer. |
| `tn_tdoc_stg_reference_context.csv` | Sanitized non-scoring TDOC correctional-system STG context table. |
| `tn_tdoc_stg_reference_validation.csv` | Validation output for the TDOC STG context layer, including non-scoring, facility-total, count-consistency, prohibited-detail, and correctional-context checks. |
| `tn_2024_hate_crime_bias_context.csv` | TBI 2024 statewide hate-crime bias context; non-scoring. |
| `tn_2024_hate_crime_offense_context.csv` | TBI 2024 statewide hate-crime offense context; non-scoring. |
| `tn_2024_hate_crime_clearance_context.csv` | TBI 2024 statewide hate-crime clearance context; non-scoring. |
| `tn_2024_hate_crime_location_context.csv` | TBI 2024 statewide hate-crime location context; non-scoring. |
| `tn_2024_hate_crime_report_context_summary.csv` | TBI 2024 statewide hate-crime report summary context; non-scoring. |
| `source_register.csv` | Source register and responsible-use notes. |
| `app.py` | Streamlit dashboard application that reads saved outputs and presents interactive tabs, filters, scenario controls, county briefs, and report download. |

---

## 18. Output Charts

The visualization layer produces bar charts and scatter plots for major model components, including:

- Final domestic security risk score
- Finance / tactical vulnerability
- Institutional / enforcement pressure
- Disaster / disruption vulnerability
- Crime / weapons pressure
- Organized violence / high-severity crime pressure
- Overall crime-rate index
- Targeted harm / public-safety pressure
- Hate-crime / targeted-harm pressure
- Law-enforcement ambush pressure
- Law-enforcement assault pressure
- ACLED political violence / civil unrest exposure
- Gang-related criminal activity pressure
- Explosive-use criminal activity pressure
- Gang + explosive intersection pressure
- Tactical access
- FFL importer and destructive-device-related subtype counts
- Banking access gap
- Sensitivity rank stability
- Crime trend YoY changes
- Final operational-risk / protective-planning score
- Operational exposure
- Resilience gap
- Transportation pressure
- Infrastructure pressure
- Healthcare capacity gap
- Law-enforcement capacity gap
- Operational exposure vs. resilience gap
- Law-enforcement capacity gap vs. resilience gap

Zero-only and no-variation optional charts are skipped to avoid misleading visuals.

The public group / network reference register, TDOC correctional-system STG context, and statewide TBI hate-crime context tables are displayed as PDF/dashboard appendix tables, not scoring charts.

The dashboard reads existing chart PNG files from `outputs/charts/`. If a chart is missing, the dashboard displays a non-fatal message rather than changing the model output.

---

## 19. Limitations

This model has several limitations:

- It is a relative county-level index, not a prediction engine.
- It does not establish causation.
- It does not identify individuals, organizations, suspects, businesses, facilities, or threat actors.
- It does not determine whether terrorism, extremism, or illicit finance exists in a county.
- Source availability varies by layer.
- Optional input layers may initially be zero-filled until populated.
- Some categories may represent true zero activity, while others may reflect missing or filtered source data.
- Min-max normalization is sensitive to outliers.
- Small counties may show high per-capita rates from low absolute counts.
- ACLED county extraction depends on available admin fields.
- TBI export formatting may require processor validation.
- Disaster/disruption optional fields may require careful sourcing to avoid site-level vulnerability disclosure.
- Public group / network references are source-documented references only, not independent model findings.
- TDOC STG context rows are correctional-system context only and are not county-level community activity findings.
- TDOC FY2025 facility aggregate counts should not be interpreted as street-level activity, county-level activity, or facility-risk ratings.
- SPLC-derived references are source classifications and are not used to score counties.
- The TBI statewide hate-crime context layer is not county-level scoring input.
- Absence of a public reference row does not mean absence of activity.
- Presence of a public reference row does not mean active local operational presence.
- Dashboard scenario controls are exploratory and should not be treated as official replacement model scores.
- Dashboard filtering changes displayed rows only; it does not alter saved output tables.
- Operational-risk results are defensive planning context, not target identification.
- Law-enforcement capacity fields are based on a 2018 structural baseline and should not be treated as current staffing estimates.
- Infrastructure and transportation layers are broad county-level pressure proxies and should not be converted into route, facility, or vulnerability guidance.

---

## 20. Interpretation Guidance

The model should be interpreted as a structured analytical triage tool. It helps identify counties where multiple aggregate indicators overlap and may justify further contextual review.

A high score means:

- The county has higher relative exposure across model indicators compared with other Tennessee counties.
- Multiple source layers may be reinforcing the same monitoring-priority signal.
- Further qualitative review may be warranted.

A high score does **not** mean:

- The county has terrorism activity.
- The county has extremist activity.
- The county has illicit-finance activity.
- Any person, business, agency, licensee, group, or organization is suspicious.
- Any specific event is predicted.
- A public group / network reference confirms active local presence.
- A TDOC correctional-system STG context row confirms current community presence or county-level activity.
- A county is a target or has specific exploitable vulnerabilities.
- A law-enforcement agency has inadequate performance or current staffing.

---

## 21. Reproducibility

The project is designed to be reproducible through the main pipeline:

```powershell
python main.py
```

The updated main pipeline runs:

1. Reference/context layer generation, including public references, TBI statewide hate-crime context, and TDOC STG correctional-system context
2. Data collection and master dataset construction
3. Phase 6 scoring
4. Sensitivity analysis
5. Crime trend analysis
6. Operational-risk source preparation and feature-layer generation
7. Chart generation
8. PDF report generation
9. Pipeline summary

After the pipeline runs, launch the dashboard with:

```powershell
streamlit run app.py
```

Optional processors can be run separately when raw source exports are refreshed:

```powershell
python -m src.crime_offense_processor
python -m src.crime_rate_processor
python -m src.gang_activity_processor
python -m src.explosives_processor
python -m src.gang_explosives_processor
python -m src.hate_crime_processor
python -m src.law_enforcement_ambush_processor
python -m src.ffl_processor
python -m src.fdic_processor
python -m src.splc_group_reference_processor
python -m src.public_group_reference
python -m src.tbi_hate_crime_report_context
python src/tdoc_stg_reference_processor.py
python -m src.acled_processor
python src.prepare_county_profile_data.py
python src.prepare_tbi_public_safety_context.py
python src.prepare_transport_context.py
python src.prepare_healthcare_capacity.py
python src.prepare_infrastructure_needs.py
python src.prepare_law_enforcement_capacity.py
python src.operational_risk_features.py
python -m src.crime_trend_analysis
```

---

## 22. Summary

Phase 6 expands the project from a finance/tactical and organized-violence model into a broader county-level domestic security and disruption-risk intelligence framework.

The major Phase 6 improvements are:

- Disaster / disruption vulnerability
- Hate-crime / targeted-harm layer
- Law-enforcement ambush layer
- Targeted harm / public-safety pressure score
- Active institutional / enforcement pressure score
- Public group / network reference appendix
- TBI 2024 statewide hate-crime context appendix
- TDOC correctional-system STG context appendix
- Expanded data-quality coverage
- Expanded sensitivity scenarios
- Expanded reporting and visualization structure
- Operational Risk & Protective Planning layer
- TDOT transportation pressure context
- Sycamore healthcare capacity context
- TACIR infrastructure needs context
- CSLLEA law-enforcement response-capacity baseline
- Streamlit dashboard with county-level filters, operational-risk tab, scenario controls, and county intelligence brief generation

The result is a more complete county-level OSINT model that remains bounded by responsible-use constraints, aggregate-only analytical design, and strict separation between scoring layers and reference/context appendices.


---

## 23. GitHub Publication Notes

For GitHub publication, the project should track source code and documentation while excluding sensitive, large, or locally generated files.

Recommended files to track:

- `README.md`
- `methodology.md`
- `data_dictionary.md`
- `docs/public_group_reference_sources.md`
- `requirements.txt`
- `.gitignore`
- `main.py`
- `app.py`
- `src/` modules
- `.gitkeep` placeholder files for empty data/output folders

Recommended files and folders to ignore:

- `.env`
- `.venv/`
- `data/raw/*`
- `data/processed/*`
- `outputs/charts/*`
- `outputs/tables/*`
- `outputs/reports/*`
- `__pycache__/`

The GitHub-facing repository should emphasize that the project is an aggregate, county-level analytical demonstration with responsible-use controls. If operational-risk screenshots or reports are shared, they should preserve the county-level-only framing and avoid any site-level, address-level, route-level, agency-level, or facility-level operational detail. If screenshots or sample reports are published, they should avoid raw source files, credentials, personally identifying information, addresses, coordinates, operational detail, facility security detail, recognition detail, and unsanitized sensitive data.
