# Data Dictionary

**Project:** Tennessee Domestic Security & Illicit Finance Risk Intelligence Model  
**Prepared by:** Jason Keen  
**Version:** Phase 6 Dashboard / Operational Risk / Reference / Context Build  
**Purpose:** Define the major input, derived, scoring, sensitivity, trend, data-quality, and non-scoring reference/context fields used in the Tennessee county-level model.

---

## Overview

This data dictionary documents the primary fields used across the model outputs, including:

- Master county dataset fields
- ACS socioeconomic indicators
- Census County Business Patterns establishment indicators
- FDIC banking and deposit-depth indicators
- ATF FFL and tactical-access indicators
- FEMA disaster exposure indicators
- Phase 6 disaster / disruption vulnerability indicators
- TBI CrimeInsight crime/weapons indicators
- TBI overall crime-rate indicators
- TBI gang-related criminal activity indicators
- TBI explosive-use criminal activity indicators
- TBI gang + explosive-use intersection indicators
- TBI hate-crime / targeted-harm indicators
- TBI law-enforcement ambush indicators
- Targeted harm / public-safety pressure indicators
- Institutional / enforcement pressure indicators
- ACLED political violence / civil unrest indicators
- Operational Risk & Protective Planning indicators
- FEMA National Risk Index / county profile indicators used in the operational-risk layer
- TDOT transportation pressure indicators
- Sycamore healthcare capacity indicators
- TACIR infrastructure needs indicators
- CSLLEA law-enforcement response-capacity baseline indicators
- Public group / network reference fields
- SPLC public group reference candidate fields
- TDOC correctional-system STG context fields
- TDOC STG context validation fields
- TBI 2024 statewide hate-crime context fields
- Crime trend analysis fields
- Sensitivity-analysis fields
- Derived per-capita rates
- Component scores
- Final risk score
- Data-quality and model-confidence fields
- Streamlit dashboard display fields and county brief generator fields

All scoring fields are county-level aggregate indicators. The model does **not** use individual-level, address-level, incident-level, suspect-level, victim-level, licensee-level, business-level, gang-name, organization-name, case-narrative, event-note, facility-level, infrastructure-map, tactical-map, or coordinate-level records.

The public group / network reference, TDOC correctional-system STG context, and TBI 2024 hate-crime context outputs are **non-scoring reference/context layers**. They are used for appendix and documentation context only.

The Streamlit dashboard is a presentation layer that reads existing output tables, charts, and the final PDF. It does not create new model scores or alter the scoring methodology.

The Operational Risk & Protective Planning layer is calculated separately from the main domestic-security risk score. It is designed as a defensive county-level planning and resilience layer, not as a threat-labeling or targeting product.

---

## Responsible-Use Notes

- The model is a county-level relative exposure and monitoring-priority framework.
- It does not predict attacks or identify threat actors.
- It does not determine whether terrorism, extremist activity, or criminal activity exists in a county.
- Gang-related crime, explosive-use activity, gang-related explosive-use activity, hate-crime offense counts, and law-enforcement ambush counts are **not terrorism labels**.
- Hate-crime offense fields are targeted-harm / bias-motivated offense pressure proxies only.
- Law-enforcement ambush fields are public-safety personnel violence / tactical-planning proxies only and do not infer motive, ideology, or actor identity.
- FFL, firearm-related retail, tactical training, sporting goods, pawn/used merchandise, tobacco/vape retail, lending, convenience stores, and other lawful business categories are exposure proxies only.
- Disaster / disruption fields are county-level continuity, access, and response-strain proxies only. They should not include site-level infrastructure vulnerability details.
- Public group / network references are source-documented references only. They are not independent model findings and are not included in scoring.
- TBI 2024 hate-crime context tables are statewide context only. They do not replace the county-level hate-crime processor and are not included in scoring.
- TDOC correctional-system STG context rows are non-scoring appendix records only. They should not be interpreted as current community presence, county-level activity, terrorism, ideology, suspicious conduct, or criminal conduct by any specific person, group, business, facility, or place.
- FY2025 TDOC STG facility counts are correctional-system aggregate classification counts only. They are not county-level gang activity indicators and should not be merged into county risk scoring.
- Historical 2010 TDOC STG rows are retained only as broad historical institutional context. The project should not publish recognition details, operational notes, or sensitive identifiers from the historical source.
- Data completeness measures input coverage, not risk.
- Operational-risk data quality flags measure operational-layer source coverage, not threat level.
- Law-enforcement capacity gap values indicate lower relative county-level response-capacity proxy values in the 2018 CSLLEA baseline, not agency performance or current staffing adequacy.
- Healthcare capacity gap, infrastructure pressure, and transportation pressure are broad county-level planning-context proxies, not site-specific vulnerability findings.
- Dashboard filters and scenario controls are exploratory presentation tools and do not replace the baseline Phase 6 model outputs.
- The Operational Risk & Protective Planning layer is defensive and county-level only. It does not identify targets, facilities, addresses, routes, schedules, individual agencies, individuals, or exploitable vulnerabilities.
- Law-enforcement capacity fields from CSLLEA 2018 are response-capacity baseline proxies only. They are not agency-performance ratings and should not be treated as current staffing adequacy measures.
- Transportation, healthcare, and infrastructure fields are county-level pressure and resilience proxies only. They should not include station-level traffic records, facility addresses, route vulnerabilities, project locations, or site-level security details.
- All scores are relative within Tennessee counties.

---

## Core County Identifiers

| Column | Type | Description |
|---|---:|---|
| `county` | Text | Tennessee county name, standardized to the ACS county naming convention. |
| `county_name` | Text | Full Census county name, usually including “County, Tennessee.” |
| `fips` | Text | Full 5-digit state-county FIPS code. |
| `state_fips` | Text | Two-digit Tennessee state FIPS code, usually `47`. |
| `county_fips` | Text | Three-digit county FIPS code. |
| `county_key` | Text | Normalized county merge key used internally by processors. Usually removed from final public-facing files unless needed for validation. |

---

## ACS Socioeconomic Fields

| Column | Type | Description |
|---|---:|---|
| `population` | Numeric | County population from ACS 5-year data. |
| `median_household_income` | Numeric | Median household income from ACS. |
| `poverty_universe` | Numeric | ACS poverty universe denominator. |
| `poverty_count` | Numeric | Number of residents below poverty threshold. |
| `poverty_rate` | Numeric | Poverty count divided by poverty universe. |
| `labor_force` | Numeric | ACS labor force count. |
| `unemployed` | Numeric | ACS unemployed count. |
| `unemployment_rate` | Numeric | Unemployed count divided by labor force. |
| `renter_households` | Numeric | ACS renter household count. |
| `rent_30_34` | Numeric | Renter households spending 30–34% of income on rent. |
| `rent_35_39` | Numeric | Renter households spending 35–39% of income on rent. |
| `rent_40_49` | Numeric | Renter households spending 40–49% of income on rent. |
| `rent_50_plus` | Numeric | Renter households spending 50%+ of income on rent. |
| `rent_burdened_households` | Numeric | Sum of renter households above 30% rent burden. |
| `rent_burden_rate` | Numeric | Rent-burdened renter households divided by renter households. |
| `acs_year` | Numeric | ACS year successfully collected by the data pipeline. |

---

## Census County Business Patterns Fields

These fields are county-level establishment counts for selected NAICS categories. They are exposure proxies only.

| Column | Type | Description |
|---|---:|---|
| `tobacco_vape_establishments` | Numeric | Tobacco/vape retail establishment count proxy. |
| `sporting_goods_establishments` | Numeric | Sporting goods store establishment count proxy. |
| `used_merchandise_establishments` | Numeric | Used merchandise store establishment count proxy. |
| `gasoline_station_establishments` | Numeric | Gasoline station with convenience store establishment count proxy. |
| `convenience_store_establishments` | Numeric | Convenience store establishment count proxy. |
| `consumer_lending_establishments` | Numeric | Consumer lending establishment count proxy. |
| `laundry_service_establishments` | Numeric | Coin-operated laundry / dry-cleaning establishment count proxy. |
| `used_auto_dealer_establishments` | Numeric | Used auto dealer establishment count proxy. |

---

## FDIC Banking Fields

| Column | Type | Description |
|---|---:|---|
| `bank_branch_count` | Numeric | County-level bank branch count from processed FDIC input. |
| `total_deposits_thousands` | Numeric | County-level deposits in thousands of dollars. |
| `total_deposits_dollars` | Numeric | Deposits converted from thousands to dollars. |
| `bank_branch_count_per_10k` | Numeric | Bank branches per 10,000 residents. |
| `deposits_per_capita` | Numeric | Total deposits divided by population. |
| `low_branch_access_score` | Numeric | Inverted score where lower branch density produces higher access-gap score. |
| `low_deposit_depth_score` | Numeric | Inverted score where lower deposits per capita produces higher access-gap score. |
| `banking_access_gap_score` | Numeric | Composite banking access gap score. Higher values indicate greater relative formal banking access gap. |

---

## ATF FFL and Tactical-Access Fields

These fields are county-level aggregates only. They should not include licensee names, business names, addresses, phone numbers, license numbers, owner names, coordinates, URLs, or site-level maps.

| Column | Type | Description |
|---|---:|---|
| `ffl_count` | Numeric | Total county-level FFL count. |
| `dealer_ffl_count` | Numeric | County-level dealer FFL count. |
| `manufacturer_ffl_count` | Numeric | County-level manufacturer FFL count. |
| `pawnbroker_ffl_count` | Numeric | County-level pawnbroker FFL count. |
| `collector_ffl_count` | Numeric | County-level collector FFL count. |
| `importer_ffl_count` | Numeric | County-level importer FFL count. |
| `destructive_device_ffl_count` | Numeric | County-level destructive-device-related FFL subtype count. This may overlap with importer/manufacturer categories and should not be summed with other subtypes to reconcile to `ffl_count`. |
| `tactical_training_count` | Numeric | Optional county-level tactical training location count. |
| `surplus_tactical_retail_count` | Numeric | Optional county-level military surplus / tactical retail count. |
| `gun_range_count` | Numeric | Optional county-level gun range count. |
| `ffl_count_per_10k` | Numeric | Total FFL count per 10,000 residents. |
| `dealer_ffl_count_per_10k` | Numeric | Dealer FFL count per 10,000 residents. |
| `manufacturer_ffl_count_per_10k` | Numeric | Manufacturer FFL count per 10,000 residents. |
| `pawnbroker_ffl_count_per_10k` | Numeric | Pawnbroker FFL count per 10,000 residents. |
| `collector_ffl_count_per_10k` | Numeric | Collector FFL count per 10,000 residents. |
| `importer_ffl_count_per_10k` | Numeric | Importer FFL count per 10,000 residents. |
| `destructive_device_ffl_count_per_10k` | Numeric | Destructive-device-related FFL count per 10,000 residents. |
| `tactical_training_count_per_10k` | Numeric | Tactical training count per 10,000 residents. |
| `surplus_tactical_retail_count_per_10k` | Numeric | Surplus/tactical retail count per 10,000 residents. |
| `gun_range_count_per_10k` | Numeric | Gun range count per 10,000 residents. |

