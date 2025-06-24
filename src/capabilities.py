"""
capabilities.py – single public helper: get_model_capabilities()
"""
from __future__ import annotations

import functools
import json
import logging
import pathlib
import time
from typing import Final

import requests  # add to your deps; tiny

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Where we persist the fetched JSON
CAPS_PATH: Final = pathlib.Path(__file__).with_name("OPENROUTER_SUPPORT_MODELS.json")

# Remote endpoint that returns {"data":[...]} same shape as your example
OPENROUTER_ENDPOINT: Final = (
    "https://openrouter.ai/api/v1/models?expand=supported_parameters"
)

# Re-check after this many seconds (0  ➜  refresh every cold start)
REFRESH_TTL_S: Final = 0

# Hand overrides & permanent fallbacks
MODEL_CAPABILITIES_OVERRIDES: dict[str, set[str]] = {
    # ----------------------------- OpenAI ----------------------------------
    "gpt-4o": {"tools"},
    "gpt-4o-mini": {"tools"},
    "gpt-4": {"tools"},
    "gpt-4-turbo": {"tools"},
    "gpt-3.5-turbo": {"tools"},

    # ----------------------------- Anthropic ----------------------------------
    "anthropic/claude-3-opus:beta": {"tools"},
    "anthropic/claude-3-opus": {"tools"},
    "anthropic/claude-3-sonnet": {"tools"},
    "anthropic/claude-3-haiku": {"tools"},
    "anthropic/claude-3.5-sonnet": {"tools"},
    "anthropic/claude-3.5-haiku": {"tools"},
    "anthropic/claude-opus-4": {"tools"},
    "anthropic/claude-sonnet-4": {"tools"},

    # ----------------------------- Google Gemini ----------------------------------
    "google/gemini-2.5-flash-lite-preview-06-17": {"tools"},
    "google/gemini-2.5-flash": {"tools"},
    "google/gemini-2.5-flash-preview-05-20": {"tools"},
    "google/gemini-2.5-flash-preview-05-20:thinking": {"tools"},
    "google/gemini-2.5-pro": {"tools"},
    "google/gemini-2.5-pro-preview": {"tools"},
    "google/gemini-2.5-pro-preview-05-06": {"tools"},
    "google/gemini-2.5-pro-preview-06-05": {"tools"},
    "google/gemini-2.5-pro-preview-05-06": {"tools"},

    # ----------------------------- Mistral / Magistral / Devstral ----------------------------------
    "mistralai/magistral-small-2506": {"tools"},
    "mistralai/magistral-medium-2506": {"tools"},
    "mistralai/magistral-medium-2506:thinking": {"tools"},
    "mistralai/mistral-medium-3": {"tools"},
    "mistralai/devstral-small": {"tools"},
    "mistralai/devstral-small:free": {"tools"},

    # ----------------------------- MiniMax & others ----------------------------------
    "minimax/minimax-m1:extended": {"tools"},
    "openai/o3-pro": {"tools"},
    "openai/codex-mini": {"tools"},
    "arcee-ai/caller-large": {"tools"},
    "arcee-ai/virtuoso-large": {"tools"},

    # ----------------------------- DeepSeek subset with tools ----------------------------------
    "deepseek/deepseek-r1-0528": {"tools"},
    "deepseek/deepseek-r1-0528-qwen3-8b": set(),  # no tools
    "deepseek/deepseek-r1-distill-qwen-7b": set(),  # no tools
    "deepseek/deepseek-r1-0528-qwen3-8b:free": set(),  # no tools

    # ----------------------------- Qwen subset with tools ----------------------------------
    "qwen/qwen3-235b-a22b": {"tools"},
    "qwen/qwen3-30b-a3b": {"tools"},
    "qwen/qwq-32b": {"tools"},

    # ----------------------------- OSS / ":free" skus (no tool support) ----------------------------------
    "mistralai/mixtral-8x7b-instruct": set(),
    "mistralai/mixtral-8x7b-instruct:free": set(),
    "deepseek/deepseek-r1-distill-llama-70b:free": set(),
    "meta-llama/llama-3.2-3b-instruct:free": set(),
    "meta-llama/llama-3.2-1b-instruct:free": set(),
    "microsoft/phi-3-mini-128k-instruct:free": set(),
    "google/gemma-2-9b-it:free": set(),
    "huggingfaceh4/zephyr-7b-beta:free": set(),
    "openchat/openchat-7b:free": set(),
    "nousresearch/nous-capybara-7b:free": set(),
    "gryphe/mythomist-7b:free": set(),
    "undi95/toppy-m-7b:free": set(),
    "sarvamai/sarvam-m:free": set(),
    "sentientagi/dobby-mini-unhinged-plus-llama-3.1-8b": set(),
    "thedrummer/valkyrie-49b-v1": set(),
    "google/gemma-3n-e4b-it:free": set(),
}

