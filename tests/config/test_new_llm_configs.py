"""Tests for new LLM configuration templates"""

import pytest
from config_templates.technical.o1_preview import O1_PREVIEW_CONFIG
from config_templates.technical.gemini_flash import GEMINI_FLASH_CONFIG

class TestO1PreviewConfig:
    def test_required_fields(self):
        assert "model" in O1_PREVIEW_CONFIG
        assert "api_key" in O1_PREVIEW_CONFIG
        assert "temperature" in O1_PREVIEW_CONFIG
        assert "max_tokens" in O1_PREVIEW_CONFIG
        
    def test_temperature_range(self):
        assert 0 <= O1_PREVIEW_CONFIG["temperature"] <= 2
        
    def test_max_tokens_positive(self):
        assert O1_PREVIEW_CONFIG["max_tokens"] > 0
        
    def test_retry_config(self):
        assert "max_retries" in O1_PREVIEW_CONFIG
        assert "retry_min_wait" in O1_PREVIEW_CONFIG
        assert "retry_max_wait" in O1_PREVIEW_CONFIG

class TestGeminiFlashConfig:
    def test_required_fields(self):
        assert "model" in GEMINI_FLASH_CONFIG
        assert "api_key" in GEMINI_FLASH_CONFIG
        assert "temperature" in GEMINI_FLASH_CONFIG
        assert "max_tokens" in GEMINI_FLASH_CONFIG
        
    def test_temperature_range(self):
        assert 0 <= GEMINI_FLASH_CONFIG["temperature"] <= 1
        
    def test_max_tokens_positive(self):
        assert GEMINI_FLASH_CONFIG["max_tokens"] > 0
        
    def test_safety_settings(self):
        assert "safety_settings" in GEMINI_FLASH_CONFIG
        assert isinstance(GEMINI_FLASH_CONFIG["safety_settings"], dict)
        
    def test_candidate_count(self):
        assert "candidate_count" in GEMINI_FLASH_CONFIG
        assert GEMINI_FLASH_CONFIG["candidate_count"] >= 1

@pytest.mark.parametrize("config", [O1_PREVIEW_CONFIG, GEMINI_FLASH_CONFIG])
class TestCommonConfig:
    def test_streaming_support(self, config):
        assert "stream" in config
        assert isinstance(config["stream"], bool)
        
    def test_timeout_positive(self, config):
        assert "timeout" in config
        assert config["timeout"] > 0
        
    def test_request_timeout_positive(self, config):
        assert "request_timeout" in config
        assert config["request_timeout"] > 0