---

## FEMA Disaster Exposure Fields

| Column | Type | Description |
|---|---:|---|
| `disaster_declaration_count` | Numeric | Count of FEMA disaster declarations associated with the county. |
| `unique_disaster_types` | Numeric | Number of distinct disaster incident types affecting the county. |
| `recent_disaster_declaration_count` | Numeric | Count of recent disaster declarations based on the pipeline’s recent-year cutoff. |
| `disaster_declaration_score` | Numeric | Min-max score for disaster declaration count. |
| `disaster_type_diversity_score` | Numeric | Min-max score for disaster-type diversity. |
| `recent_disaster_score` | Numeric | Min-max score for recent disaster declarations. |
| `infrastructure_disruption_score` | Numeric | FEMA-based disaster / infrastructure disruption score. |

---

## Phase 6 Disaster / Disruption Vulnerability Fields

These fields are optional county-level aggregate inputs. They should not include facility addresses, exact locations, substation locations, hospital addresses, airport coordinates, utility maps, road chokepoints, infrastructure diagrams, event-level coordinates, exact facility names, or operational vulnerability details.

| Column | Type | Description |
|---|---:|---|
| `severe_storm_event_count` | Numeric | County-level severe storm event count or proxy count. |
| `flood_event_count` | Numeric | County-level flood event count or proxy count. |
| `tornado_event_count` | Numeric | County-level tornado event count or proxy count. |
| `winter_weather_event_count` | Numeric | County-level winter weather event count or proxy count. |
| `wildfire_event_count` | Numeric | County-level wildfire event count or proxy count. |
| `drought_event_count` | Numeric | County-level drought event count or proxy count. |
| `power_outage_event_count` | Numeric | County-level power outage event count or proxy count. |
| `avg_outage_duration_hours` | Numeric | Average outage duration in hours where available. |
| `hospital_access_stress_score` | Numeric | County-level hospital/medical access stress proxy score. |
| `airport_access_stress_score` | Numeric | County-level airport/air-access stress proxy score. |
| `road_access_stress_score` | Numeric | County-level road/network access stress proxy score. |
| `communications_disruption_score` | Numeric | County-level communications disruption proxy score. |
| `social_vulnerability_score` | Numeric | County-level social vulnerability proxy score. |
| `recovery_strain_score` | Numeric | County-level recovery strain proxy score. |
| `repeat_disruption_exposure_score` | Numeric | County-level repeat-disruption exposure proxy score. |
| `severe_storm_event_count_per_10k` | Numeric | Severe storm event count per 10,000 residents. |
| `flood_event_count_per_10k` | Numeric | Flood event count per 10,000 residents. |
| `tornado_event_count_per_10k` | Numeric | Tornado event count per 10,000 residents. |
| `winter_weather_event_count_per_10k` | Numeric | Winter weather event count per 10,000 residents. |
| `wildfire_event_count_per_10k` | Numeric | Wildfire event count per 10,000 residents. |
| `drought_event_count_per_10k` | Numeric | Drought event count per 10,000 residents. |
| `power_outage_event_count_per_10k` | Numeric | Power outage event count per 10,000 residents. |
| `severe_weather_event_rate_per_10k` | Numeric | Combined severe weather event rate per 10,000 residents. |
| `severe_weather_exposure_score` | Numeric | Min-max score for severe weather event exposure. |
| `power_outage_event_rate_per_10k` | Numeric | Power outage event rate per 10,000 residents. |
| `power_outage_frequency_score` | Numeric | Min-max score for power outage frequency. |
| `outage_duration_score` | Numeric | Min-max score for average outage duration. |
| `power_disruption_exposure_score` | Numeric | Composite power disruption exposure score. |
| `access_stress_score` | Numeric | Composite hospital, airport, road, and communications access stress score. |
| `recovery_strain_exposure_score` | Numeric | Composite social vulnerability, recovery strain, and repeat-disruption exposure score. |
| `disaster_disruption_vulnerability_score` | Numeric | Composite Phase 6 disaster / disruption vulnerability score. Defaults back to FEMA-based `infrastructure_disruption_score` when optional Phase 6 fields are not populated. |

---

## TBI CrimeInsight Crime / Weapons Fields

These fields are county-level aggregate public-safety indicators. They do not include agency-level, incident-level, person-level, address-level, coordinate-level, narrative, or case-level records.

| Column | Type | Description |
|---|---:|---|
| `homicide_count` | Numeric | County-level murder / homicide count. |
| `kidnapping_abduction_count` | Numeric | County-level kidnapping / abduction count. |
| `weapons_law_violation_count` | Numeric | County-level weapon law violation count. |
| `violent_crime_count` | Numeric | County-level violent crime count. If not exported directly, the processor may create a partial count from selected violent-crime categories. |
| `aggravated_assault_count` | Numeric | County-level aggravated assault count. |
| `arson_count` | Numeric | County-level arson count. |
| `sex_offense_count` | Numeric | County-level sex offense count based on mapped labels such as All Rape, Criminal Sexual Contact, Incest, and Statutory Rape. |
| `hate_crime_count` | Numeric | County-level hate crime count if available from the broad crime/weapons export. |
| `law_enforcement_assault_count` | Numeric | County-level law-enforcement assault count if available from the broad crime/weapons export. |

---

## TBI Overall Crime-Rate Fields

| Column | Type | Description |
|---|---:|---|
| `overall_crime_rate_per_1000_2024` | Numeric | TBI/TNCrimeOnline overall crime rate per 1,000 residents for 2024. |
| `overall_crime_count_2024` | Numeric | TBI/TNCrimeOnline overall number of crimes for 2024. |
| `crime_population_2024` | Numeric | Population denominator from the crime-rate export. |
| `overall_crime_rate_pressure_score` | Numeric | Min-max score based on overall crime rate. |
| `overall_crime_count_pressure_score` | Numeric | Min-max score based on per-capita overall crime count. |
| `overall_crime_rate_index_score` | Numeric | Composite overall crime-rate index score. |

---

## Crime / Weapons Rate Fields

All rate fields are per 10,000 residents.

| Column | Type | Description |
|---|---:|---|
| `homicide_rate_per_10k` | Numeric | Homicide count per 10,000 residents. |
| `kidnapping_abduction_rate_per_10k` | Numeric | Kidnapping/abduction count per 10,000 residents. |
| `weapons_law_violation_rate_per_10k` | Numeric | Weapon law violation count per 10,000 residents. |
| `violent_crime_rate_per_10k` | Numeric | Violent crime count per 10,000 residents. |
| `aggravated_assault_rate_per_10k` | Numeric | Aggravated assault count per 10,000 residents. |
| `arson_rate_per_10k` | Numeric | Arson count per 10,000 residents. |
| `sex_offense_rate_per_10k` | Numeric | Sex offense count per 10,000 residents. |
| `hate_crime_rate_per_10k` | Numeric | Hate crime count per 10,000 residents. |
| `law_enforcement_assault_rate_per_10k` | Numeric | Law-enforcement assault count per 10,000 residents. |

---

## TBI Gang-Related Criminal Activity Fields

These are county-level aggregate fields from TBI/TNCrimeOnline gang-activity filtered exports. They are not terrorism labels.

| Column | Type | Description |
|---|---:|---|
| `gang_related_total_crime_count` | Numeric | Total county-level gang-related crime count across selected offense columns. |
| `gang_related_violent_crime_count` | Numeric | Gang-related violent-crime count. |
| `gang_related_weapon_law_violation_count` | Numeric | Gang-related weapon law violation count. |
| `gang_related_drug_offense_count` | Numeric | Gang-related drug offense count. |
| `gang_related_property_offense_count` | Numeric | Gang-related property offense count. |
| `gang_related_homicide_count` | Numeric | Gang-related homicide count. |
| `gang_related_kidnapping_abduction_count` | Numeric | Gang-related kidnapping/abduction count. |
| `gang_related_aggravated_assault_count` | Numeric | Gang-related aggravated assault count. |
| `gang_related_robbery_count` | Numeric | Gang-related robbery count. |
| `gang_related_arson_count` | Numeric | Gang-related arson count. |
| `gang_related_sex_offense_count` | Numeric | Gang-related sex offense count. |
| `gang_related_total_crime_count_per_10k` | Numeric | Gang-related total crime count per 10,000 residents. |
| `gang_related_violent_crime_count_per_10k` | Numeric | Gang-related violent-crime count per 10,000 residents. |
| `gang_related_weapon_law_violation_count_per_10k` | Numeric | Gang-related weapon law violation count per 10,000 residents. |
| `gang_related_crime_pressure_score` | Numeric | Composite gang-related criminal activity pressure score. |

---

## TBI Explosive-Use Criminal Activity Fields

These are county-level aggregate fields from TBI/TNCrimeOnline exports filtered to explosive-use. They are not terrorism labels.

| Column | Type | Description |
|---|---:|---|
| `explosive_related_total_offense_count` | Numeric | Total county-level explosive-related offense count. |
| `explosive_related_violent_offense_count` | Numeric | Explosive-related violent offense count. |
| `explosive_related_weapon_law_violation_count` | Numeric | Explosive-related weapon law violation count. |
| `explosive_related_drug_offense_count` | Numeric | Explosive-related drug offense count. |
| `explosive_related_property_offense_count` | Numeric | Explosive-related property offense count. |
| `explosive_related_homicide_count` | Numeric | Explosive-related homicide count. |
| `explosive_related_kidnapping_abduction_count` | Numeric | Explosive-related kidnapping/abduction count. |
| `explosive_related_aggravated_assault_count` | Numeric | Explosive-related aggravated assault count. |
| `explosive_related_robbery_count` | Numeric | Explosive-related robbery count. |
| `explosive_related_arson_count` | Numeric | Explosive-related arson count. |
| `explosive_related_sex_offense_count` | Numeric | Explosive-related sex offense count. |
| `explosive_related_property_damage_count` | Numeric | Explosive-related destruction/damage/vandalism count. |
| `explosive_related_total_offense_count_per_10k` | Numeric | Explosive-related total offense count per 10,000 residents. |
| `explosive_related_violent_offense_count_per_10k` | Numeric | Explosive-related violent offense count per 10,000 residents. |
| `explosive_related_weapon_law_violation_count_per_10k` | Numeric | Explosive-related weapon law violation count per 10,000 residents. |
| `explosive_related_homicide_count_per_10k` | Numeric | Explosive-related homicide count per 10,000 residents. |
| `explosive_related_arson_count_per_10k` | Numeric | Explosive-related arson count per 10,000 residents. |
| `explosive_related_property_damage_count_per_10k` | Numeric | Explosive-related property damage count per 10,000 residents. |
| `explosive_related_pressure_score` | Numeric | Composite explosive-use criminal activity pressure score. |

