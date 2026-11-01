from __future__ import annotations
from pathlib import Path
import pandas as pd

def validate_dataset(data_dir: str | Path) -> list[str]:
    raw = Path(data_dir) / "raw"
    errors = []
    required = ["employees.csv","roles.csv","teams.csv","tenure_snapshots.csv",
                "engagement_surveys.csv","workload_snapshots.csv","compensation_snapshots.csv",
                "promotion_history.csv","attrition_outcomes.csv","interventions.csv"]
    missing = [f for f in required if not (raw/f).exists()]
    if missing:
        return [f"Missing required files: {missing}"]
    t = {f[:-4]: pd.read_csv(raw/f) for f in required}
    def unique(table, key):
        if t[table][key].duplicated().any():
            errors.append(f"Duplicate primary key: {table}.{key}")
    unique("employees","employee_id")
    unique("roles","role_id")
    unique("teams","team_id")
    unique("tenure_snapshots","snapshot_id")
    unique("engagement_surveys","survey_id")
    unique("workload_snapshots","workload_snapshot_id")
    unique("compensation_snapshots","compensation_snapshot_id")
    unique("promotion_history","promotion_id")
    unique("attrition_outcomes","outcome_id")
    unique("interventions","intervention_id")
    employee_ids = set(t["employees"].employee_id)
    role_ids, team_ids = set(t["roles"].role_id), set(t["teams"].team_id)
    for table in ["tenure_snapshots","engagement_surveys","workload_snapshots","compensation_snapshots","promotion_history","attrition_outcomes","interventions"]:
        bad = set(t[table].employee_id) - employee_ids
        if bad: errors.append(f"Invalid employee FK in {table}: {len(bad)}")
    if not set(t["employees"].role_id).issubset(role_ids): errors.append("Invalid employee role FK")
    if not set(t["employees"].team_id).issubset(team_ids): errors.append("Invalid employee team FK")
    if not t["engagement_surveys"].engagement_score.dropna().between(0,100).all():
        errors.append("Engagement score outside 0-100")
    if not t["workload_snapshots"].weekly_hours.dropna().between(0,100).all():
        errors.append("Weekly hours outside 0-100")
    if not set(t["attrition_outcomes"].voluntary_attrition.unique()).issubset({0,1}):
        errors.append("Attrition label must be 0 or 1")
    # Date ordering and horizon reconciliation.
    outcomes = t["attrition_outcomes"].copy()
    td = pd.to_datetime(outcomes.termination_date, errors="coerce")
    start, end = pd.to_datetime(outcomes.label_horizon_start), pd.to_datetime(outcomes.label_horizon_end)
    invalid_yes = (outcomes.voluntary_attrition.eq(1) & (td.isna() | (td < start) | (td > end)))
    invalid_no = (outcomes.voluntary_attrition.eq(0) & td.notna())
    if invalid_yes.any() or invalid_no.any(): errors.append("Attrition label / termination date mismatch")
    if (pd.to_datetime(t["tenure_snapshots"].snapshot_date) < pd.to_datetime(t["employees"].set_index("employee_id").loc[t["tenure_snapshots"].employee_id].hire_date).reset_index(drop=True)).any():
        errors.append("Tenure snapshot precedes hire date")
    return errors
