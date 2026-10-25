# Contribution Review Agent

> An offline-first auditor for mechanical contribution mistakes in multi-contributor repositories.

## What it is

This tool runs a **deterministic, static audit** on a contribution directory and reports structured findings with fix hints. It never executes contributed code and makes no network calls by default.

The optional ADK layer (`review_agent/`) wraps the same deterministic engine in a Google ADK `LlmAgent` so you can interact with it through `adk web` or `adk run`. The agent calls `run_audit`, which runs the same offline rule set and returns the structured findings dict — it does not yet read project files independently or produce semantic observations beyond what the rule engine already flags. **This layer is experimental; real-model verification is pending.**

## What exists today

The deterministic auditor is implemented and tested. It uses only the Python standard library at runtime, never executes contributed code, and sends no audit data to a service.

- **Deterministic checks:** Checks project placement and naming (R01–R03), required files and manifests (R04), README completeness and template placeholders (R05), environment variable documentation in README vs `.env.example` (R06), secret/credential detection with evidence redaction (R07), `.env` artifact hygiene (R08), Git change scope (R09), example output verification (R10), undeclared third-party Python imports (R11), recognizable repository license check (R12), exact dependency pinning in `requirements.txt` (R13), and optional OSV package vulnerability lookup with `--osv` (R14). See [docs/license-and-dependencies.md](docs/license-and-dependencies.md).
- **Config-driven profiles:** Generic profile by default, compatibility profile for legacy templates, and support for repository conventions via `.contrib-audit.json` with an `init` command to write a starter file. See [docs/configuration.md](docs/configuration.md).
- **Seeded-defect evaluation:** Fully offline test harness measuring precision and recall across defect scenarios. See [docs/eval.md](docs/eval.md).
- **Read-only GitHub Action:** Composite action in `action.yml` that emits workflow annotations and job summary without modifying repositories or posting PR comments. See [docs/github-action.md](docs/github-action.md).
- **CI workflow:** Continuous integration testing on Python 3.10 and 3.12 via `.github/workflows/tests.yml`.
- **Experimental ADK layer:** Implemented in `review_agent/`, wraps `run_audit`, mock-tested, experimental, real-model verification pending. See [docs/adk-experimental.md](docs/adk-experimental.md).
- **Triage command status:** No triage command exists in this repository. `contrib_audit/github_source.py` contains read-only GitHub REST helper functions reserved for future triage, but no CLI command or automated PR triage workflow is implemented.

## Prerequisites

- Python 3.10 or later.
- `pip` for dependency management.

## Quick start — core audit (no API key needed)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the audit
python3 -m contrib_audit check /path/to/repo/sample-agent
```

Exit status is zero for `READY` and `APPROVE_WITH_NITS`, and one for `CHANGES_REQUESTED` and `REJECT`.

Pass the contribution directory and optionally the repository root:

```bash
python3 -m contrib_audit check /path/to/repo/sample-agent --repo-root /path/to/repo --format json
```

Use `python3 -m contrib_audit init` to write a generic starter configuration. `--config` overrides auto-discovery with a built-in profile name or JSON file path. Add `--osv` to query known vulnerabilities for pinned packages.

The complete JSON schema and profile behavior are documented in [docs/configuration.md](docs/configuration.md).

## Optional: experimental ADK layer

> **Experimental — real-model verification pending. Use for exploration only.**

The ADK layer wraps `run_audit` — the same offline deterministic engine — so a model can present the findings conversationally. It does not independently read project files or provide semantic observations beyond what the rule engine flags.

### Environment variables

| Variable | Required for | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | ADK layer (`adk web` / `adk run`) | — (no key needed for core audit) |
| `MODEL_NAME` | ADK layer | `gemini-2.5-flash` |

Copy `.env.example` to `.env` and fill in your key. **Never commit `.env`.**

### Install and run

```bash
# Activate virtual environment (if not already active)
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install agent dependencies
pip install -r requirements-agent.txt

# Create .env with GOOGLE_API_KEY=your_key_here
# Run web interface:
adk web
# Or run interactive CLI:
adk run review_agent
```

## Test

The test suite is offline and constructs fake credentials from fragments at runtime; it does not store a realistic credential in a fixture. The ADK layer tests use mocks and need no API key.

```bash
python3 -m pytest -q
```

To run the offline seeded-defect evaluation:

```bash
python3 -m pytest tests/test_evaluation.py -v
```

## Safety and privacy

- Static analysis only: contributed code is never executed.
- Suspected credentials in scanned files are redacted in findings. The scanner does not open `.env`; hygiene checks report local `.env` artifacts when they are not ignored.
- The deterministic core makes no network calls (unless `--osv` is explicitly passed) and does not modify GitHub.
- `GOOGLE_API_KEY` is loaded from `.env` only when the ADK layer is used; the core audit never reads it.

## Known limitations

- Regex-based secret detection can have false positives and false negatives; it is not a replacement for a dedicated secret scanner.
- Git scope checking needs either `upstream/main` or `origin/main`; otherwise it emits an informational skip.
- The generic profile expects a project to be a direct child of the configured repository root; use `.contrib-audit.json` for another layout.
- The ADK layer is experimental: real-model verification is pending, and the agent does not yet read project files directly or produce semantic observations.
- No triage command exists in this repo (helper functions in `contrib_audit/github_source.py` are reserved for future work).

## Roadmap

1. Real-run evaluation of the experimental ADK/Gemini layer with a live API key (mock tests pass; real-model verification pending).
2. Optional PR triage CLI command (read-only GitHub REST helper functions are reserved in `contrib_audit/github_source.py`, but CLI command is not yet implemented).
3. Independent project file reading and semantic observations in the ADK agent layer.

## License and provenance

This project is MIT licensed; see [LICENSE](LICENSE).
