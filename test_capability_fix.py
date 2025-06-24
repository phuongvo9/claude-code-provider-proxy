#!/usr/bin/env python3
"""
Test script to verify the tool capability detection fix.
"""

from src.capabilities import provider_supports_tools

def test_tool_capability_detection():
    """Test various models to see if tool capability detection works correctly."""
    
    # Test cases with expected results
    test_cases = [
        # Known tool-supporting models
        ("gpt-4", True),
        ("anthropic/claude-3-sonnet", True),
        ("google/gemini-2.5-flash", True),
        ("deepseek/deepseek-r1-0528", True),
        
        # Models that match prefixes but might not be in overrides
        ("gpt-4o-new", True),  # Should match gpt- prefix
        ("claude-new-model", True),  # Should match claude prefix
        ("gemini-experimental", True),  # Should match gemini- prefix
        
        # Models that should return None (unknown)
        ("some-unknown-model", None),
        ("random-provider/random-model", None),
        
        # Models explicitly marked as not supporting tools
        ("google/palm-2-chat-bison", False),
    ]
    
    print("Testing tool capability detection...")
    print("=" * 50)
    
    for model_name, expected in test_cases:
        result = provider_supports_tools(model_name)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} {model_name}: expected {expected}, got {result}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_tool_capability_detection()
