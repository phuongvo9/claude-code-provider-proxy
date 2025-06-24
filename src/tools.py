# tools.py
from typing import Dict, List, Any

BASE_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the Internet and return top results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "recency_days": {"type": "integer", "minimum": 1, "default": 30, "description": "How recent the results should be in days"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a project file from the filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The file path to read"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a project file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The file path to write to"},
                    "content": {"type": "string", "description": "The content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List contents of a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The directory path to list"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a shell command in the project directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to execute"},
                    "working_directory": {"type": "string", "description": "Working directory for the command (optional)"},
                },
                "required": ["command"],
            },
        },
    },
]


def get_tool_by_name(name: str) -> Dict[str, Any] | None:
    """Get a tool definition by its name."""
    for tool in BASE_TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None


def get_all_tool_names() -> List[str]:
    """Get all available tool names."""
    return [tool["function"]["name"] for tool in BASE_TOOLS]
