from __future__ import annotations

import pytest


def test_module_entrypoint_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure it doesn't try to hit network, and exits deterministically.
    monkeypatch.setenv("SGC_API_KEY", "")

    from smart_git_commit.__main__ import main

    with pytest.raises(SystemExit):
        main()