---

## TBI Gang + Explosive-Use Intersection Fields

These are county-level aggregate fields from TBI/TNCrimeOnline exports filtered to gang activity and explosive use. They are not terrorism labels.

| Column | Type | Description |
|---|---:|---|
| `gang_explosive_total_offense_count` | Numeric | Total county-level gang-related explosive-use offense count. |
| `gang_explosive_violent_offense_count` | Numeric | Gang-related explosive-use violent offense count. |
| `gang_explosive_weapon_law_violation_count` | Numeric | Gang-related explosive-use weapon law violation count. |
| `gang_explosive_drug_offense_count` | Numeric | Gang-related explosive-use drug offense count. |
| `gang_explosive_property_offense_count` | Numeric | Gang-related explosive-use property offense count. |
| `gang_explosive_homicide_count` | Numeric | Gang-related explosive-use homicide count. |
| `gang_explosive_kidnapping_abduction_count` | Numeric | Gang-related explosive-use kidnapping/abduction count. |
| `gang_explosive_aggravated_assault_count` | Numeric | Gang-related explosive-use aggravated assault count. |
| `gang_explosive_robbery_count` | Numeric | Gang-related explosive-use robbery count. |
| `gang_explosive_arson_count` | Numeric | Gang-related explosive-use arson count. |
| `gang_explosive_sex_offense_count` | Numeric | Gang-related explosive-use sex offense count. |
| `gang_explosive_property_damage_count` | Numeric | Gang-related explosive-use destruction/damage/vandalism count. |
| `gang_explosive_total_offense_count_per_10k` | Numeric | Gang-related explosive-use total offense count per 10,000 residents. |
| `gang_explosive_violent_offense_count_per_10k` | Numeric | Gang-related explosive-use violent offense count per 10,000 residents. |
| `gang_explosive_weapon_law_violation_count_per_10k` | Numeric | Gang-related explosive-use weapon law violation count per 10,000 residents. |
| `gang_explosive_homicide_count_per_10k` | Numeric | Gang-related explosive-use homicide count per 10,000 residents. |
| `gang_explosive_arson_count_per_10k` | Numeric | Gang-related explosive-use arson count per 10,000 residents. |
| `gang_explosive_property_damage_count_per_10k` | Numeric | Gang-related explosive-use property damage count per 10,000 residents. |
| `gang_explosive_pressure_score` | Numeric | Composite gang + explosive intersection pressure score. |

---

## TBI Hate-Crime / Targeted-Harm Fields

These are county-level aggregate fields from TBI/TNCrimeOnline hate-crime offense exports. They are not terrorism labels and should not be interpreted as motive or actor-identity determinations beyond the aggregate source category.

| Column | Type | Description |
|---|---:|---|
| `hate_crime_total_count` | Numeric | Total county-level hate-crime offense count. |
| `hate_crime_homicide_count` | Numeric | Hate-crime homicide count. |
| `hate_crime_kidnapping_abduction_count` | Numeric | Hate-crime kidnapping/abduction count. |
| `hate_crime_sex_offense_count` | Numeric | Hate-crime sex offense count. |
| `hate_crime_aggravated_assault_count` | Numeric | Hate-crime aggravated assault count. |
| `hate_crime_simple_assault_count` | Numeric | Hate-crime simple assault count. |
| `hate_crime_intimidation_count` | Numeric | Hate-crime intimidation count. |
| `hate_crime_arson_count` | Numeric | Hate-crime arson count. |
| `hate_crime_weapon_law_violation_count` | Numeric | Hate-crime weapon law violation count. |
| `hate_crime_property_damage_count` | Numeric | Hate-crime destruction/damage/vandalism count. |
| `hate_crime_property_offense_count` | Numeric | Hate-crime property offense count. |
| `hate_crime_other_offense_count` | Numeric | Hate-crime other mapped offense count. |
| `hate_crime_total_count_per_10k` | Numeric | Hate-crime total count per 10,000 residents. |
| `hate_crime_homicide_count_per_10k` | Numeric | Hate-crime homicide count per 10,000 residents. |
| `hate_crime_kidnapping_abduction_count_per_10k` | Numeric | Hate-crime kidnapping/abduction count per 10,000 residents. |
| `hate_crime_aggravated_assault_count_per_10k` | Numeric | Hate-crime aggravated assault count per 10,000 residents. |
| `hate_crime_simple_assault_count_per_10k` | Numeric | Hate-crime simple assault count per 10,000 residents. |
| `hate_crime_intimidation_count_per_10k` | Numeric | Hate-crime intimidation count per 10,000 residents. |
| `hate_crime_weapon_law_violation_count_per_10k` | Numeric | Hate-crime weapon law violation count per 10,000 residents. |
| `hate_crime_property_damage_count_per_10k` | Numeric | Hate-crime property damage count per 10,000 residents. |
| `hate_crime_total_rate_per_10k` | Numeric | Hate-crime total rate per 10,000 residents. |
| `hate_crime_violent_rate_per_10k` | Numeric | Combined hate-crime violent offense rate per 10,000 residents. |
| `hate_crime_intimidation_rate_per_10k` | Numeric | Hate-crime intimidation rate per 10,000 residents. |
| `hate_crime_weapon_law_rate_per_10k` | Numeric | Hate-crime weapon law violation rate per 10,000 residents. |
| `hate_crime_property_damage_rate_per_10k` | Numeric | Hate-crime property damage rate per 10,000 residents. |
| `hate_crime_total_pressure_score` | Numeric | Min-max score for hate-crime total rate. |
| `hate_crime_violent_pressure_score` | Numeric | Min-max score for hate-crime violent rate. |
| `hate_crime_intimidation_pressure_score` | Numeric | Min-max score for hate-crime intimidation rate. |
| `hate_crime_weapon_law_pressure_score` | Numeric | Min-max score for hate-crime weapon law violation rate. |
| `hate_crime_property_damage_pressure_score` | Numeric | Min-max score for hate-crime property damage rate. |
| `hate_crime_targeted_harm_pressure_score` | Numeric | Composite hate-crime / targeted-harm pressure score. |

---

## TBI Law-Enforcement Ambush Fields

These are county-level aggregate fields from TBI/TNCrimeOnline law-enforcement ambush exports. They are public-safety personnel violence / tactical-planning proxies only and are not terrorism indicators by themselves.

| Column | Type | Description |
|---|---:|---|
| `le_ambush_total_count` | Numeric | Total county-level law-enforcement ambush offense count. |
| `le_ambush_homicide_count` | Numeric | Law-enforcement ambush homicide count. |
| `le_ambush_kidnapping_abduction_count` | Numeric | Law-enforcement ambush kidnapping/abduction count. |
| `le_ambush_aggravated_assault_count` | Numeric | Law-enforcement ambush aggravated assault count. |
| `le_ambush_simple_assault_count` | Numeric | Law-enforcement ambush simple assault count. |
| `le_ambush_intimidation_count` | Numeric | Law-enforcement ambush intimidation count. |
| `le_ambush_weapon_law_violation_count` | Numeric | Law-enforcement ambush weapon law violation count. |
| `le_ambush_arson_count` | Numeric | Law-enforcement ambush arson count. |
| `le_ambush_property_damage_count` | Numeric | Law-enforcement ambush destruction/damage/vandalism count. |
| `le_ambush_property_offense_count` | Numeric | Law-enforcement ambush property offense count. |
| `le_ambush_drug_offense_count` | Numeric | Law-enforcement ambush drug offense count. |
| `le_ambush_other_offense_count` | Numeric | Law-enforcement ambush other mapped offense count. |
| `le_ambush_total_count_per_10k` | Numeric | Law-enforcement ambush total count per 10,000 residents. |
| `le_ambush_homicide_count_per_10k` | Numeric | Law-enforcement ambush homicide count per 10,000 residents. |
| `le_ambush_kidnapping_abduction_count_per_10k` | Numeric | Law-enforcement ambush kidnapping/abduction count per 10,000 residents. |
| `le_ambush_aggravated_assault_count_per_10k` | Numeric | Law-enforcement ambush aggravated assault count per 10,000 residents. |
| `le_ambush_simple_assault_count_per_10k` | Numeric | Law-enforcement ambush simple assault count per 10,000 residents. |
| `le_ambush_intimidation_count_per_10k` | Numeric | Law-enforcement ambush intimidation count per 10,000 residents. |
| `le_ambush_weapon_law_violation_count_per_10k` | Numeric | Law-enforcement ambush weapon law violation count per 10,000 residents. |
| `le_ambush_property_damage_count_per_10k` | Numeric | Law-enforcement ambush property damage count per 10,000 residents. |
| `le_ambush_total_rate_per_10k` | Numeric | Law-enforcement ambush total rate per 10,000 residents. |
| `le_ambush_violent_rate_per_10k` | Numeric | Combined law-enforcement ambush violent offense rate per 10,000 residents. |
| `le_ambush_weapon_law_rate_per_10k` | Numeric | Law-enforcement ambush weapon law violation rate per 10,000 residents. |
| `le_ambush_intimidation_rate_per_10k` | Numeric | Law-enforcement ambush intimidation rate per 10,000 residents. |
| `le_ambush_property_damage_rate_per_10k` | Numeric | Law-enforcement ambush property damage rate per 10,000 residents. |
| `le_ambush_total_pressure_score` | Numeric | Min-max score for law-enforcement ambush total rate. |
| `le_ambush_violent_pressure_score` | Numeric | Min-max score for law-enforcement ambush violent rate. |
| `le_ambush_weapon_law_pressure_score` | Numeric | Min-max score for law-enforcement ambush weapon law violation rate. |
| `le_ambush_intimidation_pressure_score` | Numeric | Min-max score for law-enforcement ambush intimidation rate. |
| `le_ambush_property_damage_pressure_score` | Numeric | Min-max score for law-enforcement ambush property damage rate. |
| `law_enforcement_ambush_pressure_score` | Numeric | Composite law-enforcement ambush pressure score. |

---

## Targeted Harm / Public-Safety Pressure Fields

| Column | Type | Description |
|---|---:|---|
| `targeted_harm_public_safety_pressure_score` | Numeric | Composite targeted harm / public-safety pressure score combining hate-crime / targeted-harm pressure and law-enforcement ambush pressure. |

---

## ACLED Political Violence / Civil Unrest Fields

These fields are county-level aggregates from ACLED-derived Tennessee event data. The model output does not preserve event notes, actor names, organization names, participant details, exact locations, URLs, coordinates, narratives, or site-level maps.

