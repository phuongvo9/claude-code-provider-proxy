# tool_executor.py
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """Raised when a tool execution fails."""
    pass


def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool with the given arguments.
    Returns a dict with 'success', 'result', and optionally 'error' keys.
    """
    try:
        if name == "web_search":
            return _execute_web_search(arguments)
        elif name == "read_file":
            return _execute_read_file(arguments)
        elif name == "write_file":
            return _execute_write_file(arguments)
        elif name == "list_directory":
            return _execute_list_directory(arguments)
        elif name == "execute_command":
            return _execute_command(arguments)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {name}",
                "result": None
            }
    except Exception as e:
        log.exception(f"Error executing tool {name}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }


def _execute_web_search(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute web search (placeholder implementation)."""
    query = arguments.get("query", "")
    recency_days = arguments.get("recency_days", 30)
    
    if not query:
        return {
            "success": False,
            "error": "Query parameter is required",
            "result": None
        }
    
    # Placeholder implementation - in a real system, you'd integrate with
    # a search API like Google Custom Search, Bing, or DuckDuckGo
    result = {
        "search_query": query,
        "recency_days": recency_days,
        "results": [
            {
                "title": f"Search result for: {query}",
                "url": "https://example.com",
                "snippet": f"This is a placeholder search result for the query '{query}'. In a real implementation, this would be replaced with actual search results."
            }
        ],
        "note": "This is a placeholder implementation. Integrate with a real search API for production use."
    }
    
    return {
        "success": True,
        "result": result,
        "error": None
    }


def _execute_read_file(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute file reading."""
    path = arguments.get("path", "")
    
    if not path:
        return {
            "success": False,
            "error": "Path parameter is required",
            "result": None
        }
    
    try:
        file_path = Path(path)
        
        # Security check - prevent reading files outside the project directory
        # In production, you might want more sophisticated path validation
        if file_path.is_absolute() and not str(file_path).startswith(os.getcwd()):
            return {
                "success": False,
                "error": "Access denied: Cannot read files outside the project directory",
                "result": None
            }
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {path}",
                "result": None
            }
        
        if file_path.is_dir():
            return {
                "success": False,
                "error": f"Path is a directory, not a file: {path}",
                "result": None
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "result": {
                "path": str(file_path),
                "content": content,
                "size": len(content)
            },
            "error": None
        }
        
    except UnicodeDecodeError:
        return {
            "success": False,
            "error": f"Cannot read file as text (binary file?): {path}",
            "result": None
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied reading file: {path}",
            "result": None
        }


def _execute_write_file(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute file writing."""
    path = arguments.get("path", "")
    content = arguments.get("content", "")
    
    if not path:
        return {
            "success": False,
            "error": "Path parameter is required",
            "result": None
        }
    
    try:
        file_path = Path(path)
        
        # Security check - prevent writing files outside the project directory
        if file_path.is_absolute() and not str(file_path).startswith(os.getcwd()):
            return {
                "success": False,
                "error": "Access denied: Cannot write files outside the project directory",
                "result": None
            }
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "result": {
                "path": str(file_path),
                "bytes_written": len(content.encode('utf-8'))
            },
            "error": None
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied writing file: {path}",
            "result": None
        }


def _execute_list_directory(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute directory listing."""
    path = arguments.get("path", ".")
    
    try:
        dir_path = Path(path)
        
        # Security check
        if dir_path.is_absolute() and not str(dir_path).startswith(os.getcwd()):
            return {
                "success": False,
                "error": "Access denied: Cannot list directories outside the project directory",
                "result": None
            }
        
        if not dir_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {path}",
                "result": None
            }
        
        if not dir_path.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {path}",
                "result": None
            }
        
        items = []
        for item in dir_path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None
            })
        
        # Sort by name
        items.sort(key=lambda x: x["name"])
        
        return {
            "success": True,
            "result": {
                "path": str(dir_path),
                "items": items,
                "count": len(items)
            },
            "error": None
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied accessing directory: {path}",
            "result": None
        }


def _execute_command(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute shell command."""
    command = arguments.get("command", "")
    working_directory = arguments.get("working_directory", ".")
    
    if not command:
        return {
            "success": False,
            "error": "Command parameter is required",
            "result": None
        }
    
    try:
        # Security check for working directory
        work_dir = Path(working_directory)
        if work_dir.is_absolute() and not str(work_dir).startswith(os.getcwd()):
            return {
                "success": False,
                "error": "Access denied: Cannot execute commands outside the project directory",
                "result": None
            }
        
        # Execute the command with timeout
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        return {
            "success": True,
            "result": {
                "command": command,
                "working_directory": working_directory,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            },
            "error": None
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 30 seconds",
            "result": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute command: {str(e)}",
            "result": None
        }
