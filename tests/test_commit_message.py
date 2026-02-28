from __future__ import annotations

import pytest

from smart_git_commit.commit_message import generate_commit_message
from smart_git_commit.config import LlmConfig
from smart_git_commit.errors import InvalidCommitMessageError
from smart_git_commit.git_context import GitContext


class _StubClient:
    def __init__(self, outputs: list[str]) -> None:
        self._outputs = outputs
        self.calls: int = 0

    def create(self, *, model: str, messages: object, max_tokens: int, temperature: float) -> str:
        _ = (model, messages, max_tokens, temperature)
        out = self._outputs[self.calls]
        self.calls += 1
        return out


def _cfg() -> LlmConfig:
    return LlmConfig(
        base_url="https://example.com/v1",
        api_key="k",
        model="m",
        timeout_s=1,
        max_tokens=50,
        temperature=0.2,
    )


def _ctx() -> GitContext:
    return GitContext(
        branch="main",
        status_porcelain="M a.txt",
        staged_diff="diff --git a/a.txt b/a.txt\n+hello\n",
        diff_truncated=False,
        original_diff_chars=10,
    )


def test_generate_commit_message_happy_path() -> None:
    client = _StubClient(["feat: add commit generator"])
    out = generate_commit_message(client=client, context=_ctx(), cfg=_cfg())
    assert out == "feat: add commit generator"
    assert client.calls == 1


def test_generate_commit_message_repairs_once() -> None:
    client = _StubClient(["add commit generator", "feat: add commit generator"])
    out = generate_commit_message(client=client, context=_ctx(), cfg=_cfg())
    assert out == "feat: add commit generator"
    assert client.calls == 2


def test_generate_commit_message_raises_when_unfixable() -> None:
    client = _StubClient(["add commit generator", "still bad"])
    with pytest.raises(InvalidCommitMessageError):
        generate_commit_message(client=client, context=_ctx(), cfg=_cfg())
    assert client.calls == 2

