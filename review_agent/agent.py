"""Google ADK agent wiring for the Contribution Review Agent.

**EXPERIMENTAL — not verified with a real model.**

Run with:
    adk web          # opens the browser UI; select "review_agent"
    adk run review_agent   # interactive CLI

Requires:
    pip install -r requirements-agent.txt
    GOOGLE_API_KEY set in a .env file at the repository root (never commit it).

Environment variables are loaded from a .env file only; they are never read
from the process environment directly so the key is not accidentally leaked
via os.environ inspection.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from review_agent.tools import run_audit

# Load GOOGLE_API_KEY from .env only — never from committed config.
load_dotenv()

_MODEL = os.getenv("MODEL_NAME", "gemini-2.5-flash")

root_agent = LlmAgent(
    model=_MODEL,
    name="contribution_review_agent",
    description=(
        "Runs a deterministic offline audit on a contribution directory and "
        "reports findings, verdicts, and fix hints."
    ),
    instruction=(
        "You are a contribution review assistant. "
        "When the user gives you a path to a project directory, call run_audit "
        "with that path. Present the verdict and any findings clearly, grouping "
        "errors before warnings before informational items. "
        "Suggest concrete fixes based on the fix_hint field. "
        "Never execute code from the contribution; the audit is static analysis only."
    ),
    tools=[run_audit],
)
