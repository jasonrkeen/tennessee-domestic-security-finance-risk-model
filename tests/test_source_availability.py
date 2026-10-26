"""Offline regression tests. All generated files stay in pytest temporary paths."""

import importlib
from io import StringIO

import numpy as np
import pandas as pd
import pytest

from src import data_collection, data_quality, risk_scoring
from src.source_availability import observed_values


@pytest.fixture
def socioeconomic():
    return pd.DataFrame({
        "county": ["Synthetic A", "Synthetic B", "Synthetic C"],
        "fips": ["47001", "47003", "47005"],
        "population": [10000, 20000, 30000],
        "poverty_rate": [.10, .15, .20],
        "unemployment_rate": [.03, .04, .05],
        "median_household_income": [70000, 60000, 50000],
        "rent_burden_rate": [.30, .40, .50],
    })


@pytest.fixture(autouse=True)
def isolated_outputs(monkeypatch, tmp_path):
    monkeypatch.setattr(risk_scoring, "TABLES_DIR", tmp_path / "tables")
    monkeypatch.setattr(data_quality, "TABLES_DIR", tmp_path / "tables")
    monkeypatch.setattr(data_collection, "PROCESSED_DIR", tmp_path)
    # Accidental live requests must fail the suite.
    monkeypatch.setattr(data_collection.requests, "get", lambda *a, **k: pytest.fail("Network access"))


def test_socioeconomic_only_regression_preserves_scores(socioeconomic):
    original = socioeconomic.copy(deep=True)
    result = risk_scoring.build_scores(socioeconomic).set_index("county").sort_index()
    assert result["active_source_count"].eq(1).all()
    np.testing.assert_allclose(result["data_completeness_score"], 100 / 14)
    assert result["model_confidence"].eq("Low").all()
    assert not result["crime_data_available"].any()
    assert not result["crime_true_zero_selected_categories"].any()
    assert not result["targeted_harm_public_safety_data_available"].any()
    assert not result["institutional_data_available"].any()
    # Frozen values from the pre-fix synthetic diagnostic: no scoring changes.
    np.testing.assert_allclose(result["final_domestic_security_risk_score"], [38.18, 50, 61.82])
    assert result["risk_signal"].tolist() == ["Guarded", "Guarded", "Elevated"]
    pd.testing.assert_frame_equal(socioeconomic, original)


@pytest.mark.parametrize("bad", [None, "suppressed", np.inf, -1])
def test_partial_or_invalid_values_cannot_become_coverage(bad):
    frame = pd.DataFrame({"a": [1], "b": [bad], "test_data_available": [True]})
    assert not observed_values(frame, ["a", "b"], "test_data_available").any()
    assert not observed_values(frame, ["a", "missing"], "test_data_available").any()


def test_explicit_flags_and_csv_round_trip():
    frame = pd.DataFrame({"a": [0, 0, 2, 2, 2], "test_data_available": [True, False, "False", None, "yes"]})
    frame = pd.read_csv(StringIO(frame.to_csv(index=False)))
    assert observed_values(frame, ["a"], "test_data_available").tolist() == [True, False, False, False, False]
    assert not observed_values(pd.DataFrame({"a": [0]}), ["a"], "test_data_available").any()


def test_complete_sources_count_once_and_verified_crime_zero(socioeconomic):
    # The score frame supplies all numeric fields; affirm their synthetic provenance.
    frame = risk_scoring.build_scores(socioeconomic)
    frame["crime_population_2024"] = frame["population"]
    for col in frame.columns:
        if col.endswith("_data_available"):
            frame[col] = True
    result = data_quality.add_data_quality_flags(frame)
    assert result["active_source_count"].eq(14).all()
    assert result["data_completeness_score"].eq(100).all()
    assert result["model_confidence"].eq("High").all()
    assert result["crime_true_zero_selected_categories"].all()


