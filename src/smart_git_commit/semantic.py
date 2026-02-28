"""Semantic / Conventional Commit message validation."""

from __future__ import annotations

import re

from smart_git_commit.errors import InvalidCommitMessageError


COMMIT_TYPES: tuple[str, ...] = (
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
)


_HEADER_RE = re.compile(
    r"^(?P<type>[a-z]+)(\((?P<scope>[^)\r\n]+)\))?(?P<breaking>!)?: (?P<subject>[^\r\n]+)$"
)


def normalize_commit_message(text: str) -> str:
    """Normalize a model output into a plain commit message string."""

    msg = text.strip()

    # Remove common wrapping styles.
    if msg.startswith("```") and msg.endswith("```"):
        msg = msg.strip("`")
        msg = msg.strip()
    if (msg.startswith("\"") and msg.endswith("\"")) or (msg.startswith("'") and msg.endswith("'")):
        msg = msg[1:-1].strip()

    # Remove leading labels like "Commit message:".
    msg = re.sub(r"^commit\s+message\s*:\s*", "", msg, flags=re.IGNORECASE)
    return msg.strip()


def validate_commit_message(message: str) -> None:
    """Validate a semantic commit message.

    We validate the first line (header) and allow an optional body.

    Args:
        message: Commit message (may include body).

    Raises:
        InvalidCommitMessageError: If the header is invalid.
    """

    lines = message.splitlines()
    if not lines or not lines[0].strip():
        raise InvalidCommitMessageError(
            "Invalid commit message: empty output. Expected format like 'feat: add X'."
        )

    header = lines[0].strip()
    m = _HEADER_RE.match(header)
    if not m:
        allowed = ", ".join(COMMIT_TYPES)
        raise InvalidCommitMessageError(
            "Invalid commit message header. Expected 'type(scope): subject' or 'type: subject'. "
            f"Allowed types: {allowed}. Got: {header!r}"
        )

    ctype = m.group("type")
    subject = m.group("subject").strip()
    if ctype not in COMMIT_TYPES:
        allowed = ", ".join(COMMIT_TYPES)
        raise InvalidCommitMessageError(
            f"Unknown commit type {ctype!r}. Allowed types: {allowed}."
        )
    if not subject:
        raise InvalidCommitMessageError("Commit subject must not be empty.")

