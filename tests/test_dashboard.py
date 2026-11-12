"""Exercise the dashboard with synthetic saved outputs, never the original data."""
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import app


def run_dashboard():
    import app
    app.main()


@pytest.fixture
def dashboard_files(monkeypatch, tmp_path):
    paths = {key: tmp_path / path.name for key, path in app.TABLES.items()}
    monkeypatch.setattr(app, "TABLES", paths)
    monkeypatch.setattr(app, "CHARTS_DIR", tmp_path / "charts")
    monkeypatch.setattr(app, "REPORT_PATH", tmp_path / "historical.pdf")
    app.load_csv.clear()
    yield paths
    app.load_csv.clear()


def test_empty_checkout_offers_final_report_without_pipeline(dashboard_files):
    at = AppTest.from_function(run_dashboard, default_timeout=30).run()
    assert not at.exception
    assert any("No saved county scores" in item.value for item in at.info)
    assert any("November 10, 2026" in item.label for item in at.get("download_button"))
    assert not any(path.exists() for path in dashboard_files.values())


def test_saved_coverage_is_labeled_and_filters_do_not_write(dashboard_files):
    fixture = json.loads((Path(__file__).parent / "fixtures/scoring_base.json").read_text())
    snapshot = fixture["cases"][0]["scores"]
    scores = pd.DataFrame(snapshot["data"], columns=snapshot["columns"])
    # Deliberately old labels: presentation must not pretend they were re-audited.
    scores["model_confidence"] = "High"
    scores["data_completeness_score"] = 100.0
    scores.to_csv(dashboard_files["scores"], index=False)
    before = hashlib.sha256(dashboard_files["scores"].read_bytes()).hexdigest()
    at = AppTest.from_function(run_dashboard, default_timeout=30).run()
    assert not at.exception
    assert any("Historical files may retain older" in item.value for item in at.info)
    assert any(item.label == "Saved coverage band" for item in at.metric)
    brief = next(item.value for item in at.markdown if "Saved source-coverage band:" in item.value)
    assert "not predictive confidence" in brief
    assert "Explosives filter" in brief
    assert "All Clearances block" in brief
    assert "does not authenticate other files" in brief
    assert sum("Explosives filter" in item.value for item in at.info) == 2
    selected = scores.iloc[0]["county"]
    at.sidebar.multiselect(key="sidebar_filter_counties_unique").set_value([selected]).run()
    assert not at.exception
    assert at.selectbox(key="county_brief_select").options == [selected]
    at.sidebar.multiselect(key="sidebar_filter_counties_unique").set_value([]).run()
    assert not at.exception
    assert hashlib.sha256(dashboard_files["scores"].read_bytes()).hexdigest() == before
    assert sum(path.exists() for path in dashboard_files.values()) == 1


def test_table_display_preserves_stored_scores():
    frame = pd.DataFrame({"county": ["Synthetic"], "final_domestic_security_risk_score": [42.125],
                          "model_confidence": ["High"], "data_completeness_score": [100.0]})
    before = frame.copy(deep=True)
    shown = app.make_arrow_safe(frame)
    pd.testing.assert_frame_equal(frame, before)
    assert shown["final_domestic_security_risk_score"].tolist() == [42.125]