| Column | Type | Description |
|---|---:|---|
| `protest_event_count` | Numeric | County-level ACLED protest event count. |
| `violent_unrest_event_count` | Numeric | County-level ACLED violent unrest event count. |
| `political_violence_event_count` | Numeric | County-level ACLED political violence event count. |
| `strategic_development_count` | Numeric | County-level ACLED strategic development count. |
| `public_disorder_event_count` | Numeric | County-level ACLED public disorder event count. |
| `total_acled_event_count` | Numeric | Total county-level ACLED event count. |
| `acled_fatalities` | Numeric | County-level ACLED fatalities count. |
| `protest_event_rate_per_10k` | Numeric | Protest events per 10,000 residents. |
| `violent_unrest_event_rate_per_10k` | Numeric | Violent unrest events per 10,000 residents. |
| `political_violence_event_rate_per_10k` | Numeric | Political violence events per 10,000 residents. |
| `strategic_development_rate_per_10k` | Numeric | Strategic development events per 10,000 residents. |
| `public_disorder_event_rate_per_10k` | Numeric | Public disorder events per 10,000 residents. |
| `total_acled_event_rate_per_10k` | Numeric | Total ACLED events per 10,000 residents. |
| `acled_fatality_rate_per_10k` | Numeric | ACLED fatalities per 10,000 residents. |
| `protest_event_pressure_score` | Numeric | Min-max score for protest event rate. |
| `violent_unrest_event_pressure_score` | Numeric | Min-max score for violent unrest event rate. |
| `political_violence_event_pressure_score` | Numeric | Min-max score for political violence event rate. |
| `strategic_development_pressure_score` | Numeric | Min-max score for strategic development rate. |
| `public_disorder_event_pressure_score` | Numeric | Min-max score for public disorder rate. |
| `total_acled_event_pressure_score` | Numeric | Min-max score for total ACLED event rate. |
| `acled_fatality_pressure_score` | Numeric | Min-max score for ACLED fatality rate. |
| `political_violence_exposure_score` | Numeric | Composite ACLED political violence / civil unrest exposure score. |

---


## Operational Risk & Protective Planning Fields

Generated primarily by `operational_risk_features.py` and supporting preparation scripts. The main output is `data/processed/tn_operational_risk_features.csv`.

This layer is a separate defensive planning layer. It is not part of the baseline `final_domestic_security_risk_score`. It combines existing threat/context scoring with county-level exposure, resilience, infrastructure, healthcare, transportation, public-safety, FEMA, and law-enforcement response-capacity indicators.

### Operational-Risk Source / Profile Fields

| Column | Type | Description |
|---|---:|---|
| `county` | Text | Tennessee county name, standardized for all operational-risk joins. Special capitalization such as `DeKalb`, `McMinn`, and `McNairy` should be preserved. |
| `population` | Numeric | County population used as the denominator for exposure and per-capita calculations. |
| `population_density` | Numeric | County population density, used as an exposure proxy. |
| `poverty_rate` | Numeric | County poverty rate used in socioeconomic pressure scoring. |
| `unemployment_rate` | Numeric | County unemployment rate used in socioeconomic pressure scoring. |
| `median_household_income` | Numeric | County median household income used as an inverse stress indicator. |
| `fema_social_vulnerability_score` | Numeric | FEMA National Risk Index social vulnerability score or normalized proxy. Higher values indicate greater relative vulnerability. |
| `fema_community_resilience_score` | Numeric | FEMA National Risk Index community resilience score or normalized proxy. Higher values indicate stronger relative resilience. |
| `avg_aadt` | Numeric | County average annual average daily traffic from TDOT traffic-line aggregation. |
| `total_vmt` | Numeric | County total vehicle miles traveled from TDOT traffic-line aggregation. |
| `truck_percentage` | Numeric | County average truck percentage from TDOT traffic-line aggregation. |
| `traffic_station_count` | Numeric | Count of traffic-line or station records used in county transportation aggregation. |
| `total_traffic_line_mileage` | Numeric | Total mileage represented in the TDOT traffic-line aggregation, when available. |
| `violent_crime_rate` | Numeric | County violent-crime rate derived from TBI public-safety context input. |
| `weapon_law_violation_rate` | Numeric | County weapon-law-violation rate derived from TBI public-safety context input. |
| `public_disorder_rate` | Numeric | County public-disorder or public-safety disorder rate derived from TBI public-safety context input. |
| `hate_crime_count` | Numeric | County hate-crime count if available from a hate-crime-specific county source. Blank or zero when not populated by the public-safety context file. |
| `hate_crime_rate` | Numeric | County hate-crime rate if a hate-crime-specific source is available. |
| `hospital_beds_per_100k` | Numeric | Hospital staffed-bed capacity per 100,000 residents from the healthcare-capacity layer. |
| `emergency_department_count` | Numeric | County count of emergency departments or emergency-care-capable facilities from the healthcare-capacity layer. |
| `primary_care_rate` | Numeric | County primary-care provider rate or proxy from the healthcare-capacity layer. |
| `trauma_access_proxy` | Numeric | County-level emergency/trauma access proxy. This is not a trauma-center locator and should not include facility locations. |
| `total_infrastructure_needs` | Numeric | TACIR county-level total public infrastructure needs, when retained. |
| `infrastructure_needs_per_capita` | Numeric | TACIR public infrastructure needs per resident. Used as the main infrastructure pressure input. |
| `infrastructure_project_count` | Numeric | TACIR county-level project count, when retained. |
| `regional_infrastructure_needs` | Numeric | TACIR regional infrastructure needs amount, when available. |
| `local_infrastructure_needs` | Numeric | TACIR local infrastructure needs amount, when available. |

### CSLLEA Law-Enforcement Response-Capacity Fields

These fields are county-level aggregates from the BJS / ICPSR CSLLEA 2018 agency-level dataset. They are response-capacity baseline proxies only. They do not publish agency names, ORI identifiers, addresses, station locations, tactical details, or agency-level performance judgments.

| Column | Type | Description |
|---|---:|---|
| `law_enforcement_agency_count` | Numeric | Number of CSLLEA agencies aggregated to the county. |
| `law_enforcement_complete_agency_count` | Numeric | Number of agencies with complete or usable CSLLEA response data. |
| `sheriff_office_count` | Numeric | County count of sheriff office records in the CSLLEA aggregation. |
| `local_police_agency_count` | Numeric | County count of local police agency records in the CSLLEA aggregation. |
| `law_enforcement_full_time_employees` | Numeric | County total full-time law-enforcement employees from CSLLEA. |
| `law_enforcement_sworn_personnel` | Numeric | County total sworn personnel from CSLLEA. |
| `law_enforcement_civilian_personnel` | Numeric | County total civilian / nonsworn personnel from CSLLEA, when available. |
| `law_enforcement_sworn_per_100k` | Numeric | Sworn personnel per 100,000 residents. |
| `law_enforcement_full_time_employees_per_100k` | Numeric | Full-time law-enforcement employees per 100,000 residents. |
| `patrol_response_agency_count` | Numeric | County count of agencies reporting patrol/response functions. |
| `dispatch_agency_count` | Numeric | County count of agencies reporting dispatch-related functions. |
| `criminal_investigation_agency_count` | Numeric | County count of agencies reporting criminal investigation functions. |
| `traffic_enforcement_agency_count` | Numeric | County count of agencies reporting traffic enforcement functions. |
| `specialized_response_agency_count` | Numeric | County count of agencies reporting selected specialized response functions. This is a broad capacity proxy, not tactical-detail reporting. |
| `law_enforcement_capacity_score` | Numeric | Composite county-level response-capacity score based on CSLLEA staffing and function proxies. Higher values indicate stronger relative capacity proxy values. |
| `law_enforcement_capacity_gap_score` | Numeric | Inverse of law-enforcement capacity score. Higher values indicate lower relative response-capacity proxy values. |
| `law_enforcement_data_year` | Numeric | Source year for the CSLLEA layer, currently 2018. |

### Operational-Risk Derived Scores

| Column | Type | Description |
|---|---:|---|
| `existing_threat_context_score` | Numeric | Existing county-level threat/context score imported from the main model, generally based on final domestic-security risk or related context. |
| `population_exposure_score` | Numeric | Min-max score for county population exposure. |
| `density_exposure_score` | Numeric | Min-max score for population density exposure. |
| `socioeconomic_pressure_score` | Numeric | Composite socioeconomic pressure proxy based on poverty, unemployment, and income stress fields. |
| `transport_pressure_score` | Numeric | Composite TDOT transportation pressure score using traffic volume, VMT, truck percentage, and traffic-record coverage. |
| `infrastructure_pressure_score` | Numeric | Composite infrastructure pressure score based primarily on TACIR infrastructure needs per capita. |
| `public_safety_context_score` | Numeric | Composite TBI public-safety context score based on violent-crime, weapon-law-violation, public-disorder, and related county-level rates. |
| `healthcare_capacity_score` | Numeric | Composite healthcare and emergency capacity score. Higher values indicate stronger relative county capacity proxy values. |
| `healthcare_capacity_gap_score` | Numeric | Inverse healthcare capacity score. Higher values indicate weaker relative healthcare/emergency capacity proxy values. |
| `fema_vulnerability_score` | Numeric | FEMA vulnerability proxy used in the operational resilience-gap calculation. |
| `fema_resilience_gap_score` | Numeric | Inverse FEMA community resilience score. Higher values indicate weaker relative resilience proxy values. |
| `operational_exposure_score` | Numeric | Composite operational exposure score combining population, density, socioeconomic, transportation, infrastructure, and public-safety context. |
| `resilience_gap_score` | Numeric | Composite resilience gap score combining healthcare capacity gap, FEMA vulnerability/resilience gap, and law-enforcement capacity gap. |
| `final_operational_risk_score` | Numeric | Final defensive operational-risk / protective-planning score. It is separate from the main domestic-security risk score. |
| `operational_risk_tier` | Text | Operational-risk tier such as Low, Moderate, Elevated, or High based on final operational-risk score bands. |
| `data_quality_flag` | Text | Operational-risk source-coverage label such as Strong, Partial, or Limited. This measures operational-layer data availability, not threat level. |

### Operational-Risk Input / Output Files

| File | Main Fields / Purpose |
|---|---|
| `tn_county_profile_data.csv` | County profile fields such as population, density, socioeconomic indicators, and FEMA-derived profile inputs. |
| `tbi_county_public_safety_context.csv` | County-level TBI public-safety context fields such as violent-crime, weapon-law-violation, and public-disorder rates. |
| `tn_county_transport_context.csv` | TDOT county-level transportation fields such as AADT, VMT, truck percentage, and traffic station/line counts. |
| `tn_county_healthcare_capacity.csv` | Sycamore-derived county healthcare capacity fields such as beds per 100k, emergency department count, primary care rate, and trauma access proxy. |
| `tn_county_infrastructure_needs.csv` | TACIR county-level infrastructure needs fields including total needs and needs per capita. |
| `tn_county_law_enforcement_capacity.csv` | CSLLEA 2018 county-level law-enforcement response-capacity baseline fields. |
| `tn_operational_risk_features.csv` | Final operational-risk feature layer with exposure, resilience-gap, component, tier, and data-quality fields. |

