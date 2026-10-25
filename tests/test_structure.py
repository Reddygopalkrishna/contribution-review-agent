from __future__ import annotations

from contrib_audit.rules import RuleContext
from contrib_audit.rules.structure import check_structure

from .conftest import make_project


def ids(context: RuleContext) -> set[str]:
    return {finding.id for finding in check_structure(context)}


def test_structure_accepts_complete_direct_child(tmp_path):
    repo, project = make_project(tmp_path)
    assert not ids(RuleContext(project, repo))


def test_r01_rejects_nested_project(tmp_path):
    repo, project = make_project(tmp_path)
    nested = project / "nested"
    nested.mkdir()
    assert "R01" in ids(RuleContext(nested, repo))


def test_r02_rejects_non_kebab_name(tmp_path):
    repo, project = make_project(tmp_path, "Sample_Agent")
    assert "R02" in ids(RuleContext(project, repo))


def test_r03_rejects_generic_name(tmp_path):
    repo, project = make_project(tmp_path, "demo")
    assert "R03" in ids(RuleContext(project, repo))


def test_r04_rejects_missing_required_file(tmp_path):
    repo, project = make_project(tmp_path)
    (project / "README.md").unlink()
    assert "R04" in ids(RuleContext(project, repo))