LOADERS = [
    ("crime_inputs", "load_optional_crime_weapons_inputs", "OPTIONAL_CRIME_WEAPONS_INPUT", "crime"),
    ("crime_inputs", "load_optional_gang_activity_inputs", "OPTIONAL_GANG_ACTIVITY_INPUT", "gang_activity"),
    ("crime_inputs", "load_optional_explosives_activity_inputs", "OPTIONAL_EXPLOSIVES_ACTIVITY_INPUT", "explosives_activity"),
    ("crime_inputs", "load_optional_gang_explosives_activity_inputs", "OPTIONAL_GANG_EXPLOSIVES_ACTIVITY_INPUT", "gang_explosives_activity"),
    ("crime_inputs", "load_optional_hate_crime_offense_inputs", "OPTIONAL_HATE_CRIME_OFFENSE_INPUT", "hate_crime_offense"),
    ("crime_inputs", "load_optional_law_enforcement_ambush_inputs", "OPTIONAL_LAW_ENFORCEMENT_AMBUSH_INPUT", "law_enforcement_ambush"),
    ("phase2_inputs", "load_optional_fdic_banking_inputs", "OPTIONAL_FDIC_BANKING_INPUT", "fdic"),
    ("phase2_inputs", "load_optional_ffl_inputs", "OPTIONAL_FFL_INPUT", "ffl"),
    ("political_violence_inputs", "load_optional_political_violence_inputs", "OPTIONAL_POLITICAL_VIOLENCE_INPUT", "political_violence"),
    ("disaster_disruption_inputs", "load_optional_disaster_disruption_inputs", "OPTIONAL_DISASTER_DISRUPTION_INPUT", "disaster_disruption"),
    ("data_collection", "load_optional_crime_rate_inputs", "OPTIONAL_CRIME_RATE_INPUT", "crime_rate"),
]


@pytest.mark.parametrize("module_name,function,path_name,layer", LOADERS)
def test_optional_loader_evidence(monkeypatch, tmp_path, socioeconomic, module_name, function, path_name, layer):
    module = importlib.import_module("src." + module_name)
    path = tmp_path / (layer + ".csv")
    monkeypatch.setattr(module, path_name, path)
    loader = getattr(module, function)
    flag = layer + "_data_available"
    missing = loader(socioeconomic)
    assert not missing[flag].any()
    assert not loader(socioeconomic)[flag].any()  # persisted template remains missing

    # A reviewed zero for A, an unverified zero for B, and an absent county C.
    source = missing.iloc[:2].copy()
    if layer == "crime_rate":
        source["crime_population_2024"] = 10000
    source[flag] = [True, False]
    source.to_csv(path, index=False)
    result = loader(socioeconomic).set_index("county")
    assert bool(result.loc["Synthetic A", flag])
    assert not bool(result.loc["Synthetic B", flag])
    if "Synthetic C" in result.index:
        assert not bool(result.loc["Synthetic C", flag])
    merged = socioeconomic.merge(result.reset_index(), on="county", how="left")
    scored = risk_scoring.build_scores(merged).set_index("county")
    assert bool(scored.loc["Synthetic A", flag])
    assert not bool(scored.loc["Synthetic C", flag])

    # Legacy all-zero files carry no reliable distinction from old templates.
    legacy_zero = source.drop(columns=flag).copy()
    legacy_zero.loc[:, legacy_zero.columns != "county"] = 0
    legacy_zero.to_csv(path, index=False)
    assert not loader(socioeconomic)[flag].any()

    # Even an explicit marker cannot validate a missing field or an invalid row.
    value_col = next(c for c in source if c not in {"county", flag})
    source.drop(columns=value_col).to_csv(path, index=False)
    assert not loader(socioeconomic)[flag].any()


def test_crime_duplicate_and_invalid_rows(monkeypatch, tmp_path, socioeconomic):
    from src import crime_inputs
    path = tmp_path / "crime.csv"
    monkeypatch.setattr(crime_inputs, "OPTIONAL_CRIME_WEAPONS_INPUT", path)
    template = crime_inputs.load_optional_crime_weapons_inputs(socioeconomic)
    source = pd.concat([template.iloc[:1], template.iloc[:1]], ignore_index=True)
    source["crime_data_available"] = True
    source.loc[1, "homicide_count"] = np.nan
    source.to_csv(path, index=False)
    result = crime_inputs.load_optional_crime_weapons_inputs(socioeconomic)
    assert not result["crime_data_available"].any()


