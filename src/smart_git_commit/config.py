"""Configuration utilities.

This project is intentionally minimal: environment variables + CLI flags.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess


@dataclass(frozen=True)
class LlmConfig:
    """LLM configuration.

    Attributes:
        base_url: Base URL of an OpenAI-compatible server. Example: https://api.openai.com/v1
        api_key: API key.
        model: Model name.
        timeout_s: Total request timeout in seconds.
        max_tokens: Upper bound of output tokens.
        temperature: Sampling temperature.
    """

    base_url: str
    api_key: str
    model: str
    timeout_s: float
    max_tokens: int
    temperature: float


_EXPORT_PREFIX_RE = re.compile(r"^export\s+", flags=re.IGNORECASE)


def _strip_optional_quotes(value: str) -> str:
    if len(value) >= 2 and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")):
        return value[1:-1]
    return value


def _load_dotenv_file(path: Path, *, override: bool = False) -> None:
    """Load key/value pairs from a dotenv file into os.environ.

    Notes:
        - This is intentionally minimal (no variable expansion).
        - By default, it does NOT override existing environment variables.
    """

    if not path.exists() or not path.is_file():
        return

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        line = _EXPORT_PREFIX_RE.sub("", line, count=1).strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        # Remove inline comments for unquoted values: KEY=abc # comment
        if value and value[0] not in ("\"", "'"):
            value = value.split(" #", 1)[0].rstrip()

        value = _strip_optional_quotes(value)

        if not override and key in os.environ:
            continue

        os.environ[key] = value


def _try_load_dotenv() -> None:
    """Best-effort .env loading.

    Resolution order:
        1) .env in current working directory
        2) .env in git repository root (if inside a repo)
    """

    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        _load_dotenv_file(cwd_env)
        return

    # Try repo root for common workflows (run from subdirectory).
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
            timeout=1.5,
        )
    except Exception:
        return

    if proc.returncode != 0:
        return

    root = (proc.stdout or "").strip()
    if not root:
        return

    root_env = Path(root) / ".env"
    _load_dotenv_file(root_env)


def load_default_llm_config() -> LlmConfig:
    """Load default configuration from environment variables.

    Precedence:
    - SGC_* variables
    - OPENAI_* variables (for convenience)

    Returns:
        A default LlmConfig.
    """

    _try_load_dotenv()

    base_url = os.getenv("SGC_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    api_key = os.getenv("SGC_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    model = os.getenv("SGC_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    timeout_s = float(os.getenv("SGC_TIMEOUT_S") or "15")
    max_tokens = int(os.getenv("SGC_MAX_TOKENS") or "120")
    temperature = float(os.getenv("SGC_TEMPERATURE") or "0.2")
    return LlmConfig(
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout_s=timeout_s,
        max_tokens=max_tokens,
        temperature=temperature,
    )
