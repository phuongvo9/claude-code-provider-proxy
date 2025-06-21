❯ .venv/bin/python .venv/bin/pytest

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
Test session starts (platform: darwin, Python 3.12.10, pytest 8.3.5, pytest-sugar 1.0.0)
cachedir: .pytest_cache
rootdir: /Users/Phuong.VoHuy/Documents/Projects/Personal/tools/openai-support-only/claude-code-provider-proxy
configfile: pytest.ini
testpaths: tests
plugins: respx-0.22.0, anyio-4.9.0, sugar-1.0.0, asyncio-0.26.0, mock-3.14.0, cov-6.1.1
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 9 items                                                                                                    

 tests/test_capabilities.py::test_should_refresh_file_absent ✓                                          11% █▎        
 tests/test_capabilities.py::test_should_refresh_ttl ✓                                                  22% ██▎       
 tests/test_capabilities.py::test_provider_supports_tools_true ✓                                        33% ███▍      
 tests/test_capabilities.py::test_provider_supports_tools_false ✓                                       44% ████▌     
 tests/test_main.py::test_select_target_model[claude-opus-latest-big-model] ✓                           56% █████▋    
 tests/test_main.py::test_select_target_model[claude-haiku-202402-small-model] ✓                        67% ██████▋   
 tests/test_main.py::test_select_target_model[totally-unknown-id-small-model] ✓                         78% ███████▊  

―――――――――――――――――――――――――――――――――――――――――――――― test_count_tokens_basic ―――――――――――――――――――――――――――――――――――――――――――――――

main_module = <module 'main' from '/Users/Phuong.VoHuy/Documents/Projects/Personal/tools/openai-support-only/claude-code-provider-proxy/src/main.py'>

    def test_count_tokens_basic(main_module):
        msg = main_module.Message(role="user", content="hello")
        total = main_module.count_tokens_for_anthropic_request(
            messages=[msg],
            system="sys",
            model_name="gpt-4",
            tools=None,
        )
>       assert total == 16  # 4 base +4 role +5 content +3 system
E       assert 7 == 16

tests/test_main.py:25: AssertionError

 tests/test_main.py::test_count_tokens_basic ⨯                                                          89% ████████▉ 

―――――――――――――――――――――――――――――――――――――――――――― test_count_tokens_with_tool ―――――――――――――――――――――――――――――――――――――――――――――

main_module = <module 'main' from '/Users/Phuong.VoHuy/Documents/Projects/Personal/tools/openai-support-only/claude-code-provider-proxy/src/main.py'>

    def test_count_tokens_with_tool(main_module):
        msg = main_module.Message(role="user", content="hi")
        tool = main_module.Tool(name="search", description="desc", input_schema={})
        total = main_module.count_tokens_for_anthropic_request(
            messages=[msg],
            system=None,
            model_name="gpt-4",
            tools=[tool],
        )
        # 4 base +4 role +2 content +2 tool-prefix +6 name +4 desc +2 schema
>       assert total == 24
E       assert 11 == 24

tests/test_main.py:38: AssertionError

 tests/test_main.py::test_count_tokens_with_tool ⨯                                                     100% ██████████
============================================== short test summary info ===============================================
FAILED tests/test_main.py::test_count_tokens_basic - assert 7 == 16
FAILED tests/test_main.py::test_count_tokens_with_tool - assert 11 == 24

Results (0.86s):
       7 passed
       2 failed
         - tests/test_main.py:17 test_count_tokens_basic
         - tests/test_main.py:28 test_count_tokens_with_tool