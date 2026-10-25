# Contribution Review Agent

> An offline-first auditor for mechanical contribution mistakes in multi-contributor repositories.

## What exists today

The deterministic auditor is implemented and tested. It uses only the Python standard library at runtime, never executes contributed code, and sends no audit data to a service.

- Checks project placement, names, required files, README completeness, documented environment variables, likely secrets, local artifacts, Git change scope, example output, and Python dependency declarations.
- Produces text, Markdown, or JSON findings with redacted evidence and direct fix hints.
- Uses a generic profile by default and can load repository conventions from `.contrib-audit.json`.
- Includes an offline seeded-defect evaluation harness; its measured results are in [docs/eval.md](docs/eval.md).
- Provides a read-only GitHub Action that reports through annotations and the job summary; see [docs/github-action.md](docs/github-action.md).

The optional Google ADK/Gemini layer and GitHub triage command are not implemented yet.

## Prerequisites

- Python 3.10 or later.
- `pip` to install the test dependency.

## Installation

From this repository's root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The deterministic auditor needs no API key and no `.env` file.

## Run an audit

Pass the contribution directory to inspect. A `.contrib-audit.json` in an ancestor directory is loaded automatically:

```bash
python3 -m contrib_audit check /path/to/repo/sample-agent
```

Or pass the contribution repository explicitly:

```bash
python3 -m contrib_audit check /path/to/repo/sample-agent --repo-root /path/to/repo --format json
```

Exit status is zero for `READY` and `APPROVE_WITH_NITS`, and one for `CHANGES_REQUESTED` and `REJECT`.

Use `python3 -m contrib_audit init` to write a generic starter configuration. `--config` is available when you want to override auto-discovery with a built-in compatibility profile or another JSON file.

The complete JSON schema and profile behavior are documented in [docs/configuration.md](docs/configuration.md).

## Test

The test suite is offline and constructs fake credentials from fragments at runtime; it does not store a realistic credential in a fixture.

```bash
python3 -m pytest -q
```

## Safety and privacy

- Static analysis only: contributed code is never executed.
- Suspected credentials in scanned files are redacted in findings. The scanner does not open `.env`; hygiene checks report local `.env` artifacts when they are not ignored.
- The deterministic core makes no network calls and does not modify GitHub.

## Known limitations

- Regex-based secret detection can have false positives and false negatives; it is not a replacement for a dedicated secret scanner.
- Git scope checking needs either `upstream/main` or `origin/main`; otherwise it emits an informational skip.
- The generic profile expects a project to be a direct child of the configured repository root; use `.contrib-audit.json` for another layout.

## Roadmap

1. Deterministic license and dependency checks, with optional OSV lookup.
2. Experimental ADK support for Gemini and locally served models, only after mock tests and real-run validation.

## License and provenance

This project is MIT licensed; see [LICENSE](LICENSE).
