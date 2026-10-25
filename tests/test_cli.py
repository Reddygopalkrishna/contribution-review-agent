from __future__ import annotations

import json

from contrib_audit.cli import audit, main

from .conftest import make_project


def test_cli_json_and_exit_code_for_ready_project(tmp_path, capsys):
    repo, project = make_project(tmp_path)
    assert main(["check", str(project), "--repo-root", str(repo), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["verdict"] == "READY"


def test_verdict_rejects_secret_before_other_errors(tmp_path):
    repo, project = make_project(tmp_path)
    fake = "AI" + "za" + ("x" * 24)
    (project / "leak.txt").write_text(fake, encoding="utf-8")
    report = audit(project, repo)
    assert report.verdict == "REJECT"
