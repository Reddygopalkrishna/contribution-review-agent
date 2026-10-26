# Seeded-defect evaluation

Run the fully offline test harness with:

```bash
python3 -m pytest tests/test_evaluation.py -v
```

Or print the evaluation metrics table directly:

```bash
python3 -c "from contrib_audit.evaluation import run_seeded_evaluation, render_evaluation; print(render_evaluation(run_seeded_evaluation()))"
```

It creates a fresh known-clean sample for each scenario, injects exactly one defect, and never executes sample code. The fake credential is assembled only at runtime inside a temporary directory. The tracked `.env` scenario checks Git index metadata only; its contents are not read by the auditor.

Results from the local run on 2026-10-25:

| Rule | Seeded defect | TP | FP | FN | Precision | Recall |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| R01 | wrong folder | 1 | 0 | 0 | 1.00 | 1.00 |
| R05 | missing README section | 1 | 0 | 0 | 1.00 | 1.00 |
| R06 | undocumented environment variable | 1 | 0 | 0 | 1.00 | 1.00 |
| R07 | fake credential | 1 | 0 | 0 | 1.00 | 1.00 |
| R08 | tracked `.env` | 1 | 0 | 0 | 1.00 | 1.00 |

These measurements are a seeded regression signal, not a claim of real-world secret-scanner accuracy.
