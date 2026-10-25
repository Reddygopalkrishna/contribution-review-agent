"""Recognizable repository license rule (R12)."""

from __future__ import annotations

from contrib_audit.models import Finding
from contrib_audit.rules import RuleContext


_LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
_SIGNATURES = {
    "MIT": ("MIT License",),
    "Apache-2.0": ("Apache License", "Version 2.0"),
    "BSD": ("Redistribution and use in source and binary forms",),
    "MPL-2.0": ("Mozilla Public License", "Version 2.0"),
    "GPL": ("GNU GENERAL PUBLIC LICENSE",),
}


def check_license(context: RuleContext) -> list[Finding]:
    """Require a recognizable license at the audited repository root."""
    path = next((context.repo_root / name for name in _LICENSE_NAMES if (context.repo_root / name).is_file()), None)
    if path is None:
        return [Finding("R12", "error", str(context.repo_root), None, "missing LICENSE", "Add a recognizable repository license.")]
    text = path.read_text(encoding="utf-8", errors="replace")[:20_000]
    for name, signatures in _SIGNATURES.items():
        if all(signature.lower() in text.lower() for signature in signatures):
            return []
    return [Finding("R12", "error", str(path), None, "unrecognized license text", "Use a standard SPDX-recognizable license text.")]