def test_cbp_partial_retrieval_and_valid_zero(monkeypatch):
    monkeypatch.setattr(data_collection, "CBP_INDUSTRIES", {"a": "a_establishments", "b": "b_establishments"})
    monkeypatch.setattr(data_collection, "CBP_YEARS_TO_TRY", [2023])
    def fetch(year, industry):
        return pd.DataFrame({"state": ["47"], "county": ["001"], "ESTAB": [0], "cbp_year": [year], "naics_code": [industry], "naics_param_used": ["NAICS2017"]})
    monkeypatch.setattr(data_collection, "_try_cbp_year_industry", fetch)
    assert data_collection.collect_cbp_business_exposure()["cbp_data_available"].all()
    monkeypatch.setattr(data_collection, "_try_cbp_year_industry", lambda year, industry: fetch(year, industry) if industry == "a" else None)
    assert not data_collection.collect_cbp_business_exposure()["cbp_data_available"].any()


def test_fema_failure_is_not_zero_observation(monkeypatch, tmp_path, socioeconomic):
    socioeconomic.to_csv(tmp_path / "tn_acs_county_data.csv", index=False)
    def failed(*args, **kwargs):
        raise RuntimeError("synthetic outage")
    monkeypatch.setattr(data_collection, "safe_get_json", failed)
    result = data_collection.collect_fema_disaster_data()
    assert not result["fema_data_available"].any()
    merged = socioeconomic.merge(result, on="county")
    scored = risk_scoring.build_scores(merged)
    assert not scored["fema_true_zero_selected_categories"].any()


def test_master_pipeline_keeps_missingness_across_reruns(monkeypatch, tmp_path, socioeconomic):
    # Actual master assembly and all optional loaders; only API responses are mocked.
    for module_name, _, path_name, layer in LOADERS:
        module = importlib.import_module("src." + module_name)
        monkeypatch.setattr(module, path_name, tmp_path / (layer + ".csv"))
    monkeypatch.setattr(data_collection, "OPTIONAL_TACTICAL_INPUT", tmp_path / "tactical.csv")
    monkeypatch.setattr(data_collection, "ensure_dirs", lambda: None)
    monkeypatch.setattr(data_collection, "build_source_register", lambda: None)
    def acs():
        socioeconomic.to_csv(tmp_path / "tn_acs_county_data.csv", index=False)
        return socioeconomic.copy()
    monkeypatch.setattr(data_collection, "collect_acs_county_data", acs)
    monkeypatch.setattr(data_collection, "_try_cbp_year_industry", lambda *a: None)
    monkeypatch.setattr(data_collection, "safe_get_json", lambda *a, **k: {})
    for _ in range(2):
        master = data_collection.build_master_dataset()
        # Verify serialization does not erase evidence before scoring.
        master = pd.read_csv(StringIO(master.to_csv(index=False)))
        result = risk_scoring.build_scores(master)
        assert result["active_source_count"].eq(1).all()
        assert result["model_confidence"].eq("Low").all()
        assert not result["crime_true_zero_selected_categories"].any()


@pytest.mark.parametrize("dtype", ["Int64", "Float64"])
@pytest.mark.parametrize("marker", [True, None])
def test_nullable_missing_cell_is_not_skipped(dtype, marker):
    frame = pd.DataFrame({"a": pd.Series([1], dtype=dtype), "b": pd.Series([pd.NA], dtype=dtype)})
    if marker is not None:
        frame["test_data_available"] = marker
    assert not observed_values(frame, ["a", "b"], "test_data_available").any()


@pytest.mark.parametrize("denominator", ["population", "crime_population_2024"])
def test_zero_denominator_is_unavailable(denominator):
    frame = pd.DataFrame({denominator: [0], "count": [3], "test_data_available": [True]})
    assert not observed_values(frame, [denominator, "count"], "test_data_available").any()


