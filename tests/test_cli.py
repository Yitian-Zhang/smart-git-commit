from __future__ import annotations

import pytest

from typer.testing import CliRunner

from smart_git_commit.git_context import GitContext

from smart_git_commit.cli import app


def test_cli_requires_api_key() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--max-diff-chars", "10"], env={"SGC_API_KEY": ""})
    assert result.exit_code != 0
    assert "Missing API key" in result.output


def test_cli_happy_path_prints_message_and_git_command(monkeypatch: pytest.MonkeyPatch) -> None:
    from smart_git_commit import cli as cli_mod

    class _Collector:
        def collect(self, *, max_diff_chars: int) -> GitContext:  # noqa: ARG002
            return GitContext(
                branch="main",
                status_porcelain="M a.txt",
                staged_diff="diff --git a/a.txt b/a.txt\n+hello\n",
                diff_truncated=False,
                original_diff_chars=10,
            )

    class _Client:
        def __enter__(self) -> "_Client":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

        def create(self, *, model: str, messages: object, max_tokens: int, temperature: float) -> str:
            _ = (model, messages, max_tokens, temperature)
            return "feat: add commit generator"

    # Patch the imported modules used inside cli.main.
    monkeypatch.setattr("smart_git_commit.git_context.GitContextCollector", _Collector)
    monkeypatch.setattr("smart_git_commit.llm_client.ChatCompletionsClient.from_config", lambda cfg: _Client())

    runner = CliRunner()
    result = runner.invoke(
        cli_mod.app,
        ["--api-key", "k", "--base-url", "https://example.com", "--print-git-command"],
        env={"SGC_API_KEY": "k"},
    )
    assert result.exit_code == 0
    assert "feat: add commit generator" in result.output
    assert "git commit -m" in result.output
