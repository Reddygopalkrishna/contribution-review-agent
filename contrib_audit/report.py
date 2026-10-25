"""Verdict calculation and human/machine-readable report renderers."""

from __future__ import annotations

import json
from collections import Counter

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
