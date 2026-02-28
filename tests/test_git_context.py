from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from smart_git_commit.errors import NoStagedChangesError, NotAGitRepositoryError
from smart_git_commit.git_context import GitContextCollector


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture()
def tmp_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(["git", "init"], cwd=repo)
    _run(["git", "config", "user.email", "test@example.com"], cwd=repo)
    _run(["git", "config", "user.name", "Test"], cwd=repo)
    return repo


def test_collect_raises_outside_repo(tmp_path: Path) -> None:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        with pytest.raises(NotAGitRepositoryError):
            GitContextCollector().collect()
    finally:
        os.chdir(cwd)


def test_collect_raises_without_staged_changes(tmp_git_repo: Path) -> None:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_git_repo)
        (tmp_git_repo / "a.txt").write_text("hello")
        # Not staged.
        with pytest.raises(NoStagedChangesError):
            GitContextCollector().collect()
    finally:
        os.chdir(cwd)


def test_collect_ok_with_staged_changes(tmp_git_repo: Path) -> None:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_git_repo)
        (tmp_git_repo / "a.txt").write_text("hello")
        _run(["git", "add", "a.txt"], cwd=tmp_git_repo)
        ctx = GitContextCollector().collect(max_diff_chars=200)
        assert ctx.branch
        assert "a.txt" in ctx.staged_diff
    finally:
        os.chdir(cwd)

