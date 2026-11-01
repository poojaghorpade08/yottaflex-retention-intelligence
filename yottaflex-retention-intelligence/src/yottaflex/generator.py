from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from datetime import date
import numpy as np
import pandas as pd
from .config import SEED, DEFAULT_EMPLOYEES, START_MONTH, END_MONTH, PREDICTION_CUTOFF, OUTCOME_HORIZON_END

ROLES = [
    ("ROLE-001", "Software Engineer", "Technology", 1),
    ("ROLE-002", "Data Analyst", "Analytics", 2),
    ("ROLE-003", "Product Manager", "Product", 3),
    ("ROLE-004", "Customer Support Specialist", "Operations", 4),
    ("ROLE-005", "HR Partner", "People", 5),
    ("ROLE-006", "Finance Analyst", "Finance", 6),
    ("ROLE-007", "Engineering Manager", "Technology", 1),
]
TEAMS = [
    ("TEAM-001", "Platform", "Technology"),
    ("TEAM-002", "Data", "Analytics"),
    ("TEAM-003", "Product", "Product"),
    ("TEAM-004", "Customer Operations", "Operations"),
    ("TEAM-005", "People Operations", "People"),
    ("TEAM-006", "Finance Operations", "Finance"),
]
MONTHS = pd.date_range(START_MONTH, END_MONTH, freq="MS")

