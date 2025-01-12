"""Tests for settings serialization"""

import pytest
import json
from config.settings import LLMSettings

def test_secret_str_serialization():
    """Test that SecretStr fields are properly serialized to JSON"""
    settings = LLMSettings(
        openai_api_key="test-key-123",
        deepseek_api_key="test-key-456",
        gemini_api_key="test-key-789"
    )
    
    # Convert to JSON and back
    json_str = settings.model_dump_json()
    data = json.loads(json_str)
    
    # Verify secret fields are plain strings
    assert data["openai_api_key"] == "test-key-123"
    assert data["deepseek_api_key"] == "test-key-456"
    assert data["gemini_api_key"] == "test-key-789"
    
    # Verify None values are handled
    settings = LLMSettings()
    json_str = settings.model_dump_json()
    data = json.loads(json_str)
    assert data["openai_api_key"] is None
    assert data["deepseek_api_key"] is None
    assert data["gemini_api_key"] is None

def test_get_llm_config_serialization():
    """Test that get_llm_config() returns serializable data"""
    settings = LLMSettings(
        model="openai/gpt-4",
        openai_api_key="test-key-123"
    )
    
    config = settings.get_llm_config()
    json_str = json.dumps(config)
    data = json.loads(json_str)
    
    assert data["model"] == "openai/gpt-4"
    assert data["api_key"] == "test-key-123"
    assert data["base_url"] is None
