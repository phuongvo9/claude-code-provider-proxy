#!/usr/bin/env python3
"""
Test script to verify the fix for the AttributeError: 'NoneType' object has no attribute 'get'
"""

from src.runtime import extract_tool_call

def test_function_call_none():
    """Test that function_call: null doesn't crash"""
    print("Testing function_call: null...")
    
    response_with_null = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "I understand your request, but I don't need to use any tools for this.",
                "function_call": None
            }
        }]
    }
    
    try:
        result = extract_tool_call(response_with_null)
        print(f"✅ Success: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_no_function_call():
    """Test that missing function_call doesn't crash"""
    print("Testing missing function_call...")
    
    response_no_call = {
        "choices": [{
            "message": {
                "role": "assistant", 
                "content": "Just a regular response without any tool calls."
            }
        }]
    }
    
    try:
        result = extract_tool_call(response_no_call)
        print(f"✅ Success: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_valid_function_call():
    """Test that valid function calls still work"""
    print("Testing valid function_call...")
    
    response_with_call = {
        "choices": [{
            "message": {
                "role": "assistant",
                "function_call": {
                    "name": "web_search",
                    "arguments": '{"query": "Python tutorials", "recency_days": 7}'
                }
            }
        }]
    }
    
    try:
        result = extract_tool_call(response_with_call)
        print(f"✅ Success: {result}")
        return result is not None and result.get("name") == "web_search"
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_scaffolded_tool_call():
    """Test that scaffolded tool calls still work"""
    print("Testing scaffolded tool call...")
    
    response_scaffolded = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": 'I\'ll search for that information.\n\n{"tool": "web_search", "arguments": {"query": "Python tutorials", "recency_days": 7}}'
            }
        }]
    }
    
    try:
        result = extract_tool_call(response_scaffolded)
        print(f"✅ Success: {result}")
        return result is not None and result.get("name") == "web_search"
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing the runtime fix for function_call: null crash\n")
    
    tests = [
        test_function_call_none,
        test_no_function_call,
        test_valid_function_call,
        test_scaffolded_tool_call
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 All tests passed! The fix is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
