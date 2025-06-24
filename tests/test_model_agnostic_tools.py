# test_model_agnostic_tools.py
import pytest
import json
from unittest.mock import Mock, patch

from llm_client import prepare_chat_request, should_use_structured_tools
from runtime import extract_tool_call, extract_multiple_tool_calls, is_tool_call_response
from tool_executor import execute_tool
from tools import BASE_TOOLS, get_tool_by_name, get_all_tool_names
from capabilities import provider_supports_tools, supports_structured_tools


class TestToolSystem:
    """Test the model-agnostic tool calling system."""
    
    def test_prepare_for_known_tool_capable_model(self):
        """Test that known tool-capable models get native tool blocks."""
        payload = prepare_chat_request(
            "gpt-4",
            [{"role": "user", "content": "Search the web for Python tutorials"}],
        )
        assert "tools" in payload
        assert len(payload["tools"]) > 0
        assert payload["tools"][0]["type"] == "function"

    def test_prepare_for_deepseek(self):
        """Test that DeepSeek models get native tool blocks."""
        payload = prepare_chat_request(
            "deepseek/deepseek-r1-0528",
            [{"role": "user", "content": "Search the web for AI news"}],
        )
        assert "tools" in payload
        
    def test_prepare_for_gemini(self):
        """Test that Gemini models get native tool blocks.""" 
        payload = prepare_chat_request(
            "google/gemini-2.5-flash",
            [{"role": "user", "content": "Read the README file"}],
        )
        assert "tools" in payload

    def test_scaffold_for_unknown_model(self):
        """Test that unknown models get scaffold prompts."""
        payload = prepare_chat_request(
            "mysterious-unknown-llm",
            [{"role": "user", "content": "Search the web for news"}],
        )
        # Should have system message with tool scaffold
        system_msg = None
        for msg in payload["messages"]:
            if msg["role"] == "system":
                system_msg = msg
                break
        
        assert system_msg is not None
        assert "Available tools:" in system_msg["content"]
        assert "web_search" in system_msg["content"]
        assert '"tool":' in system_msg["content"]

    def test_extract_native_tool_call(self):
        """Test extracting tool calls from native OpenAI format."""
        fake_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "arguments": '{"query": "Python tutorials", "recency_days": 7}'
                        }
                    }]
                }
            }]
        }
        
        tool_call = extract_tool_call(fake_response)
        assert tool_call is not None
        assert tool_call["name"] == "web_search"
        assert tool_call["arguments"]["query"] == "Python tutorials"
        assert tool_call["arguments"]["recency_days"] == 7

    def test_extract_scaffolded_tool_call(self):
        """Test extracting tool calls from scaffold format."""
        fake_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": 'I\'ll search for that information.\n\n{"tool": "web_search", "arguments": {"query": "Python tutorials", "recency_days": 7}}'
                }
            }]
        }
        
        tool_call = extract_tool_call(fake_response)
        assert tool_call is not None
        assert tool_call["name"] == "web_search"
        assert tool_call["arguments"]["query"] == "Python tutorials"
        assert tool_call["arguments"]["recency_days"] == 7

    def test_extract_multiple_tool_calls(self):
        """Test extracting multiple tool calls."""
        fake_response = {
            "choices": [{
                "message": {
                    "role": "assistant", 
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": "read_file",
                                "arguments": '{"path": "README.md"}'
                            }
                        },
                        {
                            "type": "function", 
                            "function": {
                                "name": "web_search",
                                "arguments": '{"query": "latest news"}'
                            }
                        }
                    ]
                }
            }]
        }
        
        tool_calls = extract_multiple_tool_calls(fake_response)
        assert len(tool_calls) == 2
        assert tool_calls[0]["name"] == "read_file"
        assert tool_calls[1]["name"] == "web_search"

    def test_is_tool_call_response(self):
        """Test detecting tool call responses."""
        # Response with native tool call
        native_msg = {
            "role": "assistant",
            "tool_calls": [{
                "type": "function",
                "function": {"name": "web_search", "arguments": '{"query": "test"}'}
            }]
        }
        assert is_tool_call_response(native_msg) is True
        
        # Response with function_call
        function_call_msg = {
            "role": "assistant",
            "function_call": {"name": "web_search", "arguments": '{"query": "test"}'}
        }
        assert is_tool_call_response(function_call_msg) is True
        
        # Response with function_call None (should be False)
        null_function_call_msg = {
            "role": "assistant",
            "function_call": None,
            "content": "Just a regular response"
        }
        assert is_tool_call_response(null_function_call_msg) is False
        
        # Response without tool call
        text_msg = {
            "role": "assistant",
            "content": "This is just a regular text response."
        }
        assert is_tool_call_response(text_msg) is False

    def test_tool_execution_web_search(self):
        """Test web search tool execution."""
        result = execute_tool("web_search", {"query": "Python", "recency_days": 30})
        assert result["success"] is True
        assert "results" in result["result"]
        assert result["result"]["search_query"] == "Python"

    def test_tool_execution_invalid_tool(self):
        """Test execution of non-existent tool."""
        result = execute_tool("nonexistent_tool", {})
        assert result["success"] is False
        assert "Unknown tool" in result["error"]

    def test_tool_execution_missing_args(self):
        """Test tool execution with missing required arguments."""
        result = execute_tool("web_search", {})  # missing query
        assert result["success"] is False
        assert "required" in result["error"].lower()

    def test_get_tool_by_name(self):
        """Test getting tool definition by name."""
        web_search_tool = get_tool_by_name("web_search")
        assert web_search_tool is not None
        assert web_search_tool["function"]["name"] == "web_search"
        
        nonexistent = get_tool_by_name("nonexistent")
        assert nonexistent is None

    def test_get_all_tool_names(self):
        """Test getting all available tool names."""
        names = get_all_tool_names()
        assert "web_search" in names
        assert "read_file" in names
        assert "write_file" in names
        assert len(names) > 0

    def test_capabilities_known_models(self):
        """Test capability detection for known models."""
        # Known tool-capable models
        assert provider_supports_tools("gpt-4") is True
        assert provider_supports_tools("anthropic/claude-3-opus") is True
        assert provider_supports_tools("google/gemini-2.5-flash") is True
        assert provider_supports_tools("deepseek/deepseek-r1-0528") is True
        
        # Models we know don't support tools
        assert provider_supports_tools("google/palm-2-chat-bison") is False

    def test_capabilities_unknown_models(self):
        """Test capability detection for unknown models."""
        # Unknown models should return None (let caller decide)
        result = provider_supports_tools("some-unknown-model-xyz")
        assert result is None

    def test_supports_structured_tools_function(self):
        """Test the compatibility function for structured tools."""
        # Should return True for known good models
        assert supports_structured_tools("gpt-4") is True
        
        # Should return False only for explicitly bad models
        assert supports_structured_tools("google/palm-2-chat-bison") is False
        
        # Should return True for unknown models (default to trying)
        assert supports_structured_tools("unknown-model") is True

    def test_no_function_call_does_not_crash(self):
        """Test that a response with no function call or None function_call doesn't crash."""
        # Model declines to call a tool - just returns normal text
        reply = {
            "choices": [{"message": {"role": "assistant", "content": "I can help you with that."}}]
        }
        assert extract_tool_call(reply) is None
        
        # Model returns function_call: null explicitly
        reply_with_null = {
            "choices": [{"message": {"role": "assistant", "content": "OK", "function_call": None}}]
        }
        assert extract_tool_call(reply_with_null) is None
        
        # Model returns empty function_call dict
        reply_with_empty = {
            "choices": [{"message": {"role": "assistant", "content": "OK", "function_call": {}}}]
        }
        assert extract_tool_call(reply_with_empty) is None

    def test_tool_choice_auto(self):
        """Test that tool_choice auto is added for tool-capable models."""
        from src.llm_client import prepare_chat_request
        payload = prepare_chat_request(
            "gemini-flash-preview",
            [{"role": "user", "content": "Run `ls` in the repo"}],
        )
        assert payload["tool_choice"] == "auto"
        assert any(t["function"]["name"] == "execute_command" for t in payload["tools"])


class TestToolExecutor:
    """Test individual tool executors."""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('builtins.open')
    def test_read_file_success(self, mock_open, mock_is_file, mock_exists):
        """Test successful file reading."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "file content"
        
        result = execute_tool("read_file", {"path": "test.txt"})
        assert result["success"] is True
        assert result["result"]["content"] == "file content"

    @patch('pathlib.Path.exists')
    def test_read_file_not_found(self, mock_exists):
        """Test reading non-existent file."""
        mock_exists.return_value = False
        
        result = execute_tool("read_file", {"path": "nonexistent.txt"})
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @patch('subprocess.run')
    def test_execute_command_success(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="command output",
            stderr=""
        )
        
        result = execute_tool("execute_command", {"command": "echo hello"})
        assert result["success"] is True
        assert result["result"]["exit_code"] == 0
        assert result["result"]["stdout"] == "command output"

    @patch('subprocess.run')
    def test_execute_command_timeout(self, mock_run):
        """Test command execution timeout."""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("test", 30)
        
        result = execute_tool("execute_command", {"command": "sleep 60"})
        assert result["success"] is False
        assert "timed out" in result["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
