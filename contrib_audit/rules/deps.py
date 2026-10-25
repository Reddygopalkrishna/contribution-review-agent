"""Python dependency consistency, pinning, and optional OSV checks (R11, R13, R14)."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from contrib_audit.models import Finding
from contrib_audit.rules import RuleContext


_REQUIREMENT = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[[^]]+\])?\s*(.*)$")


def _requirements(path: Path) -> list[tuple[str, str | None]]:
    parsed: list[tuple[str, str | None]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        item = line.split("#", 1)[0].strip()
        if not item or item.startswith(("-", ".")):
            continue
        match = _REQUIREMENT.match(item)
        if not match:
            continue
        name, specifier = match.groups()
        version = specifier.removeprefix("==").split(";", 1)[0].strip() if specifier.startswith("==") else None
        parsed.append((name.replace("_", "-").lower(), version or None))
    return parsed


def _imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module.split(".", 1)[0])
    return modules


def _osv_findings(requirements: list[tuple[str, str | None]], path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for name, version in requirements:
        if version is None:
            continue
        payload = json.dumps({"package": {"name": name, "ecosystem": "PyPI"}, "version": version}).encode()
        request = Request("https://api.osv.dev/v1/query", data=payload, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=10) as response:
                vulnerabilities = json.load(response).get("vulns", [])
        except (OSError, URLError, json.JSONDecodeError) as error:
            findings.append(Finding("R14", "info", str(path), None, f"OSV lookup unavailable: {error}", "Retry with --osv when network access is available."))
            break
        identifiers = [vulnerability.get("id") for vulnerability in vulnerabilities if isinstance(vulnerability, dict) and vulnerability.get("id")]
        if identifiers:
            findings.append(Finding("R14", "warning", str(path), None, f"{name}=={version}: {', '.join(identifiers)}", "Review and upgrade the affected dependency."))
    return findings


def check_dependencies(context: RuleContext) -> list[Finding]:
    """Check Python manifests without using the network unless --osv is enabled."""
    requirements = context.project_path / "requirements.txt"
    if not requirements.is_file():
        return []
    declared_requirements = _requirements(requirements)
    declared = {name for name, _ in declared_requirements}
    findings: list[Finding] = []
    unpinned = sorted(name for name, version in declared_requirements if version is None)
    if unpinned:
        findings.append(Finding("R13", "error", str(requirements), None, ", ".join(unpinned), "Pin every dependency with an exact == version."))
    local_modules = {path.stem for path in context.project_path.rglob("*.py")}
    local_modules.update(path.name for path in context.project_path.iterdir() if path.is_dir() and (path / "__init__.py").is_file())
    stdlib = getattr(sys, "stdlib_module_names", set())
    imported: set[str] = set()
    for path in context.project_path.rglob("*.py"):
        if any(part in {"tests", ".venv", "venv"} for part in path.parts):
            continue
        imported.update(_imports(path))
    aliases = {"dotenv": "python-dotenv", "google": "google-adk"}
    missing = sorted(module for module in imported if module not in stdlib and module not in local_modules and aliases.get(module, module).replace("_", "-").lower() not in declared)
    if missing:
        findings.append(Finding("R11", "warning", str(requirements), None, ", ".join(missing), "Declare each third-party import in requirements.txt."))
    if context.check_osv:
        findings.extend(_osv_findings(declared_requirements, requirements))
    return findings
