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
    assert res == expected  # model routing logic


def test_count_tokens_basic(main_module):
    msg = main_module.Message(role="user", content="hello")
    total = main_module.count_tokens_for_anthropic_request(
        messages=[msg],
        system="sys",
        model_name="gpt-4",
        tools=None,
    )
    assert total == 16  # 4 base +4 role +5 content +3 system


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
    assert total == 24