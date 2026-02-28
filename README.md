# Smart Git Commit

Smart Git Commit (SGC) is a CLI tool that generates a Conventional Commit / Semantic Commit message from your **staged** Git changes using an **OpenAI-compatible Chat Completions API**.

## Features

- Generates commit messages in Conventional Commits format (e.g. `feat: ...`, `fix(scope): ...`)
- Reads staged changes (`git diff --staged`) so it fits existing Git workflows
- English CLI output (errors, help, status)
- Built-in validation + one automatic “fix” retry if the model output is not valid
- Performance-oriented defaults (diff truncation, short outputs, timeouts)

## Installation

### Option A: Run with `uv` (recommended)

```bash
uv run sgc --help
```

### Option B: Install as a package

```bash
pip install .
sgc --help
```

### Option C: Install from GitHub Release

You can install the latest release directly from GitHub:

```bash
# Replace v0.1.0 with the desired version
pip install https://github.com/Yitian-Zhang/smart-git-commit/releases/download/v0.1.0/smart_git_commit-0.1.0-py3-none-any.whl
```

## Quick Start

1) Stage your changes:

```bash
git add -p
```

2) Set an API key (choose one):

```bash
export SGC_API_KEY="..."
# or
export OPENAI_API_KEY="..."
```

3) Generate a commit message:

```bash
sgc --base-url "https://api.openai.com" --model "gpt-4o-mini"
```

4) (Optional) print a ready-to-copy git command:

```bash
sgc --print-git-command
```

## Configuration

SGC is designed to be minimal: environment variables + CLI flags.

SGC also supports a local `.env` file for convenience (loaded automatically on startup, and it will NOT override existing environment variables).

### Environment variables

- `SGC_API_KEY` (or `OPENAI_API_KEY`)
- `SGC_BASE_URL` (or `OPENAI_BASE_URL`, default: `https://api.openai.com/v1`)
- `SGC_MODEL` (or `OPENAI_MODEL`, default: `gpt-4o-mini`)
- `SGC_TIMEOUT_S` (default: `15`)
- `SGC_MAX_TOKENS` (default: `120`)
- `SGC_TEMPERATURE` (default: `0.2`)

### `.env` example

Create a `.env` file in your repo root (or current directory).

Recommended:

```bash
cp .env_template .env
```

Then edit `.env`:

```bash
SGC_API_KEY="your_key_here"
SGC_BASE_URL="https://api.openai.com/v1"
SGC_MODEL="gpt-4o-mini"

# For some providers, the OpenAI-compatible endpoint may NOT be under /v1.
# In that case, set SGC_BASE_URL to the prefix that contains /chat/completions.
# Example:
# SGC_BASE_URL="https://your-provider.example.com/api/v3"
```

### CLI flags

Run `sgc --help` to see the full list. Common flags:

- `--base-url`
- `--api-key`
- `--model`
- `--timeout-s`
- `--max-diff-chars` (default: `8000`)
- `--print-git-command`

## How It Works

1) Collects Git context from your current repo:
   - `git status --porcelain=v1`
   - `git diff --staged --no-color`
2) Sends a prompt to an OpenAI-compatible `/v1/chat/completions` endpoint.
3) Validates the header against Conventional Commits rules.
4) If invalid, performs one extra “fix” attempt.
5) Prints the final message to stdout.

## Exit Codes

- `0`: success
- `2`: user/input error (not a git repo, no staged changes, invalid message)
- `3`: LLM request failed
- `130`: canceled (Ctrl+C)

## Troubleshooting

- **"No staged changes found"**: stage changes first (`git add -p`).
- **"Not inside a Git repository"**: run inside a git worktree.
- **Timeouts**: try `--timeout-s 30` or reduce `--max-diff-chars`.

## Development

```bash
uv python install 3.12
uv run -p 3.12 pytest --cov=smart_git_commit
```

## Release Process

1. Update `version` in `pyproject.toml`.
2. Create and push a git tag starting with `v` (e.g. `v0.1.0`).

```bash
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions will automatically:
1. Build the Python package (`.whl` and `.tar.gz`).
2. Create a GitHub Release.
3. Upload the artifacts.