### Operational-Risk Preparation Scripts

| Script | Purpose |
|---|---|
| `prepare_county_profile_data.py` | Builds county profile inputs from ACS/FEMA and related county baseline sources. |
| `prepare_tbi_public_safety_context.py` | Converts TBI public-safety offense exports into county-level public-safety context inputs. |
| `prepare_transport_context.py` | Aggregates TDOT traffic-line data to county-level transportation pressure inputs. |
| `prepare_healthcare_capacity.py` | Converts Sycamore healthcare capacity data into county-level healthcare capacity inputs. |
| `prepare_infrastructure_needs.py` | Extracts / converts TACIR infrastructure needs data into county-level infrastructure pressure inputs. |
| `prepare_law_enforcement_capacity.py` | Converts CSLLEA 2018 agency-level data into county-level response-capacity baseline inputs. |
| `operational_risk_features.py` | Merges operational-risk source layers and calculates final operational-risk scores. |


## Public Group / Network Reference Fields

Generated by `public_group_reference.py`.

These fields are **non-scoring reference fields**. They are used only for the public group / network reference appendix or analyst-reference table. They are not included in the master scoring dataset, final score, sensitivity scenarios, county risk signal, or model confidence score.

| Column | Type | Description |
|---|---:|---|
| `reference_id` | Text | Unique reference identifier. SPLC-generated references use IDs such as `SPLC-2024-TN-001`; manually entered rows may use custom IDs. |
| `group_or_network_name` | Text | Public-source group, network, case, or reference label. This is source context only, not an independent model finding. |
| `category` | Text | Approved reference category such as `extremist_or_hate_group`, `antigovernment_or_militia`, `terrorism_linked_case`, `violent_extremism_case`, `criminal_gang_or_organized_crime`, `public_safety_reference`, or `other_public_reference`. |
| `source_type` | Text | Approved source type such as `civil_society_tracker`, `official_government`, `court_document`, `law_enforcement_report`, `academic_report`, `credible_news`, or `other_public_source`. |
| `source_name` | Text | Name of the public source used for the reference. |
| `source_url` | Text | Public URL or source file reference. |
| `geographic_reference` | Text | Broad non-operational geography such as statewide, county, city, or region. |
| `geo_level` | Text | Geographic level such as `statewide`, `county`, `multi_county`, `city_or_region`, or `unknown`. |
| `county` | Text | County name only when `geo_level` is county. Blank for statewide, city/region, multi-county, or unknown references. |
| `date_observed` | Text | Source-observed year or date. |
| `source_publication_date` | Text | Source publication date or year. |
| `confidence_level` | Text | Reference confidence label: `high`, `moderate`, or `low`. |
| `summary_note` | Text | Short source-grounded summary. Should not contain operational, individual-level, address-level, or case-narrative detail. |
| `legal_status_note` | Text | Careful status language such as listed, alleged, charged, convicted, designated, or publicly documented by source. |
| `responsible_use_flag` | Text | Required caveat explaining that the row is reference-only, non-scoring, and not a terrorism/criminality/county-risk label. |
| `include_in_report` | Boolean | Whether the validated row may appear in the PDF appendix. |
| `include_in_score` | Boolean | Forced to `False` by the processor. This layer is not part of scoring. |
| `validation_issue_count` | Numeric | Count of validation issues detected for the row. |
| `validation_issues` | Text | Semicolon-separated validation issue labels. |
| `is_valid_reference` | Boolean | Whether the row passed validation. |

### Public Group Reference Validation Fields

Generated by `public_group_reference.py`.

| Column | Type | Description |
|---|---:|---|
| `reference_id` | Text | Reference ID from the input row. |
| `group_or_network_name` | Text | Public-source reference label. |
| `validation_issue_count` | Numeric | Number of validation issues detected. |
| `validation_issues` | Text | Semicolon-separated validation issues such as missing source URL, invalid category, or missing responsible-use flag. |
| `is_valid_reference` | Boolean | Whether the reference row is valid for report use. |
| `include_in_report` | Boolean | Whether the row is marked for report inclusion. |
| `include_in_score` | Boolean | Always false after validation. |

---

## SPLC Public Group Reference Candidate Fields

Generated by `splc_group_reference_processor.py`.

These fields are **source-assisted candidate fields**. The candidate output should be reviewed and validated by `public_group_reference.py` before being used in the PDF appendix.

| Column | Type | Description |
|---|---:|---|
| `reference_id` | Text | SPLC-generated reference ID. |
| `group_or_network_name` | Text | Group or network name from the SPLC source row. |
| `category` | Text | Model category derived from SPLC ideology/category mapping. |
| `source_type` | Text | Usually `civil_society_tracker`. |
| `source_name` | Text | Southern Poverty Law Center Hate Map 2024. |
| `source_url` | Text | SPLC Tennessee Hate Map URL. |
| `geographic_reference` | Text | Broad geography retained from the SPLC row, such as city/region or statewide. |
| `geo_level` | Text | Geographic level derived from the SPLC row. |
| `county` | Text | County value only when a county-level reference is available. Usually blank for city/region references. |
| `date_observed` | Text | Observation year, usually `2024`. |
| `source_publication_date` | Text | Source year, usually `2024`. |
| `confidence_level` | Text | Confidence label assigned by the processor, usually `moderate`. |
| `summary_note` | Text | Non-operational source-grounded summary generated by the processor. |
| `legal_status_note` | Text | Source-status note explaining that the SPLC listing is a civil-society tracker reference and not an independent model finding. |
| `responsible_use_flag` | Text | Required caveat explaining that the row is reference-only and non-scoring. |
| `include_in_report` | Boolean | Whether the candidate row is marked for report inclusion after validation. |
| `include_in_score` | Boolean | Always false. |
| `source_ideology_name` | Text | SPLC source ideology/category field retained for audit context. |
| `source_city_name` | Text | SPLC source city/region field retained for broad geography context only. |
| `source_statewide_flag` | Boolean | Whether the SPLC row is statewide. |

---

## TDOC Correctional-System STG Context Fields

Generated by `tdoc_stg_reference_processor.py`.

These fields are **non-scoring correctional-system reference fields**. They are used only for the TDOC STG appendix and dashboard context table. They are not included in the master scoring dataset, final domestic-security score, organized-violence score, operational-risk score, sensitivity scenarios, county risk signal, model confidence score, or county ranking.

The layer has two source categories:

1. **Historical 2010 TDOC institutional context** — broad major-group references only. Counts, recognition details, visual/coded identifiers, internal structures, staff contact details, incident narratives, and operational notes are not retained.
2. **FY2025 TDOC Statistical Abstract facility totals** — public aggregate facility-level confirmed, suspected, and total STG/gang classification counts. These counts are correctional-system context only and should not be interpreted as county-level or street-level activity.

### TDOC STG Reference Context Fields

| Column | Type | Description |
|---|---:|---|
| `reference_id` | Text | Unique TDOC STG context reference identifier, rebuilt after deduplication. |
| `group_or_network_name` | Text | Broad reference label. Historical rows retain broad major-group names; FY2025 facility-total rows use `All Security Threat Groups / Gangs`. |
| `record_type` | Text | Record type such as `historical_major_group_reference` or `facility_total`. |
| `category` | Text | Usually `correctional_security_threat_group_context`. |
| `source_type` | Text | Source type such as `state_corrections_historical_assessment` or `state_corrections_statistical_abstract`. |
| `source_name` | Text | Source title, such as the TDOC 2010 Security Threat Assessment or TDOC Statistical Abstract FY2025. |
| `source_year` | Numeric/Text | Source year, currently `2010` or `2025`. |
| `source_file` | Text | Source file name used by the processor. |
| `source_page` | Numeric | Source PDF page number when available for FY2025 facility-total extraction. Historical rows may be blank. |
| `geographic_reference` | Text | Broad context geography, such as `TDOC correctional system` or `TDOC facility profile`. |
| `geo_level` | Text | Geographic/context level such as `state_correctional_system` or `state_correctional_facility`. |
| `correctional_context_flag` | Boolean | Required flag marking the row as correctional-system context. Should be true for all rows. |
| `historical_context_flag` | Boolean | True for historical 2010 broad-context rows; false for FY2025 facility-total rows. |
| `facility_context` | Text | Broad facility-profile context for FY2025 aggregate rows or statewide TDOC institutional context for historical rows. This should not include addresses, coordinates, or facility security details. |
| `confirmed_member_count` | Numeric | FY2025 facility-level confirmed STG/gang classification count. Blank for historical context rows. |
| `suspected_member_count` | Numeric | FY2025 facility-level suspected STG/gang classification count. Blank for historical context rows. |
| `total_member_count` | Numeric | FY2025 facility-level total confirmed plus suspected STG/gang classification count. Blank for historical context rows. |
| `source_status_note` | Text | Short sanitized source-status note. Should not contain operational details or sensitive recognition details. |
| `responsible_use_flag` | Text | Required caveat explaining that the row is correctional-system context only, non-scoring, and not a county-level risk or activity label. |
| `include_in_report` | Boolean | Whether the row may appear in the PDF appendix. |
| `include_in_score` | Boolean | Forced to `False`. This layer is not part of scoring. |

### TDOC STG Validation Fields

Generated by `tdoc_stg_reference_processor.py` as `tn_tdoc_stg_reference_validation.csv`.

| Column | Type | Description |
|---|---:|---|
| `validation_item` | Text | Validation check name, such as row count, non-scoring status, facility row count, count population, count consistency, prohibited-detail screen, or correctional-context flag. |
| `status` | Text | Validation result such as `OK`, `WARN`, `REVIEW`, or `FAIL`. |
| `detail` | Text | Human-readable validation detail. |

### TDOC STG Context Input / Output Files

| File | Main Fields / Purpose |
|---|---|
| `stg_threat_assessment__tn_major_groups__apr_2010__les_.pdf` | Historical TDOC institutional context source. Used only to retain broad major-group historical references. Sensitive operational or recognition details are not retained. |
| `2025 Statistical Abstract.pdf` | Public FY2025 TDOC statistical source. Used to extract public aggregate facility-level STG/gang confirmed, suspected, and total counts. |
| `tn_tdoc_stg_reference_context.csv` | Final sanitized non-scoring TDOC STG correctional-system context table. |
| `tn_tdoc_stg_reference_validation.csv` | Validation summary for the TDOC STG context processor. |

### TDOC STG Processor Notes

| Script / Setting | Purpose |
|---|---|
| `tdoc_stg_reference_processor.py` | Builds the non-scoring TDOC STG correctional-system context and validation outputs. |
| `INCLUDE_FY2025_TOP_GROUP_ROWS` | Defaults to `False`. Facility-total rows are preferred because top-five chart extraction can be inconsistent and requires manual QA. |
| Count reconciliation rule | If a PDF-extracted FY2025 facility row has `confirmed + suspected != total`, the processor preserves confirmed and total and reconciles suspected to `total - confirmed`, then validates arithmetic consistency. |

