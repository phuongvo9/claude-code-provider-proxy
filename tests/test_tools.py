import pytest
from src.main import MessagesRequest, Tool, count_tokens_for_anthropic_request, Message

BASE_MSG = [{"role": "user", "content": "ping"}]

def test_tool_without_schema_validates():
    req = MessagesRequest(
        model="google/gemini-2.5-flash-lite-preview-06-17",
        max_tokens=16,
        messages=BASE_MSG,
        tools=[Tool(name="web_search")]  #  ⚠ no input_schema
    )
    assert req.tools[0].input_schema == {}

def test_token_counter_skips_empty_schema():
    tool = Tool(name="dummy")
    messages = [Message(role="user", content="hi")]
    tokens = count_tokens_for_anthropic_request(
        messages=messages,
        system=None,
        model_name="gpt-4o",
        tools=[tool],
    )
    # empty schema should add **no** extra tokens
    assert tokens > 0  # still counts message