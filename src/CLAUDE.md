# main.py Overview

This document provides a high-level explanation of the key components and request flow in `main.py` so that downstream tools or LLM agents can understand its behavior without accessing the source code directly.

## 1. Configuration and Environment

- **Environment Variables**: Uses `python-dotenv` to load `.env` values.
- **Settings**: Defines a `Settings` class (via Pydantic `BaseSettings`) to read:
  - API credentials (`openai_api_key`)
  - Model names for large/small workloads
  - Base URLs and referrer headers for OpenAI-compatible endpoints
  - App metadata (name, version), logging levels and output paths, host, port, and auto-reload flag.

## 2. Logging

- **JSONFormatter and ConsoleJSONFormatter**: Custom formatters to structure logs in JSON and optionally output to the console with styling.
- **LogEvent Enum**: Enumerates all structured event names used throughout the code (e.g., model selection, token counts, streaming interruptions).
- **LogRecord and LogError**: Data classes capturing event details, context data, request IDs, error payloads, and messages.
- **Logger Initialization**: Configured via `logging.config.dictConfig` to route messages through a single stream handler (stdout) and write to a file if specified.
- **Logging Helpers**: `debug()`, `info()`, `warning()`, `error()`, and `critical()` functions wrap calls to the central logger, attaching structured `LogRecord` instances.

## 3. OpenAI Client Setup

- Initializes an asynchronous OpenAI client (`openai.AsyncClient`) with:
  - API key and custom base URL for compatibility (e.g., OpenRouter).
  - Header injection (`HTTP-Referer`, app title) and timeout settings.
- Exits on failure to ensure the proxy cannot start without a working client.

## 4. Token Encoding and Counting

- **Encoder Cache**: Maintains a mapping from model name to a `tiktoken` encoder instance to minimize reload overhead.
- **get_token_encoder()**: Retrieves or creates an encoder for a given model.
- **count_tokens_for_anthropic_request()**: Estimates the input token count by summing tokens in system prompts, user/assistant messages, and optionally tool definitions. Emits a debug log with the result.

## 5. Message and Tool Conversion

- **convert_anthropic_to_openai_messages()**: Translates chat messages from Anthropic’s format into OpenAI’s expected sequence of message dictionaries, handling system text, user/assistant roles, and normalizing content blocks.
- **convert_anthropic_tools_to_openai()**: Maps Anthropic tool definitions to OpenAI function definitions, converting names, descriptions, and JSON schemas.
- **convert_anthropic_tool_choice_to_openai()**: Chooses between automatic or specific tool calls based on Anthropic’s `tool_choice` parameter.
- **_serialize_tool_result_content_for_openai()**: Flattens complex tool result objects (strings, lists of dicts, or arrays) into a single JSON or text string acceptable by OpenAI’s function call system.

## 6. Response Conversion and Error Mapping

- **convert_openai_to_anthropic_response()**: Takes an OpenAI chat completion response (streamed or full) and constructs an Anthropic-compatible response object:
  - Maps roles and content blocks back into the required structure.
  - Translates OpenAI stop reasons into Anthropic stop codes.
  - Wraps token usage stats.

- **Error Handling**:
  - `_get_anthropic_error_details_from_exc()`: Classifies various `openai` exceptions into Anthropic error types (e.g., authentication, rate limit).
  - `_format_anthropic_error_sse_event()`: Serializes errors into SSE event format for streaming endpoints.
  - `_build_anthropic_error_response()` and `_log_and_return_error_response()`: Construct JSON error responses for typical HTTP endpoints, logging the failure.

## 7. Streaming Handler

- **handle_anthropic_streaming_response_from_openai_stream()**: Bridges OpenAI’s async chunked stream into a sequence of Server-Sent Events (SSE) understood by Anthropic clients:
  - Generates unique Anthropic message IDs.
  - Tracks text blocks and tool invocations, correctly interleaving content.
  - Emits partial SSE payloads per chunk and finalizes on completion or interruption.

## 8. FastAPI Application

- **App Instantiation**: Creates a FastAPI app with title, description, version, and disables default docs endpoints.
- **Model Selection**: `select_target_model()` inspects the requested Anthropic model name and chooses an appropriate OpenAI-compatible model.
- **Endpoints**:
  - `POST /v1/messages`: Main chat completion proxy. Handles full and streaming requests, orchestrates conversions, calls the OpenAI client, and returns Anthropic-compliant responses.
  - `POST /v1/messages/count_tokens`: Utility endpoint to return estimated input token count without sending to OpenAI.
  - `GET /`: Health check endpoint (returns a simple status message).
- **Exception Handlers and Middleware**: Catches validation, JSON decode, generic HTTP errors, and logs them with structured details before returning errors to clients.

## 9. Entry Point

- Guards on `if __name__ == "__main__"` to allow running via Uvicorn or a direct Python invocation. Reads host, port, and reload flags from `Settings`.
