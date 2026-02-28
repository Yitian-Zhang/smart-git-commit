from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from smart_git_commit.config import load_default_llm_config


def test_loads_dotenv_from_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "SGC_API_KEY=from_env_file\nSGC_MODEL=from_env_file_model\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("SGC_API_KEY", raising=False)
    monkeypatch.delenv("SGC_MODEL", raising=False)

    cfg = load_default_llm_config()
    assert cfg.api_key == "from_env_file"
    assert cfg.model == "from_env_file_model"


def test_dotenv_does_not_override_existing_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("SGC_API_KEY=from_env_file\n", encoding="utf-8")
    monkeypatch.setenv("SGC_API_KEY", "from_real_env")

    cfg = load_default_llm_config()
    assert cfg.api_key == "from_real_env"


def test_loads_dotenv_from_git_root_when_running_in_subdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    (repo / ".env").write_text("SGC_API_KEY=from_git_root\n", encoding="utf-8")
    sub = repo / "sub"
    sub.mkdir()

    monkeypatch.chdir(sub)
    monkeypatch.delenv("SGC_API_KEY", raising=False)

    cfg = load_default_llm_config()
    assert cfg.api_key == "from_git_root"
