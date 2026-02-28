"""Error types for Smart Git Commit.

Public APIs use Google-style docstrings and English comments.
"""

from __future__ import annotations


class SgcError(RuntimeError):
    """Base error for Smart Git Commit."""


class NotAGitRepositoryError(SgcError):
    """Raised when running outside a Git worktree."""


class NoStagedChangesError(SgcError):
    """Raised when there is no staged change to summarize."""


class LlmRequestError(SgcError):
    """Raised when the LLM request fails."""


class InvalidCommitMessageError(SgcError):
    """Raised when a commit message cannot be validated."""

