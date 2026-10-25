from __future__ import annotations

from pathlib import Path

from contrib_audit.rules.readme import _FALLBACK_HEADINGS


def write_complete_readme(path: Path, extra: str = "") -> None:
    sections = ["# Sample Contribution"]
    for heading in _FALLBACK_HEADINGS:
        sections.append(f"## {heading}" if heading not in {"Problem Statement & Intended Users", "Key Features", "Example Input", "Example Output"} else f"### {heading}")
        if heading == "Configuration & Environment Variables":
            sections.extend(["| Variable Name | Required | Default | Description |", "| --- | --- | --- | --- |", "| `MODEL_NAME` | No | `gemini-2.5-flash` | Model selection. |"])
        elif heading == "Example Output":
            sections.append("Verdict: READY")
        else:
            sections.append("Project-specific documentation.")
    path.write_text("\n\n".join(sections) + extra, encoding="utf-8")


def make_project(tmp_path: Path, name: str = "sample-agent") -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    (repo / "template").mkdir(parents=True)
    (repo / "template" / "README.md").write_text("\n".join(f"## {heading}" for heading in _FALLBACK_HEADINGS), encoding="utf-8")
    project = repo / "agents" / name
    project.mkdir(parents=True)
    write_complete_readme(project / "README.md")
    (project / ".env.example").write_text("MODEL_NAME=gemini-2.5-flash\n", encoding="utf-8")
    (project / ".gitignore").write_text(".env\n.venv/\n", encoding="utf-8")
    (project / "requirements.txt").write_text("\n", encoding="utf-8")
    return repo, project
