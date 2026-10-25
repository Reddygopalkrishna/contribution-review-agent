"""Conservative, redacting secret scan (R07)."""

from __future__ import annotations

import re
from pathlib import Path

from contrib_audit.models import Finding
from contrib_audit.rules import RuleContext

_MAX_TEXT_BYTES = 1_000_000
_SKIP_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__"}
_SKIP_FILES = {".env"}
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Google API key", re.compile(r"\bAIza[\w-]{20,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("AWS access key ID", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("private-key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]{1,}?-----END [A-Z ]*PRIVATE KEY-----")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("long credential assignment", re.compile(r"(?im)^\s*[A-Z][A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Z0-9_]*\s*=\s*['\"]?([^\s'\"]{20,})")),
)
_PLACEHOLDER_WORDS = ("example", "placeholder", "replace", "your_", "your-", "changeme", "dummy", "fake", "not-a")


def _is_binary(path: Path) -> bool:
    try:
        return b"\0" in path.read_bytes()[:4096]
    except OSError:
        return True


def _redact(value: str) -> str:
    cleaned = " ".join(value.split())
    return f"{cleaned[:4]}..." if cleaned else "..."


def _is_placeholder(value: str) -> bool:
    return any(word in value.lower() for word in _PLACEHOLDER_WORDS)


def check_secrets(context: RuleContext) -> list[Finding]:
    """Scan readable project files while never returning a raw suspected secret."""
    findings: list[Finding] = []
    for path in context.project_path.rglob("*"):
        if (
            not path.is_file()
            or path.name in _SKIP_FILES
            or any(part in _SKIP_DIRS for part in path.parts)
        ):
            continue
        try:
            if path.stat().st_size > _MAX_TEXT_BYTES or _is_binary(path):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        detected_spans: list[tuple[int, int]] = []
        for label, pattern in _PATTERNS:
            for match in pattern.finditer(text):
                start, end = match.span()
                if any(start < seen_end and seen_start < end for seen_start, seen_end in detected_spans):
                    continue
                value = match.group(1) if match.lastindex else match.group()
                if _is_placeholder(value):
                    continue
                line = text[:match.start()].count("\n") + 1
                findings.append(Finding("R07", "error", str(path), line, f"{label}: {_redact(value)}", "Remove the credential, rotate it if real, and use a placeholder in .env.example."))
                detected_spans.append((start, end))
    return findings
