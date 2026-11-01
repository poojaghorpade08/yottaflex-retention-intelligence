from __future__ import annotations
import pandas as pd

FORBIDDEN_FEATURE_COLUMNS = {
    "voluntary_attrition", "termination_date", "outcome_type",
    "outcome_id", "label_horizon_start", "label_horizon_end"
}

def build_supportive_signals(surveys: pd.DataFrame, workload: pd.DataFrame,
                             promotions: pd.DataFrame, cutoff: str = "2026-09-01") -> pd.DataFrame:
    """Build transparent supportive review signals using pre-cutoff data only."""
    cutoff_ts = pd.Timestamp(cutoff)
    s = surveys[pd.to_datetime(surveys["survey_date"]) <= cutoff_ts].copy()
    s["survey_date"] = pd.to_datetime(s["survey_date"])
    s = s.sort_values("survey_date")
    latest = s.groupby("employee_id").tail(2).groupby("employee_id")["engagement_score"].mean().rename("recent_engagement")
    counts = s.groupby("employee_id").size().rename("survey_count")
    w = workload[pd.to_datetime(workload["snapshot_date"]) <= cutoff_ts].copy()
    w["snapshot_date"] = pd.to_datetime(w["snapshot_date"])
    w = w.sort_values("snapshot_date").groupby("employee_id").tail(3)
    load = w.groupby("employee_id")["weekly_hours"].mean().rename("avg_recent_weekly_hours")
    p = promotions[pd.to_datetime(promotions["effective_date"]) <= cutoff_ts]
    last_promo = p.groupby("employee_id")["effective_date"].max().rename("last_promotion_date")
    ids = sorted(set(surveys.employee_id) | set(workload.employee_id))
    out = pd.DataFrame({"employee_id": ids}).set_index("employee_id")
    out = out.join(latest).join(counts).join(load).join(last_promo)
    out["survey_status"] = out["recent_engagement"].isna().map({True: "MISSING", False: "AVAILABLE"})
    out["engagement_reason"] = out["recent_engagement"].apply(
        lambda x: "INSUFFICIENT_DATA" if pd.isna(x) else ("LOW_RECENT_ENGAGEMENT" if x < 55 else "NO_LOW_ENGAGEMENT_SIGNAL")
    )
    out["workload_reason"] = out["avg_recent_weekly_hours"].apply(
        lambda x: "INSUFFICIENT_DATA" if pd.isna(x) else ("HIGH_WORKLOAD_REVIEW" if x >= 58 else "NO_HIGH_WORKLOAD_SIGNAL")
    )
    out["supportive_priority_score"] = (
        (out["recent_engagement"].apply(lambda x: 20 if pd.notna(x) and x < 55 else 0)) +
        (out["avg_recent_weekly_hours"].apply(lambda x: 20 if pd.notna(x) and x >= 58 else 0)) +
        (out["recent_engagement"].isna().astype(int) * 0)
    ).clip(0, 40)
    out["recommendation"] = out.apply(
        lambda r: "DATA_COMPLETION_REVIEW" if r["survey_status"] == "MISSING"
        else ("SUPPORTIVE_HUMAN_CHECK_IN" if r["supportive_priority_score"] > 0 else "NO_AUTOMATED_ACTION"), axis=1
    )
    out["human_review_required"] = out["recommendation"].isin(["DATA_COMPLETION_REVIEW", "SUPPORTIVE_HUMAN_CHECK_IN"])
    return out.reset_index()

def assert_no_outcome_leakage(feature_columns):
    leaked = FORBIDDEN_FEATURE_COLUMNS.intersection(set(feature_columns))
    if leaked:
        raise ValueError(f"Outcome leakage detected in feature columns: {sorted(leaked)}")
