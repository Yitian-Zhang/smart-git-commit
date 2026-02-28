from __future__ import annotations

import respx
from httpx import Response

from smart_git_commit.llm_client import ChatCompletionsClient, ChatMessage


@respx.mock
def test_chat_completions_client_calls_expected_endpoint() -> None:
    route = respx.post("https://example.com/v1/chat/completions").mock(
        return_value=Response(
            200,
            json={"choices": [{"message": {"content": "feat: add x"}}]},
        )
    )

    client = ChatCompletionsClient(base_url="https://example.com", api_key="k", timeout_s=5)
    try:
        out = client.create(
            model="m",
            messages=[ChatMessage(role="user", content="hi")],
            max_tokens=10,
            temperature=0.0,
        )
    finally:
        client.close()

    assert out == "feat: add x"
    assert route.called

