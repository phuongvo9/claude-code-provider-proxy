import pathlib
import time
import types

import pytest

import capabilities


def test_should_refresh_file_absent(tmp_path):
    p = tmp_path / "missing.json"
    assert capabilities._should_refresh(p) is True  # file missing triggers refresh


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
    assert capabilities._should_refresh(test_file) is False


def test_provider_supports_tools_true():
    assert capabilities.provider_supports_tools("big-model") is True


def test_provider_supports_tools_false():
    assert capabilities.provider_supports_tools("no-tools") is False