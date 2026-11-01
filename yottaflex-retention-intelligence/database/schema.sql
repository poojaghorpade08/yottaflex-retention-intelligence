PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS roles (
  role_id TEXT PRIMARY KEY,
  role_name TEXT NOT NULL,
  function TEXT NOT NULL,
  role_family_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS teams (
  team_id TEXT PRIMARY KEY,
  team_name TEXT NOT NULL,
  function TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS employees (
  employee_id TEXT PRIMARY KEY,
  role_id TEXT NOT NULL REFERENCES roles(role_id),
  team_id TEXT NOT NULL REFERENCES teams(team_id),
  hire_date TEXT NOT NULL,
  employment_status TEXT NOT NULL CHECK (employment_status IN ('ACTIVE','INACTIVE')),
  work_location_type TEXT NOT NULL CHECK (work_location_type IN ('REMOTE','HYBRID','ONSITE')),
  manager_employee_id TEXT NULL REFERENCES employees(employee_id)
);
CREATE TABLE IF NOT EXISTS tenure_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES employees(employee_id),
  snapshot_date TEXT NOT NULL,
  tenure_months INTEGER NOT NULL CHECK (tenure_months >= 0),
  role_id TEXT NOT NULL REFERENCES roles(role_id),
  team_id TEXT NOT NULL REFERENCES teams(team_id),
  employment_state TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS engagement_surveys (
  survey_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES employees(employee_id),
  survey_date TEXT NOT NULL,
  engagement_score INTEGER NOT NULL CHECK (engagement_score BETWEEN 0 AND 100),
  response_status TEXT NOT NULL CHECK (response_status IN ('COMPLETED')),
  scale_min INTEGER NOT NULL DEFAULT 0,
  scale_max INTEGER NOT NULL DEFAULT 100
);
CREATE TABLE IF NOT EXISTS workload_snapshots (
  workload_snapshot_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES employees(employee_id),
  snapshot_date TEXT NOT NULL,
  weekly_hours REAL NOT NULL CHECK (weekly_hours BETWEEN 0 AND 100),
  overtime_hours REAL NOT NULL CHECK (overtime_hours >= 0),
  workload_band TEXT NOT NULL CHECK (workload_band IN ('NORMAL','MODERATE','HIGH'))
);
CREATE TABLE IF NOT EXISTS compensation_snapshots (
  compensation_snapshot_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES employees(employee_id),
  effective_date TEXT NOT NULL,
  compensation_band_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS promotion_history (
  promotion_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES employees(employee_id),
  effective_date TEXT NOT NULL,
  from_role_id TEXT NOT NULL REFERENCES roles(role_id),
  to_role_id TEXT NOT NULL REFERENCES roles(role_id),
  promotion_type TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attrition_outcomes (
  outcome_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES employees(employee_id),
  label_horizon_start TEXT NOT NULL,
  label_horizon_end TEXT NOT NULL,
  voluntary_attrition INTEGER NOT NULL CHECK (voluntary_attrition IN (0,1)),
  termination_date TEXT NULL,
  outcome_type TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interventions (
  intervention_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES employees(employee_id),
  created_date TEXT NOT NULL,
  intervention_type TEXT NOT NULL,
  trigger_reasons TEXT NOT NULL,
  status TEXT NOT NULL,
  human_review_status TEXT NOT NULL,
  simulated_followup_outcome TEXT NOT NULL
);
