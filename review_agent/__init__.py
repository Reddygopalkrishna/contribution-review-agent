"""Optional Google ADK layer for Contribution Review Agent.

**EXPERIMENTAL — not verified with a real model.**

This package wires the deterministic contrib_audit engine into a Google ADK
agent so it can be driven with ``adk web`` or ``adk run``.  It requires no
API key for the deterministic checks; GOOGLE_API_KEY is only needed when the
ADK framework calls the Gemini model.

Install the extra dependencies before use::

    pip install -r requirements-agent.txt

See docs/adk-experimental.md for full setup instructions.
"""
