# YottaFlex Retention Intelligence

A synthetic, explainable workforce-retention analytics project for the YottaFlex.ai Associate AI Forward Deployed Engineer challenge.

> **Responsible-use boundary:** This project produces supportive review signals for HR/manager conversations. It is not an automated employment decision system. Do not use the scores to hire, fire, promote, discipline, or rank employees. All records are synthetic.

## What's included

- 10,000 synthetic employees with 24 monthly periods (2024-11 through 2026-10).
- Master data: employees, roles, teams.
- Longitudinal records: tenure, engagement surveys, workload, compensation bands, promotion history.
- Future-horizon voluntary attrition outcomes, kept separate from pre-outcome features.
- Supportive interventions with simulated follow-up outcomes.
- Four explicitly labelled data-quality / governance challenge cases.
- SQL schema, data dictionary, validation, reproducibility manifest, dashboard and tests.
- Generated CSV files are included in `data/` so the repository can be inspected without running code.

## Quick start

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python scripts/validate_data.py
streamlit run dashboard/app.py
```

Regenerate the data (this overwrites generated CSV files):

```bash
python scripts/generate_data.py --employees 10000 --seed 20261022
python scripts/validate_data.py
```

For a fast development dataset:

```bash
python scripts/generate_data.py --employees 500 --seed 20261022
```

## Data window and temporal design

- Observation window: 2024-11-01 through 2026-10-01 (24 monthly snapshots).
- Prediction cutoff: 2026-09-01.
- Outcome horizon: voluntary exits in the 30 days after the cutoff (through 2026-10-01).
- Features are constructed only from records dated on or before the cutoff.
- `attrition_outcomes.csv` is a separate label table and must never be joined into model features.
- `ground_truth/ground_truth.csv` is a separate QA file; never use it as an input feature.

The synthetic generator intentionally creates rule-based outcomes from pre-cutoff signals plus a small seeded stochastic component. Labels are therefore reproducible and documented, not independently random assignments. They are not intended to represent real-world causal relationships.

## Tables and relationships

See `docs/architecture.md`, `docs/data_dictionary.md`, and `database/schema.sql`.

## Key business logic

The supportive priority score is a transparent 0-100 signal based on:
- recent engagement trend (if enough survey responses exist),
- sustained workload pressure,
- time since last promotion (where available),
- missingness as an explicit `unknown` / `needs_data` condition, never as a negative score.

The dashboard shows aggregated patterns and a review queue. Individual-level rows are only illustrative review prompts and require human context and review. A high workload period alone is not enough to trigger a recommendation.

## Edge cases

`data/ground_truth/ground_truth.csv` contains labelled challenge cases:
1. `FUTURE_FEATURE_LEAKAGE`
2. `MISSING_SURVEY_AS_NEGATIVE`
3. `OUTCOME_DATE_LABEL_MISMATCH`
4. `UNEXPLAINED_SCORE_NO_HUMAN_REVIEW`

These cases are isolated in a dedicated issue table. They do not silently corrupt the baseline employee records. `issue_type` and `ground_truth_label` document each case.

## Reproducibility

- Seed: `20261022`
- Generator: `src/yottaflex/generator.py`
- `data/source_manifest.json` records configuration, row counts, SHA-256 checksums and generation timestamp.
- Run the generator twice with the same seed/configuration and compare checksums. The manifest timestamp itself changes, so compare the per-file checksums rather than the entire manifest.

## Project layout

```text
data/                 generated CSV data and separate ground truth
database/             relational SQL schema
docs/                 architecture, dictionary, validation notes
src/yottaflex/        generator, analytics and validation modules
dashboard/            Streamlit application
scripts/              CLI entry points
tests/                automated tests
```

## Limitations

- All data is synthetic and must not be interpreted as real employee evidence.
- Attrition labels and intervention outcomes are simulated.
- No sensitive personal attributes or protected-class proxies are generated.
- The score is a transparent prioritization aid, not a validated prediction of an individual's intent.
- Before any real-world deployment, obtain legal, privacy, security, HR, and employee-representation review; validate fairness and usefulness with appropriate governance.
