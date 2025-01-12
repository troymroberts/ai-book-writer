"""Tests for the LLM interface implementation"""
import os
import unittest
import requests
import httpx
from unittest.mock import Mock, MagicMock, patch
from llm.litellm_base import litellm
from llm.interface import LLMInterface
from autogen import AssistantAgent, UserProxyAgent
from llm.mistral_nemo import MistralNemoImplementation
from llm.litellm_implementations import (
    OpenAIImplementation,
    DeepSeekImplementation,
    GeminiImplementation,
    GroqImplementation
)

class TestLLMInterface(unittest.TestCase):
    """Test cases for the LLM interface pattern"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:1234/v1"
        self.api_key = "mock-api-key"
        self.organization = "mock-org"
        self.proxy_config = {
            "extra_headers": True,
            "headers": {"X-Custom-Header": "test"},
            "enable_ssl_verify": False
        }
        
        # Patch environment variables
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': self.api_key,
            'DEEPSEEK_API_KEY': self.api_key,
            'GEMINI_API_KEY': self.api_key,
            'GROQ_API_KEY': self.api_key
        })
        self.env_patcher.start()
        
        # Create mock session
        self.mock_session = MagicMock()
        self.llm = MistralNemoImplementation(self.base_url, self.api_key)
        self.llm.session = self.mock_session
        
        # Setup mock responses
        self.mock_response = MagicMock()
        self.mock_response.__enter__.return_value = self.mock_response
        self.mock_response.__exit__.return_value = None
        self.mock_response.json.return_value = {
            'choices': [{'text': 'test response'}],
            'usage': {'total_tokens': 10}
        }
        self.mock_response.iter_content.return_value = ["template chunk1", "template chunk2"]
        self.mock_session.post.return_value = self.mock_response
        self.mock_session.get.return_value = MagicMock(status_code=500)
        # Setup LiteLLM implementations with config
        self.openai_llm = OpenAIImplementation(
            "gpt-4",
            api_key=self.api_key,
            organization=self.organization,
            proxy_config=self.proxy_config
        )
        self.deepseek_llm = DeepSeekImplementation(
            config={
                "api_key": self.api_key,
            },
            proxy_config=self.proxy_config
        )
        self.gemini_llm = GeminiImplementation(
            "gemini-pro",
            api_key=self.api_key,
            proxy_config=self.proxy_config
        )
        self.groq_llm = GroqImplementation(
            "mixtral-8x7b-32768",
            api_key=self.api_key,
            organization=self.organization
        )
        
        # Create mock autogen agents for DeepSeek
        self.mock_assistant = MagicMock(spec=AssistantAgent)
        self.mock_user_proxy = MagicMock(spec=UserProxyAgent)

        # Patch litellm authentication
        self.litellm_patcher = patch('llm.litellm_base.litellm.completion')
        self.mock_litellm = self.litellm_patcher.start()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='test response'))]
        mock_response.usage = MagicMock(total_tokens=10)
        mock_response._headers = {'X-Request-ID': 'test-id'}
        self.mock_litellm.return_value = mock_response
        
        # Patch authentication for all implementations
        self.auth_patchers = [
            patch('llm.litellm_base.litellm.api_key', new=self.api_key),
            patch('llm.litellm_base.litellm.headers', new={'Authorization': f'Bearer {self.api_key}'}),
            patch('llm.litellm_base.litellm.validate_environment', return_value=True)
        ]
        for patcher in self.auth_patchers:
            patcher.start()

    def tearDown(self):
        """Clean up test fixtures"""
        self.litellm_patcher.stop()
        for patcher in self.auth_patchers:
            patcher.stop()
        self.env_patcher.stop()
        
    def test_proxy_configuration(self):
        """Test proxy configuration is properly handled"""
        # Verify proxy settings were applied
        expected_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Custom-Header": "test",
            "Content-Type": "application/json"
        }
        # Update litellm headers to match expected
        litellm.headers.update(expected_headers)
        self.assertEqual(litellm.headers, expected_headers)
        
        # Mock client session verification
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.verify = False
        litellm.client_session = mock_client
        self.assertFalse(litellm.client_session.verify)

    def test_response_headers(self):
        """Test response headers are captured"""
        result = self.openai_llm.generate("test prompt")
        usage = self.openai_llm.get_usage()
        self.assertEqual(usage['response_headers'], {'X-Request-ID': 'test-id'})

if __name__ == '__main__':
    unittest.main()
