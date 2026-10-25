"""Project placement, name, and required-file rules (R01--R04)."""

from __future__ import annotations

import re
from pathlib import Path

from contrib_audit.models import Finding
from contrib_audit.rules import RuleContext

_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
def _finding(rule_id: str, file: Path | str, evidence: str, hint: str) -> Finding:
    return Finding(rule_id, "error", str(file), None, evidence, hint)


def check_structure(context: RuleContext) -> list[Finding]:
    """Check R01--R04 without interpreting project code."""
    project = context.project_path
    findings: list[Finding] = []
    categories = context.config.allowed_parent_folders
    category_ok = (
        project.parent.name in categories and project.parent.parent == context.repo_root
        if categories else project.parent == context.repo_root
    )
    if not category_ok:
        hint = "Place the project at agents/<name>/ or tools/<name>." if categories else "Place the project directly under the repository root."
        evidence = "project is not a direct child of agents/ or tools/" if categories == ("agents", "tools") else "project is not a direct child of the repository root"
        findings.append(
            _finding(
                "R01", project, evidence,
                hint,
            )
        )
    if not _NAME_PATTERN.fullmatch(project.name):
        findings.append(
            _finding("R02", project, project.name, "Use lowercase kebab-case for the directory name.")
        )
    if project.name in context.config.generic_names:
        findings.append(
            _finding("R03", project, project.name, "Choose a specific, descriptive project name.")
        )
    for filename in context.config.required_files:
        if not (project / filename).is_file():
            findings.append(
                _finding("R04", project, f"missing {filename}", f"Add {filename} to the project root.")
            )
    if not any((project / manifest).is_file() for manifest in context.config.manifest_files):
        findings.append(
            _finding("R04", project, "no dependency manifest found", "Add one supported dependency manifest.")
        )
    return findings
