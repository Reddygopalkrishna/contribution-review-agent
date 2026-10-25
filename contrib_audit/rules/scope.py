"""Local hygiene (R08) and Git scope (R09) checks."""

from __future__ import annotations

import subprocess
from pathlib import Path

from contrib_audit.models import Finding
from contrib_audit.rules import RuleContext

_FORBIDDEN_DIRS = {".venv", "venv", "env", "node_modules", "__pycache__"}
_FORBIDDEN_SUFFIXES = {".sqlite", ".db", ".pem", ".key"}


def _is_tracked(project: Path, path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path.relative_to(project).as_posix()],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def check_hygiene(context: RuleContext) -> list[Finding]:
    """Check local artifacts and .gitignore patterns without deleting anything."""
    project = context.project_path
    findings: list[Finding] = []
    ignore_path = project / ".gitignore"
    ignored = set()
    if ignore_path.is_file():
        ignored = {line.strip().rstrip("/") for line in ignore_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip() and not line.lstrip().startswith("#")}

    def is_ignored(path: Path) -> bool:
        for candidate in (path, *path.parents):
            if candidate == project.parent:
                break
            relative = candidate.relative_to(project).as_posix().rstrip("/")
            if candidate.name in ignored or relative in ignored or f"{candidate.name}*" in ignored:
                return True
        return False

    for path in project.rglob("*"):
        if path == project:
            continue
        if path.is_dir() and path.name in _FORBIDDEN_DIRS and not is_ignored(path):
            findings.append(Finding("R08", "error", str(path), None, path.name, "Remove local environments, caches, and dependency directories from the contribution."))
        elif path.is_file() and path.name == ".env" and _is_tracked(project, path):
            findings.append(Finding("R08", "error", str(path), None, path.name, "Remove tracked .env files; use .env.example for placeholders."))
        elif path.is_file() and (path.name == ".env" or path.suffix.lower() in _FORBIDDEN_SUFFIXES) and not is_ignored(path):
            findings.append(Finding("R08", "error", str(path), None, path.name, "Remove local credentials, databases, and private-key files from the contribution."))
    if ignore_path.is_file():
        covers_env = any(pattern in ignored for pattern in {".env", ".env*", "**/.env", "**/.env*"})
        covers_venv = any(pattern in ignored for pattern in {".venv/", ".venv", "venv/", "venv", "env/", "env"})
        if not covers_env or not covers_venv:
            missing = ", ".join(name for name, covered in ((".env", covers_env), ("virtual environments", covers_venv)) if not covered)
            findings.append(Finding("R08", "error", str(ignore_path), None, f"not ignored: {missing}", "Ignore .env at any depth and common virtual-environment directories."))
    return findings


def _git_changed_files(repo_root: Path) -> tuple[list[str] | None, str | None]:
    for ref in ("upstream/main", "origin/main"):
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{ref}...HEAD"], cwd=repo_root,
            capture_output=True, text=True, check=False,
        )
        if result.returncode == 0:
            changed = {line for line in result.stdout.splitlines() if line}
            status = subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=all"], cwd=repo_root,
                capture_output=True, text=True, check=False,
            )
            if status.returncode != 0:
                return None, "could not read git working-tree status"
            for line in status.stdout.splitlines():
                if len(line) >= 4:
                    changed.add(line[3:])
            return sorted(changed), None
    return None, "could not compare against upstream/main or origin/main"


def check_scope(context: RuleContext) -> list[Finding]:
    """Ensure committed changes are confined to this project and an optional index row."""
    files, error = _git_changed_files(context.repo_root)
    if files is None:
        return [Finding("R09", "info", str(context.repo_root), None, error or "git unavailable", "Fetch an upstream or origin main branch to enable scope checking.")]
    project_prefix = context.project_path.relative_to(context.repo_root).as_posix() + "/"
    allowed_indexes = {"agents/README.md", "tools/README.md"}
    out_of_scope = [name for name in files if not name.startswith(project_prefix) and name not in allowed_indexes]
    if out_of_scope:
        return [Finding("R09", "error", str(context.repo_root), None, ", ".join(out_of_scope), "Limit the pull request to this project plus, optionally, one category index row.")]
    index_edits = [name for name in files if name in allowed_indexes]
    if len(index_edits) > 1:
        return [Finding("R09", "error", str(context.repo_root), None, ", ".join(index_edits), "Edit at most one category index file.")]
    return []
