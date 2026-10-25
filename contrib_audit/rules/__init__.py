"""Rule registry and context for the deterministic auditor."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from contrib_audit.models import Finding

@dataclass(frozen=True)
class RuleContext:
    project_path: Path
    repo_root: Path


Rule = Callable[[RuleContext], list[Finding]]


from contrib_audit.rules.deps import check_dependencies
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
)

__all__ = ["RULES", "RuleContext"]
