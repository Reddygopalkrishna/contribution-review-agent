"""Deterministic audit tool exposed to the ADK agent.

**EXPERIMENTAL — not verified with a real model.**

This module wraps contrib_audit.cli.audit as a single ADK FunctionTool so
the agent can call it with a project path and an optional repo root, then
return structured findings to the user.
"""

from __future__ import annotations

from pathlib import Path

from contrib_audit.cli import audit as _audit


def run_audit(project_path: str, repo_root: str = "", osv: bool = False) -> dict:
    """Run the offline contribution audit and return a findings dict.

    Args:
        project_path: Absolute or relative path to the contribution directory.
        repo_root: Repository root containing the template or config.
                   Leave blank for auto-discovery.
        osv: When True, query the OSV API for pinned dependency vulnerabilities.
             Requires network access; failures are informational.

    Returns:
        A dict with keys ``verdict``, ``project_path``, ``repo_root``, and
        ``findings`` (list of dicts, each with ``id``, ``severity``,
        ``file``, ``line``, ``evidence``, ``fix_hint``).
    """
    root = Path(repo_root) if repo_root else None
    report = _audit(Path(project_path), root, check_osv=osv)
    return report.to_dict()
