"""Verdict calculation and human/machine-readable report renderers."""

from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

from contrib_audit.models import AuditReport


def compute_verdict(report: AuditReport) -> str:
    """Return the policy verdict; this intentionally never calls an LLM."""
    if any(finding.id == "R07" and finding.severity == "error" for finding in report.findings):
        return "REJECT"
    if any(finding.severity == "error" for finding in report.findings):
        return "CHANGES_REQUESTED"
    if any(finding.severity == "warning" for finding in report.findings):
        return "APPROVE_WITH_NITS"
    return "READY"


def _location(file: str, line: int | None) -> str:
    return f"{file}:{line}" if line is not None else file


def render_text(report: AuditReport) -> str:
    lines = [f"Verdict: {report.verdict}", f"Project: {report.project_path}"]
    if not report.findings:
        return "\n".join(lines + ["No findings."])
    lines.append("Findings:")
    for finding in report.findings:
        lines.append(f"- [{finding.severity.upper()}] {finding.id} {_location(finding.file, finding.line)} — {finding.evidence}")
        lines.append(f"  Fix: {finding.fix_hint}")
    counts = Counter(finding.severity for finding in report.findings)
    lines.append(f"Summary: {counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} info item(s)")
    return "\n".join(lines)


def render_markdown(report: AuditReport) -> str:
    lines = [f"# Contribution audit: {report.verdict}", "", f"Project: `{report.project_path}`", ""]
    if not report.findings:
        return "\n".join(lines + ["No findings."])
    lines.extend(["| Severity | Rule | Location | Evidence | Fix |", "| --- | --- | --- | --- | --- |"])
    for finding in report.findings:
        safe = lambda value: value.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {finding.severity} | {finding.id} | {safe(_location(finding.file, finding.line))} | {safe(finding.evidence)} | {safe(finding.fix_hint)} |")
    return "\n".join(lines)


def render_json(report: AuditReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def _github_escape(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(":", "%3A").replace(",", "%2C")


def render_github_actions(report: AuditReport) -> str:
    """Write a job summary and return GitHub workflow annotations."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary:
            summary.write(render_markdown(report) + "\n")
    annotations: list[str] = []
    for finding in report.findings:
        if finding.severity not in {"error", "warning"}:
            continue
        level = "error" if finding.severity == "error" else "warning"
        location = ""
        try:
            relative = Path(finding.file).resolve().relative_to(Path.cwd().resolve())
            location = f"file={_github_escape(relative.as_posix())}"
            if finding.line is not None:
                location += f",line={finding.line}"
        except (OSError, ValueError):
            pass
        message = _github_escape(f"{finding.id}: {finding.evidence}. {finding.fix_hint}")
        annotations.append(f"::{level} {location}::{message}")
    return "\n".join(annotations or ["No GitHub workflow annotations."])
