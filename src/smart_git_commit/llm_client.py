"""OpenAI-compatible Chat Completions client."""

from __future__ import annotations

from dataclasses import dataclass

from urllib.parse import urlparse

import httpx

from smart_git_commit.config import LlmConfig
from smart_git_commit.errors import LlmRequestError


@dataclass(frozen=True)
class ChatMessage:
    """A single chat message."""

    role: str
    content: str


def _normalize_base_url(base_url: str) -> str:
    """Normalize base URL.

    Rules:
        - If the URL has no path (e.g. https://api.openai.com), append `/v1`.
        - If the URL already has a path (e.g. https://host/api/v3), keep it as-is.
        - If the URL ends with `/v1`, keep it.

    This keeps OpenAI convenience while supporting providers whose OpenAI-compatible
    endpoint is not under `/v1`.
    """

    base = base_url.strip().rstrip("/")
    if base.endswith("/v1"):
        return base

    parsed = urlparse(base)
    path = (parsed.path or "").rstrip("/")
    if path == "":
        return f"{base}/v1"
    return base


class ChatCompletionsClient:
    """A minimal client that speaks OpenAI-compatible Chat Completions."""

    def __init__(self, *, base_url: str, api_key: str, timeout_s: float) -> None:
        self._base_url = _normalize_base_url(base_url)
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout_s),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    @classmethod
    def from_config(cls, cfg: LlmConfig) -> "ChatCompletionsClient":
        """Create a client from config."""

        return cls(base_url=cfg.base_url, api_key=cfg.api_key, timeout_s=cfg.timeout_s)

    def close(self) -> None:
        """Close the underlying HTTP client."""

        self._client.close()

    def __enter__(self) -> "ChatCompletionsClient":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def create(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Create a chat completion and return the assistant content.

        Args:
            model: Model name.
            messages: Chat messages.
            max_tokens: Max output tokens.
            temperature: Sampling temperature.

        Returns:
            The assistant message content.
        """

        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            resp = self._client.post("/chat/completions", json=payload)
        except httpx.TimeoutException as e:
            raise LlmRequestError(
                "Request timed out. Try increasing --timeout-s or reducing --max-diff-chars."
            ) from e
        except httpx.HTTPError as e:
            raise LlmRequestError(f"HTTP request failed: {e}") from e

        if resp.status_code >= 400:
            detail = ""
            try:
                data = resp.json()
                detail = str(data.get("error") or data)
            except Exception:
                detail = (resp.text or "").strip()

            url = str(resp.request.url)
            hint = (
                "If you are using a non-OpenAI provider, ensure --base-url/SGC_BASE_URL points to the API prefix "
                "that contains `/chat/completions`."
            )
            suffix = f" {detail}" if detail else ""
            raise LlmRequestError(
                f"LLM request failed ({resp.status_code}) at {url}:{suffix}\n{hint}"
            )

        try:
            data = resp.json()
            choices = data["choices"]
            message = choices[0]["message"]
            content = message.get("content")
        except Exception as e:
            raise LlmRequestError("Invalid response schema from LLM server.") from e

        if not isinstance(content, str) or not content.strip():
            raise LlmRequestError("Empty response from LLM server.")

        return content.strip()
