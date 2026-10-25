from contrib_audit.models import AuditReport, Finding
from contrib_audit.report import render_github_actions


def test_github_renderer_writes_summary_and_uses_redacted_evidence(tmp_path, monkeypatch):
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    report = AuditReport("project", "repo", [Finding("R07", "error", "project/leak.txt", 3, "Google API key: AIza...", "Remove it.")], "REJECT")
    annotation = render_github_actions(report)
    assert annotation.startswith("::error")
    assert "AIza..." in annotation
    assert summary.read_text(encoding="utf-8").startswith("# Contribution audit: REJECT")
