# Contribution Review Agent

> An offline-first auditor for mechanical contribution mistakes in multi-contributor repositories.

## What it is

This tool runs a **deterministic, static audit** on a contribution directory and reports structured findings with fix hints. It never executes contributed code and makes no network calls by default.

The optional ADK layer (`review_agent/`) wraps the same deterministic engine in a Google ADK `LlmAgent` so you can interact with it through `adk web`. The agent calls `run_audit`, which runs the same offline rule set and returns the structured findings dict — it does not yet read project files independently or produce semantic observations beyond what the rule engine already flags. **This layer is experimental and has not been verified with a real model.**

## What exists today

The deterministic auditor is implemented and tested. It uses only the Python standard library at runtime, never executes contributed code, and sends no audit data to a service.

- Checks project placement, names, required files, README completeness, documented environment variables, likely secrets, local artifacts, Git change scope, example output, and Python dependency declarations.
- Produces text, Markdown, or JSON findings with redacted evidence and direct fix hints.
- Uses a generic profile by default and can load repository conventions from `.contrib-audit.json`.
- Includes an offline seeded-defect evaluation harness; its measured results are in [docs/eval.md](docs/eval.md).
- Provides a read-only GitHub Action that reports through annotations and the job summary; see [docs/github-action.md](docs/github-action.md).
- Checks recognizable repository licenses and exact Python dependency pins; optional OSV lookup is documented in [docs/license-and-dependencies.md](docs/license-and-dependencies.md).

**Experimental (not yet verified with a real model):** The ADK/Gemini layer in `review_agent/` wires the deterministic engine into an `LlmAgent`. Mock tests exist; a real-model run has not been performed yet. See [docs/adk-experimental.md](docs/adk-experimental.md).

## Prerequisites

- Python 3.10 or later.
- `pip` to install the test dependency.

## Quick start — core audit (no API key needed)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m contrib_audit check /path/to/repo/sample-agent
```

Exit status is zero for `READY` and `APPROVE_WITH_NITS`, and one for `CHANGES_REQUESTED` and `REJECT`.

Pass the contribution directory and optionally the repository root:

```bash
python3 -m contrib_audit check /path/to/repo/sample-agent --repo-root /path/to/repo --format json
```

Use `python3 -m contrib_audit init` to write a generic starter configuration. `--config` overrides auto-discovery with a built-in profile name or JSON file path.

The complete JSON schema and profile behavior are documented in [docs/configuration.md](docs/configuration.md).

## Optional: experimental ADK layer

> **Not yet verified with a real model. Use for exploration only.**

The ADK layer wraps `run_audit` — the same offline deterministic engine — so the Gemini model can present the findings conversationally. It does not independently read project files or provide semantic observations beyond what the rule engine flags.

### Environment variables

| Variable | Required for | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | ADK layer (`adk web` / `adk run`) | — (no key needed for core audit) |
| `MODEL_NAME` | ADK layer | `gemini-2.5-flash` |

Copy `.env.example` to `.env` and fill in your key. **Never commit `.env`.**

### Install and run

```bash
pip install -r requirements-agent.txt   # adds google-adk and python-dotenv
# create .env with GOOGLE_API_KEY=your_key_here
adk web                                 # open the URL shown, select contribution_review_agent
# or:
adk run review_agent
```

## Test

The test suite is offline and constructs fake credentials from fragments at runtime; it does not store a realistic credential in a fixture. The ADK layer tests use mocks and need no API key.

```bash
python3 -m pytest -q
```

## Safety and privacy

- Static analysis only: contributed code is never executed.
- Suspected credentials in scanned files are redacted in findings. The scanner does not open `.env`; hygiene checks report local `.env` artifacts when they are not ignored.
- The deterministic core makes no network calls and does not modify GitHub.
- `GOOGLE_API_KEY` is loaded from `.env` only when the ADK layer is used; the core audit never reads it.

## Known limitations

- Regex-based secret detection can have false positives and false negatives; it is not a replacement for a dedicated secret scanner.
- Git scope checking needs either `upstream/main` or `origin/main`; otherwise it emits an informational skip.
- The generic profile expects a project to be a direct child of the configured repository root; use `.contrib-audit.json` for another layout.
- The ADK layer is experimental: it has not been verified with a real model, and the agent does not yet read project files directly or produce semantic observations.

## Roadmap

1. Real-run verification of the experimental ADK/Gemini layer (mock tests exist; a real run with a live key has not been performed yet).

## License and provenance

This project is MIT licensed; see [LICENSE](LICENSE).
