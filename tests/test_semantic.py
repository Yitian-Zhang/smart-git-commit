from __future__ import annotations

import pytest

from smart_git_commit.errors import InvalidCommitMessageError
from smart_git_commit.semantic import normalize_commit_message, validate_commit_message


def test_validate_commit_message_accepts_basic() -> None:
    validate_commit_message("feat: add commit generator")
    validate_commit_message("fix(cli): handle missing API key")
    validate_commit_message("chore!: drop python 3.11 support")


def test_validate_commit_message_rejects_invalid() -> None:
    with pytest.raises(InvalidCommitMessageError):
        validate_commit_message("add stuff")
    with pytest.raises(InvalidCommitMessageError):
        validate_commit_message("unknown: add stuff")


def test_normalize_commit_message_strips_wrappers() -> None:
    assert normalize_commit_message("Commit message: feat: add x") == "feat: add x"
    assert normalize_commit_message("'feat: add x'") == "feat: add x"

