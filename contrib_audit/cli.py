"""Command-line interface for offline contribution audits."""

from __future__ import annotations

import argparse
from pathlib import Path

from contrib_audit.models import AuditReport
from contrib_audit.report import compute_verdict, render_json, render_markdown, render_text
from contrib_audit.rules import RULES, RuleContext


def find_repo_root(start: Path) -> Path | None:
    """Find a GDG-style contribution repository by locating template/README.md."""
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "template" / "README.md").is_file():
            return candidate
    return None


def audit(project_path: Path, repo_root: Path | None = None) -> AuditReport:
    """Run every deterministic rule and calculate the final verdict."""
    project = project_path.resolve()
    root = repo_root.resolve() if repo_root else find_repo_root(project)
    if root is None:
        report = AuditReport(str(project), "", [])
        report.findings.append(__import__("contrib_audit.models", fromlist=["Finding"]).Finding("R01", "error", str(project), None, "repository template/README.md was not found", "Pass --repo-root or run inside a repository using this contribution template."))
        report.verdict = compute_verdict(report)
        return report
    context = RuleContext(project, root)
    findings = [finding for rule in RULES for finding in rule(context)]
    report = AuditReport(str(project), str(root), sorted(findings, key=lambda item: (item.id, item.file, item.line or 0)))
    report.verdict = compute_verdict(report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic auditor for repository contributions.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="Audit one project directory without an API key.")
    check.add_argument("path", type=Path)
    check.add_argument("--repo-root", type=Path)
    check.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = audit(args.path, args.repo_root)
    renderers = {"text": render_text, "markdown": render_markdown, "json": render_json}
    print(renderers[args.format](report))
    return 0 if report.verdict in {"READY", "APPROVE_WITH_NITS"} else 1
