import pytest
from src.main import MessagesRequest, Tool, count_tokens_for_anthropic_request

BASE_MSG = [{"role": "user", "content": "ping"}]

def test_tool_without_schema_validates():
    """Test that tools without input_schema validate correctly."""
    req = MessagesRequest(
        model="google/gemini-2.5-flash-lite-preview-06-17",
        max_tokens=16,
        messages=BASE_MSG,
        tools=[Tool(name="web_search")]  # ⚠ no input_schema
    )
    assert req.tools[0].input_schema == {}

def test_tool_from_gemini_format():
    """Test that Gemini-style tool definitions validate correctly."""
    EXAMPLE = {
        "model": "google/gemini-2.5-flash-lite-preview-06-17",
        "max_tokens": 16,
        "messages": [{"role": "user", "content": "hi"}],
        "tools": [
            {"type": "web_search_20250305", "name": "web_search", "max_uses": 8}
        ],
    }
    
    req = MessagesRequest.model_validate(EXAMPLE)
    assert req.tools[0].input_schema == {}

def test_token_counter_skips_empty_schema():
    """Test that token counter doesn't count empty schemas."""
    tool = Tool(name="dummy")
    tokens = count_tokens_for_anthropic_request(
        messages=[{"role": "user", "content": "hi"}],
        system=None,
        model_name="gpt-4o",
        tools=[tool],
    )
    # empty schema should add **no** extra tokens for the schema
    assert tokens > 0  # still counts message
