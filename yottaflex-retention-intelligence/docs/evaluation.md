# Evaluation plan

## Temporal evaluation

Use the 2026-09-01 cutoff for features and the subsequent 30-day horizon for labels. Do not randomly split individual monthly rows across train/test because that can leak future information. A future extension should train on earlier cohorts and test on a later time window.

## Suggested metrics

- PR-AUC and ROC-AUC for label discrimination (report prevalence alongside metrics).
- Precision/recall at a review-capacity threshold, not as employment decisions.
- Calibration and Brier score if probabilistic predictions are added.
- Coverage: share of employees with sufficient pre-cutoff observations.
- Missingness rate by table and period.
- Intervention review completion and follow-up status.
- Data quality: PK duplicates, FK violations, invalid dates and label inconsistencies.

## Safety and governance

No sensitive attributes are generated. Avoid using location type or other operational fields as risk proxies. Do not treat score as an individual truth. Human review and contextual conversation are required. Synthetic outcomes are not evidence of real-world predictive validity.
