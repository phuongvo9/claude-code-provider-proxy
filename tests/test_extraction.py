#!/usr/bin/env python3

import json
import re
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from runtime import extract_tool_call

def test_json_extraction():
    # Test simple scaffolded tool call
    content = '{"tool": "web_search", "arguments": {"query": "test"}}'
    response = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': content
            }
        }]
    }

    result = extract_tool_call(response)
    print('Extracted:', result)

    # Test regex
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, content)
    print('Regex matches:', matches)

    if matches:
        try:
            obj = json.loads(matches[0])
            print('Parsed JSON:', obj)
        except Exception as e:
            print('JSON parse error:', e)

if __name__ == '__main__':
    test_json_extraction()
