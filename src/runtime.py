# runtime.py
import json
import logging
import re
from typing import Dict, Any, Optional, List

log = logging.getLogger(__name__)

# Pattern to extract JSON objects from text
_JSON_EXTRACT = re.compile(r"\{[\s\S]*?\}")


def extract_tool_call(
    response: Dict[str, Any],
    *,
    fallback_text_search: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Works for *both* native and scaffolded calls.

    Native call ➜ assistant 'tool_calls' or 'function_call' message.
    Scaffolded call ➜ parse first JSON object present in text.
    
    Returns a dict with 'name' and 'arguments' keys if a tool call is found.
    """
    # 1. Native function-call format (OpenAI style)
    choices = response.get("choices")
    if not choices:
        return None
        
    msg = choices[0].get("message", {})
    
    # Check for tool_calls (newer OpenAI format)
    if "tool_calls" in msg and msg["tool_calls"]:
        tool_call = msg["tool_calls"][0]
        if tool_call.get("type") == "function" and "function" in tool_call:
            func = tool_call["function"]
            arguments = func.get("arguments", {})
            # Parse arguments if they're a JSON string
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    log.warning("Failed to parse tool_call arguments as JSON")
                    arguments = {}
            return {
                "name": func.get("name"),
                "arguments": arguments
            }

    # Check for function_call (older format)
    if "function_call" in msg:
        func = msg["function_call"]
        arguments = func.get("arguments", "{}")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                log.warning("Failed to parse function_call arguments as JSON")
                arguments = {}
        return {
            "name": func.get("name"),
            "arguments": arguments
        }

    # 2. Fallback: scan the text for JSON tool calls
    if fallback_text_search:
        content = msg.get("content", "")
        if not content:
            return None
            
        # Look for JSON objects in the content - be more flexible with regex
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, content)
        
        for match in matches:
            try:
                obj = json.loads(match)
                # Check if it looks like a tool call
                if isinstance(obj, dict) and "tool" in obj and "arguments" in obj:
                    return {
                        "name": obj["tool"],
                        "arguments": obj["arguments"]
                    }
                # Also check for alternative formats
                elif isinstance(obj, dict) and "name" in obj and "arguments" in obj:
                    return {
                        "name": obj["name"],
                        "arguments": obj["arguments"]
                    }
            except json.JSONDecodeError:
                continue  # Try next match
    
    return None


def extract_multiple_tool_calls(
    response: Dict[str, Any],
    *,
    fallback_text_search: bool = True,
) -> List[Dict[str, Any]]:
    """
    Extract multiple tool calls from a response.
    Returns a list of dicts with 'name' and 'arguments' keys.
    """
    tool_calls = []
    
    # 1. Native function-call format (OpenAI style)
    choices = response.get("choices")
    if not choices:
        return tool_calls
        
    msg = choices[0].get("message", {})
    
    # Check for tool_calls (newer OpenAI format)
    if "tool_calls" in msg and msg["tool_calls"]:
        for tool_call in msg["tool_calls"]:
            if tool_call.get("type") == "function" and "function" in tool_call:
                func = tool_call["function"]
                arguments = func.get("arguments", {})
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        log.warning("Failed to parse tool_call arguments as JSON")
                        arguments = {}
                tool_calls.append({
                    "name": func.get("name"),
                    "arguments": arguments
                })
        return tool_calls

    # Check for single function_call (older format)
    if "function_call" in msg:
        func = msg["function_call"]
        arguments = func.get("arguments", "{}")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                log.warning("Failed to parse function_call arguments as JSON")
                arguments = {}
        tool_calls.append({
            "name": func.get("name"),
            "arguments": arguments
        })
        return tool_calls

    # 2. Fallback: scan the text for JSON tool calls  
    if fallback_text_search:
        content = msg.get("content", "")
        if content:
            matches = _JSON_EXTRACT.findall(content)
            for match in matches:
                try:
                    obj = json.loads(match)
                    # Check if it looks like a tool call
                    if isinstance(obj, dict) and "tool" in obj and "arguments" in obj:
                        tool_calls.append({
                            "name": obj["tool"],
                            "arguments": obj["arguments"]
                        })
                    elif isinstance(obj, dict) and "name" in obj and "arguments" in obj:
                        tool_calls.append({
                            "name": obj["name"],
                            "arguments": obj["arguments"]
                        })
                except json.JSONDecodeError:
                    continue
    
    return tool_calls


def is_tool_call_response(response: Dict[str, Any]) -> bool:
    """Check if a response contains a tool call."""
    return extract_tool_call(response) is not None
