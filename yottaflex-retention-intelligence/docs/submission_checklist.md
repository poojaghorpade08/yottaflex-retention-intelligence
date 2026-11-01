# Submission checklist

- [ ] Confirm all generated data is synthetic.
- [ ] Review README, data dictionary and architecture.
- [ ] Run `python scripts/validate_data.py`.
- [ ] Run `pytest`.
- [ ] Run `streamlit run dashboard/app.py`.
- [ ] Regenerate twice with identical seed and compare CSV SHA-256 values.
- [ ] Ensure `data/ground_truth/ground_truth.csv` is not used as a feature.
- [ ] Ensure outcome table is never joined into pre-outcome features.
- [ ] Add a short demo video or screenshots if the challenge portal permits.
- [ ] Upload repository or ZIP according to challenge submission instructions.
