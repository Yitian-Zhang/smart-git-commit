"""Collect Git context used to generate commit messages."""

from __future__ import annotations

from dataclasses import dataclass
import subprocess

from smart_git_commit.errors import NoStagedChangesError, NotAGitRepositoryError


@dataclass(frozen=True)
class GitContext:
    """Git context needed for commit message generation.

    Attributes:
        branch: Current branch name.
        status_porcelain: Output of `git status --porcelain=v1`.
        staged_diff: Output of `git diff --staged --no-color` (possibly truncated).
        diff_truncated: Whether staged_diff was truncated.
        original_diff_chars: Original staged diff size (in characters).
    """

    branch: str
    status_porcelain: str
    staged_diff: str
    diff_truncated: bool
    original_diff_chars: int


def _git_run(args: list[str], *, timeout_s: float = 10.0) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except FileNotFoundError as e:
        raise NotAGitRepositoryError("git is not installed or not found in PATH") from e


def _run_git_checked(args: list[str], *, timeout_s: float = 10.0) -> str:
    proc = _git_run(args, timeout_s=timeout_s)
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        raise NotAGitRepositoryError(stderr or f"git {args!r} failed")
    return proc.stdout


class GitContextCollector:
    """Collect Git information from the current working directory."""

    def collect(self, *, max_diff_chars: int = 8000) -> GitContext:
        """Collect staged diff and minimal metadata.

        Args:
            max_diff_chars: Max characters to include from staged diff.

        Returns:
            A GitContext.

        Raises:
            NotAGitRepositoryError: If not inside a git worktree.
            NoStagedChangesError: If there is no staged change.
        """

        inside = _run_git_checked(["rev-parse", "--is-inside-work-tree"]).strip().lower()
        if inside != "true":
            raise NotAGitRepositoryError("not inside a git worktree")

        # Branch name should work even without an initial commit.
        branch_proc = _git_run(["symbolic-ref", "--quiet", "--short", "HEAD"])
        branch = (branch_proc.stdout or "").strip() if branch_proc.returncode == 0 else ""
        if not branch:
            # Detached HEAD or otherwise not resolvable.
            sha_proc = _git_run(["rev-parse", "--short", "HEAD"])
            sha = (sha_proc.stdout or "").strip() if sha_proc.returncode == 0 else ""
            branch = f"detached@{sha}" if sha else "detached"

        status = _run_git_checked(["status", "--porcelain=v1"]).rstrip("\n")
        diff = _run_git_checked(["diff", "--staged", "--no-color"]).rstrip("\n")

        if not diff.strip():
            raise NoStagedChangesError("no staged diff")

        original_len = len(diff)
        diff_truncated = original_len > max_diff_chars
        if diff_truncated:
            diff = diff[:max_diff_chars]
            diff += "\n\n[NOTE] The staged diff is truncated for performance.\n"

        return GitContext(
            branch=branch,
            status_porcelain=status,
            staged_diff=diff,
            diff_truncated=diff_truncated,
            original_diff_chars=original_len,
        )
