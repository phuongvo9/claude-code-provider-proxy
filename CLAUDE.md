# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Getting Started

### Prerequisites
- Python 3.10+
- OpenRouter API key
- [uv](https://github.com/astral-sh/uv)

### Configuration
Create a `.env` file with your configuration:
\`\`\`env
OPENAI_API_KEY=<key>
BIG_MODEL_NAME=google/gemini-2.5-pro-preview
SMALL_MODEL_NAME=google/gemini-2.0-flash-lite-001
LOG_LEVEL=DEBUG
\`\`\`
See `config.py` for more configuration options.

#### Useful environment variables
- \`CLAUDE_CODE_EXTRA_BODY\`
- \`MAX_THINKING_TOKENS\`
- \`API_TIMEOUT_MS\`
- \`ANTHROPIC_BASE_URL\`
- \`DISABLE_TELEMETRY\`
- \`DISABLE_ERROR_REPORTING\`

### Running the Server
\`\`\`bash
source .venv/bin/activate
uv run src/main.py
\`\`\`

### Running Claude Code with the Proxy
\`\`\`bash
ANTHROPIC_BASE_URL=http://localhost:8080 claude
\`\`\`

## Common Commands

### Building and Dependencies
- Install dependencies: \`source .venv/bin/activate && uv run src/main.py\` (installs dependencies and runs the server)
- Install development dependencies: \`pip install -e ".[dev]" --no-deps\` (this command might need adjustment based on actual dev dependency management)

### Linting and Formatting
- Lint with Ruff: \`ruff check .\`
- Format with Ruff: \`ruff format .\`
- Type checking with MyPy: \`mypy src/\`

### Testing
- Run all tests: \`pytest\`
- Run tests with coverage: \`pytest --cov=claude_proxy\`
- Run tests in parallel: \`pytest-xdist\` (if installed and configured)
- Run a single test file: \`pytest tests/test_file.py\`
- Run a specific test by name: \`pytest -k "test_feature_name"\`

## Code Architecture

The project is structured as follows:

- **`src/`**: Contains the main application code.
    - **`main.py`**: FastAPI application setup and server initialization.
    - **`config.py`**: Handles application configuration loading and management.
    - **`proxy.py`**: Core logic for request/response translation and forwarding.
    - **`models.py`**: Pydantic models for request and response data structures.
    - **`constants.py`**: Defines constants used throughout the application.
    - **`logging_config.py`**: Configures logging for the application.

- **`tests/`**: Contains unit and integration tests for the application.

- **`pyproject.toml`**: Project metadata, dependencies, and build configurations.

- **`README.md`**: Project overview and usage instructions.

- **`.env`**: Environment variables for configuration (should not be committed).
