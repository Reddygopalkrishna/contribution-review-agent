"""Mock-based tests for the ADK agent layer.

These tests need no API key and do not import google.adk.  They verify that:
- run_audit delegates to contrib_audit.cli.audit correctly.
- The returned dict has the expected shape.
- check_osv=False is the default (no network calls).
- check_osv=True is forwarded when requested.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from review_agent.tools import run_audit


def _make_report(verdict: str = "READY") -> MagicMock:
    report = MagicMock()
    report.to_dict.return_value = {
        "verdict": verdict,
        "project_path": "/fake/project",
        "repo_root": "/fake",
        "findings": [],
    }
    return report


def test_run_audit_returns_dict_with_expected_keys(tmp_path):
    with patch("review_agent.tools._audit", return_value=_make_report()) as mock_audit:
        result = run_audit(str(tmp_path))
    assert {"verdict", "project_path", "repo_root", "findings"} <= result.keys()
    mock_audit.assert_called_once()


def test_run_audit_passes_project_path_as_path_object(tmp_path):
    with patch("review_agent.tools._audit", return_value=_make_report()) as mock_audit:
        run_audit(str(tmp_path))
    call_args = mock_audit.call_args
    assert isinstance(call_args.args[0], Path)


def test_run_audit_repo_root_defaults_to_none(tmp_path):
    with patch("review_agent.tools._audit", return_value=_make_report()) as mock_audit:
        run_audit(str(tmp_path))
    call_args = mock_audit.call_args
    assert call_args.args[1] is None


def test_run_audit_passes_repo_root_when_given(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    with patch("review_agent.tools._audit", return_value=_make_report()) as mock_audit:
        run_audit(str(tmp_path), repo_root=str(repo))
    call_args = mock_audit.call_args
    assert isinstance(call_args.args[1], Path)
    assert call_args.args[1] == repo


def test_run_audit_osv_is_false_by_default(tmp_path):
    with patch("review_agent.tools._audit", return_value=_make_report()) as mock_audit:
        run_audit(str(tmp_path))
    call_args = mock_audit.call_args
    assert call_args.kwargs.get("check_osv") is False


def test_run_audit_forwards_osv_true(tmp_path):
    with patch("review_agent.tools._audit", return_value=_make_report()) as mock_audit:
        run_audit(str(tmp_path), osv=True)
    call_args = mock_audit.call_args
    assert call_args.kwargs.get("check_osv") is True


def test_run_audit_propagates_verdict(tmp_path):
    with patch("review_agent.tools._audit", return_value=_make_report("CHANGES_REQUESTED")):
        result = run_audit(str(tmp_path))
    assert result["verdict"] == "CHANGES_REQUESTED"
