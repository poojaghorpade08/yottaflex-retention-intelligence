# Data dictionary

All data is fictional. Dates use ISO-8601 `YYYY-MM-DD`. IDs are immutable strings.

| Entity / file | Field | Type | Req. | Allowed values / validation | Meaning |
|---|---|---:|---|---|---|
| Employee | employee_id | string | Yes | Unique `EMP-000001` format | Primary key |
| Employee | role_id | string | Yes | FK to Role | Current role |
| Employee | team_id | string | Yes | FK to Team | Current team |
| Employee | hire_date | date | Yes | <= observation end | Hire date |
| Employee | employment_status | enum | Yes | ACTIVE, INACTIVE | Current state |
| Employee | work_location_type | enum | Yes | REMOTE, HYBRID, ONSITE | Work arrangement; not used as a risk proxy |
| Employee | manager_employee_id | string | No | Nullable employee FK, not self | Manager reference |
| Role | role_id | string | Yes | Unique ROLE-NNN | Primary key |
| Role | role_name | string | Yes | Non-empty | Role label |
| Role | function | string | Yes | Non-empty | Functional group |
| Team | team_id | string | Yes | Unique TEAM-NNN | Primary key |
| Team | team_name | string | Yes | Non-empty | Team label |
| TenureSnapshot | snapshot_id | string | Yes | Unique SNAP-EMP... | Primary key |
| TenureSnapshot | employee_id | string | Yes | FK Employee | Employee |
| TenureSnapshot | snapshot_date | date | Yes | Monthly observation date | Effective date |
| TenureSnapshot | tenure_months | integer | Yes | >=0; derived from hire date | Tenure |
| TenureSnapshot | role_id/team_id | string | Yes | FK Role/Team | Effective role/team |
| EngagementSurvey | survey_id | string | Yes | Unique SURV-year-counter | Primary key |
| EngagementSurvey | employee_id | string | Yes | FK Employee | Employee |
| EngagementSurvey | survey_date | date | Yes | Within observation window | Survey date |
| EngagementSurvey | engagement_score | integer | Yes | 0..100 | Score; only completed rows exist |
| EngagementSurvey | response_status | enum | Yes | COMPLETED | Response state |
| WorkloadSnapshot | workload_snapshot_id | string | Yes | Unique LOAD-EMP-date | Primary key |
| WorkloadSnapshot | employee_id | string | Yes | FK Employee | Employee |
| WorkloadSnapshot | snapshot_date | date | Yes | Monthly | Snapshot date |
| WorkloadSnapshot | weekly_hours | decimal | Yes | 0..100 hours/week | Weekly hours |
| WorkloadSnapshot | overtime_hours | decimal | Yes | >=0 hours/week | max(weekly_hours-40, 0) |
| WorkloadSnapshot | workload_band | enum | Yes | NORMAL, MODERATE, HIGH | Derived band |
| CompensationSnapshot | compensation_snapshot_id | string | Yes | Unique COMP-EMP-date | Primary key |
| CompensationSnapshot | employee_id | string | Yes | FK Employee | Employee |
| CompensationSnapshot | effective_date | date | Yes | Monthly effective date | Effective date |
| CompensationSnapshot | compensation_band_id | enum | Yes | B1..B4 | Non-monetary band |
| PromotionHistory | promotion_id | string | Yes | Unique PROM-EMP-counter | Primary key |
| PromotionHistory | employee_id | string | Yes | FK Employee | Employee |
| PromotionHistory | effective_date | date | Yes | Within observation window | Promotion date |
| PromotionHistory | from_role_id/to_role_id | string | Yes | FK Role | Role transition |
| AttritionOutcome | outcome_id | string | Yes | Unique OUT-EMP-2026 | Primary key |
| AttritionOutcome | employee_id | string | Yes | FK Employee; one per horizon | Employee |
| AttritionOutcome | voluntary_attrition | integer | Yes | 0 or 1 | Ground-truth label |
| AttritionOutcome | termination_date | date | No | Required for label=1, absent for 0 | Outcome date |
| Intervention | intervention_id | string | Yes | Unique INT-2026-counter | Primary key |
| Intervention | employee_id | string | Yes | FK Employee | Employee |
| Intervention | created_date | date | Yes | After feature cutoff | Event date |
| Intervention | trigger_reasons | string | Yes | Pipe-separated reason codes | Explainability |
| Intervention | human_review_status | enum | Yes | PENDING in generated queue | Human oversight |
| Intervention | simulated_followup_outcome | enum | Yes | NO_CHANGE_RECORDED, SUPPORT_PLAN_AGREED, FOLLOW_UP_REQUIRED | Simulated outcome |
