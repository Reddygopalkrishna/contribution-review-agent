# Contribution Review Agent

> An offline-first auditor for mechanical contribution mistakes in multi-contributor repositories.

## What exists today

The deterministic auditor is implemented and tested. It uses only the Python standard library at runtime, never executes contributed code, and sends no audit data to a service.

- Checks project placement, names, required files, README completeness, documented environment variables, likely secrets, local artifacts, Git change scope, example output, and Python dependency declarations.
- Produces text, Markdown, or JSON findings with redacted evidence and direct fix hints.
- Supports the current GDG-style contribution layout: a project directly under `agents/` or `tools/`, with the repository template at `template/README.md`.
- Includes an offline seeded-defect evaluation harness; its measured results are in [docs/eval.md](docs/eval.md).

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

Pass the contribution directory to inspect. For a GDG-style repository, automatic discovery works when the target is below that repository:

```bash
python3 -m contrib_audit check /path/to/repo/agents/sample-agent
```

Or pass the contribution repository explicitly:

```bash
python3 -m contrib_audit check /path/to/repo/agents/sample-agent --repo-root /path/to/repo --format json
```

Exit status is zero for `READY` and `APPROVE_WITH_NITS`, and one for `CHANGES_REQUESTED` and `REJECT`.

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
- Today's conventions are GDG-style and hardcoded. Configurable profiles are planned next.

## Roadmap

1. Config-driven rules with GDG-compatible and generic profiles.
2. A read-only GitHub Action using pull-request-safe defaults.
3. Deterministic license and dependency checks, with optional OSV lookup.
4. Experimental ADK support for Gemini and locally served models, only after mock tests and real-run validation.

## License and provenance

This project is MIT licensed. Its README, `.env.example`, and `.gitignore` began from templates in [GDG Cloud Bengaluru's `open-source-agents`](https://github.com/gdgcblr/open-source-agents), also MIT licensed; the upstream copyright notice is retained in [LICENSE](LICENSE).
