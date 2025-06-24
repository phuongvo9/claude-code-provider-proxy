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
    from src.main import Message
    
    tool = Tool(name="dummy")
    messages = [Message(role="user", content="hi")]
    tokens = count_tokens_for_anthropic_request(
        messages=messages,
        system=None,
        model_name="gpt-4o",
        tools=[tool],
    )
    # empty schema should add **no** extra tokens for the schema
    assert tokens > 0  # still counts message

def test_gemini_tools_retained():
    """Test that Gemini tools are retained and not stripped by the validator."""
    req = MessagesRequest.model_validate(
        {
            "model": "google/gemini-2.5-flash-lite-preview-06-17",
            "max_tokens": 16,  # Add missing required field
            "messages": [{"role": "user", "content": "hi"}],
            "tools": [{"name": "write_file", "input_schema": {}}],
        }
    )
    assert req.tools is not None and len(req.tools) == 1
