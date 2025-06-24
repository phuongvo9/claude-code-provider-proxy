# runtime.py
import json
import logging
import re
from typing import Dict, Any, Optional, List

log = logging.getLogger(__name__)

# A more robust pattern to extract JSON objects, handling nested structures.
_JSON_EXTRACT_ROBUST = re.compile(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}')


def _parse_arguments(args: Any) -> Dict[str, Any]:
    """Safely parse tool call arguments from a string to a dict."""
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        try:
            # Handle common case of JSON string
            return json.loads(args)
        except json.JSONDecodeError:
            log.warning("Failed to parse arguments string as JSON: %r", args)
            # Fallback for non-JSON strings, treat as a single arg
            return {"content": args}
    log.warning("Unsupported argument type: %s", type(args))
    return {}


def extract_multiple_tool_calls(
    response: Dict[str, Any], fallback_text_search: bool = True
) -> List[Dict[str, Any]]:
    """
    Extracts all tool calls from a model's response, supporting multiple formats
    and prioritizing official structures (tool_calls > function_call > text).
    This function is nil-safe and robust to malformed or partial responses.
    """
    extracted_calls = []
    if not response or "choices" not in response or not response["choices"]:
        return []

    msg = response.get("choices", [{}])[0].get("message", {})
    if not msg:
        return []

    # 1. Native tool_calls format (current OpenAI standard)
    # Use .get() with a default of None, then check `is` for type safety
    tool_calls_raw = msg.get("tool_calls")
    if isinstance(tool_calls_raw, list):
        for tool_call in tool_calls_raw:
            if (
                isinstance(tool_call, dict)
                and tool_call.get("type") == "function"
                and (func := tool_call.get("function"))
                and isinstance(func, dict)
                and (name := func.get("name"))
            ):
                arguments = _parse_arguments(func.get("arguments", {}))
                extracted_calls.append({"name": name, "arguments": arguments})
        # If we found valid tool calls, trust this as the source of truth
        if extracted_calls:
            return extracted_calls

    # 2. Legacy function_call format (if no tool_calls were found)
    func_call = msg.get("function_call")
    if isinstance(func_call, dict):
        if name := func_call.get("name"):
            arguments = _parse_arguments(func_call.get("arguments", {}))
            extracted_calls.append({"name": name, "arguments": arguments})
        if extracted_calls:
            return extracted_calls

    # 3. Fallback: scan the text content for JSON tool calls
    if fallback_text_search:
        content = msg.get("content", "")
        if content and isinstance(content, str):
            matches = _JSON_EXTRACT_ROBUST.findall(content)
            for match in matches:
                try:
                    obj = json.loads(match)
                    # Heuristic check for tool call structure
                    if isinstance(obj, dict):
                        name = obj.get("tool") or obj.get("name")
                        args = obj.get("arguments")
                        if name and args is not None:
                            parsed_args = _parse_arguments(args)
                            # Avoid duplicates from fallback if content mirrors structured data
                            is_duplicate = any(
                                c["name"] == name and c["arguments"] == parsed_args
                                for c in extracted_calls
                            )
                            if not is_duplicate:
                                extracted_calls.append({
                                    "name": name,
                                    "arguments": parsed_args
                                })
                except json.JSONDecodeError:
                    continue

    return extracted_calls


def extract_tool_call(
    response: Dict[str, Any], fallback_text_search: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Extracts a single tool call from a model's response.
    Returns the first tool call found, using the same robust extraction logic
    as extract_multiple_tool_calls.
    """
    tool_calls = extract_multiple_tool_calls(response, fallback_text_search)
    return tool_calls[0] if tool_calls else None


def is_tool_call_response(response: Dict[str, Any]) -> bool:
    """
    Checks if the response message contains a tool call.
    """
    if not response or "choices" not in response or not response["choices"]:
        return False
    message = response["choices"][0].get("message", {})
    return "tool_calls" in message or "function_call" in message
