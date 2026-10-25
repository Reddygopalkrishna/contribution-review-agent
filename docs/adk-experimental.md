# ADK experimental layer

> **EXPERIMENTAL — not verified with a real model.**
>
> This document describes the optional Google ADK layer.  The deterministic
> auditor works without it.  Do not rely on this layer for production use until
> a real-run verification has been completed and the README has been updated.

## What it is

`review_agent/` wires the offline `contrib_audit` engine into a Google ADK
`LlmAgent`.  The agent exposes one tool — `run_audit` — that accepts a project
path, runs the full deterministic rule set, and returns the verdict and findings
as a structured dict for the model to interpret.

The model never executes contributed code; it only reads the structured findings
produced by static analysis.

## Prerequisites

- Python 3.10 or later
- A `GOOGLE_API_KEY` that has access to the Gemini API

## Installation

Install the extra dependencies into your virtual environment **in addition to**
`requirements.txt`:

```bash
pip install -r requirements.txt
pip install -r requirements-agent.txt
```

## Configuration

Create a `.env` file at the repository root (it is already listed in
`.gitignore`):

```bash
# .env  — never commit this file
GOOGLE_API_KEY=your_key_here
MODEL_NAME=gemini-2.5-flash   # optional, default is gemini-2.5-flash
```

The agent loads `GOOGLE_API_KEY` from `.env` only.  It is never read from a
committed file or a hard-coded string.

## Running with adk web

```bash
adk web
```

Open the URL shown in your terminal, select **contribution_review_agent** from
the dropdown, then type a message such as:

```
Audit the project at /path/to/repo/agents/sample-agent with repo root /path/to/repo
```

## Running with adk run

```bash
adk run review_agent
```

## Verifying the tool (no API key needed)

The mock-based test suite verifies the `run_audit` tool without any API key:

```bash
python3 -m pytest tests/test_review_agent_tools.py -v
```

## What to report after a real run

After running `adk web` with a real key and submitting a project path, paste the
full terminal output (not the browser screenshot) here.  The README will be
updated to say the layer was verified only after a real output is provided.
