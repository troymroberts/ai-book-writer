"""Tests for the LLM interface implementation"""
import unittest
from unittest.mock import Mock, patch
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
        self.api_key = "test-key"
        self.llm = MistralNemoImplementation(self.base_url, self.api_key)
        
        # Setup LiteLLM implementations
        self.openai_llm = OpenAIImplementation("gpt-4", self.api_key)
        self.deepseek_llm = DeepSeekImplementation("chat", self.api_key)
        self.gemini_llm = GeminiImplementation("gemini-pro", self.api_key)
        self.groq_llm = GroqImplementation("mixtral-8x7b-32768", self.api_key)
        
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
        
    @patch('llm.litellm_base.litellm.completion')
    def test_openai_generate(self, mock_completion):
        """Test OpenAI text generation"""
        mock_completion.return_value = {
            'choices': [{'message': {'content': 'test response'}}],
            'usage': {'total_tokens': 10}
        }
        
        result = self.openai_llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('llm.litellm_base.litellm.completion')
    def test_deepseek_generate(self, mock_completion):
        """Test DeepSeek text generation"""
        mock_completion.return_value = {
            'choices': [{'message': {'content': 'test response'}}],
            'usage': {'total_tokens': 10}
        }
        
        result = self.deepseek_llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('llm.litellm_base.litellm.completion')
    def test_gemini_generate(self, mock_completion):
        """Test Gemini text generation"""
        mock_completion.return_value = {
            'choices': [{'message': {'content': 'test response'}}],
            'usage': {'total_tokens': 10}
        }
        
        result = self.gemini_llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('llm.litellm_base.litellm.completion')
    def test_groq_generate(self, mock_completion):
        """Test Groq text generation"""
        mock_completion.return_value = {
            'choices': [{'message': {'content': 'test response'}}],
            'usage': {'total_tokens': 10}
        }
        
        result = self.groq_llm.generate("test prompt")
        self.assertEqual(result, "test response")
        
    @patch('llm.mistral_nemo.requests.Session')
    def test_stream(self, mock_session):
        """Test streaming generation"""
        # Setup mock response
        mock_response = Mock()
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_session.return_value.post.return_value = mock_response
        
        # Test streaming
        result = list(self.llm.stream("test prompt"))
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
        # Setup mock response
        mock_response = Mock()
        mock_response.iter_content.return_value = [b"template chunk1", b"template chunk2"]
        self.llm.session.post.return_value = mock_response
        
        # Test template streaming
        result = list(self.llm.stream_with_template(
            "Hello {name}, how are you?",
            {"name": "TestUser"}
        ))
        self.assertEqual(result, ["template chunk1", "template chunk2"])
        
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
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response
        
        result = self.llm.test_connection()
        self.assertTrue(result)

    @patch('llm.mistral_nemo.requests.Session')
    def test_connection_failure(self, mock_session):
        """Test failed connection"""
        mock_session.return_value.get.side_effect = Exception("Connection failed")
        
        result = self.llm.test_connection()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
