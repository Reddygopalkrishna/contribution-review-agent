from __future__ import annotations

from contrib_audit.rules import RuleContext
from contrib_audit.rules.scope import check_hygiene
from contrib_audit.rules.secrets import check_secrets

from .conftest import make_project


def test_r07_accepts_placeholder_and_redacts_detected_value(tmp_path):
    repo, project = make_project(tmp_path)
    (project / ".env.example").write_text("GOOGLE_API_KEY=replace_with_your_key\nMODEL_NAME=gemini-2.5-flash\n", encoding="utf-8")
    assert not check_secrets(RuleContext(project, repo))
    fake = "AI" + "za" + ("x" * 24)
    (project / "leak.txt").write_text(fake, encoding="utf-8")
    findings = check_secrets(RuleContext(project, repo))
    assert len(findings) == 1
    assert fake not in findings[0].evidence
    assert findings[0].evidence.endswith("...")


def test_r07_skips_env_and_deduplicates_overlapping_signatures(tmp_path):
    repo, project = make_project(tmp_path)
    fake = "AI" + "za" + ("x" * 24)
    (project / ".env").write_text("GOOGLE_API_KEY=" + fake + "\n", encoding="utf-8")
    (project / ".env.example").write_text("GOOGLE_API_KEY=" + fake + "\n", encoding="utf-8")
    findings = check_secrets(RuleContext(project, repo))
    assert len(findings) == 1
    assert findings[0].file.endswith(".env.example")


def test_r08_accepts_clean_project_and_rejects_local_artifacts(tmp_path):
    repo, project = make_project(tmp_path)
    assert not check_hygiene(RuleContext(project, repo))
    (project / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    (project / ".env").write_text("local-only\n", encoding="utf-8")
    (project / ".venv").mkdir()
    ids = {finding.id for finding in check_hygiene(RuleContext(project, repo))}
    assert ids == {"R08"}