## TBI 2024 Hate Crime Report Context Fields

Generated by `tbi_hate_crime_report_context.py`.

These are statewide context fields only. They are not part of the county-level scoring model and do not replace the county-level hate-crime offense input.

### Bias Context Fields

| Column | Type | Description |
|---|---:|---|
| `bias_category` | Text | Statewide TBI hate-crime bias category. |
| `known_bias_2022` | Numeric | Statewide count for the category in 2022. |
| `known_bias_2023` | Numeric | Statewide count for the category in 2023. |
| `known_bias_2024` | Numeric | Statewide count for the category in 2024. |
| `percent_of_known_bias_2024` | Numeric | Percent of known-bias total in 2024. Unknown-bias rows may be blank because unknown bias is not part of known-bias percentage interpretation. |
| `source_name` | Text | Source name, usually Tennessee Bureau of Investigation 2024 Hate Crime Report. |
| `source_file` | Text | Source file name or report reference. |
| `responsible_use_note` | Text | Context-only responsible-use note. |

### Offense Context Fields

| Column | Type | Description |
|---|---:|---|
| `crime_category` | Text | Statewide offense category such as Crimes Against Persons or Crimes Against Property. |
| `offense_type` | Text | Statewide offense type. |
| `reported_total_2024` | Numeric | Statewide reported total in 2024. |
| `source_name` | Text | Source name. |
| `source_file` | Text | Source file name or report reference. |
| `responsible_use_note` | Text | Context-only responsible-use note. |

### Clearance Context Fields

| Column | Type | Description |
|---|---:|---|
| `clearance_type` | Text | Statewide clearance type. |
| `reported_total_2024` | Numeric | Statewide reported total in 2024. |
| `source_name` | Text | Source name. |
| `source_file` | Text | Source file name or report reference. |
| `responsible_use_note` | Text | Context-only responsible-use note. |

### Location Context Fields

| Column | Type | Description |
|---|---:|---|
| `location_type` | Text | Statewide broad location type category. |
| `reported_total_2024` | Numeric | Statewide reported total in 2024. |
| `source_name` | Text | Source name. |
| `source_file` | Text | Source file name or report reference. |
| `responsible_use_note` | Text | Context-only responsible-use note. |

### Summary Context Fields

| Column | Type | Description |
|---|---:|---|
| `context_item` | Text | Summary context item label. |
| `value` | Numeric | Associated statewide value. |
| `note` | Text | Short explanation of the context item. |
| `source_name` | Text | Source name. |
| `source_file` | Text | Source file name or report reference. |
| `responsible_use_note` | Text | Context-only responsible-use note. |

---

## Score Fields

### Household Financial Stress

| Column | Type | Description |
|---|---:|---|
| `poverty_score` | Numeric | Min-max score for poverty rate. |
| `unemployment_score` | Numeric | Min-max score for unemployment rate. |
| `income_stress_score` | Numeric | Inverted min-max score for median household income. Lower income produces higher stress score. |
| `rent_burden_score` | Numeric | Min-max score for rent burden rate. |
| `household_financial_stress_score` | Numeric | Composite financial stress score. |

### Cash and Retail Exposure

| Column | Type | Description |
|---|---:|---|
| `cash_intensive_retail_score` | Numeric | Composite score for selected cash-intensive business establishment density. |
| `tobacco_vape_density_score` | Numeric | Tobacco/vape establishment density score. |
| `poverty_adjusted_tobacco_vape_score` | Numeric | Tobacco/vape score adjusted with poverty exposure. |

### Tactical Access

| Column | Type | Description |
|---|---:|---|
| `sporting_goods_density_score` | Numeric | Sporting goods establishment density score. |
| `ffl_density_score` | Numeric | Total FFL density score. |
| `dealer_ffl_density_score` | Numeric | Dealer FFL density score. |
| `manufacturer_ffl_density_score` | Numeric | Manufacturer FFL density score. |
| `pawnbroker_ffl_density_score` | Numeric | Pawnbroker FFL density score. |
| `collector_ffl_density_score` | Numeric | Collector FFL density score. |
| `importer_ffl_density_score` | Numeric | Importer FFL density score. |
| `destructive_device_ffl_density_score` | Numeric | Destructive-device-related FFL density score. |
| `training_density_score` | Numeric | Tactical training density score. |
| `surplus_tactical_density_score` | Numeric | Surplus/tactical retail density score. |
| `gun_range_density_score` | Numeric | Gun range density score. |
| `ffl_subtype_score` | Numeric | Composite score based on FFL subtypes. |
| `tactical_access_score` | Numeric | Composite tactical-access exposure score. |

### Crime / Weapons Pressure

| Column | Type | Description |
|---|---:|---|
| `homicide_pressure_score` | Numeric | Min-max score for homicide rate. |
| `kidnapping_abduction_pressure_score` | Numeric | Min-max score for kidnapping/abduction rate. |
| `weapons_law_violation_pressure_score` | Numeric | Min-max score for weapon law violation rate. |
| `violent_crime_pressure_score` | Numeric | Min-max score for violent crime rate. |
| `aggravated_assault_pressure_score` | Numeric | Min-max score for aggravated assault rate. |
| `arson_pressure_score` | Numeric | Min-max score for arson rate. |
| `sex_offense_pressure_score` | Numeric | Min-max score for sex offense rate. |
| `hate_crime_pressure_score` | Numeric | Min-max score for hate crime rate from the broad crime/weapons input. |
| `law_enforcement_assault_pressure_score` | Numeric | Min-max score for law-enforcement assault rate. |
| `violent_crime_weapons_pressure_score` | Numeric | Composite crime/weapons pressure score. |

### Organized Violence / High-Severity Crime Pressure

| Column | Type | Description |
|---|---:|---|
| `organized_violence_pressure_score` | Numeric | Composite score combining crime/weapons pressure, overall crime-rate pressure, gang-related activity pressure, explosive-use pressure, gang + explosive intersection pressure, and targeted harm / public-safety pressure. |
| `overall_crime_rate_index_score` | Numeric | Overall crime-rate index used inside organized violence pressure. |
| `gang_related_crime_pressure_score` | Numeric | Gang-related criminal activity pressure score. |
| `explosive_related_pressure_score` | Numeric | Explosive-use criminal activity pressure score. |
| `gang_explosive_pressure_score` | Numeric | Gang + explosive-use intersection pressure score. |
| `targeted_harm_public_safety_pressure_score` | Numeric | Targeted harm / public-safety score used inside organized violence pressure. |

### Institutional / Enforcement Pressure

| Column | Type | Description |
|---|---:|---|
| `institutional_enforcement_pressure_score` | Numeric | Active derived score combining law-enforcement ambush pressure, law-enforcement assault pressure, crime/weapons pressure, overall crime-rate pressure, targeted harm / public-safety pressure, and disaster/disruption vulnerability. |

### Final Composite Scores

| Column | Type | Description |
|---|---:|---|
| `finance_tactical_vulnerability_score` | Numeric | Composite score for financial, business, banking, tactical, and disruption exposure. |
| `final_domestic_security_risk_score` | Numeric | Final weighted composite model score. |
| `risk_signal` | Text | Risk band derived from final score: Low, Guarded, Elevated, or High. |

---

## Streamlit Dashboard Display Fields

Generated and displayed by `app.py`.

These fields are dashboard presentation fields only. They do not replace the scored output CSVs and do not alter the model.

| Field / Object | Type | Description |
|---|---:|---|
| `filtered_scores` | DataFrame | Score dataframe filtered by selected county and/or risk signal in the dashboard sidebar. |
| `selected_counties` | List | Sidebar-selected counties. Empty selection means all counties. |
| `selected_signals` | List | Sidebar-selected risk-signal filters. Empty selection means all signals. |
| `dashboard_scenario_score` | Numeric | Dashboard-calculated exploratory scenario score based on selected scenario preset weights. |
| `dashboard_scenario_rank` | Numeric | Rank generated from `dashboard_scenario_score` inside the dashboard scenario tab. |
| `County Brief` | Dashboard tab | Analyst-style county summary generated from existing county-level score fields. |
| `Top Contributing Model Layers` | Dashboard display | Top component scores for the selected county brief, sorted from highest to lowest. |
| `County-Level Dashboard Filters` | Dashboard sidebar | County and risk-signal filters applied across county-level dashboard tabs. |
| `PDF Download` | Dashboard button | Downloads the existing final PDF report from `outputs/reports/`. |
| `Markdown County Brief Download` | Dashboard button | Downloads the selected county brief as a Markdown file. |

### Dashboard Tabs

| Tab | Primary Source Table(s) | Notes |
|---|---|---|
| Overview | `tn_county_domestic_security_scores.csv` | Top scores, executive metrics, and selected charts. |
| Rankings | `tn_county_domestic_security_scores.csv` | Sortable county ranking table with download button. |
| County Deep Dive | `tn_county_domestic_security_scores.csv` | Full transposed record for a selected county. |
| County Brief | `tn_county_domestic_security_scores.csv` | Markdown-style analyst brief for a selected county. |
| Operational Risk | `tn_operational_risk_features.csv` | Defensive operational-risk / protective-planning layer with exposure, resilience gap, healthcare capacity, infrastructure pressure, transportation pressure, and law-enforcement capacity baseline fields. |
| Finance / Tactical | `tn_county_finance_tactical_scores.csv` | County-level finance, banking, retail, FFL, and tactical-access indicators. |
| Organized Violence | `tn_county_organized_violence_scores.csv` | Organized violence / high-severity crime component indicators. |
| Targeted Harm | `tn_county_targeted_harm_public_safety_scores.csv` | Hate-crime / targeted-harm and law-enforcement ambush indicators. |
| Disaster / Disruption | `tn_county_disaster_disruption_scores.csv` | FEMA and Phase 6 disaster/disruption vulnerability indicators. |
| Institutional | `tn_county_institutional_enforcement_scores.csv` | Institutional / enforcement pressure indicators. |
| Political Violence | `tn_county_political_violence_scores.csv` | ACLED political violence / civil unrest indicators. |
| Scenarios | `tn_county_domestic_security_scores.csv`, `model_weight_sensitivity_results.csv`, `top_county_rank_stability.csv` | Scenario presets and rank-stability outputs. |
| Data Quality | `tn_county_data_quality_flags.csv` | Data coverage and model-confidence indicators. |
| Public References | `tn_public_group_activity_reference.csv`, `tn_public_group_reference_validation.csv` | Non-scoring public group / network reference layer. |
| TBI Hate-Crime Context | `tn_2024_hate_crime_*_context.csv` | Statewide non-scoring hate-crime context. |
| TDOC STG Context | `tn_tdoc_stg_reference_context.csv`, `tn_tdoc_stg_reference_validation.csv` | Non-scoring TDOC correctional-system STG context with sanitized historical and FY2025 facility-total aggregate rows. |
| Sources | `source_register.csv` | Source register and responsible-use notes. |
| Model Card | Static dashboard text | Responsible-use summary and model limitations. |
| PDF | Final PDF report | Download button for `tennessee_domestic_security_finance_risk_report.pdf`. |

