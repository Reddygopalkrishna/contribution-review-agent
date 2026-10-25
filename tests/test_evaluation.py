from contrib_audit.evaluation import render_evaluation, run_seeded_evaluation


def test_seeded_evaluation_detects_each_injected_defect():
    metrics = run_seeded_evaluation()
    assert {metric.rule_id for metric in metrics} == {"R01", "R05", "R06", "R07", "R08"}
    assert all(metric.precision == 1 and metric.recall == 1 for metric in metrics)
    assert "| R07 | 1 | 0 | 0 | 1.00 | 1.00 |" in render_evaluation(metrics)