def _write(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def generate_dataset(output_dir: str | Path, employees: int = DEFAULT_EMPLOYEES, seed: int = SEED):
    """Generate reproducible synthetic workforce data. All generated people are fictional."""
    out = Path(output_dir)
    raw = out / "raw"
    gt_dir = out / "ground_truth"
    raw.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    roles = pd.DataFrame(ROLES, columns=["role_id", "role_name", "function", "role_family_id"])
    teams = pd.DataFrame(TEAMS, columns=["team_id", "team_name", "function"])
    n = int(employees)
    employee_ids = [f"EMP-{i:06d}" for i in range(1, n + 1)]

    role_idx = rng.integers(0, len(roles), n)
    team_idx = np.array([next((j for j, t in enumerate(TEAMS) if t[2] == ROLES[r][2]), 0) for r in role_idx])
    hire_days_ago = rng.integers(730, 3650, n)
    today = pd.Timestamp("2026-10-01")
    hire_dates = (today - pd.to_timedelta(hire_days_ago, unit="D")).date.astype(str)
    employees_df = pd.DataFrame({
        "employee_id": employee_ids,
        "role_id": roles.iloc[role_idx]["role_id"].to_numpy(),
        "team_id": teams.iloc[team_idx]["team_id"].to_numpy(),
        "hire_date": hire_dates,
        "employment_status": "ACTIVE",
        "work_location_type": rng.choice(["REMOTE", "HYBRID", "ONSITE"], n, p=[0.25, 0.5, 0.25]),
        "manager_employee_id": [None] * n,
    })
    # Assign manager references from a small pool, excluding self; valid optional FK.
    manager_pool = employee_ids[:max(1, min(100, n))]
    managers = []
    for eid in employee_ids:
        candidate = manager_pool[int(rng.integers(0, len(manager_pool)))]
        managers.append(None if candidate == eid else candidate)
    employees_df["manager_employee_id"] = managers

    tenure_rows, workload_rows, survey_rows, comp_rows, promo_rows = [], [], [], [], []
    survey_counter = 1
    snapshot_index = {m.strftime("%Y-%m"): m for m in MONTHS}
    employee_latent = rng.normal(0, 1, n)
    # A stable latent propensity is used only to simulate synthetic labels, not exposed as a feature.
    employee_exit_bias = rng.normal(0, 0.35, n)

    for i, eid in enumerate(employee_ids):
        hire = pd.Timestamp(str(hire_dates[i]))
        current_team = employees_df.iloc[i]["team_id"]
        current_role = employees_df.iloc[i]["role_id"]
        base_work = float(np.clip(rng.normal(40, 5), 28, 52))
        engagement_base = float(np.clip(rng.normal(72, 11), 35, 98))
        last_promo = hire + pd.Timedelta(days=int(rng.integers(180, 1500)))
        if last_promo > pd.Timestamp(PREDICTION_CUTOFF):
            last_promo = pd.NaT
        for mi, month in enumerate(MONTHS):
            months_since_hire = max(0, (month.year - hire.year) * 12 + month.month - hire.month)
            # Occasional internal transfer, retained as effective-dated team/role changes in snapshots.
            if mi in (8, 16) and rng.random() < 0.035:
                possible = [t[0] for t in TEAMS if t[0] != current_team]
                current_team = str(rng.choice(possible))
            workload = float(np.clip(base_work + rng.normal(0, 5) + (5 if rng.random() < 0.08 else 0), 20, 70))
            # Benign high workload periods are deliberately included.
            if rng.random() < 0.04:
                workload = float(rng.uniform(58, 68))
            engagement = float(np.clip(engagement_base - max(0, workload - 45) * 0.35 + rng.normal(0, 5), 5, 100))
            # Create a small set of longitudinal trajectories with gradual changes.
            engagement = float(np.clip(engagement - max(0, mi - 12) * max(0, employee_latent[i]) * 0.25, 0, 100))
            snap_id = f"SNAP-{eid}-{month.year}M{month.month:02d}"
            tenure_rows.append({
                "snapshot_id": snap_id, "employee_id": eid, "snapshot_date": month.date().isoformat(),
                "tenure_months": months_since_hire, "role_id": current_role, "team_id": current_team,
                "employment_state": "ACTIVE"
            })
            workload_rows.append({
                "workload_snapshot_id": f"LOAD-{eid}-{month.year}M{month.month:02d}",
                "employee_id": eid, "snapshot_date": month.date().isoformat(),
                "weekly_hours": round(workload, 1), "overtime_hours": round(max(0, workload - 40), 1),
                "workload_band": "HIGH" if workload >= 55 else ("MODERATE" if workload >= 45 else "NORMAL")
            })
            # Two survey opportunities per quarter-ish; missingness is represented by absent survey rows.
            if mi % 3 == 2 and rng.random() >= 0.18:
                score = int(np.clip(round(engagement + rng.normal(0, 4)), 0, 100))
                survey_rows.append({
                    "survey_id": f"SURV-2026-{survey_counter:06d}" if month.year == 2026 else f"SURV-{month.year}-{survey_counter:06d}",
                    "employee_id": eid, "survey_date": (month + pd.Timedelta(days=10)).date().isoformat(),
                    "engagement_score": score, "response_status": "COMPLETED", "scale_min": 0, "scale_max": 100
                })
                survey_counter += 1
            # Compensation band is a dated snapshot, not an individual salary.
            band = ["B1", "B2", "B3", "B4"][min(3, max(0, int(months_since_hire // 24)))]
            comp_rows.append({
                "compensation_snapshot_id": f"COMP-{eid}-{month.year}M{month.month:02d}",
                "employee_id": eid, "effective_date": month.date().isoformat(),
                "compensation_band_id": band
            })
            if mi > 0 and mi % 12 == 0 and rng.random() < 0.035:
                promo_date = (month + pd.Timedelta(days=5)).date().isoformat()
                promo_rows.append({
                    "promotion_id": f"PROM-{eid}-{len(promo_rows)+1:04d}",
                    "employee_id": eid, "effective_date": promo_date,
                    "from_role_id": current_role, "to_role_id": current_role,
                    "promotion_type": "LEVEL_CHANGE"
                })

    tenure = pd.DataFrame(tenure_rows)
    workload = pd.DataFrame(workload_rows)
    surveys = pd.DataFrame(survey_rows, columns=["survey_id","employee_id","survey_date","engagement_score","response_status","scale_min","scale_max"])
    comp = pd.DataFrame(comp_rows)
    promotions = pd.DataFrame(promo_rows, columns=["promotion_id","employee_id","effective_date","from_role_id","to_role_id","promotion_type"])

    # Derive outcomes from pre-outcome signals. These labels are for synthetic evaluation only.
    cutoff = pd.Timestamp(PREDICTION_CUTOFF)
    horizon_end = pd.Timestamp(OUTCOME_HORIZON_END)
    pre_work = workload[workload.snapshot_date <= PREDICTION_CUTOFF].groupby("employee_id").tail(3).groupby("employee_id").weekly_hours.mean()
    pre_survey = surveys[pd.to_datetime(surveys.survey_date) <= cutoff].sort_values("survey_date").groupby("employee_id").tail(2).groupby("employee_id").engagement_score.mean()
    outcome_rows = []
    for i, eid in enumerate(employee_ids):
        w = float(pre_work.get(eid, 40))
        s = float(pre_survey.get(eid, 70))
        # A deterministic rule-based hazard score, then seeded draw; only pre-cutoff values used.
        risk_logit = -3.35 + max(0, w - 42) * 0.055 + max(0, 65 - s) * 0.035 + employee_exit_bias[i]
        p = 1 / (1 + math.exp(-risk_logit))
        left = bool(rng.random() < p)
        exit_date = None
        if left:
            exit_date = (cutoff + pd.Timedelta(days=int(rng.integers(1, 31)))).date().isoformat()
        outcome_rows.append({
            "outcome_id": f"OUT-{eid}-2026", "employee_id": eid,
            "label_horizon_start": (cutoff + pd.Timedelta(days=1)).date().isoformat(),
            "label_horizon_end": horizon_end.date().isoformat(),
            "voluntary_attrition": int(left), "termination_date": exit_date,
            "outcome_type": "VOLUNTARY" if left else "NO_VOLUNTARY_EXIT"
        })
    outcomes = pd.DataFrame(outcome_rows)

    # Supportive interventions are generated from transparent pre-cutoff rules.
    intervention_rows = []
    latest_survey = surveys[pd.to_datetime(surveys.survey_date) <= cutoff].sort_values("survey_date").groupby("employee_id").tail(1).set_index("employee_id")
    latest_load = workload[workload.snapshot_date <= PREDICTION_CUTOFF].sort_values("snapshot_date").groupby("employee_id").tail(1).set_index("employee_id")
    for i, eid in enumerate(employee_ids):
        srow = latest_survey.loc[eid] if eid in latest_survey.index else None
        lrow = latest_load.loc[eid] if eid in latest_load.index else None
        reasons = []
        if srow is not None and int(srow.engagement_score) < 55:
            reasons.append("LOW_RECENT_ENGAGEMENT")
        if lrow is not None and float(lrow.weekly_hours) >= 58:
            reasons.append("SUSTAINED_HIGH_WORKLOAD_SIGNAL")
        if reasons:
            intervention_rows.append({
                "intervention_id": f"INT-2026-{len(intervention_rows)+1:06d}",
                "employee_id": eid, "created_date": "2026-10-02",
                "intervention_type": "SUPPORTIVE_CHECK_IN",
                "trigger_reasons": "|".join(reasons),
                "status": "SUGGESTED", "human_review_status": "PENDING",
                "simulated_followup_outcome": str(rng.choice(["NO_CHANGE_RECORDED", "SUPPORT_PLAN_AGREED", "FOLLOW_UP_REQUIRED"], p=[0.35,0.4,0.25]))
            })
    interventions = pd.DataFrame(intervention_rows, columns=[
        "intervention_id","employee_id","created_date","intervention_type","trigger_reasons","status","human_review_status","simulated_followup_outcome"
    ])

    # Isolated labelled QA/anomaly cases; not joined to baseline features.
    gt = pd.DataFrame([
        {"case_id":"EDGE-001","issue_type":"FUTURE_FEATURE_LEAKAGE","record_reference":"OUTCOME_LABEL_IN_FEATURES","ground_truth_label":"INVALID_FEATURE","expected_handling":"Reject any post-cutoff outcome or termination field from feature matrix."},
        {"case_id":"EDGE-002","issue_type":"MISSING_SURVEY_AS_NEGATIVE","record_reference":"MISSING_SURVEY_EXAMPLE","ground_truth_label":"MISSING_NOT_NEGATIVE","expected_handling":"Represent missing survey as unknown; do not impute a zero or negative engagement score."},
        {"case_id":"EDGE-003","issue_type":"OUTCOME_DATE_LABEL_MISMATCH","record_reference":"OUTCOME_DATE_AFTER_HORIZON","ground_truth_label":"INVALID_OUTCOME_RECORD","expected_handling":"Flag termination date outside the documented label horizon or inconsistent with outcome_type."},
        {"case_id":"EDGE-004","issue_type":"UNEXPLAINED_SCORE_NO_HUMAN_REVIEW","record_reference":"INDIVIDUAL_SCORE_WITHOUT_REVIEW","ground_truth_label":"REQUIRES_HUMAN_REVIEW","expected_handling":"Do not use an individual score for action without reason codes, context and human review."},
    ])

    tables = {
        "roles.csv": roles, "teams.csv": teams, "employees.csv": employees_df,
        "tenure_snapshots.csv": tenure, "engagement_surveys.csv": surveys,
        "workload_snapshots.csv": workload, "compensation_snapshots.csv": comp,
        "promotion_history.csv": promotions, "attrition_outcomes.csv": outcomes,
        "interventions.csv": interventions
    }
    for name, df in tables.items():
        _write(df, raw / name)
    _write(gt, gt_dir / "ground_truth.csv")

    # Reproducibility manifest (checksums refer to CSV payloads).
    manifest = {
        "project": "YottaFlex Retention Intelligence",
        "seed": int(seed), "employees_requested": n,
        "observation_months": [m.strftime("%Y-%m-%d") for m in MONTHS],
        "prediction_cutoff": PREDICTION_CUTOFF,
        "outcome_horizon_end": OUTCOME_HORIZON_END,
        "generator_version": "1.0.0",
        "row_counts": {name: int(len(df)) for name, df in tables.items()},
        "checksums_sha256": {name: _sha256(raw / name) for name in tables},
        "ground_truth_rows": int(len(gt)),
    }
    (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