def test_crime_rate_evidence_uses_actual_join_keys(monkeypatch, tmp_path, socioeconomic):
    path = tmp_path / "rates.csv"
    monkeypatch.setattr(data_collection, "OPTIONAL_CRIME_RATE_INPUT", path)
    source = pd.DataFrame({
        "county": ["Synthetic A County", "Synthetic B"],
        "overall_crime_rate_per_1000_2024": [2, 3],
        "overall_crime_count_2024": [20, 60],
        "crime_population_2024": [10000, 20000],
        "crime_rate_data_available": [True, True],
    })
    source.to_csv(path, index=False)
    result = data_collection.load_optional_crime_rate_inputs(socioeconomic).set_index("county")
    assert not bool(result.loc["Synthetic A", "crime_rate_data_available"])
    assert bool(result.loc["Synthetic B", "crime_rate_data_available"])
    # Preserve existing exact-match behavior instead of changing the scored data.
    assert result.loc["Synthetic A", "overall_crime_count_2024"] == 0
    assert result.loc["Synthetic B", "overall_crime_count_2024"] == 60


def test_acled_legacy_aliases_keep_coverage(monkeypatch, tmp_path, socioeconomic):
    from src import political_violence_inputs as module
    path = tmp_path / "acled.csv"
    monkeypatch.setattr(module, "OPTIONAL_POLITICAL_VIOLENCE_INPUT", path)
    source = module.load_optional_political_violence_inputs(socioeconomic).iloc[:1].copy()
    source["political_violence_data_available"] = True
    source["political_violence_event_count"] = 2
    source = source.rename(columns={"political_violence_event_count": "extremism_related_event_count", "strategic_development_count": "threat_incident_count"})
    source.to_csv(path, index=False)
    result = module.load_optional_political_violence_inputs(socioeconomic)
    assert bool(result.iloc[0]["political_violence_data_available"])
    assert result.iloc[0]["political_violence_event_count"] == 2


@pytest.mark.parametrize("missing", ["fyDeclared", "incidentType", "declarationTitle"])
def test_fema_partial_record_does_not_establish_coverage(monkeypatch, missing):
    good = {"designatedArea": "Synthetic A County", "fyDeclared": 2024, "incidentType": "Flood", "declarationTitle": "Synthetic event"}
    bad = {**good, "designatedArea": "Synthetic B County", missing: None}
    monkeypatch.setattr(data_collection, "safe_get_json", lambda *a, **k: {"DisasterDeclarationsSummaries": [good, bad]})
    result = data_collection.collect_fema_disaster_data().set_index("county")
    assert bool(result.loc["Synthetic A", "fema_data_available"])
    assert not bool(result.loc["Synthetic B", "fema_data_available"])


def test_fema_page_limit_is_not_complete_coverage(monkeypatch):
    row = {"designatedArea": "Synthetic A County", "fyDeclared": 2024, "incidentType": "Flood", "declarationTitle": "Synthetic event"}
    monkeypatch.setattr(data_collection, "safe_get_json", lambda *a, **k: {"DisasterDeclarationsSummaries": [row] * 5000})
    result = data_collection.collect_fema_disaster_data()
    assert not result["fema_data_available"].any()
    assert result.iloc[0]["disaster_declaration_count"] == 5000


def test_acs_missing_component_not_hidden_by_sum(monkeypatch):
    fields = list(data_collection.ACS_VARIABLES)
    header = ["NAME"] + fields + ["state", "county"]
    values = [10000, 60000, 10000, 1000, 5000, 200, 1000, None, 100, 100, 100]
    row = ["Synthetic A County, Tennessee"] + values + ["47", "001"]
    monkeypatch.setattr(data_collection, "safe_get_json", lambda *a, **k: [header, row])
    result = data_collection.collect_acs_county_data()
    assert result.iloc[0]["rent_burden_rate"] == .3  # unchanged sum behavior
    assert not result["acs_data_available"].any()
