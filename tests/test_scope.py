from __future__ import annotations

from types import SimpleNamespace

from contrib_audit.rules import RuleContext
from contrib_audit.rules.scope import check_scope

from .conftest import make_project


def test_r09_accepts_project_only_changes(tmp_path, monkeypatch):
    repo, project = make_project(tmp_path)
    responses = iter((
        SimpleNamespace(returncode=0, stdout="agents/sample-agent/README.md\n", stderr=""),
        SimpleNamespace(returncode=0, stdout="?? agents/sample-agent/README.md\n", stderr=""),
    ))
    monkeypatch.setattr("contrib_audit.rules.scope.subprocess.run", lambda *args, **kwargs: next(responses))
    assert not check_scope(RuleContext(project, repo))


def test_r09_reports_external_change(tmp_path, monkeypatch):
    repo, project = make_project(tmp_path)
    responses = iter((
        SimpleNamespace(returncode=0, stdout="CONTRIBUTING.md\n", stderr=""),
        SimpleNamespace(returncode=0, stdout="", stderr=""),
    ))
    monkeypatch.setattr("contrib_audit.rules.scope.subprocess.run", lambda *args, **kwargs: next(responses))
    assert {finding.id for finding in check_scope(RuleContext(project, repo))} == {"R09"}


def test_r09_reports_unavailable_git_comparison(tmp_path, monkeypatch):
    repo, project = make_project(tmp_path)
    monkeypatch.setattr("contrib_audit.rules.scope.subprocess.run", lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr="missing ref"))
    findings = check_scope(RuleContext(project, repo))
    assert len(findings) == 1 and findings[0].severity == "info"
