# Architecture and entity relationships

## Entity cardinality

- Role 1:N Employee; each employee has one current role in the master table.
- Team 1:N Employee; each employee has one current team in the master table.
- Employee 1:N TenureSnapshot (monthly history).
- Employee 1:N EngagementSurvey (optional; missing response means no row).
- Employee 1:N WorkloadSnapshot (monthly history).
- Employee 1:N CompensationSnapshot (effective-dated band history).
- Employee 1:N PromotionHistory (zero or many promotion events).
- Employee 1:1 AttritionOutcome for the defined evaluation horizon.
- Employee 1:N Intervention (zero or many supportive check-in events).
- Employee 0:1 Employee (optional self-reference to manager).

## Temporal rules

- Snapshot dates are monthly and fall within the 24-month observation window.
- Survey rows exist only for completed responses; absence is missingness, not a negative value.
- Outcome horizon starts after the feature cutoff. Outcome and termination fields are labels only.
- Interventions are immutable event records with status and review state.
- Team changes are represented by effective team values in each tenure snapshot, preserving history.

## Primary and foreign keys

Every entity has an immutable primary key. Child tables reference `employee_id`; role and team references are validated against parent tables. See `database/schema.sql`.

## Many-to-many relationships

No mandatory many-to-many relationship exists in this starter scope. If employees are assigned to multiple teams concurrently, add an `employee_team_assignments` bridge table with `valid_from` and `valid_to` rather than placing multiple team IDs in a single field.
