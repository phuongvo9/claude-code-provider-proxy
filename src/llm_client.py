# llm_client.py
import json
import logging
from typing import List, Dict, Any, Optional

from tools import BASE_TOOLS
from capabilities import provider_supports_tools

log = logging.getLogger(__name__)


def _system_scaffold(tools: List[Dict[str, Any]]) -> str:
    """Human-readable tool teaching for models WITHOUT native function API."""
    funcs = [
        f"- `{t['function']['name']}`: {t['function']['description']}"
        for t in tools
    ]
    how_to = (
        "When you need one of the above functions, reply with a JSON block:\n"
        '{ "tool": "<name>", "arguments": { ... } }\n'
        "and nothing else on that turn."
    )
    return "Available tools:\n" + "\n".join(funcs) + "\n\n" + how_to


def prepare_chat_request(
    model: str,
    messages: List[Dict[str, Any]],
    *,
    tools: Optional[List[Dict[str, Any]]] = None,
    **extra,
) -> Dict[str, Any]:
    """
    Returns an OpenAI-compatible payload ready to send downstream.
    Adds tool metadata if supported, otherwise adds a scaffold prompt.
    """
    tools = tools or BASE_TOOLS
    
    # Check if this model supports native structured tools
    tool_support = provider_supports_tools(model)
    if tool_support is True:  # Only use native tools for models we KNOW support them
        log.debug("Injecting native tool block for %s", model)
        return {
            "model": model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",  # ✅ lets backend models decide freely
            **extra,
        }

    # Fallback: textual instruction for models without native tool support
    # This includes both False (known not to support) and None (unknown)
    log.debug("Model %s lacks native tool support – using scaffold", model)
    scaffold = _system_scaffold(tools)
    
    # Add scaffold to system message or create new system message
    enhanced_messages = []
    system_message_found = False
    
    for msg in messages:
        if msg.get("role") == "system":
            # Enhance existing system message
            existing_content = msg.get("content", "")
            enhanced_content = f"{existing_content}\n\n{scaffold}".strip()
            enhanced_messages.append({"role": "system", "content": enhanced_content})
            system_message_found = True
        else:
            enhanced_messages.append(msg)
    
    # If no system message found, add one at the beginning
    if not system_message_found:
        enhanced_messages.insert(0, {"role": "system", "content": scaffold})
    
    return {
        "model": model,
        "messages": enhanced_messages,
        **extra,
    }


def should_use_structured_tools(model: str) -> bool:
    """Check if a model should use structured tool calling."""
    return provider_supports_tools(model) is not False
