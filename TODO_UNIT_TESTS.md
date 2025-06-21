```python
# tests/conftest.py
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
```

```python
# tests/test_capabilities.py
import pathlib
import time

import pytest

import capabilities


def test_should_refresh_file_absent(tmp_path):
    p = tmp_path / "missing.json"
    assert capabilities._should_refresh(p) is True  # file missing triggers refresh :contentReference[oaicite:0]{index=0}


def test_should_refresh_ttl(monkeypatch, tmp_path):
    test_file = tmp_path / "caps.json"
    test_file.write_text("{}")
    monkeypatch.setattr(capabilities, "REFRESH_TTL_S", 3600)
    monkeypatch.setattr(
        capabilities,
        "_time",
        types.SimpleNamespace(time=lambda: time.time() + 10),
        raising=False,
    )
    # Fresh file within TTL ➜ no refresh
    assert capabilities._should_refresh(test_file) is False :contentReference[oaicite:1]{index=1}


def test_provider_supports_tools_true():
    assert capabilities.provider_supports_tools("big-model") is True :contentReference[oaicite:2]{index=2}


def test_provider_supports_tools_false():
    assert capabilities.provider_supports_tools("no-tools") is False :contentReference[oaicite:3]{index=3}
```

```python
# tests/test_main.py
import importlib

import pytest

import main


@pytest.mark.parametrize(
    ("client_model", "expected"),
    [
        ("claude-opus-latest", "big-model"),
        ("claude-haiku-202402", "small-model"),
        ("totally-unknown-id", "small-model"),
    ],
)
def test_select_target_model(monkeypatch, main_module, client_model, expected):
    res = main_module.select_target_model(client_model, request_id="r1")
    assert res == expected  # model routing logic :contentReference[oaicite:4]{index=4}


def test_count_tokens_basic(main_module):
    msg = main_module.Message(role="user", content="hello")
    total = main_module.count_tokens_for_anthropic_request(
        messages=[msg],
        system="sys",
        model_name="gpt-4",
        tools=None,
    )
    assert total == 16  # 4 base +4 role +5 content +3 system :contentReference[oaicite:5]{index=5}


def test_count_tokens_with_tool(main_module):
    msg = main_module.Message(role="user", content="hi")
    tool = main_module.Tool(name="search", description="desc", input_schema={})
    total = main_module.count_tokens_for_anthropic_request(
        messages=[msg],
        system=None,
        model_name="gpt-4",
        tools=[tool],
    )
    # 4 base +4 role +2 content +2 tool-prefix +6 name +4 desc +2 schema
    assert total == 24 :contentReference[oaicite:6]{index=6}
```

### Notes

* Tests isolate external effects by patching `capabilities._ensure_fresh_local_copy` and substituting a deterministic capability map, preventing network or disk writes.
* Environment variables are injected via `monkeypatch` so `main.Settings` instantiates without leaking secrets.
* Reloading `main` after patching guarantees its import-time side effects use the stubbed capabilities.
* Parameterized assertions cover positive, negative and fallback branches in `select_target_model`, while `count_tokens_for_anthropic_request` arithmetic is verified on minimal and tool-rich payloads.
* The `capabilities` unit tests exercise refresh logic and capability queries without real I/O or HTTP.