# ---------------------------------------------------------------------------
# INTERNALS
# ---------------------------------------------------------------------------


def _remote_supported_models() -> list[dict]:
    """Hit OpenRouter and return raw JSON list."""
    resp = requests.get(OPENROUTER_ENDPOINT, timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]


def _should_refresh(path: pathlib.Path) -> bool:
    if not path.exists():
        return True
    if REFRESH_TTL_S == 0:
        return True
    return time.time() - path.stat().st_mtime > REFRESH_TTL_S


def _ensure_fresh_local_copy() -> None:
    """Fetch remote metadata if our cached file is stale or missing."""
    if not _should_refresh(CAPS_PATH):
        return

    try:
        data = _remote_supported_models()
        CAPS_PATH.write_text(json.dumps({"data": data}, indent=2))
        logging.info("Refreshed %s (%s models)", CAPS_PATH.name, len(data))
    except Exception as exc:
        logging.warning("Could not refresh model list: %s", exc)


@functools.lru_cache(maxsize=1)
def _load_capabilities_file() -> dict[str, set[str]]:
    try:
        parsed = json.loads(CAPS_PATH.read_text())["data"]
        return {
            m["id"]: {"tools"} if "tools" in m.get("supported_parameters", []) else set()
            for m in parsed
        }
    except Exception as exc:
        logging.warning("Falling back to overrides only: %s", exc)
        return {}


def _merge_with_overrides(base: dict[str, set[str]]) -> dict[str, set[str]]:
    merged: dict[str, set[str]] = {**base}  # shallow copy
    for mid, caps in MODEL_CAPABILITIES_OVERRIDES.items():
        merged[mid] = caps  # hand-curated wins
    return merged


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------


def get_model_capabilities() -> dict[str, set[str]]:
    """
    1. Makes sure local OpenRouter list is up to date (once per process).
    2. Loads capabilities from disk.
    3. Applies overrides.
    4. Returns a cached dict[str, set[str]] for the remainder of the process.
    """
    _ensure_fresh_local_copy()
    return _get_capabilities_cached()


@functools.lru_cache(maxsize=1)
def _get_capabilities_cached() -> dict[str, set[str]]:
    return _merge_with_overrides(_load_capabilities_file())


# Providers that ARE tool-capable (prefix match, case-insensitive)
TOOL_CAPABLE_PREFIXES = (
    # OpenAI & derivatives
    "gpt-", "openai/",
    # Anthropic Claude
    "claude", "anthropic/",
    # Google Gemini family (tool-calling in JSON spec)
    "google/gemini", "gemini",
    # DeepSeek-V3 exposes function calling behind OpenAI API
    "deepseek-llm", "deepseek/",
    # Mistral & variants
    "mistralai/", "mistral/",
    # Meta models
    "meta-llama/", "llama-",
    # Qwen family
    "qwen/",
    # Additional tool-capable models
    "minimax/", "x-ai/", "arcee-ai/",
)

# Models whose providers are confirmed NOT to implement the tool-calling API
NON_TOOL_MODELS = {"google/palm-2-chat-bison"}

def provider_supports_tools(model_name: str) -> bool | None:
    """
    Returns:
    - True: Model is known to support tools natively
    - False: Model is known NOT to support tools 
    - None: Unknown/uncertain - let caller decide
    
    This enables model-agnostic tool calling where unknown models
    can use prompt scaffolding as fallback.
    """
    # Explicitly check for models that don't support tools
    if model_name.lower() in NON_TOOL_MODELS:
        return False
    
    # Check capabilities from loaded model data
    caps = get_model_capabilities()
    if model_name in caps:
        return "tools" in caps[model_name]
    
    # Check if model matches any tool-capable prefix
    m = model_name.lower()
    if any(m.startswith(pfx) for pfx in TOOL_CAPABLE_PREFIXES):
        return True
    
    # Return None for unknown models - let the caller decide strategy
    return None


def supports_structured_tools(model_name: str) -> bool:
    """
    Compatibility function that returns True for models that support
    native structured tool calling, False otherwise.
    Used by the model-agnostic tool system.
    """
    result = provider_supports_tools(model_name)
    return result is not False  # True or None -> True, False -> False