### Dashboard Filter Behavior

| Filter | Applies To | Notes |
|---|---|---|
| County filter | County-level dashboard tabs | Empty selection means all counties. |
| Risk-signal filter | Score-based dashboard views | Empty selection means all risk signals. |
| Public reference tabs | Not county-score filtered | These layers remain non-scoring appendix/context layers. |
| TBI hate-crime context tabs | Not county-score filtered | These are statewide context tables, not county scoring tables. |
| TDOC STG context tab | Not county-score filtered | This is correctional-system appendix context, not county scoring data. |

---

## Current Phase 6 Scoring Weights

### Final Domestic Security Risk Score

| Component | Weight |
|---|---:|
| Finance & Tactical Vulnerability | 30% |
| Organized Violence / High-Severity Crime Pressure | 20% |
| Political Violence / Civil Unrest Exposure | 15% |
| Household Financial Stress | 15% |
| Disaster / Disruption Vulnerability | 10% |
| Tactical Access Exposure | 5% |
| Institutional / Enforcement Pressure | 5% |

### Organized Violence / High-Severity Crime Pressure

| Component | Weight |
|---|---:|
| Crime / Weapons Pressure | 30% |
| Overall Crime Rate Index | 15% |
| Gang-Related Criminal Activity Pressure | 18% |
| Explosive-Use Criminal Activity Pressure | 13% |
| Gang + Explosive Intersection Pressure | 13% |
| Targeted Harm / Public-Safety Pressure | 11% |

### Targeted Harm / Public-Safety Pressure

| Component | Weight |
|---|---:|
| Hate-Crime / Targeted-Harm Pressure | 55% |
| Law-Enforcement Ambush Pressure | 45% |

### Institutional / Enforcement Pressure

| Component | Weight |
|---|---:|
| Law-Enforcement Ambush Pressure | 25% |
| Law-Enforcement Assault Pressure | 20% |
| Crime / Weapons Pressure | 20% |
| Overall Crime Rate Index | 15% |
| Targeted Harm / Public-Safety Pressure | 10% |
| Disaster / Disruption Vulnerability | 10% |

### Operational Risk & Protective Planning Score

The operational-risk score is maintained outside the final domestic-security risk score. Exact component weights should be checked in `operational_risk_features.py` for the current build. Conceptually, the layer combines:

| Component | Treatment |
|---|---|
| Existing Threat Context | Uses the existing model context as one input to the operational-risk layer. |
| Operational Exposure | Population, density, socioeconomic pressure, transportation pressure, infrastructure pressure, and public-safety context. |
| Resilience Gap | Healthcare capacity gap, FEMA vulnerability/resilience gap, and law-enforcement capacity gap. |
| Final Operational Risk | Separate defensive planning score with tier labels such as Low, Moderate, Elevated, or High. |

---

## CrimeInsight Label Mapping Validation Fields

Generated by `crime_offense_processor.py`.

| Column | Type | Description |
|---|---:|---|
| `source_offense_label` | Text | Raw CrimeInsight offense label from the export. |
| `normalized_offense_label` | Text | Cleaned and normalized version of the offense label. |
| `metric` | Text | Model field the raw offense label is mapped into. |
| `total_count` | Numeric | Statewide total count for the mapped label across county columns. |
| `unmapped_offense_label` | Text | Raw offense label not mapped into a model field. |
| `normalized_unmapped_label` | Text | Normalized version of an unmapped label. |

---

## Processor Validation / Summary Fields

Generated by the TBI focused processors.

| File | Main Fields |
|---|---|
| `tn_hate_crime_offense_summary.csv` | County-level hate-crime offense totals and mapped category counts. |
| `tn_hate_crime_offense_mapping_validation.csv` | Source offense label mapping validation for the hate-crime processor. |
| `tn_law_enforcement_ambush_summary.csv` | County-level law-enforcement ambush totals and mapped category counts. |
| `tn_law_enforcement_ambush_mapping_validation.csv` | Source offense label mapping validation for the law-enforcement ambush processor. |
| `tn_gang_activity_summary.csv` | County-level gang-related activity summary. |
| `tn_gang_activity_mapping_validation.csv` | Source offense label mapping validation for the gang-activity processor. |
| `tn_explosives_activity_summary.csv` | County-level explosive-use activity summary. |
| `tn_explosives_activity_mapping_validation.csv` | Source offense label mapping validation for the explosives processor. |
| `tn_gang_explosives_activity_summary.csv` | County-level gang + explosive-use intersection summary. |
| `tn_gang_explosives_activity_mapping_validation.csv` | Source offense label mapping validation for the gang + explosives processor. |
| `tn_tdoc_stg_reference_validation.csv` | Validation summary for the non-scoring TDOC correctional-system STG context layer. |

---

## Crime Trend Analysis Fields

Generated by `crime_trend_analysis.py`.

| Column | Type | Description |
|---|---:|---|
| `total_selected_crime_count_2023` | Numeric | Selected crime/weapons count for 2023. |
| `total_selected_crime_count_2024` | Numeric | Selected crime/weapons count for 2024. |
| `total_selected_crime_abs_change` | Numeric | Absolute 2024 minus 2023 change in selected crime/weapons count. |
| `total_selected_crime_pct_change` | Numeric | Percent change in selected crime/weapons count. |
| `weapon_law_violation_yoy_change` | Numeric | Year-over-year change in weapon law violation count. |
| `violent_crime_yoy_change` | Numeric | Year-over-year change in violent crime count. |
| `crime_pressure_yoy_change` | Numeric | Composite or selected trend-change indicator used for ranking trend increases. |
| `trend_signal` | Text | Trend classification label based on year-over-year change. |

---

## Sensitivity Analysis Fields

Generated by `sensitivity_analysis.py`.

| Column | Type | Description |
|---|---:|---|
| `scenario` | Text | Weighting scenario name. |
| `scenario_score` | Numeric | County score under the selected sensitivity scenario. |
| `scenario_rank` | Numeric | County rank under the selected sensitivity scenario. |
| `best_rank` | Numeric | Best rank achieved across sensitivity scenarios. |
| `worst_rank` | Numeric | Worst rank achieved across sensitivity scenarios. |
| `average_rank` | Numeric | Average rank across sensitivity scenarios. |
| `rank_range` | Numeric | Difference between worst rank and best rank. |
| `top_10_scenario_count` | Numeric | Number of scenarios in which the county appears in the top 10. |
| `rank_stability_signal` | Text | Rank stability label: Very Stable, Stable, Moderately Sensitive, or Highly Sensitive. |

### Sensitivity Scenarios

| Scenario | Description |
|---|---|
| `baseline_phase6` | Current Phase 6 final scoring structure. |
| `finance_heavy` | Places greater weight on finance and tactical vulnerability. |
| `organized_violence_heavy` | Places greater weight on organized violence / high-severity crime pressure. |
| `targeted_harm_public_safety_heavy` | Places greater weight on targeted harm / public-safety pressure and law-enforcement ambush pressure. |
| `institutional_enforcement_heavy` | Places greater weight on institutional / enforcement pressure. |
| `gang_explosives_heavy` | Places greater weight on gang activity, explosive-use, and gang + explosive intersection layers. |
| `political_violence_heavy` | Places greater weight on ACLED political violence / civil unrest exposure. |
| `disaster_disruption_heavy` | Places greater weight on disaster / disruption vulnerability. |
| `socioeconomic_heavy` | Places greater weight on household financial stress. |
| `tactical_access_heavy` | Places greater weight on tactical-access exposure. |

---

## Data Quality Fields

