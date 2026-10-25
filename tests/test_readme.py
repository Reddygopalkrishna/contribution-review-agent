from __future__ import annotations

from contrib_audit.rules import RuleContext
from contrib_audit.rules.readme import check_readme

from .conftest import make_project, write_complete_readme


def findings_for(project, repo):
    return check_readme(RuleContext(project, repo))


def test_readme_rules_accept_completed_readme(tmp_path):
    repo, project = make_project(tmp_path)
    assert not findings_for(project, repo)


def test_r05_reports_missing_heading(tmp_path):
    repo, project = make_project(tmp_path)
    (project / "README.md").write_text("# Sample\n", encoding="utf-8")
    assert "R05" in {finding.id for finding in findings_for(project, repo)}


def test_r05_reports_template_placeholder(tmp_path):
    repo, project = make_project(tmp_path)
    write_complete_readme(project / "README.md", "\n[Project Name]\n")
    assert "R05" in {finding.id for finding in findings_for(project, repo)}


def test_r06_reports_environment_documentation_mismatch(tmp_path):
    repo, project = make_project(tmp_path)
    (project / ".env.example").write_text("MODEL_NAME=gemini-2.5-flash\nEXTRA_VALUE=placeholder\n", encoding="utf-8")
    assert "R06" in {finding.id for finding in findings_for(project, repo)}


def test_r10_reports_template_example(tmp_path):
    repo, project = make_project(tmp_path)
    write_complete_readme(project / "README.md", "\nAnalysis completed:\n")
    assert "R10" in {finding.id for finding in findings_for(project, repo)}
