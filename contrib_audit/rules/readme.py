"""README and environment documentation rules (R05, R06, R10)."""

from __future__ import annotations

import re
from pathlib import Path

from contrib_audit.models import Finding
from contrib_audit.rules import RuleContext

_FALLBACK_HEADINGS = (
    "Overview", "Problem Statement & Intended Users", "Key Features", "Technical Stack",
    "Architecture & Data Flow", "Prerequisites", "Installation & Setup",
    "Configuration & Environment Variables", "How to Run", "Example Input & Output",
    "Example Input", "Example Output", "How to Test", "Known Limitations",
    "Security & Privacy Considerations", "Future Improvements", "License",
)
_PLACEHOLDER_PATTERNS = (
    re.compile(r"\[Project Name\]"),
    re.compile(r"\[One-sentence summary[^\]]*\]"),
    re.compile(r"<project-slug>"),
    re.compile(r"\[(?:Language Runtime|Package manager|Required API keys)[^\]]*\]"),
    re.compile(r"Feature [123]: Brief description"),
    re.compile(r"Provide the exact command\(s\) to run"),
)


def _line_number(text: str, fragment: str) -> int:
    return text[: text.find(fragment)].count("\n") + 1 if fragment in text else 1


def _template_headings(repo_root: Path) -> tuple[str, ...]:
    template = repo_root / "template" / "README.md"
    try:
        text = template.read_text(encoding="utf-8")
    except OSError:
        return _FALLBACK_HEADINGS
    headings = [line.lstrip("#").strip() for line in text.splitlines() if line.startswith("##")]
    return tuple(headings) if headings else _FALLBACK_HEADINGS


def _table_variables(readme: str) -> set[str]:
    in_section = False
    variables: set[str] = set()
    for line in readme.splitlines():
        if line.startswith("## "):
            in_section = line.removeprefix("## ").strip() == "Configuration & Environment Variables"
            continue
        if in_section:
            variables.update(re.findall(r"`([A-Z][A-Z0-9_]*)`", line))
    return variables


def _env_variables(env_example: Path) -> set[str]:
    variables: set[str] = set()
    for line in env_example.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*=", line)
        if match:
            variables.add(match.group(1))
    return variables


def check_readme(context: RuleContext) -> list[Finding]:
    """Check README completeness, placeholders, documented env vars, and examples."""
    readme_path = context.project_path / "README.md"
    env_path = context.project_path / ".env.example"
    if not readme_path.is_file():
        return []  # R04 already gives the precise missing-file finding.
    text = readme_path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []
    headings = {line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")}
    missing = [heading for heading in _template_headings(context.repo_root) if heading not in headings]
    if missing:
        findings.append(Finding("R05", "error", str(readme_path), None, ", ".join(missing), "Add every section from template/README.md."))
    for pattern in _PLACEHOLDER_PATTERNS:
        match = pattern.search(text)
        if match:
            findings.append(Finding("R05", "error", str(readme_path), _line_number(text, match.group()), match.group(), "Replace this template placeholder with project-specific text."))
    if env_path.is_file():
        documented, declared = _table_variables(text), _env_variables(env_path)
        absent_from_readme = sorted(declared - documented)
        absent_from_env = sorted(documented - declared)
        if absent_from_readme or absent_from_env:
            evidence = "; ".join(
                part for part in (
                    f"not documented: {', '.join(absent_from_readme)}" if absent_from_readme else "",
                    f"not declared: {', '.join(absent_from_env)}" if absent_from_env else "",
                ) if part
            )
            findings.append(Finding("R06", "error", str(readme_path), None, evidence, "Keep .env.example and the configuration table in sync."))
    example_marker = "### Example Output"
    if example_marker not in text or "Analysis completed:" in text:
        findings.append(Finding("R10", "warning", str(readme_path), None, "template example output or no project output", "Replace the template example with output from a real local run."))
    return findings
