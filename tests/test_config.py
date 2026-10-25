from __future__ import annotations

import json
from dataclasses import replace
from types import SimpleNamespace

from contrib_audit.cli import audit, main
from contrib_audit.config import get_profile, starter_config
from contrib_audit.rules import RuleContext
from contrib_audit.rules.scope import check_scope

from .conftest import make_project


def test_legacy_template_automatically_uses_compatible_profile(tmp_path):
    repo, project = make_project(tmp_path)
    assert audit(project, repo).verdict == "READY"


def test_generic_profile_accepts_a_direct_child_without_template_requirements(tmp_path):
    repo = tmp_path / "repo"
    project = repo / "sample-project"
    project.mkdir(parents=True)
    (repo / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    (project / "README.md").write_text("# Sample\n\n### Example Output\n\nVerdict: READY\n", encoding="utf-8")
    (project / ".gitignore").write_text(".env\n.venv/\n", encoding="utf-8")
    (project / "requirements.txt").write_text("\n", encoding="utf-8")
    findings = audit(project, repo, get_profile("generic")).findings
    assert not {finding.id for finding in findings if finding.id in {"R01", "R04", "R05"}}


def test_cli_accepts_a_builtin_profile_override(tmp_path, capsys):
    repo = tmp_path / "repo"
    project = repo / "sample-project"
    project.mkdir(parents=True)
    (repo / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    (project / "README.md").write_text("# Sample\n\n### Example Output\n\nVerdict: READY\n", encoding="utf-8")
    (project / ".gitignore").write_text(".env\n.venv/\n", encoding="utf-8")
    (project / "requirements.txt").write_text("\n", encoding="utf-8")
    assert main(["check", str(project), "--repo-root", str(repo), "--config", "generic", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["verdict"] == "READY"


def test_init_writes_a_generic_config_that_is_auto_discovered(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    config_path = repo / ".contrib-audit.json"
    assert main(["init", str(config_path)]) == 0
    assert "generic" in capsys.readouterr().out
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["profile"] == "generic"


def test_custom_config_controls_allowed_folder_and_generic_names(tmp_path):
    repo, project = make_project(tmp_path)
    nested = repo / "contributions" / "demo"
    nested.parent.mkdir()
    project.rename(nested)
    config = json.loads(starter_config("generic"))
    config["allowed_parent_folders"] = ["contributions"]
    config["generic_names"] = ["demo"]
    (repo / ".contrib-audit.json").write_text(json.dumps(config), encoding="utf-8")
    findings = audit(nested).findings
    assert "R01" not in {finding.id for finding in findings}
    assert "R03" in {finding.id for finding in findings}


def test_config_controls_scope_refs_and_extra_paths(tmp_path, monkeypatch):
    repo, project = make_project(tmp_path)
    config = replace(get_profile("generic"), scope_base_refs=("review/base",), scope_allowed_extra_paths=("catalog.md",), scope_max_extra_paths=1)
    responses = iter((
        SimpleNamespace(returncode=0, stdout="catalog.md\n", stderr=""),
        SimpleNamespace(returncode=0, stdout="", stderr=""),
    ))
    monkeypatch.setattr("contrib_audit.rules.scope.subprocess.run", lambda *args, **kwargs: next(responses))
    assert not check_scope(RuleContext(project, repo, config))
