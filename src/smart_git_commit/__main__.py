"""Module entrypoint: `python -m smart_git_commit`."""

from __future__ import annotations

from smart_git_commit.cli import app


def main() -> None:
    """Run the CLI application."""

    app()


if __name__ == "__main__":
    main()

