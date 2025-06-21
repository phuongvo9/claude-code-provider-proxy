import importlib
import os
import types

import pytest

import capabilities


@pytest.fixture(autouse=True)
def _patch_env_and_capabilities(monkeypatch, tmp_path):
    # Mandatory env-vars for main.Settings
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("BIG_MODEL_NAME", "big-model")
    monkeypatch.setenv("SMALL_MODEL_NAME", "small-model")

    # Stub expensive I/O in capabilities
    monkeypatch.setattr(capabilities, "_ensure_fresh_local_copy", lambda: None)

    # Ensure a deterministic capability map for provider_supports_tools
    monkeypatch.setattr(
        capabilities,
        "get_model_capabilities",
        lambda: {"big-model": {"tools"}, "no-tools": set()},
    )

    # Force a fresh import of main after the patches above
    if "main" in globals():
        importlib.reload(globals()["main"])
    else:
        import main  # noqa: F401


@pytest.fixture
def main_module():
    import importlib, main

    return importlib.reload(main)