"""Command-line interface for offline contribution audits."""

from __future__ import annotations

import argparse
from pathlib import Path

from contrib_audit.config import AuditConfig, BUILTIN_PROFILES, ConfigError, get_profile, load_config, write_starter_config
from contrib_audit.models import AuditReport
from contrib_audit.report import compute_verdict, render_github_actions, render_json, render_markdown, render_text
from contrib_audit.rules import RULES, RuleContext


def find_repo_root(start: Path) -> Path | None:
    """Find an enclosing repository configuration or legacy template."""
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".contrib-audit.json").is_file() or (candidate / "template" / "README.md").is_file():
            return candidate
    return None


def _default_config(repo_root: Path) -> AuditConfig:
    config_path = repo_root / ".contrib-audit.json"
    if config_path.is_file():
        return load_config(str(config_path))
    if (repo_root / "template" / "README.md").is_file():
        return get_profile("legacy-template")
    return get_profile("generic")


def audit(project_path: Path, repo_root: Path | None = None, config: AuditConfig | None = None, check_osv: bool = False) -> AuditReport:
    """Run every deterministic rule and calculate the final verdict."""
    project = project_path.resolve()
    root = repo_root.resolve() if repo_root else find_repo_root(project)
    if root is None:
        report = AuditReport(str(project), "", [])
        report.findings.append(__import__("contrib_audit.models", fromlist=["Finding"]).Finding("R01", "error", str(project), None, "repository template/README.md was not found", "Pass --repo-root or run inside a repository using this contribution template."))
        report.verdict = compute_verdict(report)
        return report
    context = RuleContext(project, root, config or _default_config(root), check_osv)
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
    check.add_argument("--format", choices=("text", "markdown", "json", "github"), default="text")
    check.add_argument("--config", help="Built-in profile name or path to a JSON configuration file.")
    check.add_argument("--osv", action="store_true", help="Query OSV for pinned PyPI dependencies; disabled by default.")
    init = subparsers.add_parser("init", help="Write a starter .contrib-audit.json without overwriting one.")
    init.add_argument("path", type=Path, nargs="?", default=Path(".contrib-audit.json"))
    init.add_argument("--profile", choices=tuple(BUILTIN_PROFILES), default="generic")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            write_starter_config(args.path, args.profile)
            print(f"Wrote {args.path} using the {args.profile} profile.")
            return 0
        config = load_config(args.config) if args.config else None
    except ConfigError as error:
        build_parser().error(str(error))
    report = audit(args.path, args.repo_root, config, args.osv)
    renderers = {"text": render_text, "markdown": render_markdown, "json": render_json, "github": render_github_actions}
    print(renderers[args.format](report))
    return 0 if report.verdict in {"READY", "APPROVE_WITH_NITS"} else 1
