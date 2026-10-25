"""Optional Python manifest consistency rule (R11)."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from contrib_audit.models import Finding
from contrib_audit.rules import RuleContext


def _requirements_names(path: Path) -> set[str]:
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        item = line.split("#", 1)[0].strip()
        if item and not item.startswith(("-", ".")):
            names.add(item.split("=", 1)[0].split("<", 1)[0].split(">", 1)[0].split("[", 1)[0].replace("_", "-").lower())
    return names


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


def check_dependencies(context: RuleContext) -> list[Finding]:
    """Warn if a third-party top-level Python import is absent from requirements.txt."""
    requirements = context.project_path / "requirements.txt"
    if not requirements.is_file():
        return []
    declared = _requirements_names(requirements)
    local_modules = {path.stem for path in context.project_path.rglob("*.py")}
    local_modules.update(
        path.name for path in context.project_path.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    )
    stdlib = getattr(sys, "stdlib_module_names", set())
    imported: set[str] = set()
    for path in context.project_path.rglob("*.py"):
        if any(part in {"tests", ".venv", "venv"} for part in path.parts):
            continue
        imported.update(_imports(path))
    aliases = {"dotenv": "python-dotenv", "google": "google-adk"}
    missing = sorted(
        module for module in imported
        if module not in stdlib and module not in local_modules and aliases.get(module, module).replace("_", "-").lower() not in declared
    )
    if not missing:
        return []
    return [Finding("R11", "warning", str(requirements), None, ", ".join(missing), "Declare each third-party import in requirements.txt.")]
