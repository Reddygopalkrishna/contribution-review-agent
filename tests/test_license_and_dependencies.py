from __future__ import annotations

import io
import json

from contrib_audit.rules import RuleContext
from contrib_audit.rules.deps import check_dependencies
from contrib_audit.rules.license import check_license

from .conftest import make_project


def test_r12_requires_a_recognizable_repository_license(tmp_path):
    repo, project = make_project(tmp_path)
    assert not check_license(RuleContext(project, repo))
    (repo / "LICENSE").write_text("custom words\n", encoding="utf-8")
    assert {finding.id for finding in check_license(RuleContext(project, repo))} == {"R12"}


def test_r13_reports_unpinned_requirements(tmp_path):
    repo, project = make_project(tmp_path)
    requirements = project / "requirements.txt"
    requirements.write_text("requests>=2\npytest==9.1.1\n", encoding="utf-8")
    findings = check_dependencies(RuleContext(project, repo))
    assert {finding.id for finding in findings} == {"R13"}


def test_osv_query_is_opt_in_and_reports_returned_identifiers(tmp_path, monkeypatch):
    repo, project = make_project(tmp_path)
    (project / "requirements.txt").write_text("requests==2.0.0\n", encoding="utf-8")
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return io.StringIO(json.dumps({"vulns": [{"id": "TEST-1"}]}))

    monkeypatch.setattr("contrib_audit.rules.deps.urlopen", fake_urlopen)
    assert not check_dependencies(RuleContext(project, repo))
    findings = check_dependencies(RuleContext(project, repo, check_osv=True))
    assert calls and {finding.id for finding in findings} == {"R14"}
