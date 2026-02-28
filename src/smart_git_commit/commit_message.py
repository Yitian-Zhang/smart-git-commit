"""Commit message generation pipeline."""

from __future__ import annotations

from smart_git_commit.config import LlmConfig
from smart_git_commit.errors import InvalidCommitMessageError
from smart_git_commit.git_context import GitContext
from smart_git_commit.llm_client import ChatCompletionsClient, ChatMessage
from smart_git_commit.semantic import COMMIT_TYPES, normalize_commit_message, validate_commit_message


def _build_generation_messages(context: GitContext) -> list[ChatMessage]:
    allowed = ", ".join(COMMIT_TYPES)
    system = (
        "You are a senior engineer. Generate a Conventional Commit message in English. "
        "Output ONLY the commit message (no quotes, no code fences, no extra text)."
    )
    user = (
        "Rules:\n"
        "- Use Conventional Commits header format: type(scope): subject OR type: subject\n"
        f"- Allowed types: {allowed}\n"
        "- Subject must be concise and imperative, no trailing period\n"
        "- If a body is helpful, put it after a blank line\n\n"
        f"Branch: {context.branch}\n"
        "Git status (porcelain):\n"
        f"{context.status_porcelain}\n\n"
        "Staged diff:\n"
        f"{context.staged_diff}\n"
    )
    return [ChatMessage(role="system", content=system), ChatMessage(role="user", content=user)]


def _build_fix_messages(bad_message: str) -> list[ChatMessage]:
    allowed = ", ".join(COMMIT_TYPES)
    system = (
        "You are a formatter. Fix the commit message to match Conventional Commits. "
        "Output ONLY the corrected commit message."
    )
    user = (
        "Fix the following output to be a valid Conventional Commit message in English.\n"
        "Requirements:\n"
        "- Header must match: type(scope): subject OR type: subject\n"
        f"- Allowed types: {allowed}\n"
        "- No quotes, no code fences, no leading labels\n\n"
        f"Bad output:\n{bad_message}\n"
    )
    return [ChatMessage(role="system", content=system), ChatMessage(role="user", content=user)]


def generate_commit_message(*, client: ChatCompletionsClient, context: GitContext, cfg: LlmConfig) -> str:
    """Generate and validate a commit message.

    This function performs at most one additional "fix" attempt if the initial output is invalid.

    Args:
        client: Chat completions client.
        context: Git context.
        cfg: LLM config.

    Returns:
        A validated commit message.

    Raises:
        InvalidCommitMessageError: If output cannot be validated after a fix attempt.
    """

    raw = client.create(
        model=cfg.model,
        messages=_build_generation_messages(context),
        max_tokens=cfg.max_tokens,
        temperature=cfg.temperature,
    )
    msg = normalize_commit_message(raw)

    try:
        validate_commit_message(msg)
        return msg
    except InvalidCommitMessageError:
        # One lightweight fix attempt.
        fixed_raw = client.create(
            model=cfg.model,
            messages=_build_fix_messages(raw),
            max_tokens=cfg.max_tokens,
            temperature=0.0,
        )
        fixed = normalize_commit_message(fixed_raw)
        validate_commit_message(fixed)
        return fixed

