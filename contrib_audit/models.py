"""Data types shared by the deterministic contribution auditor."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Finding:
    """One auditable rule result, with safe evidence for a human reviewer."""

    id: str
    severity: Severity
    file: str
    line: int | None
    evidence: str
    fix_hint: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class AuditReport:
    """Complete result of a local contribution check."""

    project_path: str
    repo_root: str
    findings: list[Finding] = field(default_factory=list)
    verdict: str = "READY"

    def to_dict(self) -> dict[str, object]:
        return {
            "project_path": self.project_path,
            "repo_root": self.repo_root,
            "verdict": self.verdict,
            "findings": [finding.to_dict() for finding in self.findings],
        }
