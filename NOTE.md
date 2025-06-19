# Result

it is working with OpenRouter Claude Code Provider Proxy

it seems what have to use OPEN AI API key - No Support for OpenRouter API key

```
> which model are you
  ⎿  API Error (Connection error.) · Retrying in 1 seconds… (attempt 1/10)
    ⎿  TypeError (fetch failed)
  ⎿  API Error (Connection error.) · Retrying in 1 seconds… (attempt 2/10)
    ⎿  TypeError (fetch failed)
  ⎿  API Error (Connection error.) · Retrying in 2 seconds… (attempt 3/10)
    ⎿  TypeError (fetch failed)
  ⎿  API Error (Connection error.) · Retrying in 5 seconds… (attempt 4/10)
    ⎿  TypeError (fetch failed)
  ⎿  API Error (Connection error.) ·
```
# how it works?

The Claude Code Provider Proxy acts as an intermediary between the user and the Claude AI model. When a user sends a request for code generation or modification, the proxy intercepts this request and forwards it to the Claude model. Once the model generates a response, the proxy can apply additional processing or filtering before sending the final output back to the user.
# Commands



# Attempts

```

> which model are you
  ⎿ API Error: 402 {"error":{"type":"api_error","message":"Error code: 402 - {'error': {'message': 
    'Insufficient credits. Add more using https://openrouter.ai/settings/credits', 'code': 402}}"}}

> which model are you
  ⎿ API Error: 404 {"error":{"type":"not_found_error","message":"Error code: 404 - {'error': {'message': 'No 
    endpoints found that support tool use. To learn more about provider routing, visit: 
    https://openrouter.ai/docs/provider-routing', 'code': 404}}"}
```

It looks like proxies requests works but the endpoint does not accept the payload

```json
{"timestamp": "2025-06-17T10:53:07.033447+00:00", "level": "ERROR", "logger": "AnthropicProxy", "detail": {"event": "request_failure", "message": "Request failed: Error code: 429 - {'error': {'message': 'Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day', 'code': 429, 'metadata': {'headers': {'X-RateLimit-Limit': '50', 'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1750204800000'}, 'provider_name': None}}, 'user_id': 'user_2ycixVJ953ICUk6VBtjpitvP7Pq'}", "request_id": "9da25b30-6b68-490f-8024-3617726eddd3", "data": {"status_code": 429, "duration_ms": 10977.659832977224, "error_type": "rate_limit_error", "client_ip": "127.0.0.1"}, "error": {"name": "RateLimitError", "message": "Error code: 429 - {'error': {'message': 'Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day', 'code': 429, 'metadata': {'headers': {'X-RateLimit-Limit': '50', 'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1750204800000'}, 'provider_name': None}}, 'user_id': 'user_2ycixVJ953ICUk6VBtjpitvP7Pq'}", "args": ["Error code: 429 - {'error': {'message': 'Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day', 'code': 429, 'metadata': {'headers': {'X-RateLimit-Limit': '50', 'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1750204800000'}, 'provider_name': None}}, 'user_id': 'user_2ycixVJ953ICUk6VBtjpitvP7Pq'}"]}}}
```