| Column | Type | Description |
|---|---:|---|
| `acs_data_available` | Boolean | Whether ACS socioeconomic data is available. |
| `cbp_data_available` | Boolean | Whether CBP business exposure columns are present. |
| `fdic_data_available` | Boolean | Whether FDIC banking data has usable values. |
| `ffl_data_available` | Boolean | Whether FFL aggregate data has usable values. |
| `fema_data_available` | Boolean | Whether FEMA disaster data has usable values. |
| `disaster_disruption_data_available` | Boolean | Whether Phase 6 disaster/disruption columns are present. |
| `crime_data_available` | Boolean | Whether TBI CrimeInsight crime/weapons columns are present. |
| `crime_rate_data_available` | Boolean | Whether TBI overall crime-rate columns are present. |
| `political_violence_data_available` | Boolean | Whether ACLED political violence / civil unrest columns are present. |
| `gang_activity_data_available` | Boolean | Whether TBI gang-related activity columns are present. |
| `explosives_activity_data_available` | Boolean | Whether TBI explosive-use activity columns are present. |
| `gang_explosives_activity_data_available` | Boolean | Whether TBI gang + explosives intersection columns are present. |
| `hate_crime_offense_data_available` | Boolean | Whether TBI hate-crime offense columns are present. |
| `law_enforcement_ambush_data_available` | Boolean | Whether TBI law-enforcement ambush columns are present. |
| `targeted_harm_public_safety_data_available` | Boolean | Whether targeted harm / public-safety derived columns are present. |
| `institutional_data_available` | Boolean | Whether institutional / enforcement pressure derived columns are present. |
| `active_source_count` | Numeric | Number of active available source layers. |
| `data_completeness_score` | Numeric | Percentage of active model source layers available for a county. |
| `model_confidence` | Text | Data-completeness band: Low, Moderate, Good, or High. |
| `possible_fdic_gap_flag` | Boolean | Indicates possible missing or zero-filled FDIC data. |
| `possible_cbp_gap_flag` | Boolean | Indicates possible missing CBP columns. |
| `possible_ffl_gap_flag` | Boolean | Indicates possible missing or zero-filled FFL data. |
| `possible_fema_gap_flag` | Boolean | Indicates possible missing or zero-filled FEMA data. |
| `possible_disaster_disruption_gap_flag` | Boolean | Indicates possible missing Phase 6 disaster/disruption columns. |
| `possible_crime_gap_flag` | Boolean | Indicates possible missing TBI CrimeInsight fields. |
| `possible_crime_rate_gap_flag` | Boolean | Indicates possible missing TBI overall crime-rate fields. |
| `possible_political_violence_gap_flag` | Boolean | Indicates possible missing ACLED fields. |
| `possible_gang_activity_gap_flag` | Boolean | Indicates possible missing TBI gang-related activity fields. |
| `possible_explosives_activity_gap_flag` | Boolean | Indicates possible missing TBI explosive-use fields. |
| `possible_gang_explosives_activity_gap_flag` | Boolean | Indicates possible missing TBI gang + explosives fields. |
| `possible_hate_crime_offense_gap_flag` | Boolean | Indicates possible missing TBI hate-crime offense fields. |
| `possible_law_enforcement_ambush_gap_flag` | Boolean | Indicates possible missing TBI law-enforcement ambush fields. |
| `possible_targeted_harm_public_safety_gap_flag` | Boolean | Indicates possible missing targeted harm / public-safety fields. |
| `possible_institutional_gap_flag` | Boolean | Indicates possible missing institutional / enforcement pressure fields. |
| `cbp_selected_establishment_total` | Numeric | Sum of selected CBP establishment counts. |
| `cbp_true_zero_selected_categories` | Boolean | Indicates CBP columns exist but selected category totals are zero. |
| `ffl_selected_total` | Numeric | Sum of selected FFL aggregate values. |
| `ffl_true_zero_selected_categories` | Boolean | Indicates FFL columns exist but selected totals are zero. |
| `fema_selected_total` | Numeric | Sum of selected FEMA disaster values. |
| `fema_true_zero_selected_categories` | Boolean | Indicates FEMA columns exist but selected values are zero. |
| `disaster_disruption_selected_total` | Numeric | Sum of selected Phase 6 disaster/disruption values. |
| `disaster_disruption_true_zero_selected_categories` | Boolean | Indicates disaster/disruption columns exist but selected values are zero. |
| `crime_weapons_selected_total` | Numeric | Sum of selected crime/weapons counts. |
| `crime_true_zero_selected_categories` | Boolean | Indicates CrimeInsight columns exist but selected totals are zero. |
| `crime_rate_selected_total` | Numeric | Sum of selected crime-rate input values. |
| `crime_rate_true_zero_selected_categories` | Boolean | Indicates crime-rate columns exist but selected values are zero. |
| `political_violence_selected_total` | Numeric | Sum of selected ACLED political violence / civil unrest values. |
| `political_violence_true_zero_selected_categories` | Boolean | Indicates ACLED columns exist but selected values are zero. |
| `gang_activity_selected_total` | Numeric | Sum of selected TBI gang-related activity values. |
| `gang_activity_true_zero_selected_categories` | Boolean | Indicates gang-related activity columns exist but selected values are zero. |
| `explosives_activity_selected_total` | Numeric | Sum of selected explosive-use activity values. |
| `explosives_activity_true_zero_selected_categories` | Boolean | Indicates explosive-use columns exist but selected values are zero. |
| `gang_explosives_activity_selected_total` | Numeric | Sum of selected gang + explosives values. |
| `gang_explosives_activity_true_zero_selected_categories` | Boolean | Indicates gang + explosives columns exist but selected values are zero. |
| `hate_crime_offense_selected_total` | Numeric | Sum of selected hate-crime offense values. |
| `hate_crime_offense_true_zero_selected_categories` | Boolean | Indicates hate-crime offense columns exist but selected values are zero. |
| `law_enforcement_ambush_selected_total` | Numeric | Sum of selected law-enforcement ambush values. |
| `law_enforcement_ambush_true_zero_selected_categories` | Boolean | Indicates law-enforcement ambush columns exist but selected values are zero. |
| `targeted_harm_public_safety_selected_total` | Numeric | Sum of selected targeted harm / public-safety values. |
| `targeted_harm_public_safety_true_zero_selected_categories` | Boolean | Indicates targeted harm / public-safety columns exist but selected values are zero. |
| `institutional_selected_total` | Numeric | Sum of selected institutional / enforcement pressure fields. |
| `institutional_true_zero_selected_categories` | Boolean | Indicates institutional / enforcement fields exist but selected values are zero. |
| `data_quality_note` | Text | Notes explaining missing, zero-filled, or true-zero source conditions. |

Reference/context validation fields are tracked separately and are not included in `data_completeness_score`.

---

## Output Files and Main Fields

| File | Main Fields |
|---|---|
| `tn_county_master_dataset.csv` | Merged county-level input dataset before scoring. |
| `tn_county_domestic_security_scores.csv` | Full dataset with all input, rate, score, and quality fields. |
| `tn_county_component_scores.csv` | County, population, major component scores, final score, risk signal, confidence. |
| `tn_county_finance_tactical_scores.csv` | Banking, retail, FFL, tactical, disaster, finance/tactical scores. |
| `tn_county_crime_weapons_scores.csv` | Crime counts, per-capita rates, crime pressure scores, organized violence score, crime quality flags. |
| `tn_county_organized_violence_scores.csv` | Gang, explosives, gang + explosives, targeted harm, overall crime, and organized violence pressure fields. |
| `tn_county_targeted_harm_public_safety_scores.csv` | Hate-crime, law-enforcement ambush, targeted harm / public-safety, and organized violence pressure fields. |
| `tn_county_disaster_disruption_scores.csv` | FEMA disaster, optional disaster/disruption, access stress, recovery strain, and disruption vulnerability fields. |
| `tn_county_institutional_enforcement_scores.csv` | Law-enforcement assault, ambush, crime pressure, targeted harm, disaster/disruption, and institutional/enforcement pressure fields. |
| `tn_county_political_violence_scores.csv` | ACLED county-level political violence / civil unrest counts, rates, and scores. |
| `tn_operational_risk_features.csv` | Final Operational Risk & Protective Planning feature layer with exposure, resilience gap, healthcare, infrastructure, transportation, law-enforcement capacity, tier, and operational data-quality fields. |
| `tn_county_law_enforcement_capacity.csv` | CSLLEA 2018 county-level law-enforcement response-capacity baseline. |
| `tn_county_healthcare_capacity.csv` | County-level healthcare capacity and emergency-capacity proxy fields. |
| `tn_county_transport_context.csv` | County-level TDOT transportation pressure fields. |
| `tn_county_infrastructure_needs.csv` | County-level TACIR infrastructure needs and infrastructure-needs-per-capita fields. |
| `tbi_county_public_safety_context.csv` | County-level TBI public-safety context fields used in the operational-risk layer. |
| `tn_county_data_quality_flags.csv` | Source availability and model-confidence fields. |
| `crime_offense_label_mapping_validation.csv` | Raw CrimeInsight label-to-model-field mapping validation. |
| `crime_offense_unmapped_labels.csv` | Unmapped CrimeInsight labels retained for audit review. |
| `model_weight_sensitivity_results.csv` | Scenario-level sensitivity scores and ranks. |
| `top_county_rank_stability.csv` | Rank-stability summary across sensitivity scenarios. |
| `scenario_top_county_leaders.csv` | Top counties under each sensitivity scenario. |
| `tn_crime_weapons_trend_analysis.csv` | 2023-to-2024 selected crime/weapons trend analysis. |
| `tn_gang_activity_summary.csv` | County-level gang-related activity summary. |
| `tn_explosives_activity_summary.csv` | County-level explosive-use activity summary. |
| `tn_gang_explosives_activity_summary.csv` | County-level gang + explosive-use intersection summary. |
| `tn_hate_crime_offense_summary.csv` | County-level hate-crime offense summary. |
| `tn_law_enforcement_ambush_summary.csv` | County-level law-enforcement ambush summary. |
| `tn_splc_public_group_reference_candidates_2024.csv` | SPLC-derived public group / network reference candidates; non-scoring. |
| `tn_public_group_activity_reference.csv` | Validated public group / network reference register; non-scoring. |
| `tn_public_group_reference_validation.csv` | Validation table for public group / network reference layer. |
| `tn_2024_hate_crime_bias_context.csv` | TBI 2024 statewide hate-crime bias context; non-scoring. |
| `tn_2024_hate_crime_offense_context.csv` | TBI 2024 statewide hate-crime offense context; non-scoring. |
| `tn_2024_hate_crime_clearance_context.csv` | TBI 2024 statewide hate-crime clearance context; non-scoring. |
| `tn_2024_hate_crime_location_context.csv` | TBI 2024 statewide hate-crime location context; non-scoring. |
| `tn_2024_hate_crime_report_context_summary.csv` | TBI 2024 statewide hate-crime context summary; non-scoring. |
| `tn_tdoc_stg_reference_context.csv` | Sanitized TDOC correctional-system STG context table; non-scoring. Includes broad 2010 historical context rows and FY2025 public facility-total aggregate rows. |
| `tn_tdoc_stg_reference_validation.csv` | Validation output for TDOC STG context, including non-scoring status, facility row count, count consistency, prohibited-detail screen, and correctional-context flag. |
| `source_register.csv` | Source register with source use, URL/path, and responsible-use notes. |
| `app.py` | Streamlit dashboard application. Reads existing outputs and presents dashboard tabs, filters, scenario controls, and county brief generator. |

---

## Interpretation Notes

- All scores are relative within Tennessee counties.
- Higher scores indicate higher relative exposure or vulnerability within the model, not proof of wrongdoing.
- The model should not be interpreted as a prediction engine.
- Lawful businesses, FFLs, training locations, and retail categories are exposure proxies only.
- Gang-related activity, explosive-use activity, gang + explosive-use activity, hate-crime offense counts, and law-enforcement ambush counts are aggregate indicators, not terrorism labels.
- Disaster/disruption indicators are planning-complexity and response-strain proxies, not operational vulnerability disclosures.
- Institutional/enforcement pressure is a derived county-level pressure measure, not a judgment about agency performance or misconduct.
- Public group / network references are source-context entries only, not independent findings or county-risk labels.
- TDOC correctional-system STG context rows are source-context entries only, not independent findings, county-risk labels, or community-presence indicators.
- FY2025 TDOC facility totals are correctional-system aggregate classification counts only and should not be merged into county scoring.
- TBI 2024 hate-crime context tables are statewide background only and are not county-level scoring input.
- Data completeness measures input coverage, not risk.
- Operational-risk data quality flags measure operational-layer source coverage, not threat level.
- Law-enforcement capacity gap values indicate lower relative county-level response-capacity proxy values in the 2018 CSLLEA baseline, not agency performance or current staffing adequacy.
- Healthcare capacity gap, infrastructure pressure, and transportation pressure are broad county-level planning-context proxies, not site-specific vulnerability findings.
- Dashboard filters and scenario controls are exploratory presentation tools and do not replace the baseline Phase 6 model outputs.


---

## GitHub Publication Notes

Recommended repository behavior:

- Do not commit `.env`.
- Do not commit raw source data.
- Do not commit processed data containing large local source exports unless intentionally publishing a sanitized sample.
- Do not commit generated `outputs/` files unless intentionally publishing sample screenshots or a selected final report.
- Use `.gitkeep` placeholder files to preserve empty folder structure.
- Include `README.md`, `methodology.md`, `data_dictionary.md`, `docs/public_group_reference_sources.md`, `requirements.txt`, `.gitignore`, `main.py`, `app.py`, and all `src/` modules.

Suggested tracked folders:

```text
data/raw/.gitkeep
data/processed/.gitkeep
outputs/charts/.gitkeep
outputs/tables/.gitkeep
outputs/reports/.gitkeep
```

Suggested ignored folders:

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

The final GitHub-facing project should emphasize that the dashboard and report are analytical demonstrations built from aggregate public-source indicators and responsible-use constraints.
