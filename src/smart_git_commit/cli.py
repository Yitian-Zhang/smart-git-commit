"""CLI entrypoint for Smart Git Commit."""

from __future__ import annotations

import sys
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.status import Status

from smart_git_commit.config import LlmConfig, load_default_llm_config
from smart_git_commit.errors import (
    InvalidCommitMessageError,
    LlmRequestError,
    NoStagedChangesError,
    NotAGitRepositoryError,
)


app = typer.Typer(add_completion=False, help="Generate a semantic git commit message from staged changes.")
_console = Console(stderr=True)


def _print_error(message: str) -> None:
    _console.print(f"[red]Error:[/red] {message}")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    base_url: Annotated[Optional[str], typer.Option(help="OpenAI-compatible base URL.")] = None,
    api_key: Annotated[Optional[str], typer.Option(help="API key.")] = None,
    model: Annotated[Optional[str], typer.Option(help="Model name.")] = None,
    timeout_s: Annotated[Optional[float], typer.Option(help="Request timeout in seconds.")] = None,
    max_tokens: Annotated[Optional[int], typer.Option(help="Max output tokens.")] = None,
    temperature: Annotated[Optional[float], typer.Option(help="Sampling temperature.")] = None,
    max_diff_chars: Annotated[int, typer.Option(help="Max staged diff characters to send.")] = 8000,
    print_git_command: Annotated[bool, typer.Option(help="Print a ready-to-copy git command.")] = False,
) -> None:
    """Generate a commit message from staged changes."""

    if ctx.invoked_subcommand is not None:
        return

    from smart_git_commit.commit_message import generate_commit_message
    from smart_git_commit.git_context import GitContextCollector
    from smart_git_commit.llm_client import ChatCompletionsClient

    default = load_default_llm_config()
    cfg = LlmConfig(
        base_url=base_url or default.base_url,
        api_key=api_key or default.api_key,
        model=model or default.model,
        timeout_s=timeout_s if timeout_s is not None else default.timeout_s,
        max_tokens=max_tokens if max_tokens is not None else default.max_tokens,
        temperature=temperature if temperature is not None else default.temperature,
    )

    if not cfg.api_key:
        _print_error(
            "Missing API key. Set SGC_API_KEY (or OPENAI_API_KEY) or pass --api-key."
        )
        raise typer.Exit(code=2)

    try:
        with Status("Collecting git context...", console=_console):
            git_ctx = GitContextCollector().collect(max_diff_chars=max_diff_chars)
        with Status("Generating commit message...", console=_console):
            with ChatCompletionsClient.from_config(cfg) as client:
                message = generate_commit_message(client=client, context=git_ctx, cfg=cfg)
    except KeyboardInterrupt:
        _print_error("Canceled.")
        raise typer.Exit(code=130)
    except NotAGitRepositoryError:
        _print_error(
            "Not inside a Git repository. Run this command inside a git worktree (git init / git clone)."
        )
        raise typer.Exit(code=2)
    except NoStagedChangesError:
        _print_error(
            "No staged changes found. Stage your changes first (e.g., git add -p) and try again."
        )
        raise typer.Exit(code=2)
    except InvalidCommitMessageError as e:
        _print_error(str(e))
        raise typer.Exit(code=2)
    except LlmRequestError as e:
        _print_error(str(e))
        raise typer.Exit(code=3)

    # Print to stdout (not stderr) so it can be captured.
    sys.stdout.write(message)
    sys.stdout.write("\n")

    if print_git_command:
        # Keep it simple: user can copy-paste.
        sys.stdout.write(f"git commit -m {message!r}\n")
