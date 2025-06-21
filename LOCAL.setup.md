# start proxy server
uv run src/main.py

# Run claude with the proxy
ANTHROPIC_BASE_URL=http://localhost:8080 claude

# test all tests
uv run pytest

# Run specific test
uv run pytest tests/test_main.py