"""Offline seeded-defect evaluation for deterministic rules."""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from contrib_audit.rules.readme import _FALLBACK_HEADINGS


@dataclass(frozen=True)
class EvaluationMetric:
    rule_id: str
    true_positives: int
    false_positives: int
    false_negatives: int

    @property
    def precision(self) -> float:
        denominator = self.true_positives + self.false_positives
        return self.true_positives / denominator if denominator else 0.0

    @property
    def recall(self) -> float:
        denominator = self.true_positives + self.false_negatives
        return self.true_positives / denominator if denominator else 0.0


def _write_clean_sample(root: Path) -> tuple[Path, Path]:
    (root / "template").mkdir()
    (root / "template" / "README.md").write_text("\n".join(f"## {heading}" for heading in _FALLBACK_HEADINGS), encoding="utf-8")
    project = root / "agents" / "sample-agent"
    project.mkdir(parents=True)
    sections = ["# Sample"]
    for heading in _FALLBACK_HEADINGS:
        sections.append(f"## {heading}")
        if heading == "Configuration & Environment Variables":
            sections.extend(["| Variable |", "| --- |", "| `MODEL_NAME` |"])
        elif heading == "Example Output":
            sections.append("Verdict: READY")
        else:
            sections.append("Complete documentation.")
    (project / "README.md").write_text("\n\n".join(sections), encoding="utf-8")
    (project / ".env.example").write_text("MODEL_NAME=local\n", encoding="utf-8")
    (project / ".gitignore").write_text(".env\n.venv/\n", encoding="utf-8")
    (project / "requirements.txt").write_text("\n", encoding="utf-8")
    return root, project


def _scenario(rule_id: str, defect) -> tuple[str, set[str]]:
    from contrib_audit.cli import audit

    with tempfile.TemporaryDirectory() as directory:
        root, project = _write_clean_sample(Path(directory))
        target = defect(root, project)
        actual = {finding.id for finding in audit(target, root).findings}
    return rule_id, actual


def _missing_heading(_: Path, project: Path) -> Path:
    readme = project / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8").replace("## Overview\n\nComplete documentation.\n\n", ""), encoding="utf-8")
    return project


def _undocumented_env(_: Path, project: Path) -> Path:
    with (project / ".env.example").open("a", encoding="utf-8") as handle:
        handle.write("EXTRA_VALUE=placeholder\n")
    return project


def _wrong_folder(root: Path, project: Path) -> Path:
    target = root / "nested" / project.name
    target.parent.mkdir()
    project.rename(target)
    return target


def _fake_secret(_: Path, project: Path) -> Path:
    value = "AI" + "za" + ("x" * 24)
    (project / "leak.txt").write_text(value, encoding="utf-8")
    return project


def _tracked_env(_: Path, project: Path) -> Path:
    env_file = project / ".env"
    env_file.write_text("LOCAL_ONLY=fixture\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    subprocess.run(["git", "add", "-f", ".env"], cwd=project, check=True)
    return project


def run_seeded_evaluation() -> list[EvaluationMetric]:
    """Inject one known defect at a time into fresh, known-clean sample projects."""
    scenarios = (("R05", _missing_heading), ("R06", _undocumented_env), ("R01", _wrong_folder), ("R07", _fake_secret), ("R08", _tracked_env))
    metrics: list[EvaluationMetric] = []
    for expected, defect in scenarios:
        _, actual = _scenario(expected, defect)
        scored = {rule for rule in actual if rule in {"R01", "R05", "R06", "R07", "R08"}}
        metrics.append(EvaluationMetric(expected, int(expected in scored), len(scored - {expected}), int(expected not in scored)))
    return metrics


def render_evaluation(metrics: list[EvaluationMetric]) -> str:
    lines = ["| Rule | TP | FP | FN | Precision | Recall |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for metric in metrics:
        lines.append(f"| {metric.rule_id} | {metric.true_positives} | {metric.false_positives} | {metric.false_negatives} | {metric.precision:.2f} | {metric.recall:.2f} |")
    return "\n".join(lines)
