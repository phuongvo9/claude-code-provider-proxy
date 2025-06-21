The detailed unit test implementation plan for main.py has been created in TODO_UNIT_TESTS.md. It
  includes:

  1. Test structure organization
  2. Request validation tests for:
    - Invalid JSON format
    - Missing required fields
    - Invalid model names
    - Stream vs non-stream requests
  3. Response conversion tests for:
    - Text content blocks
    - Tool use blocks
    - Tool result blocks
    - Error handling
  4. Model selection logic tests for:
    - Opus model mapping
    - Sonnet model mapping
    - Haiku model mapping
    - Unknown model handling
  5. Error handling tests for:
    - OpenAI API errors
    - Authentication errors
    - Rate limiting
    - Invalid requests
  6. Middleware tests for:
    - Request ID generation
    - Timing metrics
    - Header propagation