import sys
from pathlib import Path
import pandas as pd
import pytest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from yottaflex.analytics import assert_no_outcome_leakage, build_supportive_signals

def test_leakage_guard_rejects_outcome_columns():
    with pytest.raises(ValueError):
        assert_no_outcome_leakage(["employee_id", "weekly_hours", "voluntary_attrition"])

def test_leakage_guard_accepts_pre_outcome_features():
    assert_no_outcome_leakage(["employee_id", "recent_engagement", "avg_recent_weekly_hours"])

def test_missing_survey_is_not_negative():
    surveys = pd.DataFrame(columns=["employee_id","survey_date","engagement_score"])
    workload = pd.DataFrame([{"employee_id":"EMP-000001","snapshot_date":"2026-08-01","weekly_hours":40}])
    promotions = pd.DataFrame(columns=["employee_id","effective_date"])
    result = build_supportive_signals(surveys, workload, promotions)
    assert result.loc[0, "survey_status"] == "MISSING"
    assert pd.isna(result.loc[0, "recent_engagement"])
    assert result.loc[0, "supportive_priority_score"] == 0
