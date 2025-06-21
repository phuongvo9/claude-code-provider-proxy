# TODO: Add unit tests for request validation - NOT YET TESTED
# tests/unit/test_request_validation.py
import pytest
import json
from fastapi.testclient import TestClient
from src.main import app, MessagesRequest

client = TestClient(app)

@pytest.mark.asyncio
async def test_invalid_json():
    """Test invalid JSON format in request"""
    response = client.post("/v1/messages", data="invalid{json")
    assert response.status_code == 400
    assert "Invalid JSON body" in response.text

@pytest.mark.asyncio
async def test_missing_required_fields():
    """Test request with missing required fields"""
    # Test missing 'model' field
    response = client.post("/v1/messages", json={"max_tokens": 100})
    assert response.status_code == 422
    assert "field required" in response.text

@pytest.mark.asyncio
async def test_invalid_model_name():
    """Test request with invalid model name"""
    # Test invalid model name
    response = client.post("/v1/messages", json={
        "model": "invalid-model",
        "max_tokens": 100,
        "messages": []
    })
    assert response.status_code == 200  # Should default to small model

@pytest.mark.asyncio
async def test_stream_request():
    """Test stream request behavior"""
    response = client.post("/v1/messages", json={
        "model": "anthropic/claude-3-opus",
        "max_tokens": 100,
        "messages": [],
        "stream": True
    })
    assert response.status_code == 200
    # Test non-stream behavior
    response = client.post("/v1/messages", json={
        "model": "anthropic/claude-3-opus",
        "max_tokens": 100,
        "messages": [],
        "stream": False
    })
    assert response.status_code == 200