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
    # Token counting is approximate, just ensure it's reasonable
    assert total > 0 and total < 50


def test_count_tokens_with_tool(main_module):
    msg = main_module.Message(role="user", content="hi")
    tool = main_module.Tool(name="search", description="desc", input_schema={})
    total = main_module.count_tokens_for_anthropic_request(
        messages=[msg],
        system=None,
        model_name="gpt-4",
        tools=[tool],
    )
    # Should be more tokens than without tools
    assert total > 5  # basic message should be at least 5 tokens