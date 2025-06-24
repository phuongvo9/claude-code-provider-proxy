# Model-Agnostic Tool Support

The claude-code-provider-proxy now supports **model-agnostic tool calling**, allowing any OpenAI-compatible model—including DeepSeek-V3, Gemini-Lite, and others—to discover and invoke the same tool set you already expose for Claude 4 Code.

## Architecture Overview

```
┌─────────┐       ┌──────────────────────────┐
│  User   │  -->  │  Proxy (this repo)       │
└─────────┘       │  • adds tool metadata    │
                  │  • normalises prompts    │
                  │  • post-processes calls  │
                  └────────────┬─────────────┘
                               │
                ┌──────────────▼──────────────┐
                │ Any chat completion backend │
                │ – Claude / GPT / Gemini / … │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │  Tool-runner (mcp, web …)   │
                └─────────────────────────────┘
```

## How It Works

The system uses **one unified codepath** that decides:

1. **Does the target model support structured tool calling natively?**
   → Inject a `tools=[…]` block.

2. **If not:** Teach it via *prompt scaffolding* and parse JSON in the reply.

3. **After the model responds:** Execute or forward the requested tool call.

## Supported Models

### Native Tool Support
These models get the full OpenAI-style `tools` parameter:

- **OpenAI**: `gpt-4`, `gpt-4o`, `gpt-3.5-turbo`, etc.
- **Anthropic**: `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`, `claude-4-opus`, etc.
- **Google**: `gemini-2.5-flash`, `gemini-2.5-pro`, etc.
- **DeepSeek**: `deepseek-r1-0528`, etc.
- **Mistral**: `magistral-small-2506`, `magistral-medium-2506`, etc.
- **And many more...**

### Scaffold Support
Unknown models automatically get prompt-based tool instructions, making them tool-capable through text parsing.

## Available Tools

The system provides these built-in tools:

- **`web_search`**: Search the Internet and return top results
- **`read_file`**: Read a project file from the filesystem
- **`write_file`**: Write content to a project file
- **`list_directory`**: List contents of a directory
- **`execute_command`**: Execute a shell command in the project directory

## Integration

### For Known Tool-Capable Models

The system automatically detects models with native tool support and sends standard OpenAI tool calls:

```json
{
  "model": "gpt-4",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "web_search",
        "description": "Search the Internet and return top results.",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {"type": "string"},
            "recency_days": {"type": "integer", "minimum": 1, "default": 30}
          },
          "required": ["query"]
        }
      }
    }
  ]
}
```

### For Unknown Models

Unknown models get a system prompt with tool instructions:

```
Available tools:
- `web_search`: Search the Internet and return top results.
- `read_file`: Read a project file.
- `write_file`: Write content to a project file.
- `list_directory`: List contents of a directory.
- `execute_command`: Execute a shell command in the project directory.

When you need one of the above functions, reply with a JSON block:
{ "tool": "<name>", "arguments": { ... } }
and nothing else on that turn.
```

## Response Processing

The system automatically detects and executes tool calls in both formats:

### Native Format
```json
{
  "choices": [{
    "message": {
      "tool_calls": [{
        "type": "function",
        "function": {
          "name": "web_search",
          "arguments": "{\"query\": \"Python tutorials\"}"
        }
      }]
    }
  }]
}
```

### Scaffolded Format
```json
{
  "choices": [{
    "message": {
      "content": "I'll search for that.\n\n{\"tool\": \"web_search\", \"arguments\": {\"query\": \"Python tutorials\"}}"
    }
  }]
}
```

## Adding New Tools

To add a new tool:

1. **Define the tool** in `src/tools.py`:
```python
{
    "type": "function", 
    "function": {
        "name": "my_new_tool",
        "description": "Description of what the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Parameter description"},
                "param2": {"type": "integer", "description": "Another parameter"}
            },
            "required": ["param1"]
        }
    }
}
```

2. **Implement the executor** in `src/tool_executor.py`:
```python
def _execute_my_new_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute my new tool."""
    param1 = arguments.get("param1", "")
    param2 = arguments.get("param2", 0)
    
    # Your tool logic here
    result = do_something(param1, param2)
    
    return {
        "success": True,
        "result": result,
        "error": None
    }
```

3. **Register the executor** in the `execute_tool` function:
```python
def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if name == "my_new_tool":
            return _execute_my_new_tool(arguments)
        # ... existing tools
```

## Testing

Run the model-agnostic tool tests:

```bash
source .venv/bin/activate
python -m pytest tests/test_model_agnostic_tools.py -v
```

Run all tests:

```bash
source .venv/bin/activate  
python -m pytest tests/ -v
```

## Benefits

- **Universal compatibility**: Any OpenAI-compatible model can use tools
- **Single source of truth**: All models share the same tool definitions
- **Automatic fallback**: Unknown models get prompt-based tool access
- **Zero changes for existing models**: Claude 4 and GPT-4 keep their native flow
- **Easy extensibility**: Add new tools once, available everywhere

## Implementation Status

| Task                                                                                                      | Done? |
| --------------------------------------------------------------------------------------------------------- | ----- |
| ✅ Drop the four new modules into your proxy (`tools.py`, `capabilities.py`, `llm_client.py`, `runtime.py`). | ✅     |
| ✅ Wire `prepare_chat_request` + `extract_tool_call` into your request / response flow.                      | ✅     |
| ✅ Confirm `execute_tool()` exists with basic tools (web search, file ops, etc.).                           | ✅     |
| ✅ Add unit tests & run in CI.                                                                               | ✅     |
| ✅ Update docs / README so contributors know how to register new tools.                                      | ✅     |

The model-agnostic tool system is now fully implemented and tested!
