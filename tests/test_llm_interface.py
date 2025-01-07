"""Tests for the LLM interface implementation"""
import os
import unittest
import requests
from unittest.mock import Mock, MagicMock, patch
from llm.interface import LLMInterface
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
        self.api_key = "mock-api-key"  # Always use mock API key for tests
        
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
        
        # Setup LiteLLM implementations with mocks
        self.openai_llm = OpenAIImplementation("gpt-4", self.api_key)
        self.deepseek_llm = DeepSeekImplementation("chat", self.api_key)
        self.gemini_llm = GeminiImplementation("gemini-pro", self.api_key)
        self.groq_llm = GroqImplementation("mixtral-8x7b-32768", self.api_key)
        
        # Patch litellm authentication
        self.litellm_patcher = patch('llm.litellm_base.litellm.completion')
        self.mock_litellm = self.litellm_patcher.start()
        self.mock_litellm.return_value = {
            'choices': [{'message': {'content': 'test response'}}],
            'usage': {'total_tokens': 10}
        }
        
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
        
    @patch('llm.mistral_nemo.requests.Session')
    def test_generate(self, mock_session):
        """Test text generation"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'text': 'test response'}],
            'usage': {'total_tokens': 10}
        }
        mock_session.return_value.post.return_value = mock_response
        
        # Test generation
        result = self.llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('litellm.completion')
    def test_openai_generate(self, mock_completion):
        """Test OpenAI text generation"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='test response'))],
            usage=MagicMock(total_tokens=10)
        )
        
        result = self.openai_llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('llm.litellm_base.litellm.completion')
    def test_deepseek_generate(self, mock_completion):
        """Test DeepSeek text generation"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='test response'))],
            usage=MagicMock(total_tokens=10)
        )
        
        result = self.deepseek_llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('llm.litellm_base.litellm.completion')
    def test_gemini_generate(self, mock_completion):
        """Test Gemini text generation"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='test response'))],
            usage=MagicMock(total_tokens=10)
        )
        
        result = self.gemini_llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('llm.litellm_base.litellm.completion')
    def test_groq_generate(self, mock_completion):
        """Test Groq text generation"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='test response'))],
            usage=MagicMock(total_tokens=10)
        )
        
        result = self.groq_llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('llm.mistral_nemo.requests.Session')
    def test_stream(self, mock_session):
        """Test streaming generation"""
        # Create a new LLM instance with mocked session
        llm = MistralNemoImplementation(self.base_url, "not-needed")
        
        # Setup mock response with proper byte encoding
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_session.return_value.post.return_value = mock_response
        
        # Test streaming
        result = list(llm.stream("test prompt"))
        self.assertEqual(result, ["chunk1", "chunk2"])
        
    @patch('llm.litellm_base.litellm.acompletion')
    async def test_openai_stream(self, mock_acompletion):
        """Test OpenAI streaming generation"""
        mock_acompletion.return_value = [
            {'choices': [{'delta': {'content': 'chunk1'}}]},
            {'choices': [{'delta': {'content': 'chunk2'}}]}
        ]
        
        result = []
        async for chunk in self.openai_llm.stream("test prompt"):
            result.append(chunk)
        self.assertEqual(result, ["chunk1", "chunk2"])
        
    def test_usage_tracking(self):
        """Test usage statistics tracking"""
        # Initial state
        usage = self.llm.get_usage()
        self.assertEqual(usage['total_tokens'], 0)
        
        # Simulate usage
        self.llm._update_usage({'total_tokens': 10})
        usage = self.llm.get_usage()
        self.assertEqual(usage['total_tokens'], 10)
        
    def test_template_generation(self):
        """Test template-based text generation"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'text': 'test response with template'}],
            'usage': {'total_tokens': 15}
        }
        self.llm.session.post.return_value = mock_response
        
        # Test template generation
        result = self.llm.generate_with_template(
            "Hello {name}, how are you?",
            {"name": "TestUser"}
        )
        self.assertEqual(result, "test response with template")
        
    def test_template_streaming(self):
        """Test template-based streaming generation"""
        # Create a new LLM instance with not-needed API key
        llm = MistralNemoImplementation(self.base_url, "not-needed")
        
        # Setup mock response with proper byte encoding
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_response.iter_content.return_value = [
            b"template chunk1", 
            b"template chunk2"
        ]
        
        # Create a mock session
        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        llm.session = mock_session
        
        # Test template streaming
        result = list(llm.stream_with_template(
            "Hello {name}, how are you?",
            {"name": "TestUser"}
        ))
        self.assertEqual(result, [
            "template chunk1", 
            "template chunk2"
        ])
        # Verify the template was formatted correctly
        mock_session.post.assert_called_once_with(
            f"{llm.base_url}/completions",
            json={
                "prompt": "Hello TestUser, how are you?",
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": True
            },
            headers={"Authorization": "Bearer not-needed"},
            stream=True
        )
        
    def test_invalid_template(self):
        """Test invalid template handling"""
        with self.assertRaises(ValueError):
            self.llm.generate_with_template(
                "Hello {name, how are you?",  # Invalid template
                {"name": "TestUser"}
            )

    @patch('llm.mistral_nemo.requests.Session')
    def test_connection_success(self, mock_session):
        """Test successful connection"""
        # Create a mock session instance with proper response
        mock_session_instance = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new LLM instance with the mocked session
        llm = MistralNemoImplementation(self.base_url, self.api_key)
        llm.session = mock_session_instance
        
        result = llm.test_connection()
        self.assertTrue(result)
        mock_session_instance.get.assert_called_once()

    def test_connection_failure(self):
        """Test failed connection"""
        # Force connection error by raising an exception
        self.mock_session.get.side_effect = requests.exceptions.ConnectionError()
        
        result = self.llm.test_connection()
        self.assertFalse(result)
        self.mock_session.get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
