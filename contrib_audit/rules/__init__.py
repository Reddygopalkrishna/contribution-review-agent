"""Rule registry and context for the deterministic auditor."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from contrib_audit.config import AuditConfig, get_profile
from contrib_audit.models import Finding

@dataclass(frozen=True)
class RuleContext:
    project_path: Path
    repo_root: Path
    config: AuditConfig = field(default_factory=lambda: get_profile("legacy-template"))
    check_osv: bool = False


Rule = Callable[[RuleContext], list[Finding]]


from contrib_audit.rules.deps import check_dependencies
from contrib_audit.rules.license import check_license
from contrib_audit.rules.readme import check_readme
from contrib_audit.rules.scope import check_hygiene, check_scope
from contrib_audit.rules.secrets import check_secrets
from contrib_audit.rules.structure import check_structure

RULES: tuple[Rule, ...] = (
    check_structure,
    check_readme,
    check_secrets,
    check_hygiene,
    check_scope,
    check_dependencies,
    check_license,
)

__all__ = ["RULES", "RuleContext"]
